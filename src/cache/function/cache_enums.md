# cache_enums.py

**Version:** 2025-12-08_1  
**Module:** CACHE  
**Layer:** Core  
**Lines:** 60

---

## Purpose

Cache enums, types, and configuration constants.

---

## Constants

### DEFAULT_CACHE_TTL
- **Value:** 300 (5 minutes)
- **Purpose:** Default time-to-live for cache entries

### MAX_CACHE_BYTES
- **Value:** 104857600 (100MB)
- **Purpose:** Maximum cache memory limit

### RATE_LIMIT_WINDOW_MS
- **Value:** 1000 (1 second)
- **Purpose:** Rate limiting window duration

### RATE_LIMIT_MAX_OPS
- **Value:** 1000
- **Purpose:** Maximum operations per rate limit window

---

## Classes

### _CacheMiss

**Purpose:** Sentinel value for cache misses

**Usage:**
```python
from cache.cache_enums import _CACHE_MISS

result = cache.get('key')
if result is _CACHE_MISS:
    print("Cache miss")
```

---

### CacheOperation

**Purpose:** Enum for cache operation types used in metrics

**Values:**
- `GET` - Get operation
- `SET` - Set operation
- `DELETE` - Delete operation
- `CLEAR` - Clear operation
- `CLEANUP` - Cleanup operation

**Usage:**
```python
from cache.cache_enums import CacheOperation

operation = CacheOperation.GET
```

---

### CacheEntry

**Purpose:** Dataclass for cache entry with metadata

**Attributes:**
- `value: Any` - Cached value
- `timestamp: float` - Entry creation timestamp
- `ttl: int` - Time-to-live in seconds
- `source_module: Optional[str]` - Module that created entry (for LUGS)
- `access_count: int` - Number of times accessed
- `last_access: float` - Last access timestamp
- `value_size_bytes: int` - Estimated memory size

**Usage:**
```python
from cache.cache_enums import CacheEntry

entry = CacheEntry(
    value="data",
    timestamp=time.time(),
    ttl=300,
    source_module="my_module",
    access_count=0,
    last_access=time.time(),
    value_size_bytes=1024
)
```

---

## Exports

```python
__all__ = [
    'DEFAULT_CACHE_TTL',
    'MAX_CACHE_BYTES',
    'RATE_LIMIT_WINDOW_MS',
    'RATE_LIMIT_MAX_OPS',
    '_CacheMiss',
    '_CACHE_MISS',
    'CacheOperation',
    'CacheEntry',
]
```

---

## Related Files

- cache_core.py - Uses these enums and types
- cache_operations.py - Uses constants
- interface_cache.py - Uses sentinel for detection

---

## Changelog

### 2025-12-08_1
- Initial version extracted from cache_core.py
- Consolidated enums, types, and constants
- Added documentation
