# singleton_manager.md

**Version:** 2025-12-13_1  
**Purpose:** Singleton instance manager with rate limiting  
**Module:** singleton/singleton_manager.py  
**Type:** Singleton Manager

---

## OVERVIEW

Manages singleton instances across the application with rate limiting, factory pattern support, and comprehensive lifecycle management.

**Key Features:**
- Singleton instance per Lambda container
- Factory pattern for lazy initialization
- Rate limiting (1000 ops/sec)
- Access count tracking
- Creation time tracking
- Memory estimation
- Lambda-safe (no threading)

**Irony:** The singleton manager itself uses the SINGLETON pattern!

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SINGLETON: Single instance via get_singleton_manager()
- Factory Pattern: Lazy initialization support
- Rate Limiting: 1000 operations/second protection

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern (self-referential!)
- LESS-21: Rate limiting for DoS protection

---

## SINGLETON vs CACHE DISTINCTION

**SINGLETON manages:**
- **Object instances** (classes, managers, services)
- CacheManager, ConfigManager, SecurityValidator
- No TTL - permanent until explicitly deleted
- Factory pattern for complex initialization
- Access count tracking for monitoring

**CACHE manages:**
- **Data values** (strings, dicts, primitives)
- API responses, computed values, temporary data
- TTL and LRU eviction for automatic cleanup
- Simple get/set operations
- Memory optimization focus

**Example:**
```python
# SINGLETON - Object instance
singleton.set('cache_manager', CacheManager())

# CACHE - Data value
cache.set('user:123', user_data, ttl=300)
```

---

## ENUMS

### SingletonOperation

Enumeration of all singleton operations.

**Definition:**
```python
class SingletonOperation(Enum):
    GET = "get"
    SET = "set"
    HAS = "has"
    DELETE = "delete"
    CLEAR = "clear"
    GET_STATS = "get_stats"
    RESET = "reset"
    # Legacy operations
    RESET_ALL = "reset_all"
    EXISTS = "exists"
```

**Usage:**
```python
from singleton.singleton_manager import SingletonOperation

operation = SingletonOperation.GET
result = execute_singleton_operation(operation, name='cache_manager')
```

---

## CLASSES

### SingletonCore

Main manager class for singleton instances with SINGLETON pattern and rate limiting.

**Initialization:**
```python
def __init__(self):
    self._instances: Dict[str, Any] = {}
    self._creation_times: Dict[str, float] = {}
    self._access_counts: Dict[str, int] = {}
    
    # Rate limiting (1000 ops/sec)
    self._rate_limiter = deque(maxlen=1000)
    self._rate_limit_window_ms = 1000
    self._rate_limited_count = 0
```

**State:**
- `_instances`: Dictionary mapping names to instances
- `_creation_times`: When each singleton was created
- `_access_counts`: How many times each accessed
- `_rate_limiter`: Deque tracking operation timestamps
- `_rate_limit_window_ms`: Rate limit window (1000ms)
- `_rate_limited_count`: Count of rate-limited operations

---

## METHODS

### _check_rate_limit()

**Private method** - Check if operation is within rate limit.

**Signature:**
```python
def _check_rate_limit(self) -> bool
```

**Returns:**
- `bool`: True if allowed, False if rate limited

**Algorithm:** Same as other manager rate limiters (sliding window with deque)

**Rate Limit:** 1000 operations per second

---

### get()

Get or create singleton instance with factory pattern support.

**Signature:**
```python
def get(
    self,
    name: str,
    factory_func: Optional[Callable] = None,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `factory_func` (Optional[Callable]): Factory function to create instance
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Any`: Singleton instance
- `None`: If not exists and no factory provided

**Raises:**
- `ValueError`: If name is empty or invalid type
- `ValueError`: If rate limited
- `Exception`: If factory function raises exception

**Factory Pattern:**
```python
manager = get_singleton_manager()

def create_cache():
    """Factory function for cache manager."""
    cache = CacheManager()
    cache.initialize()
    return cache

# First call - creates instance (slow)
cache = manager.get('cache_manager', factory_func=create_cache)

# Subsequent calls - returns cached (fast)
cache = manager.get('cache_manager')  # No factory needed
```

**Access Counting:**
```python
manager = get_singleton_manager()

# Each get() increments access count
cache = manager.get('cache_manager')  # access_count = 1
cache = manager.get('cache_manager')  # access_count = 2
cache = manager.get('cache_manager')  # access_count = 3

stats = manager.get_stats()
print(stats['access_counts']['cache_manager'])  # 3
```

---

### set()

Set singleton instance.

**Signature:**
```python
def set(
    self,
    name: str,
    instance: Any,
    correlation_id: str = None,
    **kwargs
)
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `instance` (Any): Instance to store
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Raises:**
- `ValueError`: If name is empty or invalid type
- `ValueError`: If rate limited

**Behavior:**
- Stores instance under given name
- Records creation time (current timestamp)
- Resets access count to 0
- Overwrites existing instance if present

**Example:**
```python
manager = get_singleton_manager()

# Create and store
config = ConfigManager()
config.load('/path/to/config.yaml')
manager.set('config_manager', config)

# Overwrite existing
new_config = ConfigManager()
manager.set('config_manager', new_config)  # Replaces old instance
```

---

### has()

Check if singleton exists.

**Signature:**
```python
def has(
    self,
    name: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `name` (str): Singleton name
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if exists, False otherwise
- `False`: If rate limited

**Example:**
```python
manager = get_singleton_manager()

# Check existence
if manager.has('cache_manager'):
    cache = manager.get('cache_manager')
else:
    cache = CacheManager()
    manager.set('cache_manager', cache)
```

---

### delete()

Delete singleton instance.

**Signature:**
```python
def delete(
    self,
    name: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `name` (str): Singleton name
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if deleted, False if didn't exist or rate limited

**Behavior:**
- Removes instance from `_instances`
- Removes creation time from `_creation_times`
- Removes access count from `_access_counts`
- Python GC handles memory cleanup

**Example:**
```python
manager = get_singleton_manager()

# Delete specific singleton
if manager.delete('temp_cache'):
    print("Temp cache deleted")
else:
    print("Temp cache didn't exist")

# Clean up test instances
manager.delete('test_manager_1')
manager.delete('test_manager_2')
```

---

### clear()

Clear all singleton instances.

**Signature:**
```python
def clear(
    self,
    correlation_id: str = None,
    **kwargs
) -> int
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs**: Additional arguments (ignored)

**Returns:**
- `int`: Count of singletons cleared
- `0`: If rate limited

**Behavior:**
- Clears all dictionaries: instances, creation times, access counts
- Python GC handles memory cleanup
- Useful for test isolation and memory relief

**Example:**
```python
manager = get_singleton_manager()

# Clear all singletons
count = manager.clear()
print(f"Cleared {count} singletons")

# Verify cleared
stats = manager.get_stats()
assert stats['total_singletons'] == 0
```

---

### get_stats()

Get comprehensive statistics about managed singletons.

**Signature:**
```python
def get_stats(
    self,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs**: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Response Structure:**
```python
{
    'total_singletons': 5,
    'singleton_names': ['cache_manager', 'config', 'validator', ...],
    'singleton_types': {
        'cache_manager': 'CacheManager',
        'config': 'ConfigManager',
        'validator': 'SecurityValidator'
    },
    'creation_times': {
        'cache_manager': 1702500000.123,
        'config': 1702500001.456
    },
    'access_counts': {
        'cache_manager': 42,
        'config': 15,
        'validator': 8
    },
    'estimated_memory_bytes': 12345,
    'estimated_memory_kb': 12.05,
    'estimated_memory_mb': 0.01,
    'memory_note': 'Estimates are shallow size only (sys.getsizeof)',
    'rate_limited_count': 2,
    'timestamp': 1702500100.789
}
```

**Memory Estimation:**
- Uses `sys.getsizeof()` - shallow size only
- Does NOT include referenced objects
- Underestimates true memory usage
- Useful for relative comparisons

**Example:**
```python
manager = get_singleton_manager()

stats = manager.get_stats()

print(f"Total singletons: {stats['total_singletons']}")
print(f"Memory (shallow): {stats['estimated_memory_mb']:.2f} MB")
print(f"Rate limited: {stats['rate_limited_count']}")

# List all with details
for name in stats['singleton_names']:
    print(f"{name}:")
    print(f"  Type: {stats['singleton_types'][name]}")
    print(f"  Accessed: {stats['access_counts'][name]} times")
    print(f"  Created: {stats['creation_times'][name]}")
```

---

### reset()

Reset SINGLETON manager state (lifecycle management).

**Signature:**
```python
def reset(
    self,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs**: Additional arguments (ignored)

**Returns:**
- `bool`: True if reset successful, False if rate limited

**Behavior:**
- Clears rate limiter deque
- Resets rate limited count to 0
- Does NOT clear singleton instances (use clear() for that)

**Use Cases:**
- Reset rate limiting for testing
- Clear rate limit statistics

**Example:**
```python
manager = get_singleton_manager()

# Reset manager state
if manager.reset():
    print("Manager reset successful")
    # Rate limiter cleared, can now perform 1000 ops
else:
    print("Reset failed (rate limited)")
```

---

### reset_all() [Legacy]

Legacy name for clear() operation.

**Signature:**
```python
def reset_all(self, **kwargs) -> int
```

**Note:** Backward compatibility alias. Use clear() for new code.

---

### exists() [Legacy]

Legacy name for has() operation.

**Signature:**
```python
def exists(self, name: str, **kwargs) -> bool
```

**Note:** Backward compatibility alias. Use has() for new code.

---

## SINGLETON PATTERN

### get_singleton_manager()

Get SINGLETON manager instance (ironic self-reference!).

**Function:** Module-level singleton factory

**Signature:**
```python
def get_singleton_manager() -> SingletonCore
```

**Returns:**
- `SingletonCore`: The singleton manager instance

**Implementation:**
```python
_manager_core = None  # Module-level singleton

def get_singleton_manager() -> SingletonCore:
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        # Try gateway SINGLETON registry first
        manager = singleton_get('singleton_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = SingletonCore()
            singleton_register('singleton_manager', _manager_core)
            manager = _manager_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _manager_core is None:
            _manager_core = SingletonCore()
        return _manager_core
```

**Irony:**
The singleton manager manages singletons, including itself! It uses the SINGLETON pattern to ensure only one manager instance exists.

**Usage:**
```python
# Always use this function to get manager
manager = get_singleton_manager()

# Never instantiate directly
# manager = SingletonCore()  # ❌ WRONG
```

---

## RATE LIMITING

### Design

**Limit:** 1000 operations/second  
**Window:** 1000ms sliding window  
**Implementation:** Deque with maxlen=1000

**Why 1000 ops/sec?**
- Infrastructure component needs high throughput
- Prevents DoS attacks
- Still allows burst traffic
- Higher than typical usage

---

## FACTORY PATTERN

### Lazy Initialization Benefits

**Without Factory:**
```python
# Eager initialization - always creates
cache = CacheManager()
cache.initialize()  # Expensive!
manager.set('cache_manager', cache)

# Problem: Initialization cost paid even if never used
```

**With Factory:**
```python
# Lazy initialization - creates only when needed
def create_cache():
    cache = CacheManager()
    cache.initialize()  # Expensive!
    return cache

# First get() - creates instance (slow)
cache = manager.get('cache_manager', factory_func=create_cache)

# Subsequent get() - fast retrieval
cache = manager.get('cache_manager')  # No initialization!
```

**Benefits:**
1. Defers expensive initialization until first use
2. Only one instance ever created
3. Subsequent access is fast (no recreation)
4. Reduces cold start time if not needed
5. Thread-safe in Lambda's single-threaded environment

---

## USAGE PATTERNS

### Pattern 1: Lazy Initialization

```python
from singleton.singleton_manager import get_singleton_manager

manager = get_singleton_manager()

def get_or_create_cache():
    """Get or create cache manager (lazy)."""
    return manager.get(
        'cache_manager',
        factory_func=lambda: CacheManager()
    )

# Usage
cache = get_or_create_cache()  # Creates on first call
cache = get_or_create_cache()  # Fast on subsequent calls
```

---

### Pattern 2: Explicit Registration

```python
from singleton.singleton_manager import get_singleton_manager

manager = get_singleton_manager()

def initialize_services():
    """Initialize all singleton services (explicit)."""
    # Cache manager
    cache = CacheManager()
    cache.initialize()
    manager.set('cache_manager', cache)
    
    # Config manager
    config = ConfigLoader()
    config.load('/path/to/config')
    manager.set('config', config)
    
    # Security validator
    validator = SecurityValidator()
    validator.load_rules()
    manager.set('validator', validator)

# Call during Lambda initialization
initialize_services()
```

---

### Pattern 3: Conditional Creation

```python
from singleton.singleton_manager import get_singleton_manager

manager = get_singleton_manager()

def ensure_validator():
    """Ensure validator exists."""
    if not manager.has('validator'):
        validator = SecurityValidator()
        validator.load_rules()
        manager.set('validator', validator)
    
    return manager.get('validator')

# Safe to call multiple times
validator = ensure_validator()
```

---

### Pattern 4: Test Isolation

```python
from singleton.singleton_manager import get_singleton_manager

manager = get_singleton_manager()

def test_with_mocks():
    """Test with mock singletons."""
    # Setup - clear existing
    manager.clear()
    
    # Register mocks
    mock_cache = MockCacheManager()
    manager.set('cache_manager', mock_cache)
    
    mock_config = MockConfigManager()
    manager.set('config', mock_config)
    
    # Run test
    result = my_function()
    
    # Verify
    assert mock_cache.get_called
    assert mock_config.load_called
    
    # Teardown
    manager.clear()
```

---

### Pattern 5: Access Monitoring

```python
from singleton.singleton_manager import get_singleton_manager

manager = get_singleton_manager()

def monitor_singleton_usage():
    """Monitor which singletons are heavily used."""
    stats = manager.get_stats()
    
    for name, count in stats['access_counts'].items():
        if count > 1000:
            logger.warning(
                "High singleton access",
                extra={'name': name, 'count': count}
            )
        elif count == 0:
            logger.info(
                "Unused singleton",
                extra={'name': name}
            )
```

---

## EXPORTS

```python
__all__ = [
    'SingletonOperation',
    'SingletonCore',
    'get_singleton_manager',
]
```

---

## RELATED DOCUMENTATION

- **singleton_core.md**: Gateway implementation functions
- **singleton_convenience.md**: Convenience accessor functions
- **singleton_memory.md**: Memory monitoring utilities
- **interface_singleton.md**: Interface layer

---

**END OF DOCUMENTATION**

**Module:** singleton/singleton_manager.py  
**Classes:** 2 (SingletonOperation, SingletonCore)  
**Functions:** 1 (get_singleton_manager)  
**Pattern:** SINGLETON managing SINGLETONs (ironic!)
