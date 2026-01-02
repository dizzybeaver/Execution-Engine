# utility_sanitize.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_sanitize.py  
**Module:** Utility sanitization operations

---

## Overview

Sanitization operations for data cleaning and error extraction. Provides PII protection, safe string conversion, and detailed error extraction.

**File:** `utility/utility_sanitize.py`  
**Lines:** 116  
**Pattern:** Operation class with manager reference

---

## Classes

### UtilitySanitizeOperations

**Purpose:** Sanitization operations for data cleaning  
**Pattern:** Operation class initialized with manager reference

**Initialization:**
```python
def __init__(self, manager):
    """Initialize with reference to SharedUtilityCore manager."""
    self._manager = manager
```

---

## Methods

### sanitize_data()

**Purpose:** Sanitize response data by removing sensitive fields  
**Returns:** dict (sanitized data)

**Parameters:**
- `data` (dict): Data to sanitize
- `correlation_id` (str, optional): Debug correlation ID

**Sensitive Fields:**
- password
- secret
- token
- api_key
- private_key

**Behavior:**
- Recursive sanitization for nested dicts
- Case-insensitive matching
- Replaces with "***REDACTED***"

**Usage:**
```python
ops = UtilitySanitizeOperations(manager)

data = {
    'user': 'alice',
    'password': 'secret123',
    'api_key': 'abc123',
    'profile': {
        'name': 'Alice',
        'private_key': 'xyz789'
    }
}

result = ops.sanitize_data(data)
# Result: {
#     'user': 'alice',
#     'password': '***REDACTED***',
#     'api_key': '***REDACTED***',
#     'profile': {
#         'name': 'Alice',
#         'private_key': '***REDACTED***'
#     }
# }

# Non-dict input (returns unchanged)
result = ops.sanitize_data([1, 2, 3])
# Result: [1, 2, 3]
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data sanitized (redacted_count=3, total_keys=4)
[abc123] [UTILITY-DEBUG] Sanitize skipped: not a dict (data_type=list)
```

---

### safe_string_conversion()

**Purpose:** Safely convert data to string with length limits  
**Returns:** str (converted string)

**Parameters:**
- `data` (Any): Data to convert
- `max_length` (int, default=10000): Maximum length
- `correlation_id` (str, optional): Debug correlation ID

**Behavior:**
- Converts any data type to string
- Truncates if exceeds max_length
- Adds "... [TRUNCATED]" indicator

**Usage:**
```python
ops = UtilitySanitizeOperations(manager)

# Simple conversion
result = ops.safe_string_conversion({'key': 'value'})
# Result: "{'key': 'value'}"

# Truncation
long_data = 'a' * 20000
result = ops.safe_string_conversion(long_data, max_length=100)
# Result: "aaaa... [TRUNCATED]" (100 chars + indicator)

# Complex object
result = ops.safe_string_conversion([1, 2, 3, {'key': 'value'}])
# Result: "[1, 2, 3, {'key': 'value'}]"

# Error handling
result = ops.safe_string_conversion(unconvertible_object)
# Result: "[conversion_error]"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] String conversion successful (result_length=16)
[abc123] [UTILITY-DEBUG] String conversion truncated (original_length=20000, max_length=100)
[abc123] [UTILITY-DEBUG] String conversion failed (error=...)
```

---

### extract_error_details()

**Purpose:** Extract detailed error information with stack trace  
**Returns:** dict (error details)

**Parameters:**
- `error` (Exception): Exception to extract details from
- `correlation_id` (str, optional): Debug correlation ID

**Extracted Info:**
- Error type
- Error message
- Error args
- Full traceback

**Usage:**
```python
ops = UtilitySanitizeOperations(manager)

try:
    raise ValueError("Invalid input: must be positive")
except Exception as e:
    details = ops.extract_error_details(e)
    
# Result: {
#     'type': 'ValueError',
#     'message': 'Invalid input: must be positive',
#     'args': ('Invalid input: must be positive',),
#     'traceback': 'Traceback (most recent call last):
  File "test.py", line 2, in <module>
    raise ValueError("Invalid input: must be positive")
ValueError: Invalid input: must be positive'
# }

# Extraction failure (fallback)
details = ops.extract_error_details(problematic_error)
# Result: {
#     'type': 'UnknownError',
#     'message': 'Failed to extract error details',
#     'traceback': None
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Error details extracted (error_type=ValueError)
[abc123] [UTILITY-DEBUG] Error detail extraction failed (error=...)
```

---

## Usage Patterns

### Initialization
```python
from utility.utility_manager import get_utility_manager
from utility.utility_sanitize import UtilitySanitizeOperations

manager = get_utility_manager()
ops = UtilitySanitizeOperations(manager)
```

### Data Sanitization
```python
# Before logging/returning
data = {'user': 'alice', 'password': 'secret', 'data': {...}}
safe_data = ops.sanitize_data(data)
logger.info(f"User data: {safe_data}")
```

### String Conversion
```python
# Safe logging of complex objects
result = complex_operation()
log_str = ops.safe_string_conversion(result, max_length=1000)
logger.debug(f"Operation result: {log_str}")
```

### Error Detail Extraction
```python
# Error reporting
try:
    risky_operation()
except Exception as e:
    details = ops.extract_error_details(e)
    error_response = {
        'success': False,
        'error': details['message'],
        'error_type': details['type'],
        'traceback': details['traceback']
    }
    return error_response
```

---

## Security Features

### PII Protection

**Protected Fields:**
- password (case-insensitive)
- secret (case-insensitive)
- token (case-insensitive)
- api_key (case-insensitive)
- private_key (case-insensitive)

**Behavior:**
- Recursive scanning
- Partial matching (e.g., "user_password" matches)
- Safe for logging and responses

### Safe String Conversion

**Protection:**
- Prevents memory overflow (max_length limit)
- Handles conversion errors gracefully
- Provides clear truncation indicator

---

## Debug Integration

**Master Switch:**
- `DEBUG_MODE` - Enables all debugging

**Scope Switches:**
- `UTILITY_DEBUG_MODE` - Utility debug logging

**Correlation ID:**
- All methods accept optional `correlation_id` parameter
- Auto-generated via gateway if not provided

---

## Related Files

- **Manager:** `utility/utility_manager.py`
- **Core:** `utility/utility_core.py`
- **Interface:** `interface/interface_utility.py`

---

**END OF DOCUMENTATION**
