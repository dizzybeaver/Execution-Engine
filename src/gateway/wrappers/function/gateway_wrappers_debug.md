# gateway_wrappers_debug.py

**Version:** 2025-12-08_1  
**Module:** DEBUG Interface  
**Layer:** Gateway  
**Lines:** 98

---

## Purpose

Gateway wrappers for DEBUG interface (INT-14). Provides 7 wrapper functions with lazy imports.

---

## Architecture

**SUGA Layer:** Gateway  
**Interface:** DEBUG (INT-14)  
**Pattern:** Lazy import wrappers

**Flow:**
```
Gateway wrapper → interface_debug → debug_core
```

---

## Functions

### debug_log()

**Purpose:** Single-line debug logging with hierarchical control

**Signature:**
```python
def debug_log(corr_id: str, scope: str, message: str, **context) -> None
```

**Parameters:**
- `corr_id` - Correlation ID
- `scope` - Debug scope (ALEXA, HA, CACHE, etc.)
- `message` - Debug message
- `**context` - Additional context

**Usage:**
```python
from gateway import debug_log

debug_log(corr_id, "ALEXA", "Starting enrichment", entity_id="light.kitchen")
```

---

### debug_timing()

**Purpose:** Timing context manager with hierarchical control

**Signature:**
```python
def debug_timing(corr_id: str, scope: str, operation: str, **context)
```

**Parameters:**
- `corr_id` - Correlation ID
- `scope` - Debug scope
- `operation` - Operation name
- `**context` - Additional context

**Usage:**
```python
from gateway import debug_timing

with debug_timing(corr_id, "ALEXA", "enrichment"):
    # operation code
```

---

### generate_correlation_id()

**Purpose:** Generate correlation ID for request tracking

**Signature:**
```python
def generate_correlation_id() -> str
```

**Returns:** 13-character correlation ID

**Usage:**
```python
from gateway import generate_correlation_id

corr_id = generate_correlation_id()
```

---

### generate_trace_id()

**Purpose:** Generate trace ID for distributed tracing

**Signature:**
```python
def generate_trace_id() -> str
```

**Returns:** Full UUID as string

**Usage:**
```python
from gateway import generate_trace_id

trace_id = generate_trace_id()
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

**Usage:**
```python
from gateway import set_trace_context

set_trace_context(trace_id, user="alice", operation="discovery")
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

**Returns:** Context dict or None

**Usage:**
```python
from gateway import get_trace_context

context = get_trace_context(trace_id)
```

---

### clear_trace_context()

**Purpose:** Clear trace context

**Signature:**
```python
def clear_trace_context(trace_id: str) -> None
```

**Parameters:**
- `trace_id` - Trace ID

**Usage:**
```python
from gateway import clear_trace_context

clear_trace_context(trace_id)
```

---

## Lazy Import Pattern

**All wrappers use lazy imports:**
```python
def debug_log(corr_id: str, scope: str, message: str, **context) -> None:
    from interface_debug import execute_debug_operation
    return execute_debug_operation('log', corr_id=corr_id, scope=scope, 
                                   message=message, **context)
```

**Purpose:** Minimize cold start time (LMMS pattern)

**Performance:**
- First call: ~5-10ms (import + execution)
- Subsequent calls: <1ms (cached import)

---

## Integration with Gateway

**In gateway.py:**
```python
# Import all DEBUG wrappers
from gateway_wrappers_debug import (
    debug_log,
    debug_timing,
    generate_correlation_id,
    generate_trace_id,
    set_trace_context,
    get_trace_context,
    clear_trace_context
)

# Export
__all__ = [
    # ... existing exports
    # DEBUG operations
    'debug_log',
    'debug_timing',
    'generate_correlation_id',
    'generate_trace_id',
    'set_trace_context',
    'get_trace_context',
    'clear_trace_context'
]
```

---

## Usage Examples

**Before (Verbose Debug Code):**
```python
# 10+ lines per debug statement
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
ALEXA_DEBUG = os.environ.get('ALEXA_DEBUG_MODE', 'false').lower() == 'true'

if DEBUG_MODE and ALEXA_DEBUG:
    log_debug(f"[{correlation_id}] [ALEXA-DEBUG] Starting enrichment (entity_id={entity_id})")
```

**After (Single Line):**
```python
# 1 line
gateway.debug_log(correlation_id, "ALEXA", "Starting enrichment", entity_id=entity_id)
```

**Before (Verbose Timing Code):**
```python
# 10+ lines per timing block
DEBUG_TIMING = os.environ.get('ALEXA_DEBUG_TIMING', 'false').lower() == 'true'

if DEBUG_TIMING:
    start = time.perf_counter()

# ... operation ...

if DEBUG_TIMING:
    duration_ms = (time.perf_counter() - start) * 1000
    log_info(f"[{correlation_id}] [ALEXA-TIMING] enrichment: {duration_ms:.2f}ms")
```

**After (Context Manager):**
```python
# 2 lines
with gateway.debug_timing(correlation_id, "ALEXA", "enrichment"):
    # ... operation ...
```

---

## Dependencies

**Internal:**
- interface_debug (execute_debug_operation)

**External:**
- typing (type hints)

---

## Related Files

**Interface:**
- interface_debug.py - DEBUG interface router

**Core:**
- debug_core.py - Core debug implementations
- debug_config.py - Debug configuration

---

## Changelog

### 2025-12-08_1
- Initial version for hierarchical debug system
- 7 wrapper functions (log, timing, IDs, trace context)
- Lazy import pattern (LMMS)
- Minimal docstrings per SIMA standards
- Complete __all__ exports
