# interface_logging.py

**Version:** 2025-12-08_1  
**Module:** LOGGING  
**Layer:** Interface  
**Interface:** INT-03  
**Lines:** ~200

---

## Purpose

Logging router with SECURITY HARDENING - Firewall for LOGGING interface with sanitization.

Protects against:
- CVE-LOG-001: Message injection
- CVE-LOG-002: Extra data injection
- CVE-LOG-003: Sensitive data logging
- CVE-LOG-004: Exception information disclosure

---

## Main Function

### execute_logging_operation()

**Signature:**
```python
def execute_logging_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Execute logging operation with security hardening

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** None (logging operations typically return nothing)

**Operations:**
- `log_info` - Log info message
- `log_error` - Log error with exception
- `log_warning` - Log warning message
- `log_debug` - Log debug message (if DEBUG_MODE enabled)
- `log_operation_start` - Log operation start
- `log_operation_success` - Log operation success with duration
- `log_operation_failure` - Log operation failure with error
- `reset` / `reset_logging` - Reset logging state

**Raises:**
- `RuntimeError` - If Logging system not available
- `ValueError` - If operation unknown or parameters invalid

---

## Operations

### log_info

**Purpose:** Log informational message

**Parameters:**
- `message` (str, required) - Log message
- `**extra` - Additional context (key=value pairs)

**Security:**
- Message sanitized (newlines removed, max 500 chars)
- Extra data sanitized (sensitive keys redacted)

**Usage:**
```python
execute_logging_operation(
    'log_info',
    message='User logged in',
    user_id='12345',
    ip_address='192.168.1.1'
)
```

---

### log_error

**Purpose:** Log error message with exception details

**Parameters:**
- `message` (str, required) - Error message
- `error` (Exception/str, optional) - Exception or error string
- `**extra` - Additional context

**Security:**
- Exception details sanitized (CVE-LOG-004)
- File paths removed
- Credentials redacted
- Traceback limited (debug mode only)

**Usage:**
```python
try:
    risky_operation()
except Exception as e:
    execute_logging_operation(
        'log_error',
        message='Operation failed',
        error=e,
        operation='risky_operation'
    )
```

---

### log_warning

**Purpose:** Log warning message

**Parameters:**
- `message` (str, required) - Warning message
- `**extra` - Additional context

**Security:** Same as log_info

**Usage:**
```python
execute_logging_operation(
    'log_warning',
    message='Resource limit approaching',
    usage_percent=85
)
```

---

### log_debug

**Purpose:** Log debug message (only if DEBUG_MODE enabled)

**Parameters:**
- `message` (str, required) - Debug message
- `**extra` - Additional context

**Security:**
- Only logs if DEBUG_MODE=true
- Same sanitization as other log levels

**Usage:**
```python
execute_logging_operation(
    'log_debug',
    message='Cache lookup',
    key='user_123',
    hit=True
)
```

---

### log_operation_start

**Purpose:** Log operation start

**Parameters:**
- `operation_name` (str, required) - Operation name
- `**extra` - Additional context

**Security:**
- Operation name sanitized (max 200 chars)
- Extra data sanitized

**Usage:**
```python
execute_logging_operation(
    'log_operation_start',
    operation_name='user_authentication',
    user_id='12345'
)
```

---

### log_operation_success

**Purpose:** Log operation success with duration

**Parameters:**
- `operation_name` (str, required) - Operation name
- `duration_ms` (float, required) - Duration in milliseconds
- `**extra` - Additional context

**Validation:**
- `duration_ms` must be numeric

**Usage:**
```python
execute_logging_operation(
    'log_operation_success',
    operation_name='user_authentication',
    duration_ms=45.2,
    user_id='12345'
)
```

---

### log_operation_failure

**Purpose:** Log operation failure with error

**Parameters:**
- `operation_name` (str, required) - Operation name
- `error` (Exception/str, required) - Error details
- `**extra` - Additional context

**Security:**
- Exception sanitized (CVE-LOG-004)

**Usage:**
```python
execute_logging_operation(
    'log_operation_failure',
    operation_name='user_authentication',
    error='Invalid credentials',
    user_id='12345'
)
```

---

### reset / reset_logging

**Purpose:** Reset logging core state

**Parameters:** None

**Returns:** bool (True on success)

**Clears:**
- Template cache
- Error log
- Rate limiter state

**Usage:**
```python
execute_logging_operation('reset')
```

---

## Security Sanitization

### _sanitize_log_data()

**Purpose:** Sanitize log message and extra data

**CVE Mitigations:**
- **CVE-LOG-001**: Removes newlines, limits message to 500 chars
- **CVE-LOG-002**: Limits extra values to 200 chars
- **CVE-LOG-003**: Redacts sensitive keys

**Sensitive Keys:**
- password
- token
- secret
- api_key
- auth
- credential

**Behavior:**
```python
# Input
message = "User login\nwith token=abc123"
extra = {'password': 'secret123', 'username': 'alice'}

# Output
message = "User login with token=abc123"  # newline removed
extra = {'password': '***REDACTED***', 'username': 'alice'}
```

---

## Validation Functions

### _validate_message_param()

**Purpose:** Validate and sanitize message parameter

**Actions:**
- Checks message exists
- Removes newlines
- Limits to 500 chars
- Sanitizes extra data

---

### _validate_operation_start_params()

**Purpose:** Validate operation_start parameters

**Actions:**
- Checks operation_name exists
- Removes newlines
- Limits to 200 chars
- Sanitizes extra data

---

### _validate_operation_success_params()

**Purpose:** Validate operation_success parameters

**Actions:**
- Checks operation_name and duration_ms exist
- Validates duration_ms is numeric
- Sanitizes extra data

**Raises:**
- `ValueError` if duration_ms not numeric

---

### _validate_operation_failure_params()

**Purpose:** Validate operation_failure parameters

**Actions:**
- Checks operation_name and error exist
- Limits error to 500 chars
- Sanitizes extra data

---

## Import Structure

```python
from logging.logging_core import (
    _execute_log_info_implementation,
    _execute_log_warning_implementation,
    _execute_log_error_implementation,
    _execute_log_debug_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_operation_failure_implementation,
    _execute_log_reset_implementation,
)
from logging.logging_manager import get_logging_core
```

---

## Dispatch Dictionary

```python
_OPERATION_DISPATCH = {
    'log_info': _execute_log_info_implementation,
    'log_error': _execute_log_error_implementation,
    'log_warning': _execute_log_warning_implementation,
    'log_debug': _execute_log_debug_implementation,
    'log_operation_start': _execute_log_operation_start_implementation,
    'log_operation_success': _execute_log_operation_success_implementation,
    'log_operation_failure': _execute_log_operation_failure_implementation,
    'reset': _execute_log_reset_implementation,
    'reset_logging': _execute_log_reset_implementation,
}
```

---

## Security Best Practices

**Always:**
- Sanitize all log inputs
- Redact sensitive data
- Limit message/error lengths
- Use structured logging (extra params)

**Never:**
- Log passwords, tokens, secrets
- Log full stack traces in production
- Log PII without sanitization
- Trust user input in log messages

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Security Hardening:** CVE mitigations  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Data Sanitization:** Sensitive data protection  
✅ **Parameter Validation:** Type and presence checks

---

## Related Files

- `/logging/` - Logging implementation
- `/gateway/wrappers/gateway_wrappers_logging.py` - Gateway wrappers
- `/logging/logging_directory.md` - Directory structure

---

**END OF DOCUMENTATION**
