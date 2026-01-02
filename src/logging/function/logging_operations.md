# logging_operations.py

**Version:** 2025-12-08_1  
**Module:** LOGGING Interface  
**Layer:** Core  
**Lines:** 74

---

## Purpose

Operation dispatcher with performance monitoring. **Deprecated** - retained for backward compatibility. New code should use `interface_logging.execute_logging_operation()` instead.

---

## Configuration

### Environment Variables

```bash
USE_GENERIC_OPERATIONS=true     # Enable generic dispatcher (default: true)
```

**Note:** This setting is legacy and has no effect in current implementation.

---

## Functions

### execute_logging_operation()

**Purpose:** Universal logging operation executor with dispatcher performance monitoring

**Status:** DEPRECATED - Use interface_logging instead

**Signature:**
```python
def execute_logging_operation(operation: LogOperation, *args, **kwargs)
```

**Parameters:**
- `operation` - LogOperation enum value or string
- `*args` - Positional arguments (unused)
- `**kwargs` - Operation parameters

**Returns:** Result from operation or None on error

**Behavior:**
1. Record start time
2. Route through interface_logging:
   ```python
   from interface_logging import execute_logging_operation as interface_execute
   result = interface_execute(operation.value, **kwargs)
   ```
3. Calculate duration
4. Record dispatcher metric
5. Return result

**Error Handling:**
- Catches all exceptions
- Logs error to Python logger
- Returns None on error

**Performance Monitoring:**
- Measures operation duration
- Records via METRICS interface
- Includes operation name and duration_ms

**Usage (Legacy):**
```python
from logging.logging_operations import execute_logging_operation
from logging.logging_types import LogOperation

execute_logging_operation(
    LogOperation.LOG_INFO,
    message="System initialized"
)
```

**Recommended (New Code):**
```python
from interface_logging import execute_logging_operation

execute_logging_operation(
    'log_info',
    message="System initialized"
)
```

**Even Better (Use Gateway):**
```python
import gateway

gateway.log_info("System initialized")
```

**Performance:** <2ms (includes interface routing + metric recording)

---

### _record_dispatcher_metric() (Internal)

**Purpose:** Record dispatcher performance metric via METRICS interface

**Signature:**
```python
def _record_dispatcher_metric(operation, duration_ms: float)
```

**Parameters:**
- `operation` - LogOperation enum or string
- `duration_ms` - Operation duration in milliseconds

**Behavior:**
1. Try to import gateway:
   ```python
   from gateway import execute_operation, GatewayInterface
   ```
2. Call METRICS interface:
   ```python
   execute_operation(
       GatewayInterface.METRICS,
       'record_dispatcher_timing',
       interface_name='LoggingCore',
       operation_name=operation.value,
       duration_ms=duration_ms
   )
   ```
3. Silently ignore all exceptions

**Metric Data:**
- `interface_name`: "LoggingCore"
- `operation_name`: Operation name (e.g., "log_info")
- `duration_ms`: Duration in milliseconds

**Purpose:** Track dispatcher performance for optimization

**Performance:** <0.5ms (lazy import + metric call)

---

## Deprecation Notice

**Status:** DEPRECATED as of 2025-12-08_1

**Reason:**
- Redundant layer - interface_logging already routes operations
- Adds unnecessary overhead (~0.5ms per call)
- Maintained only for backward compatibility

**Migration Path:**

**Old Code:**
```python
from logging.logging_operations import execute_logging_operation
from logging.logging_types import LogOperation

execute_logging_operation(
    LogOperation.LOG_INFO,
    message="System started"
)
```

**Step 1 - Use Interface:**
```python
from interface_logging import execute_logging_operation

execute_logging_operation(
    'log_info',
    message="System started"
)
```

**Step 2 - Use Gateway (Best):**
```python
import gateway

gateway.log_info("System started")
```

---

## Performance Impact

### Legacy Path (This Module)
```
User Code
  → logging_operations.execute_logging_operation()
    → interface_logging.execute_logging_operation()
      → logging_core._execute_log_info_implementation()
        → logging_manager.get_logging_core().log()

Overhead: ~0.5ms extra (lazy import + metric recording)
```

### Direct Path (Recommended)
```
User Code
  → interface_logging.execute_logging_operation()
    → logging_core._execute_log_info_implementation()
      → logging_manager.get_logging_core().log()

Overhead: None (direct routing)
```

### Gateway Path (Best)
```
User Code
  → gateway.log_info()
    → gateway_core.execute_operation()
      → interface_logging.execute_logging_operation()
        → logging_core._execute_log_info_implementation()
          → logging_manager.get_logging_core().log()

Overhead: Minimal (<0.2ms for gateway routing)
Benefits: Consistent API, automatic error handling
```

---

## Exports

```python
__all__ = [
    'execute_logging_operation',
]
```

---

## Dependencies

**Internal:**
- `logging.logging_types` (LogOperation)
- `interface_logging` (execute_logging_operation) - lazy import
- `gateway` (execute_operation, GatewayInterface) - lazy import

**External:**
- `os` - Environment variable access
- `time` - Performance timing
- `logging` - Python logger

---

## Use Cases

### When To Use

**Backward Compatibility:**
- Existing code already using this module
- Cannot refactor immediately
- Need LogOperation enum support

**Testing:**
- Testing dispatcher performance monitoring
- Verifying metric recording

### When NOT To Use

**New Code:**
- Use interface_logging or gateway instead
- Avoid LogOperation enum (use strings)
- No need for extra dispatcher layer

**Performance-Critical:**
- Extra ~0.5ms overhead per call
- Use interface_logging directly

---

## Migration Examples

### Example 1: Simple Log

**Before:**
```python
from logging.logging_operations import execute_logging_operation
from logging.logging_types import LogOperation

execute_logging_operation(
    LogOperation.LOG_INFO,
    message="User logged in",
    user_id="user123"
)
```

**After:**
```python
import gateway

gateway.log_info(
    "User logged in",
    user_id="user123"
)
```

---

### Example 2: Error Log

**Before:**
```python
from logging.logging_operations import execute_logging_operation
from logging.logging_types import LogOperation

execute_logging_operation(
    LogOperation.LOG_ERROR,
    message="Database connection failed",
    error=str(exception)
)
```

**After:**
```python
import gateway

gateway.log_error(
    "Database connection failed",
    error=exception
)
```

---

### Example 3: Operation Logging

**Before:**
```python
from logging.logging_operations import execute_logging_operation
from logging.logging_types import LogOperation

execute_logging_operation(
    LogOperation.LOG_OPERATION_START,
    operation_name="user_authentication"
)
# ... operation ...
execute_logging_operation(
    LogOperation.LOG_OPERATION_SUCCESS,
    operation_name="user_authentication",
    duration_ms=45.2
)
```

**After:**
```python
import gateway

gateway.log_operation_start("user_authentication")
# ... operation ...
gateway.log_operation_success("user_authentication", duration_ms=45.2)
```

---

## Related Files

**Interface:**
- interface_logging.py - Target for migration (direct routing)

**Gateway:**
- gateway/wrappers/gateway_wrappers_logging.py - Best migration target

**Core:**
- logging_core.py - Final destination for all operations
- logging_types.py - LogOperation enum (legacy)

---

## Performance Metrics

### Timing Breakdown

**execute_logging_operation():**
- Lazy import interface_logging: ~0.2ms (first call only)
- Route to interface: ~0.1ms
- Metric recording: ~0.2ms
- Total overhead: ~0.5ms per call

**Alternative (interface_logging directly):**
- No lazy import needed
- Direct routing: 0ms overhead
- No metric recording: 0ms

**Savings:** ~0.5ms per log call by using interface_logging directly

**Volume Impact:**
- 1000 logs: 500ms saved
- 10000 logs: 5s saved

---

## Changelog

### 2025-12-08_1
- **DEPRECATED:** Module marked as deprecated
- Moved to logging/ subdirectory
- Updated imports for subdirectory structure
- Removed _MANAGER reference
- Routes through interface_logging for compatibility

### 2025-10-14_01
- Initial implementation with generic operations
- Added dispatcher performance monitoring
- Integrated with METRICS interface
