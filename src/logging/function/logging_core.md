# logging_core.py

**Version:** 2025-12-08_1  
**Module:** LOGGING Interface  
**Layer:** Core  
**Lines:** 257

---

## Purpose

Core logging implementation functions with security hardening and debug integration. Provides 9 implementation functions called by interface_logging.py with exception sanitization (CVE-LOG-004 mitigation).

---

## Configuration

### Environment Variables

**Security:**
```bash
SANITIZE_EXCEPTIONS=true     # Exception sanitization (default: true)
LAMBDA_MODE=normal          # Lambda execution mode
```

**Debug:**
```bash
DEBUG_MODE=true             # Master debug switch
LOGGING_DEBUG_MODE=true     # Logging-specific debug
```

---

## Functions

### _sanitize_exception_details()

**Purpose:** Sanitize exception details to prevent information disclosure (CVE-LOG-004)

**Signature:**
```python
def _sanitize_exception_details(
    error: Union[str, Exception], 
    include_traceback: bool = False
) -> str
```

**Parameters:**
- `error` - Exception object or error string
- `include_traceback` - Whether to include sanitized traceback

**Returns:** Sanitized error description string

**Behavior:**

1. **None Check:** Return "No error details" if error is None

2. **Type Extraction:**
   - If Exception: Get type name and message
   - If string: Use "Error" as type

3. **Length Limit:** Truncate message to 500 characters

4. **Development Mode** (`SANITIZE_EXCEPTIONS=false`):
   - Return full details
   - Include complete traceback if requested

5. **Production Mode** (`SANITIZE_EXCEPTIONS=true`):
   - Remove AWS Lambda paths:
     - `/var/task/` → `[APP]/`
     - `/opt/python/` → `[LIB]/`
     - `/usr/local/` → `[SYS]/`
   - Remove SSM parameter paths:
     - `/lambda-execution-engine/` → `[PARAM]/`
   - Redact credentials:
     - `password=xxx` → `password=***`
     - `token=xxx` → `token=***`
   - Optional minimal traceback:
     - Extract last frame only
     - Show filename (no path) and line number
     - Format: `at filename.py:123`

**Example Output (Production):**
```
ValueError: Invalid parameter
  at logging_core.py:145
```

**Example Output (Development):**
```
ValueError: Invalid parameter
Full traceback:
  File "/var/task/logging_core.py", line 145, in validate_param
    raise ValueError("Invalid parameter")
```

**Security:** Prevents CVE-LOG-004 information disclosure

**Usage:**
```python
try:
    operation()
except Exception as e:
    sanitized = _sanitize_exception_details(e, include_traceback=True)
    log_error(sanitized)
```

---

### _execute_log_info_implementation()

**Purpose:** Log info message (message already sanitized by interface_logging)

**Signature:**
```python
def _execute_log_info_implementation(message: str, **kwargs) -> None
```

**Parameters:**
- `message` - Log message (pre-sanitized, max 500 chars)
- `**kwargs` - Extra context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. Call `core.log(message, level=logging.INFO, **kwargs)`

**Performance:** <1ms

**Usage:**
```python
from logging.logging_core import _execute_log_info_implementation

_execute_log_info_implementation("Operation completed", request_id="12345")
```

**Note:** Called by interface_logging, not directly by users

---

### _execute_log_warning_implementation()

**Purpose:** Log warning message (message already sanitized)

**Signature:**
```python
def _execute_log_warning_implementation(message: str, **kwargs) -> None
```

**Parameters:**
- `message` - Warning message (pre-sanitized)
- `**kwargs` - Extra context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. Call `core.log(message, level=logging.WARNING, **kwargs)`

**Performance:** <1ms

---

### _execute_log_error_implementation()

**Purpose:** Log error message with sanitized exception details

**Signature:**
```python
def _execute_log_error_implementation(
    message: str, 
    error: Union[str, Exception] = None, 
    **kwargs
) -> None
```

**Parameters:**
- `message` - Error message (pre-sanitized)
- `error` - Exception or error string (optional)
- `**kwargs` - Extra context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. If error provided:
   - Check debug mode via debug module
   - Sanitize exception details
   - Add to kwargs
   - Extract error type if Exception
3. Determine severity level (default: MEDIUM)
4. Call `core.log_error_with_tracking()`

**Security:** Exception sanitization via `_sanitize_exception_details()`

**Performance:** <2ms

**Usage:**
```python
try:
    database.connect()
except ConnectionError as e:
    _execute_log_error_implementation(
        "Database connection failed",
        error=e,
        db_host="localhost"
    )
```

---

### _execute_log_debug_implementation()

**Purpose:** Log debug message (only if DEBUG_MODE enabled)

**Signature:**
```python
def _execute_log_debug_implementation(message: str, **kwargs) -> None
```

**Parameters:**
- `message` - Debug message (pre-sanitized)
- `**kwargs` - Extra context (pre-sanitized)

**Behavior:**
1. Check debug enabled via debug module:
   ```python
   from debug import get_debug_config
   config = get_debug_config()
   if config.is_debug_enabled('LOGGING'):
       # Log the message
   ```
2. Fallback to environment variable if debug module unavailable
3. If enabled: Get core and log with DEBUG level
4. If disabled: Return immediately (no log)

**Performance:** 
- Disabled: <0.1ms (instant return)
- Enabled: <1ms

**Debug Control:**
- Master: `DEBUG_MODE=true`
- Scope: `LOGGING_DEBUG_MODE=true`

---

### _execute_log_critical_implementation()

**Purpose:** Log critical message

**Signature:**
```python
def _execute_log_critical_implementation(message: str, **kwargs) -> None
```

**Parameters:**
- `message` - Critical message (pre-sanitized)
- `**kwargs` - Extra context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. Call `core.log(message, level=logging.CRITICAL, **kwargs)`

**Performance:** <1ms

---

### _execute_log_operation_start_implementation()

**Purpose:** Log operation start (operation_name already sanitized)

**Signature:**
```python
def _execute_log_operation_start_implementation(
    operation_name: str, 
    **kwargs
) -> None
```

**Parameters:**
- `operation_name` - Operation name (pre-sanitized, max 200 chars)
- `**kwargs` - Additional context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. Format message: `"Operation started: {operation_name}"`
3. Call `core.log(message, level=logging.INFO, **kwargs)`

**Performance:** <1ms

**Usage:**
```python
_execute_log_operation_start_implementation(
    "user_authentication",
    user_id="user123"
)
```

**Output:**
```
2025-12-08 10:30:45 [INFO] Operation started: user_authentication
```

---

### _execute_log_operation_success_implementation()

**Purpose:** Log operation success with duration

**Signature:**
```python
def _execute_log_operation_success_implementation(
    operation_name: str, 
    duration_ms: float, 
    **kwargs
) -> None
```

**Parameters:**
- `operation_name` - Operation name (pre-sanitized, max 200 chars)
- `duration_ms` - Duration in milliseconds
- `**kwargs` - Additional context (pre-sanitized)

**Behavior:**
1. Get logging core singleton
2. Format message: `"Operation completed: {operation_name} ({duration_ms:.2f}ms)"`
3. Call `core.log(message, level=logging.INFO, **kwargs)`

**Performance:** <1ms

**Usage:**
```python
_execute_log_operation_success_implementation(
    "user_authentication",
    duration_ms=45.23,
    user_id="user123"
)
```

**Output:**
```
2025-12-08 10:30:45 [INFO] Operation completed: user_authentication (45.23ms)
```

---

### _execute_log_operation_failure_implementation()

**Purpose:** Log operation failure with sanitized error

**Signature:**
```python
def _execute_log_operation_failure_implementation(
    operation_name: str, 
    error: Union[str, Exception], 
    **kwargs
) -> None
```

**Parameters:**
- `operation_name` - Operation name (pre-sanitized, max 200 chars)
- `error` - Exception or error message
- `**kwargs` - Additional context (pre-sanitized)

**Behavior:**
1. Check debug mode via debug module
2. Sanitize error details (SECURITY CRITICAL)
3. Get logging core singleton
4. Call `core.log_error_with_tracking()`:
   - Message: `"Operation failed: {operation_name}"`
   - Error: sanitized_error
   - Level: HIGH
   - Context: kwargs

**Security:** Exception sanitization via `_sanitize_exception_details()`

**Performance:** <2ms

**Usage:**
```python
try:
    authenticate_user()
except Exception as e:
    _execute_log_operation_failure_implementation(
        "user_authentication",
        error=e,
        user_id="user123"
    )
```

**Output:**
```
2025-12-08 10:30:45 [ERROR] Operation failed: user_authentication: ValueError: Invalid credentials
```

---

### _execute_log_reset_implementation()

**Purpose:** Reset logging core state (Phase 1 requirement)

**Signature:**
```python
def _execute_log_reset_implementation(**kwargs) -> bool
```

**Parameters:** None used (accepts **kwargs for compatibility)

**Returns:** True on success

**Behavior:**
1. Get logging core singleton
2. Call `core.reset()`
3. Return result

**What Gets Reset:**
- Template cache and statistics
- Error log deque
- Error count dictionary
- Rate limiter state

**Performance:** <1ms

**Usage:**
```python
success = _execute_log_reset_implementation()
assert success
```

**Purpose:** Testing and debugging - reset state between tests

---

## Exports

```python
__all__ = [
    '_execute_log_info_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_error_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_critical_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
    '_execute_log_reset_implementation',
]
```

---

## Security Features

### CVE-LOG-004 Mitigation

**Vulnerability:** Exception information disclosure

**Mitigation:**
1. Remove internal file paths
2. Remove AWS Lambda environment details
3. Limit traceback exposure in production
4. Redact credentials in error messages

**Implementation:** `_sanitize_exception_details()`

**Configuration:** `SANITIZE_EXCEPTIONS=true` (default)

---

## Debug Integration

**Hierarchical Control:**
- Uses debug module's `get_debug_config()`
- Checks `LOGGING_DEBUG_MODE` scope
- Falls back to `DEBUG_MODE` environment variable

**Usage in Code:**
```python
from debug import get_debug_config

config = get_debug_config()
if config.is_debug_enabled('LOGGING'):
    # Include full traceback
    include_traceback = True
```

---

## Dependencies

**Internal:**
- `logging.logging_manager` (get_logging_core)
- `logging.logging_types` (ErrorLogLevel)
- `debug` (get_debug_config) - lazy import, optional

**External:**
- `os` - Environment variable access
- `traceback` - Exception formatting
- `typing` - Type hints
- `logging` - Python logging framework

---

## Performance

**Operation Timing:**
- log_info/warning/critical: <1ms
- log_error (with sanitization): <2ms
- log_debug (disabled): <0.1ms
- log_operation_*: <1ms
- reset: <1ms

**Overhead:**
- Exception sanitization: ~0.5ms
- Debug mode check: <0.1ms

---

## Related Files

**Core:**
- logging_manager.py - LoggingCore class used by implementations
- logging_types.py - ErrorLogLevel enum

**Interface:**
- interface_logging.py - Calls these implementation functions

**Gateway:**
- gateway/wrappers/gateway_wrappers_logging.py - User-facing wrappers

---

## Changelog

### 2025-12-08_1
- Moved to logging/ subdirectory
- Integrated hierarchical debug control via debug module
- Updated imports for subdirectory structure

### 2025-10-22_01
- Added _execute_log_reset_implementation for Phase 1

### 2025-10-21_02
- Enhanced exception sanitization (CVE-LOG-004 fix)
- Added credential redaction
- Added traceback sanitization
