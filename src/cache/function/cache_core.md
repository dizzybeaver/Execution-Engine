# cache_core.py

**Version:** 2025-12-08_1  
**Module:** CACHE  
**Layer:** Core  
**Lines:** 295

---

## Purpose

LUGS-integrated cache with TTL expiration, LRU eviction, rate limiting, and metrics integration.

---

## Classes

### LUGSIntegratedCache

**Purpose:** In-memory cache with LUGS tracking, metrics, and DoS protection

**Initialization:**
```python
cache = LUGSIntegratedCache(max_bytes=104857600)
```

**Features:**
- TTL-based expiration
- LRU eviction on memory pressure
- Module dependency tracking (LUGS)
- Rate limiting (1000 ops/sec)
- Metrics integration via gateway
- Memory bounded (100MB default)

---

## Methods

### set()

**Signature:**
```python
def set(key: str, value: Any, ttl: int = 300, source_module: Optional[str] = None) -> None
```

**Purpose:** Set cache entry with TTL and optional module tracking

**Parameters:**
- `key` - Cache key (validated via security interface)
- `value` - Value to cache (any type)
- `ttl` - Time-to-live in seconds (default: 300)
- `source_module` - Module name for LUGS tracking (optional)

**Behavior:**
1. Check rate limit (returns silently if limited)
2. Validate parameters via security interface
3. Handle memory pressure if needed
4. Evict LRU entries if space needed
5. Create/update cache entry
6. Track metrics
7. Register LUGS dependency if source_module provided

**Performance:** ~1-5ms typical

---

### get()

**Signature:**
```python
def get(key: str) -> Any
```

**Purpose:** Get cached value if exists and not expired

**Returns:** 
- Cached value if found and valid
- `_CACHE_MISS` sentinel if not found or expired

**Behavior:**
1. Check rate limit
2. Check if key exists
3. Validate TTL (remove if expired)
4. Update access metadata
5. Track hit/miss metrics
6. Return value or sentinel

**Performance:** <1ms typical

---

### exists()

**Signature:**
```python
def exists(key: str) -> bool
```

**Purpose:** Check if key exists and is not expired

**Returns:** True if exists and valid, False otherwise

---

### delete()

**Signature:**
```python
def delete(key: str) -> bool
```

**Purpose:** Delete cache entry if exists

**Returns:** True if deleted, False if not found

---

### clear()

**Signature:**
```python
def clear() -> int
```

**Purpose:** Clear all cache entries

**Returns:** Number of entries cleared

---

### reset()

**Signature:**
```python
def reset() -> bool
```

**Purpose:** Reset cache to initial state (clears entries, stats, rate limiter)

**Returns:** True on success

---

### cleanup_expired()

**Signature:**
```python
def cleanup_expired() -> int
```

**Purpose:** Remove all expired entries

**Returns:** Number of entries removed

---

### get_metadata()

**Signature:**
```python
def get_metadata(key: str) -> Optional[Dict[str, Any]]
```

**Purpose:** Get cache entry metadata without accessing value

**Returns:**
```python
{
    'source_module': str,
    'timestamp': float,
    'age_seconds': float,
    'ttl': int,
    'ttl_remaining': int,
    'access_count': int,
    'last_access': float,
    'size_bytes': int,
    'is_expired': bool
}
```

---

### get_stats()

**Signature:**
```python
def get_stats() -> Dict[str, Any]
```

**Purpose:** Get cache statistics

**Returns:**
```python
{
    'size': int,
    'memory_bytes': int,
    'memory_mb': float,
    'max_bytes': int,
    'max_mb': float,
    'memory_utilization_percent': float,
    'default_ttl_seconds': int,
    'rate_limited_count': int
}
```

---

### get_module_dependencies()

**Signature:**
```python
def get_module_dependencies() -> Set[str]
```

**Purpose:** Get set of all module names with cache dependencies

**Returns:** Set of module names

---

## Functions

### _get_cache_instance()

**Purpose:** Get or create cache singleton via SINGLETON interface

**Returns:** LUGSIntegratedCache instance

**Pattern:**
```python
cache = _get_cache_instance()
```

**Behavior:**
1. Try to get from SINGLETON interface
2. Create and register if not exists
3. Fallback to module-level singleton if gateway unavailable

---

## Internal Methods

### _check_rate_limit()
Rate limiting using sliding window (1000 ops/sec)

### _calculate_entry_size()
Estimate memory size of cache entry

### _check_memory_pressure()
Check if cache >80% full

### _evict_lru_entries()
Evict least recently used entries

### _handle_memory_pressure()
Free 20% of memory via LRU eviction

---

## Usage Examples

```python
from cache.cache_core import _get_cache_instance

cache = _get_cache_instance()

# Set value
cache.set('key', 'value', ttl=600, source_module='my_module')

# Get value
value = cache.get('key')
if value is not _CACHE_MISS:
    print(f"Found: {value}")

# Check existence
if cache.exists('key'):
    print("Key exists")

# Get metadata
metadata = cache.get_metadata('key')
print(f"TTL remaining: {metadata['ttl_remaining']}s")

# Get stats
stats = cache.get_stats()
print(f"Cache size: {stats['size']} entries, {stats['memory_mb']}MB")

# Cleanup
expired_count = cache.cleanup_expired()
print(f"Removed {expired_count} expired entries")
```

---

## Integration

**SUGA Layer:** Core  
**Gateway Access:** Via cache operations and interface

**Metrics Integration:**
- `cache.total_sets` - Set operations
- `cache.entries_evicted` - LRU evictions
- `cache.entries_expired` - Expired entries
- `cache.metadata_queries` - Metadata queries

**Security Integration:**
- Key validation via `gateway.validate_cache_key()`
- TTL validation via `gateway.validate_ttl()`
- Module name validation via `gateway.validate_module_name()`

**LUGS Integration:**
- Dependency tracking via `gateway.add_cache_module_dependency()`

---

## Related Files

- cache_enums.py - Enums and types
- cache_operations.py - Module-level operations
- interface_cache.py - Interface router
- gateway/gateway_wrappers_cache.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Refactored from monolithic cache_core.py
- Extracted enums to cache_enums.py
- Extracted operations to cache_operations.py
- Reduced from 600 to 295 lines
- Applied consistent documentation
- Maintained all functionality
