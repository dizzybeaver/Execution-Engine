# interface_utility.py

**Version:** 2025-12-13_1  
**Module:** UTILITY  
**Layer:** Interface  
**Interface:** INT-01  
**Lines:** ~85

---

## Purpose

Utility interface router with import protection for helper functions.

---

## Main Function

### execute_utility_operation()

**Signature:**
```python
def execute_utility_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route utility operation requests using dispatch dictionary

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (varies by operation)

**Operations:**
- **UUID and Timestamp:**
  - `generate_uuid` - Generate UUID
  - `get_timestamp` - Get current timestamp
  - `generate_correlation_id` - Generate correlation ID
- **Template and Config:**
  - `render_template` - Render template string
  - `config_get` - Get config value
- **Data Operations:**
  - `parse_json` - Parse JSON string
  - `parse_json_safely` - Parse JSON with error handling
  - `deep_merge` - Deep merge dictionaries
  - `safe_get` - Safe nested dictionary access
  - `format_bytes` - Format bytes to human-readable
  - `merge_dictionaries` - Merge multiple dictionaries
  - `format_data_for_response` - Format data for API response
- **Validation:**
  - `validate_string` - Validate string
  - `validate_data_structure` - Validate data structure
  - `validate_operation_parameters` - Validate operation params
- **Sanitization:**
  - `sanitize_data` - Sanitize data
  - `safe_string_conversion` - Safe string conversion
  - `extract_error_details` - Extract error details
- **Performance:**
  - `cleanup_cache` - Cleanup cache
  - `get_performance_stats` - Get performance stats
  - `optimize_performance` - Optimize performance
  - `configure_caching` - Configure caching
  - `get_stats` - Get utility stats
  - `reset` - Reset utility state

**Raises:**
- `RuntimeError` - If Utility interface unavailable
- `ValueError` - If operation unknown

---

## UUID and Timestamp Operations

### generate_uuid

**Purpose:** Generate UUID

**Parameters:** None

**Returns:** str (UUID string)

**Usage:**
```python
uuid = execute_utility_operation('generate_uuid')
# Returns: '123e4567-e89b-12d3-a456-426614174000'
```

---

### get_timestamp

**Purpose:** Get current timestamp

**Parameters:**
- `format` (str, optional) - Timestamp format

**Returns:** str or float (timestamp)

**Formats:**
- `iso` - ISO 8601 format
- `unix` - Unix timestamp (default)
- `datetime` - Python datetime object

**Usage:**
```python
timestamp = execute_utility_operation('get_timestamp')
iso_time = execute_utility_operation('get_timestamp', format='iso')
```

---

### generate_correlation_id

**Purpose:** Generate correlation ID for request tracking

**Parameters:** None

**Returns:** str (correlation ID)

**Usage:**
```python
corr_id = execute_utility_operation('generate_correlation_id')
```

---

## Template and Config Operations

### render_template

**Purpose:** Render template string with variables

**Parameters:**
- `template` (str, required) - Template string
- `variables` (dict, required) - Template variables

**Returns:** str (rendered template)

**Usage:**
```python
result = execute_utility_operation(
    'render_template',
    template='Hello {name}!',
    variables={'name': 'Alice'}
)
# Returns: 'Hello Alice!'
```

---

### config_get

**Purpose:** Get configuration value

**Parameters:**
- `key` (str, required) - Config key
- `default` (Any, optional) - Default value

**Returns:** Configuration value

**Usage:**
```python
log_level = execute_utility_operation(
    'config_get',
    key='log_level',
    default='INFO'
)
```

---

## Data Operations

### parse_json

**Purpose:** Parse JSON string

**Parameters:**
- `json_string` (str, required) - JSON string

**Returns:** Parsed data (dict/list/etc)

**Raises:**
- `ValueError` - If JSON invalid

**Usage:**
```python
data = execute_utility_operation(
    'parse_json',
    json_string='{"key": "value"}'
)
```

---

### parse_json_safely

**Purpose:** Parse JSON with error handling

**Parameters:**
- `json_string` (str, required) - JSON string
- `default` (Any, optional) - Default value on error

**Returns:** Parsed data or default

**Usage:**
```python
data = execute_utility_operation(
    'parse_json_safely',
    json_string='invalid json',
    default={}
)
# Returns: {}
```

---

### deep_merge

**Purpose:** Deep merge dictionaries

**Parameters:**
- `dict1` (dict, required) - First dictionary
- `dict2` (dict, required) - Second dictionary

**Returns:** dict (merged dictionary)

**Usage:**
```python
merged = execute_utility_operation(
    'deep_merge',
    dict1={'a': {'b': 1}},
    dict2={'a': {'c': 2}}
)
# Returns: {'a': {'b': 1, 'c': 2}}
```

---

### safe_get

**Purpose:** Safe nested dictionary access

**Parameters:**
- `data` (dict, required) - Dictionary
- `path` (str, required) - Dot-notation path
- `default` (Any, optional) - Default value

**Returns:** Value at path or default

**Usage:**
```python
value = execute_utility_operation(
    'safe_get',
    data={'user': {'name': 'Alice'}},
    path='user.name',
    default='Unknown'
)
# Returns: 'Alice'
```

---

### format_bytes

**Purpose:** Format bytes to human-readable string

**Parameters:**
- `bytes` (int, required) - Bytes count

**Returns:** str (formatted string)

**Usage:**
```python
formatted = execute_utility_operation('format_bytes', bytes=1048576)
# Returns: '1.0 MB'
```

---

### merge_dictionaries

**Purpose:** Merge multiple dictionaries

**Parameters:**
- `dicts` (list, required) - List of dictionaries

**Returns:** dict (merged dictionary)

**Usage:**
```python
merged = execute_utility_operation(
    'merge_dictionaries',
    dicts=[{'a': 1}, {'b': 2}, {'c': 3}]
)
# Returns: {'a': 1, 'b': 2, 'c': 3}
```

---

### format_data_for_response

**Purpose:** Format data for API response

**Parameters:**
- `data` (Any, required) - Data to format
- `metadata` (dict, optional) - Response metadata

**Returns:** dict (formatted response)

**Usage:**
```python
response = execute_utility_operation(
    'format_data_for_response',
    data={'users': [...]},
    metadata={'count': 10}
)
# Returns: {'data': {...}, 'metadata': {...}}
```

---

## Validation Operations

### validate_string

**Purpose:** Validate string

**Parameters:**
- `value` (str, required) - String to validate
- `min_length` (int, optional) - Minimum length
- `max_length` (int, optional) - Maximum length

**Returns:** bool (True if valid)

**Usage:**
```python
is_valid = execute_utility_operation(
    'validate_string',
    value='username',
    min_length=3,
    max_length=20
)
```

---

### validate_data_structure

**Purpose:** Validate data structure

**Parameters:**
- `data` (Any, required) - Data to validate
- `schema` (dict, required) - Validation schema

**Returns:** bool (True if valid)

**Usage:**
```python
is_valid = execute_utility_operation(
    'validate_data_structure',
    data={'name': 'Alice', 'age': 30},
    schema={'name': str, 'age': int}
)
```

---

### validate_operation_parameters

**Purpose:** Validate operation parameters

**Parameters:**
- `operation` (str, required) - Operation name
- `parameters` (dict, required) - Parameters to validate

**Returns:** bool (True if valid)

**Usage:**
```python
is_valid = execute_utility_operation(
    'validate_operation_parameters',
    operation='cache_get',
    parameters={'key': 'user_123'}
)
```

---

## Sanitization Operations

### sanitize_data

**Purpose:** Sanitize data for safe use

**Parameters:**
- `data` (Any, required) - Data to sanitize

**Returns:** Sanitized data

**Usage:**
```python
clean = execute_utility_operation(
    'sanitize_data',
    data='<script>alert("XSS")</script>'
)
```

---

### safe_string_conversion

**Purpose:** Safely convert value to string

**Parameters:**
- `value` (Any, required) - Value to convert
- `max_length` (int, optional) - Maximum length

**Returns:** str (converted string)

**Usage:**
```python
string = execute_utility_operation(
    'safe_string_conversion',
    value=12345,
    max_length=10
)
```

---

### extract_error_details

**Purpose:** Extract error details from exception

**Parameters:**
- `error` (Exception, required) - Exception object

**Returns:** dict (error details)

**Usage:**
```python
try:
    risky_operation()
except Exception as e:
    details = execute_utility_operation('extract_error_details', error=e)
```

---

## Performance Operations

### cleanup_cache

**Purpose:** Cleanup utility cache

**Parameters:** None

**Returns:** int (items cleaned)

**Usage:**
```python
count = execute_utility_operation('cleanup_cache')
```

---

### get_performance_stats

**Purpose:** Get performance statistics

**Parameters:** None

**Returns:** dict (performance stats)

**Usage:**
```python
stats = execute_utility_operation('get_performance_stats')
```

---

### optimize_performance

**Purpose:** Optimize utility performance

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_utility_operation('optimize_performance')
```

---

### configure_caching

**Purpose:** Configure caching settings

**Parameters:**
- `enabled` (bool, required) - Enable caching
- `max_size` (int, optional) - Max cache size

**Returns:** bool (True on success)

**Usage:**
```python
execute_utility_operation(
    'configure_caching',
    enabled=True,
    max_size=100
)
```

---

### get_stats

**Purpose:** Get utility statistics

**Parameters:** None

**Returns:** dict (utility stats)

**Usage:**
```python
stats = execute_utility_operation('get_stats')
```

---

### reset

**Purpose:** Reset utility state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_utility_operation('reset')
```

---

## Import Protection

**Pattern:**
```python
try:
    import utility
    _UTILITY_AVAILABLE = True
except ImportError as e:
    _UTILITY_AVAILABLE = False
    _UTILITY_IMPORT_ERROR = str(e)
```

---

## Dispatch Dictionary

**Benefits:**
- O(1) operation lookup
- Easy to extend
- Clean separation

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Comprehensive Utilities:** UUID, data, validation, sanitization  
✅ **Import Protection:** Graceful failure handling

---

## Related Files

- `/utility/` - Utility implementation
- `/gateway/wrappers/gateway_wrappers_utility.py` - Gateway wrappers
- `/utility/utility_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
