# DEBUG Interface Directory Structure

**Version:** 2025-12-08_1  
**Status:** Phase 1.3 Complete

---

## File Organization

```
/src/
├── interface_debug.py              (61 lines)  - Router at root level
├── gateway_wrappers_debug.py       (98 lines)  - Gateway wrappers at root level
│
└── debug/                           - DEBUG implementation subdirectory
    ├── __init__.py                 (32 lines)  - Package init
    ├── debug_config.py             (56 lines)  - Hierarchical configuration
    └── debug_core.py               (148 lines) - Core debug functions
```

---

## Import Patterns

### From Root Level (interface_debug.py)
```python
from debug import (
    debug_log,
    debug_timing,
    generate_correlation_id,
    generate_trace_id,
    set_trace_context,
    get_trace_context,
    clear_trace_context
)
```

### Within debug/ Directory (debug_core.py)
```python
# Relative imports for same package
from .debug_config import get_debug_config
```

### From Gateway Level (gateway_wrappers_debug.py)
```python
from interface_debug import execute_debug_operation
# Gateway never directly imports from debug/ subdirectory
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → interface_debug.py → debug/*.py  
✅ **Lazy Loading:** All imports at function level  
✅ **No Circular Imports:** Clean dependency flow  
✅ **Subdirectory Isolation:** Implementation details in debug/  
✅ **Package Structure:** Follows diagnosis/ pattern exactly

---

## Total Line Count

- **Root Level:** 159 lines (interface + wrappers)
- **debug/ Directory:** 236 lines (3 files + init)
- **Total:** 395 lines across 5 files

---

## Comparison with DIAGNOSIS Interface

**DIAGNOSIS Structure:**
```
/diagnosis/
  ├── __init__.py
  ├── diagnosis_imports.py
  ├── diagnosis_performance.py
  ├── diagnosis_core.py
  └── health.py
/interface_diagnosis.py
/gateway_wrappers_diagnosis.py
```

**DEBUG Structure:**
```
/debug/
  ├── __init__.py
  ├── debug_config.py
  └── debug_core.py
/interface_debug.py
/gateway_wrappers_debug.py
```

**Pattern Consistency:** ✅ Both follow identical SUGA architecture

---

## Lambda Deployment

All files deploy together as single package:
- interface_debug.py routes operations
- debug/ subdirectory contains implementations
- Lazy imports minimize cold start impact
- AWS Lambda compatible (sys.path fix in lambda_function.py handles subdirectories)

---

## Environment Variables

**Master Control:**
```bash
DEBUG_MODE=true|false  # Default: false
```

**Scope-Specific (14 scopes):**
```bash
ALEXA_DEBUG_MODE=true|false
ALEXA_DEBUG_TIMING=true|false
HA_DEBUG_MODE=true|false
HA_DEBUG_TIMING=true|false
# ... (repeat for all 14 scopes)
```

**14 Scopes:** ALEXA, HA, DEVICES, CACHE, HTTP, CONFIG, SECURITY, METRICS, CIRCUIT_BREAKER, SINGLETON, GATEWAY, INIT, WEBSOCKET, LOGGING

---

## Usage Examples

**Before (10+ lines per statement):**
```python
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
ALEXA_DEBUG = os.environ.get('ALEXA_DEBUG_MODE', 'false').lower() == 'true'

if DEBUG_MODE and ALEXA_DEBUG:
    log_debug(f"[{corr_id}] [ALEXA-DEBUG] Starting enrichment (entity_id={entity_id})")
```

**After (1 line):**
```python
gateway.debug_log(corr_id, "ALEXA", "Starting enrichment", entity_id=entity_id)
```

---

## Files Created

1. **debug/__init__.py** (32 lines) ✓
   - Package exports
   - Groups functions logically

2. **debug/debug_config.py** (56 lines) ✓
   - Hierarchical configuration
   - Master + scope switches
   - Singleton pattern

3. **debug/debug_core.py** (148 lines) ✓
   - 7 core functions
   - Lazy gateway imports
   - Relative package imports

4. **interface_debug.py** (61 lines) ✓
   - Router at root level
   - Imports from debug package
   - 7 operations routed

5. **gateway_wrappers_debug.py** (98 lines) ✓
   - Gateway wrappers at root level
   - Lazy imports to interface
   - 7 wrapper functions

---

## Documentation Created

1. **debug_config.md** ✓
2. **debug_core.md** ✓
3. **interface_debug.md** ✓
4. **gateway_wrappers_debug.md** ✓

---

## Next Integration Step

**Update gateway.py:**
```python
# Import DEBUG wrappers
from gateway_wrappers_debug import (
    debug_log,
    debug_timing,
    generate_correlation_id,
    generate_trace_id,
    set_trace_context,
    get_trace_context,
    clear_trace_context
)

# Add to __all__
__all__ = [
    # ... existing exports
    # DEBUG operations (INT-14)
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

**END OF STRUCTURE DOCUMENT**
