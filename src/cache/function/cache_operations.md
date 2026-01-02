# cache_operations.py

**Version:** 2025-12-08_1  
**Module:** CACHE  
**Layer:** Core  
**Lines:** 145

---

## Purpose

Module-level cache operations and interface implementation wrappers.

---

## Module-Level Operations

### cache_get()

**Signature:**
```python
def cache_get(key: str) -> Any
```

**Purpose:** Get value from cache

**Returns:** Cached value or `_CACHE_MISS` sentinel

**Usage:**
```python
from cache import cache_get

value = cache_get('my_key')
```

---

### cache_set()

**Signature:**
```python
def cache_set(key: str, value: Any, ttl: int = 300, source_module: Optional[str] = None) -> None
```

**Purpose:** Set cache entry

**Parameters:**
- `key` - Cache key
- `value` - Value to cache
- `ttl` - Time-to-live (default: 300s)
- `source_module` - Module name for LUGS (optional)

---

### cache_exists()

**Signature:**
```python
def cache_exists(key: str) -> bool
```

**Purpose:** Check if key exists in cache

---

### cache_delete()

**Signature:**
```python
def cache_delete(key: str) -> bool
```

**Purpose:** Delete cache entry

**Returns:** True if deleted, False if not found

---

### cache_clear()

**Signature:**
```python
def cache_clear() -> int
```

**Purpose:** Clear all cache entries

**Returns:** Number of entries cleared

---

### cache_reset()

**Signature:**
```python
def cache_reset() -> bool
```

**Purpose:** Reset cache to initial state

**Returns:** True on success

---

### cache_cleanup_expired()

**Signature:**
```python
def cache_cleanup_expired() -> int
```

**Purpose:** Remove expired entries

**Returns:** Number of entries removed

---

### cache_get_stats()

**Signature:**
```python
def cache_get_stats() -> Dict[str, Any]
```

**Purpose:** Get cache statistics

**Returns:** Statistics dictionary

---

### cache_get_metadata()

**Signature:**
```python
def cache_get_metadata(key: str) -> Optional[Dict[str, Any]]
```

**Purpose:** Get cache entry metadata

**Returns:** Metadata dictionary or None

---

### cache_get_module_dependencies()

**Signature:**
```python
def cache_get_module_dependencies() -> Set[str]
```

**Purpose:** Get module dependencies

**Returns:** Set of module names

---

## Interface Implementation Wrappers

These functions are used by `interface_cache.py` and should not be called directly.

### _execute_get_implementation()

**Purpose:** Implementation wrapper for cache get operation

---

### _execute_set_implementation()

**Purpose:** Implementation wrapper for cache set operation

---

### _execute_exists_implementation()

**Purpose:** Implementation wrapper for cache exists operation

---

### _execute_delete_implementation()

**Purpose:** Implementation wrapper for cache delete operation

---

### _execute_clear_implementation()

**Purpose:** Implementation wrapper for cache clear operation

---

### _execute_reset_implementation()

**Purpose:** Implementation wrapper for cache reset operation

---

### _execute_cleanup_expired_implementation()

**Purpose:** Implementation wrapper for cache cleanup operation

---

### _execute_get_stats_implementation()

**Purpose:** Implementation wrapper for cache stats operation

---

### _execute_get_metadata_implementation()

**Purpose:** Implementation wrapper for cache metadata operation

---

### _execute_get_module_dependencies_implementation()

**Purpose:** Implementation wrapper for module dependencies operation

---

## Usage Examples

### Basic Operations

```python
from cache import cache_get, cache_set, cache_exists

# Set value
cache_set('user:123', {'name': 'Alice'}, ttl=600)

# Get value
user = cache_get('user:123')

# Check existence
if cache_exists('user:123'):
    print("User cached")
```

### LUGS Tracking

```python
from cache import cache_set, cache_get_module_dependencies

# Set with module tracking
cache_set('config', data, source_module='config_loader')

# Get dependencies
modules = cache_get_module_dependencies()
print(f"Modules using cache: {modules}")
```

### Cache Maintenance

```python
from cache import cache_cleanup_expired, cache_get_stats

# Remove expired entries
removed = cache_cleanup_expired()
print(f"Removed {removed} expired entries")

# Check stats
stats = cache_get_stats()
print(f"Cache: {stats['size']} entries, {stats['memory_mb']}MB")
```

---

## Integration

**SUGA Layer:** Core  
**Used By:**
- interface_cache.py (via implementation wrappers)
- Direct imports via `import cache`
- Gateway wrappers

**Pattern:**
```python
# Module-level convenience
from cache import cache_get
value = cache_get('key')

# Via gateway
import gateway
value = gateway.cache_get('key')

# Via interface
from cache.interface_cache import execute_cache_operation
value = execute_cache_operation('get', key='key')
```

---

## Related Files

- cache_core.py - LUGSIntegratedCache class
- cache_enums.py - Types and constants
- interface_cache.py - Interface router
- gateway/gateway_wrappers_cache.py - Gateway wrappers

---

## Exports

```python
__all__ = [
    # Module-level operations
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_reset',
    'cache_cleanup_expired',
    'cache_get_stats',
    'cache_get_metadata',
    'cache_get_module_dependencies',
    
    # Implementation wrappers (internal)
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_exists_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_reset_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_get_metadata_implementation',
    '_execute_get_module_dependencies_implementation',
]
```

---

## Changelog

### 2025-12-08_1
- Extracted from cache_core.py
- 10 module-level operations
- 10 interface implementation wrappers
- Consistent documentation
- 145 lines (well under 300 limit)
