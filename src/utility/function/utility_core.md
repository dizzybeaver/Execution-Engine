# utility_core.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_core.py  
**Module:** Utility implementation layer

---

## Overview

Gateway implementation functions for the utility interface. This file provides the public implementation layer that connects the interface router to the underlying operation classes.

**File:** `utility/utility_core.py`  
**Lines:** 197  
**Pattern:** SUGA Implementation Layer

---

## Functions

### UUID and Timestamp Functions

#### generate_uuid_implementation()

**Purpose:** Generate UUID with pool optimization  
**Layer:** Implementation  
**Returns:** str (UUID)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
uuid = utility.generate_uuid_implementation()
# or via gateway
from gateway import generate_uuid
uuid = generate_uuid()
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] UUID from pool (pool_size=15)
[abc123] [UTILITY-DEBUG] UUID generated (new_uuid=True)
```

---

#### get_timestamp_implementation()

**Purpose:** Get current timestamp as ISO string  
**Layer:** Implementation  
**Returns:** str (ISO timestamp)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
timestamp = utility.get_timestamp_implementation()
# Result: "2025-12-13T14:30:00Z"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Timestamp generated (timestamp=2025-12-13T14:30:00Z)
```

---

#### generate_correlation_id_implementation()

**Purpose:** Generate correlation ID with optional prefix  
**Layer:** Implementation  
**Returns:** str (correlation ID)

**Parameters:**
- `prefix` (str, optional): Prefix for correlation ID
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
corr_id = utility.generate_correlation_id_implementation(prefix='req')
# Result: "req_550e8400-e29b-41d4-a716-446655440000"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Correlation ID with prefix (prefix=req, result_length=41)
[abc123] [UTILITY-DEBUG] Correlation ID generated (result_length=36)
```

---

### Template and Config Functions

#### render_template_implementation()

**Purpose:** Render template with {placeholder} substitution  
**Layer:** Implementation  
**Returns:** dict (rendered template)

**Parameters:**
- `template` (dict): Template with {placeholder} strings
- `data` (dict): Data for placeholder substitution
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
template = {'message': 'Hello {name}', 'user': '{user_id}'}
data = {'name': 'Alice', 'user_id': '123'}
result = utility.render_template_implementation(template, data)
# Result: {'message': 'Hello Alice', 'user': '123'}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Rendering template (placeholder_count=2)
[abc123] [UTILITY-TIMING] render_template: 1.23ms
[abc123] [UTILITY-DEBUG] Template rendered successfully
```

---

#### config_get_implementation()

**Purpose:** Get typed configuration value from environment  
**Layer:** Implementation  
**Returns:** Any (typed config value)

**Parameters:**
- `key` (str): Environment variable key
- `default` (Any, optional): Default value (determines type conversion)
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
# Boolean conversion
debug_mode = utility.config_get_implementation('DEBUG_MODE', False)
# Integer conversion
timeout = utility.config_get_implementation('TIMEOUT', 30)
# String (no conversion)
api_key = utility.config_get_implementation('API_KEY')
```

**Type Conversion:**
- `default=False` → Boolean ('true', '1', 'yes', 'on')
- `default=0` → Integer
- `default=0.0` → Float
- `default=None` → String (no conversion)

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Config retrieved and converted (key=DEBUG_MODE, result_type=bool)
[abc123] [UTILITY-DEBUG] Config not found, using default (key=API_KEY, has_default=True)
```

---

### Data Operation Functions

#### parse_json_implementation()

**Purpose:** Parse JSON string  
**Layer:** Implementation  
**Returns:** dict (parsed JSON)

**Parameters:**
- `data` (str): JSON string to parse
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.parse_json_implementation('{"key": "value"}')
# Result: {'key': 'value'}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] JSON parsed successfully (result_keys=1)
[abc123] [UTILITY-DEBUG] JSON parse failed (error=...)
```

---

#### parse_json_safely_implementation()

**Purpose:** Parse JSON safely with optional caching  
**Layer:** Implementation  
**Returns:** Optional[dict] (parsed JSON or None on error)

**Parameters:**
- `json_str` (str): JSON string to parse
- `use_cache` (bool, default=True): Enable caching
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.parse_json_safely_implementation('{"key": "value"}')
# Cached result on second call
result2 = utility.parse_json_safely_implementation('{"key": "value"}')
```

**Features:**
- LRU cache (100 items)
- Cache hit/miss tracking
- Automatic eviction
- Returns None on error (no exception)

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] JSON parse cache hit
[abc123] [UTILITY-TIMING] parse_json: 0.45ms
[abc123] [UTILITY-DEBUG] JSON parsed and cached
```

---

#### deep_merge_implementation()

**Purpose:** Deep merge two dictionaries  
**Layer:** Implementation  
**Returns:** dict (merged result)

**Parameters:**
- `dict1` (dict): First dictionary
- `dict2` (dict): Second dictionary (takes precedence)
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
d1 = {'a': 1, 'b': {'c': 2}}
d2 = {'b': {'d': 3}, 'e': 4}
result = utility.deep_merge_implementation(d1, d2)
# Result: {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Dictionaries merged (dict1_keys=2, dict2_keys=2, result_keys=3)
```

---

#### safe_get_implementation()

**Purpose:** Safely get nested dictionary value using dot notation  
**Layer:** Implementation  
**Returns:** Any (value or default)

**Parameters:**
- `dictionary` (dict): Dictionary to query
- `key_path` (str): Dot-separated key path (e.g., "user.address.city")
- `default` (Any, optional): Default value if not found
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
data = {'user': {'address': {'city': 'NYC'}}}
city = utility.safe_get_implementation(data, 'user.address.city')
# Result: 'NYC'
missing = utility.safe_get_implementation(data, 'user.phone', 'N/A')
# Result: 'N/A'
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Value retrieved via safe_get (key_path=user.address.city, has_value=True)
[abc123] [UTILITY-DEBUG] Key path not found, using default (key_path=user.phone)
```

---

#### format_bytes_implementation()

**Purpose:** Format bytes to human-readable string  
**Layer:** Implementation  
**Returns:** str (formatted size)

**Parameters:**
- `size` (int): Size in bytes
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs**: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.format_bytes_implementation(1024)
# Result: "1.00 KB"
result = utility.format_bytes_implementation(1048576)
# Result: "1.00 MB"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Bytes formatted (size=1024, result=1.00 KB)
```

---

#### merge_dictionaries_implementation()

**Purpose:** Merge multiple dictionaries safely  
**Layer:** Implementation  
**Returns:** dict (merged result)

**Parameters:**
- `*dicts` (dict): Variable number of dictionaries
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.merge_dictionaries_implementation({'a': 1}, {'b': 2}, {'c': 3})
# Result: {'a': 1, 'b': 2, 'c': 3}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Multiple dictionaries merged (dict_count=3, result_keys=3)
```

---

#### format_data_for_response_implementation()

**Purpose:** Format data for API response  
**Layer:** Implementation  
**Returns:** dict (formatted response)

**Parameters:**
- `data` (Any): Data to format
- `format_type` (str, default="json"): Format type
- `include_metadata` (bool, default=True): Include metadata
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.format_data_for_response_implementation({'key': 'value'})
# Result: {
#   'data': {'key': 'value'},
#   'format': 'json',
#   'metadata': {'timestamp': 1702480800, 'type': 'dict'}
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data formatted for response (format_type=json, include_metadata=True)
```

---

### Validation Functions

#### validate_string_implementation()

**Purpose:** Validate string input  
**Layer:** Implementation  
**Returns:** dict (validation result)

**Parameters:**
- `value` (str): String to validate
- `min_length` (int, default=0): Minimum length
- `max_length` (int, default=1000): Maximum length
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.validate_string_implementation('test', min_length=1, max_length=100)
# Result: {'valid': True}
result = utility.validate_string_implementation('', min_length=1)
# Result: {'valid': False, 'error': 'String too short (min: 1)'}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] String validation passed (length=4)
[abc123] [UTILITY-DEBUG] String validation failed: too short (length=0, min_length=1)
```

---

#### validate_data_structure_implementation()

**Purpose:** Validate data structure  
**Layer:** Implementation  
**Returns:** bool (True if valid)

**Parameters:**
- `data` (Any): Data to validate
- `expected_type` (type): Expected type
- `required_fields` (list[str], optional): Required fields (for dicts)
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
valid = utility.validate_data_structure_implementation(
    {'name': 'Alice', 'age': 30},
    dict,
    required_fields=['name', 'age']
)
# Result: True
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data structure validation passed (expected_type=dict)
[abc123] [UTILITY-DEBUG] Data structure validation failed: missing field (field=age)
```

---

#### validate_operation_parameters_implementation()

**Purpose:** Generic parameter validation  
**Layer:** Implementation  
**Returns:** dict (validation result)

**Parameters:**
- `required_params` (list[str]): Required parameter names
- `optional_params` (list[str], optional): Optional parameter names
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Parameters to validate

**Usage:**
```python
import utility
result = utility.validate_operation_parameters_implementation(
    required_params=['name', 'age'],
    optional_params=['email'],
    name='Alice',
    age=30
)
# Result: {'valid': True}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Parameter validation passed (required_count=2)
[abc123] [UTILITY-DEBUG] Parameter validation failed: missing params (missing_params=['age'])
```

---

### Sanitization Functions

#### sanitize_data_implementation()

**Purpose:** Sanitize response data by removing sensitive fields  
**Layer:** Implementation  
**Returns:** dict (sanitized data)

**Parameters:**
- `data` (dict): Data to sanitize
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
data = {'user': 'alice', 'password': 'secret123', 'api_key': 'abc123'}
result = utility.sanitize_data_implementation(data)
# Result: {'user': 'alice', 'password': '***REDACTED***', 'api_key': '***REDACTED***'}
```

**Sensitive Keys:**
- password
- secret
- token
- api_key
- private_key

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data sanitized (redacted_count=2, total_keys=3)
```

---

#### safe_string_conversion_implementation()

**Purpose:** Safely convert data to string with length limits  
**Layer:** Implementation  
**Returns:** str (converted string)

**Parameters:**
- `data` (Any): Data to convert
- `max_length` (int, default=10000): Maximum length
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.safe_string_conversion_implementation({'key': 'value'})
# Result: "{'key': 'value'}"
long_text = 'a' * 20000
result = utility.safe_string_conversion_implementation(long_text, max_length=100)
# Result: "aaaa... [TRUNCATED]"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] String conversion successful (result_length=16)
[abc123] [UTILITY-DEBUG] String conversion truncated (original_length=20000, max_length=100)
```

---

#### extract_error_details_implementation()

**Purpose:** Extract detailed error information with stack trace  
**Layer:** Implementation  
**Returns:** dict (error details)

**Parameters:**
- `error` (Exception): Exception to extract details from
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs**: Additional parameters (ignored)

**Usage:**
```python
import utility
try:
    raise ValueError("Test error")
except Exception as e:
    details = utility.extract_error_details_implementation(e)
# Result: {
#   'type': 'ValueError',
#   'message': 'Test error',
#   'args': ('Test error',),
#   'traceback': '...'
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Error details extracted (error_type=ValueError)
```

---

### Performance Functions

#### cleanup_cache_implementation()

**Purpose:** Clean up old cached utility data  
**Layer:** Implementation  
**Returns:** int (number of items cleared)

**Parameters:**
- `max_age_seconds` (int, default=3600): Maximum age (currently clears all)
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
cleared = utility.cleanup_cache_implementation()
# Result: 25 (number of cached items cleared)
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Cache cleaned up (cleared_count=25)
```

---

#### optimize_performance_implementation()

**Purpose:** Optimize utility performance based on usage patterns  
**Layer:** Implementation  
**Returns:** dict (optimization results)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs**: Additional parameters (ignored)

**Usage:**
```python
import utility
result = utility.optimize_performance_implementation()
# Result: {
#   'optimizations_applied': ['Replenished ID pool', 'JSON cache approaching limit'],
#   'timestamp': 1702480800
# }
```

**Optimizations:**
- Replenish UUID pool if < 10 UUIDs
- Warn if JSON cache > 90% full
- Detect high latency operations
- Detect low cache hit rates

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Performance optimization complete (optimizations_count=2)
```

---

#### configure_caching_implementation()

**Purpose:** Configure utility caching settings  
**Layer:** Implementation  
**Returns:** bool (True if successful)

**Parameters:**
- `enabled` (bool): Enable/disable caching
- `ttl` (int, default=300): Cache TTL in seconds
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
success = utility.configure_caching_implementation(enabled=True, ttl=600)
# Result: True
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Caching configured (enabled=True, ttl=600)
```

---

#### get_performance_stats_implementation()

**Purpose:** Get utility performance statistics  
**Layer:** Implementation  
**Returns:** dict (performance stats)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs**: Additional parameters (ignored)

**Usage:**
```python
import utility
stats = utility.get_performance_stats_implementation()
```

**Returns:**
```python
{
    'overall_stats': {
        'template_hits': 150,
        'cache_optimizations': 5,
        'id_pool_reuse': 75,
        'templates_rendered': 150,
        'configs_retrieved': 50
    },
    'operation_stats': {
        'parse_json': {
            'call_count': 100,
            'avg_duration_ms': 1.25,
            'cache_hit_rate_percent': 75.0,
            'error_rate_percent': 2.0
        }
    },
    'id_pool_size': 15,
    'json_cache_size': 45,
    'cache_enabled': True
}
```

---

#### get_stats_implementation()

**Purpose:** Get utility statistics (alias for get_performance_stats)  
**Layer:** Implementation  
**Returns:** dict (statistics)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
stats = utility.get_stats_implementation()
```

---

#### reset_implementation()

**Purpose:** Reset utility manager state  
**Layer:** Implementation  
**Returns:** bool (True if successful)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Usage:**
```python
import utility
success = utility.reset_implementation()
# Result: True
```

**Resets:**
- All metrics
- All statistics
- JSON cache
- UUID pool
- Rate limiter

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Resetting utility manager state
[abc123] [UTILITY-DEBUG] Utility manager reset complete
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import generate_uuid, parse_json, validate_string

uuid = generate_uuid()
data = parse_json('{"key": "value"}')
result = validate_string('test', min_length=1)
```

### Direct Import (Testing Only)
```python
import utility

uuid = utility.generate_uuid_implementation()
data = utility.parse_json_implementation('{"key": "value"}')
```

---

## Debug Integration

All functions support hierarchical debug control via:

**Master Switch:**
- `DEBUG_MODE` - Enables all debugging

**Scope Switches:**
- `UTILITY_DEBUG_MODE` - Utility debug logging
- `UTILITY_DEBUG_TIMING` - Utility timing measurements

**Correlation ID:**
- All functions accept optional `correlation_id` parameter
- Auto-generated if not provided
- Used for tracking related operations

---

## Related Files

- **Interface:** `interface/interface_utility.py`
- **Manager:** `utility/utility_manager.py`
- **Operations:** `utility/utility_data.py`, `utility/utility_validation.py`, `utility/utility_sanitize.py`
- **Gateway:** `gateway/wrappers/gateway_wrappers_utility.py`

---

**END OF DOCUMENTATION**
