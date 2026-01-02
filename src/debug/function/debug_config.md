# debug_config.py

**Version:** 2025-12-08_1  
**Module:** DEBUG Interface  
**Layer:** Core  
**Lines:** 56

---

## Purpose

Debug configuration with hierarchical control. Manages master DEBUG_MODE switch and 14 scope-specific debug/timing flags.

---

## Architecture

**Hierarchical Control:**
```
DEBUG_MODE (master)
    └─> {SCOPE}_DEBUG_MODE (debug logging)
    └─> {SCOPE}_DEBUG_TIMING (timing measurements)
```

**14 Debug Scopes:**
ALEXA, HA, DEVICES, CACHE, HTTP, CONFIG, SECURITY, METRICS, CIRCUIT_BREAKER, SINGLETON, GATEWAY, INIT, WEBSOCKET, LOGGING

---

## Classes

### DebugConfig

**Purpose:** Manage hierarchical debug configuration

**Attributes:**
- `master_enabled` - Master DEBUG_MODE switch (bool)
- `scopes` - Dict of scope configurations (Dict[str, Dict[str, bool]])

**Methods:**

#### is_debug_enabled()

**Signature:**
```python
def is_debug_enabled(self, scope: str) -> bool
```

**Behavior:**
1. Check master switch (instant return if False)
2. Check scope-specific debug flag
3. Return combined result

**Performance:** <1ms (two dict lookups)

#### is_timing_enabled()

**Signature:**
```python
def is_timing_enabled(self, scope: str) -> bool
```

**Behavior:**
1. Check master switch (instant return if False)
2. Check scope-specific timing flag
3. Return combined result

**Performance:** <1ms (two dict lookups)

---

## Functions

### get_debug_config()

**Purpose:** Get singleton DebugConfig instance

**Signature:**
```python
def get_debug_config() -> DebugConfig
```

**Returns:** Singleton DebugConfig instance

**Behavior:**
1. Check if singleton exists
2. Create if needed (reads environment variables)
3. Return singleton

**Thread Safety:** Safe for Lambda (single-threaded)

---

## Environment Variables

**Master Control:**
```bash
DEBUG_MODE=true|false  # Default: false
```

**Scope-Specific Debug:**
```bash
ALEXA_DEBUG_MODE=true|false
HA_DEBUG_MODE=true|false
DEVICES_DEBUG_MODE=true|false
CACHE_DEBUG_MODE=true|false
HTTP_DEBUG_MODE=true|false
CONFIG_DEBUG_MODE=true|false
SECURITY_DEBUG_MODE=true|false
METRICS_DEBUG_MODE=true|false
CIRCUIT_BREAKER_DEBUG_MODE=true|false
SINGLETON_DEBUG_MODE=true|false
GATEWAY_DEBUG_MODE=true|false
INIT_DEBUG_MODE=true|false
WEBSOCKET_DEBUG_MODE=true|false
LOGGING_DEBUG_MODE=true|false
```

**Scope-Specific Timing:**
```bash
ALEXA_DEBUG_TIMING=true|false
HA_DEBUG_TIMING=true|false
# ... (same pattern for all 14 scopes)
```

---

## Usage

```python
from debug_config import get_debug_config

config = get_debug_config()

# Check if debug enabled for scope
if config.is_debug_enabled('ALEXA'):
    # Debug logging

# Check if timing enabled
if config.is_timing_enabled('CACHE'):
    # Timing measurement
```

---

## Performance

**Initialization:** Once per Lambda container (~1ms)  
**Lookups:** <1ms (dict access)  
**Memory:** ~2KB (14 scopes × 2 flags)

---

## Dependencies

**External:**
- os (environment variable access)
- typing (type hints)

---

## Related Files

**Core:**
- debug_core.py - Uses get_debug_config() for hierarchical control

**Interface:**
- interface_debug.py - DEBUG interface router

**Gateway:**
- gateway_wrappers_debug.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version for hierarchical debug system
- Master DEBUG_MODE switch
- 14 scope-specific debug/timing flags
- Singleton pattern for configuration
- Fast path when master disabled
