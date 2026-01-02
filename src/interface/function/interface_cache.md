# interface_cache.py

**Version:** 2025-12-08_1  
**Module:** CACHE  
**Layer:** Interface  
**Lines:** 155

---

## Purpose

Cache interface router with dictionary dispatch and sentinel sanitization.

---

## Main Function

### execute_cache_operation()

**Signature:**
```python
def execute_cache_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route cache operation requests using dispatch dictionary pattern

**Parameters:**
- `operation` - Operation name to execute
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (type varies by operation)

**Operations:**
- `get` - Get cached value by key
- `set` - Set cached value with optional TTL
- `exists` - Check if key exists
- `delete` - Delete cached value
- `get_metadata` - Get metadata for cache entry
- `clear` - Clear all cache entries
- `reset` - Reset cache to initial state
- `reset_cache` - Alias for reset
- `cleanup_expired` - Remove expired entries
- `get_stats` - Get cache statistics

**Raises:**
- `RuntimeError` - If cache interface unavailable
- `ValueError` - If operation unknown or parameters invalid

---

## Sentinel Sanitization

### _is_sentinel_object()

**Purpose:** Detect if value is object() sentinel

**Pattern:**
```python
if _is_sentinel_object(value):
    return None  # Sanitize
```

**Detection:**
- Type name is 'object'
- Not a standard type (str, int, float, bool, list, dict, tuple, set, None)
- String representation starts with '<object object'

---

### _sanitize_value_deep()

**Purpose:** Recursively remove sentinel objects from data structure

**Signature:**
```python
def _sanitize_value_deep(value: Any, path: str = "root") -> Any
```

**Behavior:**
- Detects sentinel at current level
- Recursively sanitizes nested dicts
- Recursively sanitizes lists/tuples
- Recursively sanitizes sets
- Logs warning when sentinel removed
- Returns sanitized structure

**Usage:**
```python
sanitized = _sanitize_value_deep(raw_value, "cache[key]")
```

---

## Validation Helpers

### _validate_key_param()

**Purpose:** Validate key parameter exists and is string

**Raises:**
- `ValueError` - If key missing
- `TypeError` - If key not string

---

### _validate_set_params()

**Purpose:** Validate and sanitize set operation parameters

**Behavior:**
1. Validate key parameter
2. Check value parameter exists
3. Sanitize value deeply
4. Replace value with sanitized version

---

## Dispatch Dictionary

### _build_dispatch_dict()

**Purpose:** Build dispatch dictionary for O(1) operation lookup

**Pattern:**
```python
_OPERATION_DISPATCH = {
    'get': lambda **kwargs: (
        _validate_key_param(kwargs, 'get'),
        _sanitize_value_deep(
            _execute_get_implementation(**kwargs),
            f"cache[{kwargs['key']}]"
        )
    )[1],
    
    'set': lambda **kwargs: (
        _validate_set_params(kwargs),
        _execute_set_implementation(**kwargs)
    )[1],
    
    # ... other operations
}
```

**Features:**
- O(1) lookup performance
- Inline validation
- Automatic sanitization on get
- Tuple trick for validation + execution

---

## Usage Examples

### Via Gateway

```python
import gateway

# Get with automatic sanitization
value = gateway.cache_get('key')

# Set with validation
gateway.cache_set('key', 'value', ttl=600)

# Check existence
if gateway.cache_exists('key'):
    print("Key exists")
```

### Direct Interface

```python
from cache.interface_cache import execute_cache_operation

# Get operation
result = execute_cache_operation('get', key='my_key')

# Set operation
execute_cache_operation('set', key='my_key', value='data', ttl=300)

# Stats operation
stats = execute_cache_operation('get_stats')
```

### Error Handling

```python
from cache.interface_cache import execute_cache_operation

try:
    result = execute_cache_operation('invalid_op', key='key')
except ValueError as e:
    print(f"Invalid operation: {e}")

try:
    result = execute_cache_operation('get')  # Missing key
except ValueError as e:
    print(f"Missing parameter: {e}")
```

---

## Architecture Integration

**SUGA Pattern:**
```
Gateway → Interface → Core
gateway.cache_get() → execute_cache_operation('get') → _execute_get_implementation()
```

**Dispatch Flow:**
1. Gateway calls `execute_cache_operation()`
2. Interface validates parameters
3. Interface sanitizes sentinels
4. Interface dispatches to core implementation
5. Core executes operation
6. Interface sanitizes result
7. Result returned to gateway

**Performance:**
- O(1) operation lookup via dictionary
- Validation happens inline
- Sanitization only on get operations
- Minimal overhead (~0.1ms)

---

## Security Features

### Sentinel Detection

Prevents `object()` sentinels from leaking into cache responses:
- Detects on get operations
- Detects on set operations
- Recursively sanitizes nested structures
- Logs warnings when detected

### Parameter Validation

- Key must be string
- Value must be provided for set
- Operation must be valid
- Automatic sanitization before storage

---

## Related Files

- cache_core.py - Core cache implementation
- cache_operations.py - Implementation wrappers
- cache_enums.py - Types and constants
- gateway/gateway_wrappers_cache.py - Gateway wrappers

---

## Exports

```python
__all__ = ['execute_cache_operation']
```

---

## Changelog

### 2025-12-08_1
- Updated imports to use cache package
- Maintained sentinel sanitization
- Dictionary dispatch pattern
- Consistent documentation
- 155 lines (under 300 limit)

### 2025.10.21.01
- Added reset operation to dispatch

### 2025.10.19.21
- Added sentinel sanitization on get

### 2025.10.17.18
- Added get_metadata operation

### 2025.10.17.17
- Modernized with dispatch dictionary
