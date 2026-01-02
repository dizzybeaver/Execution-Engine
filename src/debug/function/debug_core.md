# debug_core.py

**Version:** 2025-12-08_1  
**Module:** DEBUG Interface  
**Layer:** Core  
**Lines:** 148

---

## Purpose

Core debug functionality with hierarchical control. Provides debug logging, timing measurements, and trace correlation.

---

## Functions

### debug_log()

**Purpose:** Single-line debug logging with hierarchical control

**Signature:**
```python
def debug_log(corr_id: str, scope: str, message: str, **context) -> None
```

**Parameters:**
- `corr_id` - Correlation ID for request tracking
- `scope` - Debug scope (ALEXA, HA, CACHE, etc.)
- `message` - Debug message
- `**context` - Additional context to log

**Behavior:**
1. Check if debug enabled for scope (fast return if disabled)
2. Format message with correlation ID and scope
3. Append context if provided
4. Log via gateway.log_debug()

**Performance:**
- Disabled: <1ms (instant return)
- Enabled: ~5-10ms (formatting + logging)

**Usage:**
```python
import gateway

gateway.debug_log(corr_id, "ALEXA", "Starting enrichment", entity_id="light.kitchen")
```

---

### debug_timing()

**Purpose:** Timing context manager with hierarchical control

**Signature:**
```python
@contextmanager
def debug_timing(corr_id: str, scope: str, operation: str, **context)
```

**Parameters:**
- `corr_id` - Correlation ID
- `scope` - Debug scope
- `operation` - Operation name
- `**context` - Additional context

**Behavior:**
1. Log operation start if debug enabled
2. Start timing if timing enabled
3. Yield control to operation
4. Log duration if timing enabled

**Performance:**
- Disabled: <1ms (no measurement)
- Enabled: ~0.1ms overhead + operation duration

**Usage:**
```python
import gateway

with gateway.debug_timing(corr_id, "ALEXA", "enrichment"):
    # operation code
    result = enrich_state(entity_id)
```

---

### generate_correlation_id()

**Purpose:** Generate correlation ID for request tracking

**Signature:**
```python
def generate_correlation_id() -> str
```

**Returns:** 13-character correlation ID (UUID prefix)

**Behavior:**
1. Generate UUID
2. Take first 13 characters
3. Return as string

**Performance:** ~1ms

**Usage:**
```python
import gateway

corr_id = gateway.generate_correlation_id()
gateway.debug_log(corr_id, "ALEXA", "Request started")
```

---

### generate_trace_id()

**Purpose:** Generate trace ID for distributed tracing

**Signature:**
```python
def generate_trace_id() -> str
```

**Returns:** Full UUID as string

**Behavior:**
1. Generate UUID
2. Convert to string
3. Return

**Performance:** ~1ms

**Usage:**
```python
import gateway

trace_id = gateway.generate_trace_id()
gateway.set_trace_context(trace_id, user="alice", operation="discovery")
```

---

### set_trace_context()

**Purpose:** Set trace context for log correlation

**Signature:**
```python
def set_trace_context(trace_id: str, **context) -> None
```

**Parameters:**
- `trace_id` - Trace ID
- `**context` - Context to store

**Behavior:**
1. Create global trace context dict if needed
2. Store context with trace ID
3. Add timestamp

**Performance:** ~1ms

**Usage:**
```python
import gateway

trace_id = gateway.generate_trace_id()
gateway.set_trace_context(trace_id, user="alice", operation="discovery")
```

---

### get_trace_context()

**Purpose:** Get trace context by ID

**Signature:**
```python
def get_trace_context(trace_id: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `trace_id` - Trace ID

**Returns:** Context dict or None if not found

**Behavior:**
1. Check if trace context exists
2. Return context for trace ID
3. Return None if not found

**Performance:** <1ms (dict lookup)

**Usage:**
```python
import gateway

context = gateway.get_trace_context(trace_id)
if context:
    print(f"User: {context['user']}")
```

---

### clear_trace_context()

**Purpose:** Clear trace context

**Signature:**
```python
def clear_trace_context(trace_id: str) -> None
```

**Parameters:**
- `trace_id` - Trace ID to clear

**Behavior:**
1. Check if trace context exists
2. Remove trace ID entry
3. Silently succeed if not found

**Performance:** <1ms (dict delete)

**Usage:**
```python
import gateway

gateway.clear_trace_context(trace_id)
```

---

## Patterns

**Hierarchical Debug Pattern:**
```python
# Before (10+ lines)
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
ALEXA_DEBUG = os.environ.get('ALEXA_DEBUG_MODE', 'false').lower() == 'true'

if DEBUG_MODE and ALEXA_DEBUG:
    log_debug(f"[{corr_id}] [ALEXA-DEBUG] Starting enrichment (entity_id={entity_id})")

# After (1 line)
gateway.debug_log(corr_id, "ALEXA", "Starting enrichment", entity_id=entity_id)
```

**Timing Pattern:**
```python
# Before (10+ lines)
DEBUG_TIMING = os.environ.get('ALEXA_DEBUG_TIMING', 'false').lower() == 'true'

if DEBUG_TIMING:
    start = time.perf_counter()

# ... operation ...

if DEBUG_TIMING:
    duration_ms = (time.perf_counter() - start) * 1000
    log_info(f"[{corr_id}] [ALEXA-TIMING] enrichment: {duration_ms:.2f}ms")

# After (2 lines)
with gateway.debug_timing(corr_id, "ALEXA", "enrichment"):
    # ... operation ...
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DEBUG (INT-14)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From gateway (preferred)
from gateway import debug_log, debug_timing, generate_correlation_id

# Direct (for testing)
from debug_core import debug_log, debug_timing
```

---

## Dependencies

**Internal:**
- debug_config (get_debug_config)
- gateway (log_debug, log_info) - lazy import

**External:**
- time (timing measurements)
- uuid (ID generation)
- typing (type hints)
- contextlib (context manager)

---

## Related Files

**Configuration:**
- debug_config.py - Hierarchical debug configuration

**Interface:**
- interface_debug.py - DEBUG interface router

**Gateway:**
- gateway_wrappers_debug.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version for hierarchical debug system
- debug_log() with scope-based control
- debug_timing() context manager
- Correlation and trace ID generation
- Trace context management
- Fast path when debug disabled (instant return)
