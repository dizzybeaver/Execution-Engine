# utility_data.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_data.py  
**Module:** Utility data operations

---

## Overview

Data operations for parsing, merging, and formatting data. Provides JSON parsing with caching, dictionary merging, byte formatting, and response formatting.

**File:** `utility/utility_data.py`  
**Lines:** 273  
**Pattern:** Operation class with manager reference

---

## Classes

### UtilityDataOperations

**Purpose:** Data operations for parsing, merging, and formatting  
**Pattern:** Operation class initialized with manager reference

**Initialization:**
```python
def __init__(self, manager):
    """Initialize with reference to SharedUtilityCore manager."""
    self._manager = manager
```

---

## Methods

### JSON Operations

#### parse_json()

**Purpose:** Parse JSON string  
**Returns:** dict (parsed JSON or empty dict on error)

**Parameters:**
- `data` (str): JSON string to parse
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityDataOperations(manager)
result = ops.parse_json('{"key": "value"}')
# Result: {'key': 'value'}
```

**Error Handling:**
- Returns `{}` on parse error
- Logs error details
- Debug logs failure

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] JSON parsed successfully (result_keys=1)
[abc123] [UTILITY-DEBUG] JSON parse failed (error=Expecting property name enclosed in double quotes: line 1 column 2 (char 1))
```

---

#### parse_json_safely()

**Purpose:** Parse JSON safely with optional caching  
**Returns:** Optional[dict] (parsed JSON or None on error)

**Parameters:**
- `json_str` (str): JSON string to parse
- `use_cache` (bool, default=True): Enable caching
- `correlation_id` (str, optional): Debug correlation ID

**Caching:**
- Cache key: `hash(json_str)`
- LRU eviction when cache reaches 100 items
- Tracks cache order for eviction

**Usage:**
```python
ops = UtilityDataOperations(manager)

# First call - cache miss
result = ops.parse_json_safely('{"key": "value"}')
# Second call - cache hit
result2 = ops.parse_json_safely('{"key": "value"}')

# Disable cache
result3 = ops.parse_json_safely('{"key": "value"}', use_cache=False)
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] JSON parse cache hit
[abc123] [UTILITY-TIMING] parse_json: 0.45ms
[abc123] [UTILITY-DEBUG] JSON parsed and cached
[abc123] [UTILITY-DEBUG] JSON decode error (error=...)
```

**Rate Limiting:**
- Checks rate limit before parsing
- Returns None if rate limited

---

### Dictionary Operations

#### deep_merge()

**Purpose:** Deep merge two dictionaries  
**Returns:** dict (merged result)

**Parameters:**
- `dict1` (dict): First dictionary
- `dict2` (dict): Second dictionary (takes precedence)
- `correlation_id` (str, optional): Debug correlation ID

**Behavior:**
- Recursively merges nested dictionaries
- dict2 values override dict1
- Non-dict values replaced entirely

**Usage:**
```python
ops = UtilityDataOperations(manager)

d1 = {
    'a': 1,
    'b': {'c': 2, 'd': 3},
    'e': 4
}
d2 = {
    'b': {'d': 30, 'f': 40},
    'g': 5
}

result = ops.deep_merge(d1, d2)
# Result: {
#   'a': 1,
#   'b': {'c': 2, 'd': 30, 'f': 40},
#   'e': 4,
#   'g': 5
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Dictionaries merged (dict1_keys=3, dict2_keys=2, result_keys=4)
```

---

#### safe_get()

**Purpose:** Safely get nested dictionary value using dot notation  
**Returns:** Any (value or default)

**Parameters:**
- `dictionary` (dict): Dictionary to query
- `key_path` (str): Dot-separated key path
- `default` (Any, default=None): Default value if not found
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityDataOperations(manager)

data = {
    'user': {
        'profile': {
            'name': 'Alice',
            'address': {
                'city': 'NYC',
                'zip': '10001'
            }
        }
    }
}

# Get nested value
name = ops.safe_get(data, 'user.profile.name')
# Result: 'Alice'

city = ops.safe_get(data, 'user.profile.address.city')
# Result: 'NYC'

# Missing path - use default
phone = ops.safe_get(data, 'user.profile.phone', 'N/A')
# Result: 'N/A'
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Value retrieved via safe_get (key_path=user.profile.name, has_value=True)
[abc123] [UTILITY-DEBUG] Key path not found, using default (key_path=user.phone)
[abc123] [UTILITY-DEBUG] Invalid path, using default (key_path=...)
```

**Error Handling:**
- Returns default if path not found
- Returns default if intermediate value not dict
- Returns default on any exception

---

#### merge_dictionaries()

**Purpose:** Merge multiple dictionaries safely  
**Returns:** dict (merged result)

**Parameters:**
- `*dicts` (dict): Variable number of dictionaries
- `correlation_id` (str, optional): Debug correlation ID

**Behavior:**
- Shallow merge (uses dict.update())
- Later dicts override earlier
- Skips non-dict values

**Usage:**
```python
ops = UtilityDataOperations(manager)

result = ops.merge_dictionaries(
    {'a': 1, 'b': 2},
    {'c': 3, 'd': 4},
    {'b': 20, 'e': 5}
)
# Result: {'a': 1, 'b': 20, 'c': 3, 'd': 4, 'e': 5}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Multiple dictionaries merged (dict_count=3, result_keys=5)
[abc123] [UTILITY-DEBUG] Dictionary merge failed (error=...)
```

**Error Handling:**
- Returns `{}` on error
- Logs error details

---

### Formatting Operations

#### format_bytes()

**Purpose:** Format bytes to human-readable string  
**Returns:** str (formatted size)

**Parameters:**
- `size` (int): Size in bytes
- `correlation_id` (str, optional): Debug correlation ID

**Units:** B, KB, MB, GB, TB, PB

**Usage:**
```python
ops = UtilityDataOperations(manager)

result = ops.format_bytes(1024)
# Result: "1.00 KB"

result = ops.format_bytes(1048576)
# Result: "1.00 MB"

result = ops.format_bytes(1073741824)
# Result: "1.00 GB"

result = ops.format_bytes(500)
# Result: "500.00 B"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Bytes formatted (size=1048576, result=1.00 MB)
[abc123] [UTILITY-DEBUG] Bytes formatted (PB) (result=5.00 PB)
```

---

#### format_data_for_response()

**Purpose:** Format data for API response  
**Returns:** dict (formatted response)

**Parameters:**
- `data` (Any): Data to format
- `format_type` (str, default="json"): Format type
- `include_metadata` (bool, default=True): Include metadata
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityDataOperations(manager)

result = ops.format_data_for_response(
    {'key': 'value'},
    format_type='json',
    include_metadata=True
)
# Result: {
#   'data': {'key': 'value'},
#   'format': 'json',
#   'metadata': {
#       'timestamp': 1702480800,
#       'type': 'dict'
#   }
# }

# Without metadata
result = ops.format_data_for_response(
    [1, 2, 3],
    include_metadata=False
)
# Result: {
#   'data': [1, 2, 3],
#   'format': 'json'
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data formatted for response (format_type=json, include_metadata=True)
```

---

### Cache Management

#### cleanup_cache()

**Purpose:** Clean up old cached utility data  
**Returns:** int (number of items cleared)

**Parameters:**
- `max_age_seconds` (int, default=3600): Maximum age (currently unused - clears all)
- `correlation_id` (str, optional): Debug correlation ID

**Behavior:**
- Clears JSON cache
- Clears cache order tracking
- Increments LUGS integration counter

**Usage:**
```python
ops = UtilityDataOperations(manager)

cleared = ops.cleanup_cache()
# Result: 45 (number of cached items)
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Cache cleaned up (cleared_count=45)
[abc123] [UTILITY-DEBUG] Cache cleanup failed (error=...)
[abc123] [UTILITY-DEBUG] Rate limit exceeded in cleanup_cache()
```

**Error Handling:**
- Returns 0 on error
- Logs error details
- Returns 0 if rate limited

---

### Performance Optimization

#### optimize_performance()

**Purpose:** Optimize utility performance based on usage patterns  
**Returns:** dict (optimization results)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Optimizations:**
1. **High Latency Detection:** Operations > 100ms
2. **Low Cache Hit Rate:** < 50% with > 10 misses
3. **ID Pool Replenishment:** < 10 UUIDs remaining
4. **Cache Limit Warning:** > 90% full

**Usage:**
```python
ops = UtilityDataOperations(manager)

result = ops.optimize_performance()
# Result: {
#   'optimizations_applied': [
#       'High latency detected for parse_json',
#       'Replenished ID pool',
#       'JSON cache approaching limit'
#   ],
#   'timestamp': 1702480800
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Performance optimization complete (optimizations_count=3)
[abc123] [UTILITY-DEBUG] Rate limit exceeded in optimize_performance()
```

**Error Handling:**
- Returns `{'error': 'Rate limit exceeded'}` if rate limited

---

#### configure_caching()

**Purpose:** Configure utility caching settings  
**Returns:** bool (True if successful)

**Parameters:**
- `enabled` (bool): Enable/disable caching
- `ttl` (int, default=300): Cache TTL in seconds
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityDataOperations(manager)

# Enable caching with 10-minute TTL
success = ops.configure_caching(enabled=True, ttl=600)
# Result: True

# Disable caching
success = ops.configure_caching(enabled=False)
# Result: True
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Caching configured (enabled=True, ttl=600)
[abc123] [UTILITY-DEBUG] Caching configuration failed (error=...)
```

**Error Handling:**
- Returns False on error
- Logs debug error details

---

## Usage Patterns

### Initialization
```python
from utility.utility_manager import get_utility_manager
from utility.utility_data import UtilityDataOperations

manager = get_utility_manager()
ops = UtilityDataOperations(manager)
```

### JSON Parsing
```python
# Simple parse
data = ops.parse_json('{"key": "value"}')

# Safe parse with caching
data = ops.parse_json_safely('{"key": "value"}')

# Disable cache
data = ops.parse_json_safely('{"key": "value"}', use_cache=False)
```

### Dictionary Operations
```python
# Deep merge
merged = ops.deep_merge(dict1, dict2)

# Safe nested access
value = ops.safe_get(data, 'user.profile.name', 'Unknown')

# Merge multiple
result = ops.merge_dictionaries(dict1, dict2, dict3)
```

### Formatting
```python
# Bytes
size_str = ops.format_bytes(1048576)

# Response
response = ops.format_data_for_response(data, include_metadata=True)
```

### Cache Management
```python
# Cleanup
cleared = ops.cleanup_cache()

# Configure
ops.configure_caching(enabled=True, ttl=600)

# Optimize
ops.optimize_performance()
```

---

## Debug Integration

**Master Switch:**
- `DEBUG_MODE` - Enables all debugging

**Scope Switches:**
- `UTILITY_DEBUG_MODE` - Utility debug logging
- `UTILITY_DEBUG_TIMING` - Utility timing measurements

**Correlation ID:**
- All methods accept optional `correlation_id` parameter
- Auto-generated via gateway if not provided

---

## Performance Characteristics

### JSON Caching
- **Size:** 100 items (DEFAULT_MAX_JSON_CACHE_SIZE)
- **Key:** hash(json_str)
- **Eviction:** LRU (oldest first)
- **Tracking:** Separate order list

### Deep Merge
- **Recursion:** Unlimited depth
- **Behavior:** Recursive for nested dicts
- **Performance:** O(n) where n = total keys

### Safe Get
- **Path Format:** Dot-separated (e.g., "a.b.c")
- **Validation:** Checks each level is dict
- **Fallback:** Returns default on any error

---

## Related Files

- **Manager:** `utility/utility_manager.py`
- **Core:** `utility/utility_core.py`
- **Types:** `utility/utility_types.py`
- **Interface:** `interface/interface_utility.py`

---

**END OF DOCUMENTATION**
