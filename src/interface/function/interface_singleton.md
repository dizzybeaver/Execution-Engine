# interface_singleton.py

**Version:** 2025-12-13_1  
**Module:** SINGLETON  
**Layer:** Interface  
**Interface:** INT-00  
**Lines:** ~95

---

## Purpose

Singleton interface router with import protection for managing singleton instances.

---

## Main Function

### execute_singleton_operation()

**Signature:**
```python
def execute_singleton_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route singleton operation requests to internal implementations

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (varies by operation)

**Operations:**
- `get` - Get singleton instance by name
- `set` - Set/register singleton instance
- `has` - Check if singleton exists
- `delete` - Delete singleton instance
- `clear` - Clear all singletons
- `stats` / `get_stats` - Get singleton statistics
- `reset` - Reset singleton state

**Raises:**
- `RuntimeError` - If Singleton interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### get

**Purpose:** Get singleton instance by name

**Parameters:**
- `name` (str, required) - Singleton name

**Returns:** Singleton instance or None

**Validation:**
- Name must be provided
- Name must be string

**Usage:**
```python
manager = execute_singleton_operation('get', name='cache_manager')
```

**Behavior:**
- Returns existing instance if found
- Returns None if not found
- Does not create instance

---

### set

**Purpose:** Set/register singleton instance

**Parameters:**
- `name` (str, required) - Singleton name
- `instance` (Any, required) - Instance to register

**Returns:** Instance that was set

**Validation:**
- Name must be provided and be string
- Instance must be provided

**Usage:**
```python
manager = CacheManager()
execute_singleton_operation('set', name='cache_manager', instance=manager)
```

**Behavior:**
- Registers instance with given name
- Overwrites existing instance with same name
- Returns the instance

---

### has

**Purpose:** Check if singleton exists

**Parameters:**
- `name` (str, required) - Singleton name

**Returns:** bool (True if exists)

**Validation:**
- Name must be provided
- Name must be string

**Usage:**
```python
exists = execute_singleton_operation('has', name='cache_manager')
if not exists:
    # Register singleton
```

---

### delete

**Purpose:** Delete singleton instance

**Parameters:**
- `name` (str, required) - Singleton name to delete

**Returns:** bool (True if deleted, False if not found)

**Validation:**
- Name must be provided
- Name must be string

**Usage:**
```python
execute_singleton_operation('delete', name='cache_manager')
```

**Warning:** Deleting singletons can cause issues if other code expects them to exist.

---

### clear

**Purpose:** Clear all singleton instances

**Parameters:** None

**Returns:** int (number of singletons cleared)

**Usage:**
```python
count = execute_singleton_operation('clear')
# Returns: 5 (if 5 singletons were cleared)
```

**Warning:** This clears ALL singletons. Use with caution, typically only in testing.

---

### stats / get_stats

**Purpose:** Get singleton statistics

**Parameters:** None

**Returns:** Dict with statistics:
- `total_singletons` - Number of registered singletons
- `singleton_names` - List of singleton names
- `memory_usage_estimate` - Estimated memory usage

**Usage:**
```python
stats = execute_singleton_operation('get_stats')
# {
#     'total_singletons': 5,
#     'singleton_names': ['cache_manager', 'config_manager', ...],
#     'memory_usage_estimate': 12345
# }
```

---

### reset

**Purpose:** Reset singleton state (clears all singletons)

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_singleton_operation('reset')
```

**Note:** This is an alias for `clear` operation but returns bool instead of count.

---

## Valid Operations

```python
_VALID_SINGLETON_OPERATIONS = [
    'get', 'set', 'has', 'delete', 'clear', 'stats', 'get_stats', 'reset'
]
```

---

## Validation Helpers

### _validate_name_param()

**Purpose:** Validate name parameter presence and type

**Parameters:**
- `kwargs` (dict) - Operation kwargs
- `operation` (str) - Operation name for error messages

**Raises:**
- `ValueError` - If name missing
- `TypeError` - If name not string

---

### _validate_set_params()

**Purpose:** Validate set operation parameters

**Parameters:**
- `kwargs` (dict) - Operation kwargs
- `operation` (str) - Operation name

**Checks:**
- Name exists and is string
- Instance exists

**Raises:**
- `ValueError` - If parameters missing
- `TypeError` - If types incorrect

---

## Import Protection

**Pattern:**
```python
try:
    import singleton
    _SINGLETON_AVAILABLE = True
except ImportError as e:
    _SINGLETON_AVAILABLE = False
    _SINGLETON_IMPORT_ERROR = str(e)
```

**Error Handling:**
- Checks availability before every operation
- Raises RuntimeError with import error details
- Allows graceful degradation

---

## Singleton Pattern

**Purpose:**
- Ensure single instance of objects
- Global access point
- Memory optimization
- State sharing

**Common Singletons in LEE:**
- `cache_manager` - Cache management
- `config_manager` - Configuration
- `logging_manager` - Logging
- `metrics_manager` - Metrics collection
- `security_manager` - Security operations

---

## Usage Patterns

### Factory Pattern

```python
def get_cache_manager():
    """Get or create cache manager singleton."""
    manager = execute_singleton_operation('get', name='cache_manager')
    if manager is None:
        manager = CacheManager()
        execute_singleton_operation('set', name='cache_manager', instance=manager)
    return manager
```

---

### Dependency Injection

```python
class MyService:
    def __init__(self):
        self.cache = execute_singleton_operation('get', name='cache_manager')
        self.config = execute_singleton_operation('get', name='config_manager')
```

---

### Testing

```python
def test_my_feature():
    # Clear singletons before test
    execute_singleton_operation('clear')
    
    # Set up test singletons
    test_cache = MockCacheManager()
    execute_singleton_operation('set', name='cache_manager', instance=test_cache)
    
    # Run test
    result = my_feature()
    
    # Clean up
    execute_singleton_operation('clear')
```

---

## Best Practices

**Do:**
- Use singletons for shared state
- Register singletons early (initialization)
- Check existence before getting
- Clear singletons in tests

**Don't:**
- Overuse singletons (can hide dependencies)
- Delete singletons during normal operation
- Create singletons in performance-critical paths
- Assume singleton exists without checking

---

## Memory Management

**Considerations:**
- Singletons persist for lifetime of process
- Can accumulate memory over time
- Clear unused singletons to free memory
- Monitor singleton count in production

**Monitoring:**
```python
stats = execute_singleton_operation('get_stats')
if stats['total_singletons'] > 20:
    # Investigate potential singleton leak
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Import Protection:** Graceful failure handling  
✅ **Parameter Validation:** Type and presence checks  
✅ **SINGLETON Pattern:** Single instance guarantee  
✅ **State Management:** Centralized singleton registry

---

## Related Files

- `/singleton/` - Singleton implementation
- `/gateway/wrappers/gateway_wrappers_singleton.py` - Gateway wrappers
- `/singleton/singleton_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
