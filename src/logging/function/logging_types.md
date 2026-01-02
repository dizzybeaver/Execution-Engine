# logging_types.py

**Version:** 2025-12-08_1  
**Module:** LOGGING Interface  
**Layer:** Core  
**Lines:** 107

---

## Purpose

Type definitions and enumerations for the LOGGING interface. Provides operation enums, templates, severity levels, and error entry dataclasses.

---

## Classes

### LogOperation (Enum)

**Purpose:** Enumeration of all logging operations

**Values:**
```python
LOG_INFO = "log_info"
LOG_ERROR = "log_error"
LOG_WARNING = "log_warning"
LOG_DEBUG = "log_debug"
LOG_OPERATION_START = "log_operation_start"
LOG_OPERATION_SUCCESS = "log_operation_success"
LOG_OPERATION_FAILURE = "log_operation_failure"
LOG_WITH_TEMPLATE = "log_with_template"
LOG_TEMPLATE_FAST = "log_template_fast"
GET_ERROR_ENTRIES = "get_error_entries"
GET_STATS = "get_stats"
CLEAR_ERROR_ENTRIES = "clear_error_entries"
LOG_ERROR_RESPONSE = "log_error_response"
GET_ERROR_ANALYTICS = "get_error_analytics"
CLEAR_ERROR_LOGS = "clear_error_logs"
```

**Usage:**
```python
from logging.logging_types import LogOperation

operation = LogOperation.LOG_INFO
print(operation.value)  # "log_info"
```

---

### LogTemplate (Enum)

**Purpose:** Pre-formatted log templates for optimal performance

**Values:**
```python
OPERATION_START = "[OP_START]"
OPERATION_SUCCESS = "[OP_SUCCESS]"
OPERATION_FAILURE = "[OP_FAIL]"
CACHE_HIT = "[CACHE_HIT]"
CACHE_MISS = "[CACHE_MISS]"
```

**Usage:**
```python
from logging.logging_types import LogTemplate

template = LogTemplate.OPERATION_START
print(template.value)  # "[OP_START]"
```

**Note:** Template optimization is optional via `USE_LOG_TEMPLATES` environment variable

---

### ErrorLogLevel (Enum)

**Purpose:** Error severity levels for error tracking

**Values:**
```python
LOW = "low"
MEDIUM = "medium"
HIGH = "high"
CRITICAL = "critical"
```

**Usage:**
```python
from logging.logging_types import ErrorLogLevel

level = ErrorLogLevel.HIGH
print(level.value)  # "high"
```

**Mapping to Python logging levels:**
- LOW → logging.WARNING
- MEDIUM → logging.ERROR
- HIGH → logging.ERROR
- CRITICAL → logging.CRITICAL

---

### ErrorEntry (Dataclass)

**Purpose:** Simple error entry with metadata (used by logging_manager.py)

**Attributes:**
```python
timestamp: datetime           # When error occurred
error_type: str              # Type of error (e.g., "ValueError")
message: str                 # Error message
level: ErrorLogLevel         # Severity level
details: Optional[str]       # Additional error details
context: Optional[Dict[str, Any]]  # Additional context
```

**Usage:**
```python
from datetime import datetime
from logging.logging_types import ErrorEntry, ErrorLogLevel

entry = ErrorEntry(
    timestamp=datetime.now(),
    error_type="ValueError",
    message="Invalid input parameter",
    level=ErrorLogLevel.MEDIUM,
    details="Expected string, got int",
    context={"param": "user_id", "value": 123}
)

print(entry.timestamp)  # 2025-12-08 10:30:45.123456
print(entry.error_type)  # "ValueError"
print(entry.level)  # ErrorLogLevel.MEDIUM
```

**Storage:**
- Used in LoggingCore error log (deque with maxlen=100)
- Automatically tracked by `log_error_with_tracking()`

---

### ErrorLogEntry (Dataclass)

**Purpose:** Structured error response log entry (used by error response logging)

**Attributes:**
```python
id: str                                    # Unique error ID
timestamp: float                           # Unix timestamp
datetime: datetime                         # Datetime object
correlation_id: str                        # Request correlation ID
source_module: Optional[str]               # Module where error originated
error_type: str                            # Error type/category
severity: ErrorLogLevel                    # Severity level
status_code: int                           # HTTP status code
error_response: Dict[str, Any]             # Full error response
lambda_context_info: Optional[Dict[str, Any]]  # Lambda context data
additional_context: Optional[Dict[str, Any]]   # Extra context
```

**Methods:**

#### determine_severity() (Static)

**Purpose:** Determine severity from error response

**Signature:**
```python
@staticmethod
def determine_severity(error_response: Dict[str, Any]) -> ErrorLogLevel
```

**Parameters:**
- `error_response` - Error response dictionary with error.code

**Returns:** ErrorLogLevel based on error code keywords

**Logic:**
```python
error_code = error_response.get('error', {}).get('code', '')

if 'critical' in error_code.lower() or 'fatal' in error_code.lower():
    return ErrorLogLevel.CRITICAL
elif 'error' in error_code.lower():
    return ErrorLogLevel.HIGH
elif 'warning' in error_code.lower():
    return ErrorLogLevel.MEDIUM
else:
    return ErrorLogLevel.LOW
```

**Usage:**
```python
from logging.logging_types import ErrorLogEntry, ErrorLogLevel

error_response = {
    'error': {
        'code': 'CRITICAL_SYSTEM_FAILURE',
        'message': 'Database connection lost'
    }
}

severity = ErrorLogEntry.determine_severity(error_response)
print(severity)  # ErrorLogLevel.CRITICAL

entry = ErrorLogEntry(
    id="err_12345",
    timestamp=time.time(),
    datetime=datetime.now(),
    correlation_id="req_abc123",
    source_module="database_core",
    error_type="ConnectionError",
    severity=severity,
    status_code=500,
    error_response=error_response,
    lambda_context_info={"request_id": "lambda_xyz"},
    additional_context={"retry_count": 3}
)
```

---

## Exports

```python
__all__ = [
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
]
```

---

## Dependencies

**External (Standard Library):**
- `enum` - Enum base class
- `dataclasses` - Dataclass decorator
- `datetime` - Datetime and timestamp support
- `typing` - Type hints (Dict, Any, Optional)

**Internal:** None

---

## Usage Patterns

### Basic Enum Usage
```python
from logging.logging_types import LogOperation, ErrorLogLevel

# Check operation type
if operation == LogOperation.LOG_ERROR:
    level = ErrorLogLevel.HIGH
```

### Error Entry Creation
```python
from datetime import datetime
from logging.logging_types import ErrorEntry, ErrorLogLevel

entry = ErrorEntry(
    timestamp=datetime.now(),
    error_type=type(exception).__name__,
    message=str(exception),
    level=ErrorLogLevel.MEDIUM
)
```

### Severity Determination
```python
from logging.logging_types import ErrorLogEntry

error_response = {'error': {'code': 'DATABASE_ERROR'}}
severity = ErrorLogEntry.determine_severity(error_response)
```

---

## Related Files

**Core:**
- logging_manager.py - Uses ErrorEntry for error tracking
- logging_core.py - Uses ErrorLogLevel for error logging

**Interface:**
- interface_logging.py - Uses LogOperation enum (legacy)

---

## Changelog

### 2025-12-08_1
- Moved to logging/ subdirectory
- Updated documentation for subdirectory structure

### 2025-10-21_02
- Fixed ErrorEntry dataclass for logging_manager compatibility
- Simplified dataclass structure

### 2025-10-14_01
- Initial comprehensive type definitions
- Added all enum types and dataclasses
