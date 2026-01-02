# singleton_core.md

**Version:** 2025-12-13_1  
**Purpose:** Gateway implementation functions for singleton interface  
**Module:** singleton/singleton_core.py  
**Type:** Core Implementation Functions

---

## OVERVIEW

Provides gateway-accessible implementation functions for singleton instance management. All functions delegate to the singleton SingletonManager and include comprehensive debug integration.

**Pattern:** Gateway → Interface → Core (SUGA)  
**Singleton:** All operations use get_singleton_manager() (ironic self-reference!)  
**Debug:** All functions integrate correlation_id tracking

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SUGA: Gateway implementation layer
- SINGLETON: Uses get_singleton_manager() (LESS-18)
- Debug Integration: All functions support correlation_id

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-21: Rate limiting (1000 ops/sec)

---

## SINGLETON vs CACHE

**SINGLETON manages:**
- Object instances (classes, managers, services)
- No TTL (permanent until explicitly deleted)
- Factory pattern for lazy initialization
- Access count tracking

**CACHE manages:**
- Data values (strings, dicts, primitives)
- TTL and LRU eviction
- Simple get/set operations
- Memory optimization

---

## FUNCTIONS

### execute_singleton_operation()

Universal singleton operation executor with error handling.

**Signature:**
```python
def execute_singleton_operation(
    operation: SingletonOperation,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `operation` (SingletonOperation): Operation enum value
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Operation-specific parameters

**Returns:**
- `Any`: Result from the specific operation

**Raises:**
- `ValueError`: If operation type is invalid
- `Exception`: If operation execution fails

**Supported Operations:**
- GET: Get or create singleton instance
- SET: Set singleton instance
- HAS: Check if singleton exists
- DELETE: Delete singleton instance
- CLEAR: Clear all singleton instances
- GET_STATS: Get statistics
- RESET: Reset manager state
- RESET_ALL: Legacy clear operation
- EXISTS: Legacy has operation

**Example:**
```python
from singleton.singleton_core import execute_singleton_operation
from singleton.singleton_manager import SingletonOperation

# Get singleton
instance = execute_singleton_operation(
    SingletonOperation.GET,
    name='cache_manager'
)

# Set singleton
execute_singleton_operation(
    SingletonOperation.SET,
    name='config',
    instance=config_obj
)
```

---

### get_implementation()

Get or create singleton instance.

**Signature:**
```python
def get_implementation(
    name: str,
    factory_func: Optional[Callable] = None,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `factory_func` (Optional[Callable]): Factory function to create instance if not exists
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Any`: Singleton instance
- `None`: If not exists and no factory provided

**Raises:**
- `ValueError`: If name is empty or rate limited
- `Exception`: If factory function raises exception

**Factory Pattern:**
```python
from singleton.singleton_core import get_implementation

def create_cache_manager():
    """Factory function for cache manager."""
    manager = CacheManager()
    manager.initialize()
    return manager

# First call - creates instance
cache = get_implementation('cache_manager', factory_func=create_cache_manager)

# Subsequent calls - returns cached instance
cache = get_implementation('cache_manager')  # No factory needed
```

**Example:**
```python
from singleton.singleton_core import get_implementation

# Get existing singleton
config = get_implementation('config_manager')

# Get or create with factory
cache = get_implementation(
    'cache_manager',
    factory_func=lambda: CacheManager()
)

# Get non-existent singleton (returns None)
validator = get_implementation('validator')
if validator is None:
    print("Validator not initialized")
```

---

### set_implementation()

Set singleton instance.

**Signature:**
```python
def set_implementation(
    name: str,
    instance: Any,
    correlation_id: str = None,
    **kwargs
)
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `instance` (Any): Instance to store (required)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Raises:**
- `ValueError`: If name is empty or instance is None
- `ValueError`: If rate limited

**Behavior:**
- Stores instance under given name
- Overwrites existing instance if present
- Records creation time
- Resets access count to 0

**Example:**
```python
from singleton.singleton_core import set_implementation

# Create and store manager
config = ConfigManager()
config.load('/path/to/config.yaml')
set_implementation('config_manager', config)

# Store service instance
validator = SecurityValidator()
set_implementation('security_validator', validator)
```

---

### has_implementation()

Check if singleton exists.

**Signature:**
```python
def has_implementation(
    name: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if exists, False otherwise
- `False`: If rate limited

**Raises:**
- `ValueError`: If name is empty

**Example:**
```python
from singleton.singleton_core import has_implementation, get_implementation

# Check before getting
if has_implementation('cache_manager'):
    cache = get_implementation('cache_manager')
    print("Cache available")
else:
    print("Cache not initialized")

# Conditional initialization
if not has_implementation('validator'):
    validator = SecurityValidator()
    set_implementation('validator', validator)
```

---

### delete_implementation()

Delete singleton instance.

**Signature:**
```python
def delete_implementation(
    name: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `name` (str): Singleton name (required, non-empty)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if deleted, False if didn't exist or rate limited

**Raises:**
- `ValueError`: If name is empty

**Behavior:**
- Removes instance from storage
- Removes creation time record
- Removes access count record
- Does NOT call destructor (Python GC handles cleanup)

**Example:**
```python
from singleton.singleton_core import delete_implementation, has_implementation

# Delete specific singleton
if delete_implementation('temp_cache'):
    print("Temp cache deleted")
else:
    print("Temp cache didn't exist")

# Clean up after test
delete_implementation('test_manager')
delete_implementation('test_validator')
```

---

### clear_implementation()

Clear all singleton instances.

**Signature:**
```python
def clear_implementation(
    correlation_id: str = None,
    **kwargs
) -> int
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `int`: Count of singletons cleared
- `0`: If rate limited

**Behavior:**
- Removes ALL instances
- Clears ALL creation times
- Clears ALL access counts
- Python GC handles cleanup

**Use Cases:**
- Test isolation
- Memory pressure relief
- Container reset

**Example:**
```python
from singleton.singleton_core import clear_implementation

# Clear all singletons
count = clear_implementation()
print(f"Cleared {count} singletons")

# Test teardown
def teardown():
    clear_implementation()
    assert get_stats_implementation()['total_singletons'] == 0
```

---

### get_stats_implementation()

Get singleton statistics.

**Signature:**
```python
def get_stats_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Response Fields:**
- `total_singletons`: Number of managed instances
- `singleton_names`: List of all singleton names
- `singleton_types`: Type of each singleton
- `creation_times`: When each singleton was created
- `access_counts`: How many times each accessed
- `estimated_memory_bytes`: Total memory (shallow)
- `estimated_memory_kb`: Memory in KB
- `estimated_memory_mb`: Memory in MB
- `memory_note`: Explanation of memory estimation
- `rate_limited_count`: Number of rate-limited operations
- `timestamp`: When stats were collected

**Example:**
```python
from singleton.singleton_core import get_stats_implementation

stats = get_stats_implementation()

print(f"Total singletons: {stats['total_singletons']}")
print(f"Memory used: {stats['estimated_memory_mb']:.2f} MB")
print(f"Rate limited: {stats['rate_limited_count']}")

# List all singletons
for name in stats['singleton_names']:
    singleton_type = stats['singleton_types'][name]
    access_count = stats['access_counts'][name]
    print(f"  {name}: {singleton_type} (accessed {access_count} times)")
```

---

### reset_implementation()

Reset singleton manager state (lifecycle management).

**Signature:**
```python
def reset_implementation(
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if reset successful, False if rate limited

**Behavior:**
- Clears rate limiter deque
- Resets rate limited count to 0
- Does NOT clear singleton instances (use clear for that)

**Use Cases:**
- Reset rate limiting for testing
- Clear rate limit statistics

**Example:**
```python
from singleton.singleton_core import reset_implementation

# Reset manager state
if reset_implementation():
    print("Manager reset successful")
else:
    print("Reset failed (rate limited)")

# Test setup
def setup_test():
    reset_implementation()
    # Rate limiter now reset, can perform 1000 ops
```

---

## DEBUG INTEGRATION

All functions include debug integration:

**Automatic Correlation IDs:**
```python
# If not provided, correlation_id is auto-generated
instance = get_implementation('cache_manager')
# Generates: correlation_id='singleton_1234567890'
```

**Debug Logging:**
```python
# All operations logged with:
# - correlation_id
# - Operation name
# - Key parameters
# - Results

debug_log(correlation_id, "SINGLETON",
         "get_implementation called",
         name=name, has_factory=factory_func is not None)
```

**CloudWatch Traces:**
```
[correlation_id=sing_abc123] SINGLETON: get_implementation called
  name=cache_manager has_factory=True
[correlation_id=sing_abc123] SINGLETON: Creating new instance
  name=cache_manager has_factory=True
[correlation_id=sing_abc123] SINGLETON: factory:cache_manager duration=5.67ms
[correlation_id=sing_abc123] SINGLETON: Instance created
  name=cache_manager instance_type=CacheManager
```

---

## USAGE PATTERNS

### Pattern 1: Lazy Initialization

```python
from singleton.singleton_core import get_implementation

def get_cache_manager():
    """Get or create cache manager (lazy initialization)."""
    return get_implementation(
        'cache_manager',
        factory_func=lambda: CacheManager()
    )

# First call - creates instance
cache = get_cache_manager()

# Subsequent calls - fast retrieval
cache = get_cache_manager()
```

---

### Pattern 2: Explicit Registration

```python
from singleton.singleton_core import set_implementation, get_implementation

# Initialize during startup
def initialize_services():
    """Initialize all singleton services."""
    cache = CacheManager()
    cache.initialize()
    set_implementation('cache_manager', cache)
    
    config = ConfigLoader()
    config.load('/path/to/config')
    set_implementation('config', config)
    
    validator = SecurityValidator()
    set_implementation('validator', validator)

# Use throughout application
cache = get_implementation('cache_manager')
config = get_implementation('config')
```

---

### Pattern 3: Conditional Creation

```python
from singleton.singleton_core import has_implementation, get_implementation, set_implementation

def ensure_validator():
    """Ensure validator exists, create if not."""
    if not has_implementation('validator'):
        validator = SecurityValidator()
        validator.load_rules()
        set_implementation('validator', validator)
    
    return get_implementation('validator')

# Always safe to call
validator = ensure_validator()
```

---

### Pattern 4: Test Isolation

```python
from singleton.singleton_core import clear_implementation, set_implementation

def test_with_mock_services():
    """Test with mock singleton services."""
    # Setup
    clear_implementation()  # Clear any existing singletons
    
    # Register mocks
    mock_cache = MockCacheManager()
    set_implementation('cache_manager', mock_cache)
    
    # Run test
    result = my_function()
    
    # Verify
    assert mock_cache.get_called
    
    # Teardown
    clear_implementation()
```

---

### Pattern 5: Health Monitoring

```python
from singleton.singleton_core import get_stats_implementation

def singleton_health_check():
    """Monitor singleton health."""
    stats = get_stats_implementation()
    
    # Check memory usage
    if stats['estimated_memory_mb'] > 50:
        logger.warning(
            "High singleton memory usage",
            extra={'memory_mb': stats['estimated_memory_mb']}
        )
    
    # Check rate limiting
    if stats['rate_limited_count'] > 100:
        logger.error(
            "Excessive rate limiting",
            extra={'rate_limited': stats['rate_limited_count']}
        )
    
    # List singleton types
    for name, singleton_type in stats['singleton_types'].items():
        logger.info(f"Singleton: {name} ({singleton_type})")
```

---

## EXPORTS

```python
__all__ = [
    'execute_singleton_operation',
    'get_implementation',
    'set_implementation',
    'has_implementation',
    'delete_implementation',
    'clear_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
```

---

## RELATED DOCUMENTATION

- **singleton_manager.md**: Manager singleton and core logic
- **singleton_convenience.md**: Convenience accessor functions
- **singleton_memory.md**: Memory monitoring utilities
- **interface_singleton.md**: Interface layer

---

**END OF DOCUMENTATION**

**Module:** singleton/singleton_core.py  
**Functions:** 8  
**Pattern:** SUGA Core Implementation  
**Debug:** Fully Integrated
