# singleton_convenience.md

**Version:** 2025-12-13_1  
**Purpose:** Convenience accessor functions for common singletons  
**Module:** singleton/singleton_convenience.py  
**Type:** Convenience Wrappers

---

## OVERVIEW

Provides semantic named accessors for commonly-used singletons, eliminating the need to remember exact singleton keys and following the SUGA gateway pattern.

**Benefits:**
- Semantic function names (get_cache_manager vs get_named_singleton('cache_manager'))
- Type hints in IDE autocomplete
- Centralized singleton key management
- Consistent error handling
- Gateway pattern compliance

---

## FUNCTIONS

### get_named_singleton()

Universal singleton accessor with SUGA gateway pattern.

**Signature:**
```python
def get_named_singleton(
    name: str,
    factory_func: Optional[Any] = None
) -> Optional[Any]
```

**Parameters:**
- `name` (str): Singleton instance name
- `factory_func` (Optional[Any]): Factory function to create singleton if not exists

**Returns:**
- `Any`: Singleton instance
- `None`: If not found and no factory provided, or on error

**Error Handling:**
- Logs error on failure
- Returns None instead of raising exception
- Allows graceful degradation

**Example:**
```python
from singleton.singleton_convenience import get_named_singleton

# Get existing singleton
cache = get_named_singleton('cache_manager')

# Get or create with factory
config = get_named_singleton(
    'config_manager',
    factory_func=lambda: ConfigManager()
)
```

---

## SINGLETON ACCESSORS

### get_cost_protection()

Get cost protection singleton.

**Signature:**
```python
def get_cost_protection() -> Optional[Any]
```

**Returns:**
- Cost protection instance or None

**Example:**
```python
from singleton.singleton_convenience import get_cost_protection

cost_protection = get_cost_protection()
if cost_protection:
    cost_protection.check_budget()
```

---

### get_cache_manager()

Get cache manager singleton.

**Signature:**
```python
def get_cache_manager() -> Optional[Any]
```

**Returns:**
- CacheManager instance or None

**Example:**
```python
from singleton.singleton_convenience import get_cache_manager

cache = get_cache_manager()
if cache:
    value = cache.get('key')
```

---

### get_security_validator()

Get security validator singleton.

**Signature:**
```python
def get_security_validator() -> Optional[Any]
```

**Returns:**
- SecurityValidator instance or None

**Example:**
```python
from singleton.singleton_convenience import get_security_validator

validator = get_security_validator()
if validator:
    is_valid = validator.validate_email('user@example.com')
```

---

### get_unified_validator()

Get unified validator singleton.

**Signature:**
```python
def get_unified_validator() -> Optional[Any]
```

**Returns:**
- UnifiedValidator instance or None

---

### get_config_manager()

Get config manager singleton.

**Signature:**
```python
def get_config_manager() -> Optional[Any]
```

**Returns:**
- ConfigManager instance or None

**Example:**
```python
from singleton.singleton_convenience import get_config_manager

config = get_config_manager()
if config:
    timeout = config.get('timeout', default=30)
```

---

### get_memory_manager()

Get memory manager singleton.

**Signature:**
```python
def get_memory_manager() -> Optional[Any]
```

**Returns:**
- MemoryManager instance or None

---

### get_lambda_cache()

Get lambda cache singleton.

**Signature:**
```python
def get_lambda_cache() -> Optional[Any]
```

**Returns:**
- Lambda cache instance or None

---

### get_response_cache()

Get response cache singleton.

**Signature:**
```python
def get_response_cache() -> Optional[Any]
```

**Returns:**
- Response cache instance or None

**Example:**
```python
from singleton.singleton_convenience import get_response_cache

response_cache = get_response_cache()
if response_cache:
    cached_response = response_cache.get('api_call_123')
```

---

### get_circuit_breaker_manager()

Get circuit breaker manager singleton.

**Signature:**
```python
def get_circuit_breaker_manager() -> Optional[Any]
```

**Returns:**
- Circuit breaker manager instance or None

**Example:**
```python
from singleton.singleton_convenience import get_circuit_breaker_manager

cb_manager = get_circuit_breaker_manager()
if cb_manager:
    result = cb_manager.call('ha_api', api_function)
```

---

### get_response_processor()

Get response processor singleton.

**Signature:**
```python
def get_response_processor() -> Optional[Any]
```

**Returns:**
- Response processor instance or None

---

### get_lambda_optimizer()

Get lambda optimizer singleton.

**Signature:**
```python
def get_lambda_optimizer() -> Optional[Any]
```

**Returns:**
- Lambda optimizer instance or None

---

### get_response_metrics_manager()

Get response metrics manager singleton.

**Signature:**
```python
def get_response_metrics_manager() -> Optional[Any]
```

**Returns:**
- Response metrics manager instance or None

---

## HELPER FUNCTIONS

### has_singleton()

Check if a singleton exists.

**Signature:**
```python
def has_singleton(name: str) -> bool
```

**Parameters:**
- `name` (str): Singleton name

**Returns:**
- `bool`: True if exists, False otherwise or on error

**Error Handling:**
- Logs error on failure
- Returns False instead of raising exception

**Example:**
```python
from singleton.singleton_convenience import has_singleton

if has_singleton('cache_manager'):
    cache = get_cache_manager()
else:
    print("Cache not initialized")
```

---

### delete_singleton()

Delete a specific singleton.

**Signature:**
```python
def delete_singleton(name: str) -> bool
```

**Parameters:**
- `name` (str): Singleton name

**Returns:**
- `bool`: True if deleted, False if didn't exist or on error

**Error Handling:**
- Logs error on failure
- Returns False instead of raising exception

**Example:**
```python
from singleton.singleton_convenience import delete_singleton

# Clean up temporary singleton
if delete_singleton('temp_cache'):
    print("Temp cache deleted")
```

---

### clear_all_singletons()

Clear all singletons.

**Signature:**
```python
def clear_all_singletons() -> int
```

**Returns:**
- `int`: Count of singletons cleared
- `0`: On error

**Error Handling:**
- Logs error on failure
- Returns 0 instead of raising exception

**Example:**
```python
from singleton.singleton_convenience import clear_all_singletons

# Test teardown
count = clear_all_singletons()
print(f"Cleared {count} singletons")
```

---

### get_singleton_stats()

Get singleton statistics.

**Signature:**
```python
def get_singleton_stats() -> dict
```

**Returns:**
- `dict`: Statistics dictionary
- `{}`: Empty dict on error

**Error Handling:**
- Logs error on failure
- Returns empty dict instead of raising exception

**Example:**
```python
from singleton.singleton_convenience import get_singleton_stats

stats = get_singleton_stats()
if stats:
    print(f"Total singletons: {stats.get('total_singletons', 0)}")
    print(f"Memory: {stats.get('estimated_memory_mb', 0):.2f} MB")
```

---

## USAGE PATTERNS

### Pattern 1: Direct Access

```python
from singleton.singleton_convenience import (
    get_cache_manager,
    get_config_manager,
    get_security_validator
)

# Direct semantic access
cache = get_cache_manager()
config = get_config_manager()
validator = get_security_validator()

# Use without worrying about singleton keys
if cache:
    value = cache.get('key')
```

---

### Pattern 2: Safe Access with None Checking

```python
from singleton.singleton_convenience import get_cache_manager

def process_request(request):
    """Process request with optional cache."""
    cache = get_cache_manager()
    
    # Safe to use - None if not available
    if cache:
        cached = cache.get(request.key)
        if cached:
            return cached
    
    # Fallback to processing
    result = process(request)
    
    if cache:
        cache.set(request.key, result)
    
    return result
```

---

### Pattern 3: Health Check

```python
from singleton.singleton_convenience import (
    get_singleton_stats,
    has_singleton
)

def singleton_health_check():
    """Check singleton health."""
    stats = get_singleton_stats()
    
    if not stats:
        return {'healthy': False, 'error': 'Stats unavailable'}
    
    # Check critical singletons
    critical = ['cache_manager', 'config_manager', 'security_validator']
    missing = [name for name in critical if not has_singleton(name)]
    
    return {
        'healthy': len(missing) == 0,
        'total_singletons': stats.get('total_singletons', 0),
        'missing_critical': missing,
        'memory_mb': stats.get('estimated_memory_mb', 0)
    }
```

---

### Pattern 4: Test Isolation

```python
from singleton.singleton_convenience import (
    clear_all_singletons,
    get_cache_manager
)

def test_with_clean_state():
    """Test with clean singleton state."""
    # Setup - clear all
    clear_all_singletons()
    
    # Test runs with no singletons
    cache = get_cache_manager()
    assert cache is None  # Not initialized
    
    # Test logic...
    
    # Teardown
    clear_all_singletons()
```

---

### Pattern 5: Lazy Registration

```python
from singleton.singleton_convenience import (
    get_cache_manager,
    get_named_singleton
)

def ensure_cache():
    """Ensure cache manager exists."""
    cache = get_cache_manager()
    
    if cache is None:
        # Create and register
        cache = get_named_singleton(
            'cache_manager',
            factory_func=lambda: CacheManager()
        )
    
    return cache

# Usage
cache = ensure_cache()  # Always returns cache (creates if needed)
```

---

### Pattern 6: Monitoring

```python
from singleton.singleton_convenience import (
    get_singleton_stats,
    has_singleton
)
import logging

logger = logging.getLogger(__name__)

def monitor_singletons():
    """Monitor singleton usage."""
    stats = get_singleton_stats()
    
    if not stats:
        logger.error("Failed to get singleton stats")
        return
    
    # Log memory usage
    memory_mb = stats.get('estimated_memory_mb', 0)
    if memory_mb > 10:
        logger.warning(
            "High singleton memory usage",
            extra={'memory_mb': memory_mb}
        )
    
    # Check for expected singletons
    expected = ['cache_manager', 'config_manager']
    for name in expected:
        if not has_singleton(name):
            logger.error(
                "Expected singleton missing",
                extra={'singleton': name}
            )
    
    # Log statistics
    logger.info(
        "Singleton statistics",
        extra={
            'total': stats.get('total_singletons', 0),
            'memory_mb': memory_mb,
            'names': stats.get('singleton_names', [])
        }
    )
```

---

## ERROR HANDLING

All convenience functions include error handling:

**Pattern:**
```python
def get_cache_manager() -> Optional[Any]:
    """Get cache manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name='cache_manager'
        )
    except Exception as e:
        logger.error(f"Failed to get cache_manager: {e}")
        return None
```

**Benefits:**
1. Never raises exceptions (returns None instead)
2. Logs errors for debugging
3. Allows graceful degradation
4. Simplifies error handling in calling code

**Example:**
```python
# No try/except needed - function handles errors
cache = get_cache_manager()

if cache:
    # Cache available
    value = cache.get('key')
else:
    # Cache not available - fallback
    value = compute_value()
```

---

## GATEWAY PATTERN

All functions use SUGA gateway pattern:

**Implementation:**
```python
from gateway import execute_operation, GatewayInterface

def get_cache_manager() -> Optional[Any]:
    """Get cache manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name='cache_manager'
        )
    except Exception as e:
        logger.error(f"Failed to get cache_manager: {e}")
        return None
```

**Benefits:**
1. Consistent with SUGA architecture
2. Proper layer separation
3. Gateway handles routing
4. Interface handles dispatch
5. Core handles logic

---

## EXPORTS

```python
__all__ = [
    'get_named_singleton',
    'get_cost_protection',
    'get_cache_manager',
    'get_security_validator',
    'get_unified_validator',
    'get_config_manager',
    'get_memory_manager',
    'get_lambda_cache',
    'get_response_cache',
    'get_circuit_breaker_manager',
    'get_response_processor',
    'get_lambda_optimizer',
    'get_response_metrics_manager',
    'has_singleton',
    'delete_singleton',
    'clear_all_singletons',
    'get_singleton_stats',
]
```

---

## RELATED DOCUMENTATION

- **singleton_core.md**: Core implementation functions
- **singleton_manager.md**: Manager singleton and logic
- **singleton_memory.md**: Memory monitoring utilities
- **interface_singleton.md**: Interface layer

---

**END OF DOCUMENTATION**

**Module:** singleton/singleton_convenience.py  
**Functions:** 17  
**Pattern:** Convenience Wrappers using SUGA Gateway
