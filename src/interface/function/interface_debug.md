# interface_debug.py

**Version:** 2025-12-08_1  
**Module:** DEBUG Interface  
**Layer:** Interface  
**Lines:** 61

---

## Purpose

DEBUG interface router (INT-14). Routes 7 debug operations to core implementations using simple if/elif dispatch.

---

## Architecture

**SUGA Pattern:**
```
Gateway → interface_debug.py → debug_core.py
```

**Operations Routed:** 7 total
- log
- timing
- generate_correlation_id
- generate_trace_id
- set_trace_context
- get_trace_context
- clear_trace_context

---

## Functions

### execute_debug_operation()

**Purpose:** Route debug operations to core implementations

**Signature:**
```python
def execute_debug_operation(operation: str, **kwargs) -> Any
```

**Parameters:**
- `operation` - Operation name (e.g., 'log', 'timing')
- `**kwargs` - Operation-specific parameters

**Returns:**
Operation result (varies by operation)

**Behavior:**
1. Checks if DEBUG available (imports succeeded)
2. Routes via if/elif chain (7 operations)
3. Calls handler function with kwargs
4. Returns result

**Error Scenarios:**
- DEBUG unavailable → RuntimeError with import error details
- Unknown operation → ValueError with operation name

**Usage:**
```python
from interface_debug import execute_debug_operation

# Via interface
result = execute_debug_operation('log', corr_id='abc123', scope='ALEXA', message='Test')

# Via gateway (preferred)
from gateway import debug_log
debug_log('abc123', 'ALEXA', 'Test')
```

**Performance:** <1ms (if/elif chain overhead only)

---

## Import Protection

**Pattern:**
```python
try:
    from debug_core import (...)
    _DEBUG_AVAILABLE = True
    _DEBUG_IMPORT_ERROR = None
except ImportError as e:
    _DEBUG_AVAILABLE = False
    _DEBUG_IMPORT_ERROR = str(e)
```

**Purpose:** Graceful degradation if debug_core unavailable

**Behavior:**
- Import success → _DEBUG_AVAILABLE = True
- Import failure → Store error, raise on use

---

## Error Handling

### Import Failure
If debug_core fails to import:
- `_DEBUG_AVAILABLE` = False
- `_DEBUG_IMPORT_ERROR` = Error message
- All operations raise RuntimeError with details

### Unknown Operation
If operation not recognized:
- Raises ValueError with operation name
- Lists valid operations (implicitly via code)

---

## Core Module Dependencies

**Import:**
```python
from debug_core import (
    debug_log,
    debug_timing,
    generate_correlation_id,
    generate_trace_id,
    set_trace_context,
    get_trace_context,
    clear_trace_context
)
```

**Total:** 7 functions from 1 module

---

## Dispatch Pattern

**Structure:**
```python
if operation == 'log':
    return debug_log(**kwargs)
elif operation == 'timing':
    return debug_timing(**kwargs)
# ... etc
```

**Why not Dictionary Dispatch:**
- Only 7 operations (simple if/elif sufficient)
- Context manager (debug_timing) needs special handling
- Direct function calls clearer for small operation count

**Performance:**
- If/elif: O(n) lookup, n=7 max
- Dictionary: O(1) lookup
- Difference: ~0.001ms (negligible for 7 operations)

---

## Integration with Gateway

**Gateway Integration:**
```python
# In gateway.py
from gateway_wrappers_debug import *

# Or explicit imports
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

## Dependencies

**Internal:**
- debug_core (all 7 functions)

**External:**
- typing (type hints)

---

## Related Files

**Core:**
- debug_core.py - Core debug implementations
- debug_config.py - Debug configuration

**Gateway:**
- gateway_wrappers_debug.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version for hierarchical debug system
- 7 operations routed (log, timing, IDs, trace context)
- Import protection pattern
- Simple if/elif dispatch (sufficient for 7 operations)
- Minimal docstrings per SIMA standards
