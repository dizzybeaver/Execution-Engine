# LESS-PY-01: Module-Level State Pattern

**Category:** Python Concurrency Pattern
**Context:** Managing shared state across instances
**Difficulty:** Intermediate

---

## Overview

Use module-level variables with `threading.RLock()` for persistent state that must survive across object instances.

## Problem

When you need state that:
- Persists across multiple instances of a class
- Survives factory re-initialization
- Must be thread-safe in concurrent environments
- Should be accessible without passing references

## Solution

Define state at module scope with thread-safe locks. Use singleton patterns carefully with proper locking.

## Pattern Structure

```python
"""
Module with persistent state.
"""

import threading
from typing import Any, Dict

# 1. Module-level state variables
_STATE_CACHE: Dict[str, Any] = {}
_STATE_LOCK = threading.RLock()
_STATE_INITIALIZED = False

# 2. Thread-safe accessor functions
def get_state(key: str, default: Any = None) -> Any:
    """Get state value with lock protection."""
    with _STATE_LOCK:
        return _STATE_CACHE.get(key, default)

def set_state(key: str, value: Any) -> None:
    """Set state value with lock protection."""
    with _STATE_LOCK:
        _STATE_CACHE[key] = value

def clear_state() -> None:
    """Clear all state with lock protection."""
    with _STATE_LOCK:
        _STATE_CACHE.clear()
```

## Detailed Implementation

### Example 1: Configuration Cache

```python
"""
Config Factory - Foundation Domain

UG-ISP Compliant:
- Factory contains actual implementation
- Module-level cache for persistence across instances
- Thread-safe with RLock
"""

import os
import logging
from typing import Any, Dict, Optional, Callable
import threading


# =============================================================================
# Module-level configuration cache (shared across all instances)
# This ensures config persists even when new factory instances are created
# =============================================================================

_CONFIG_CACHE: Dict[str, Any] = {}
_CONFIG_LOCK = threading.RLock()
_CONFIG_LOADED = False


class ConfigFactory:
    """Configuration management factory.

    Uses module-level cache to ensure persistence across instances.
    Multiple instances can be created, but all share the same cache.
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize config factory.

        Note: Creating new instances doesn't clear the cache.
        The cache persists at module level.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Load global config if not already loaded
        self._load_global_config()

    def get(self, category: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value.

        Access is thread-safe via module-level lock.
        """
        with _CONFIG_LOCK:
            config = _CONFIG_CACHE.get(category)

            if config is None:
                self.logger.warning(f"Configuration category not found: {category}")
                return default

            if key is None:
                return config.copy() if isinstance(config, dict) else config

            return config.get(key, default)

    def set(self, category: str, key: str, value: Any) -> bool:
        """Set configuration value at runtime.

        Thread-safe update to module-level cache.
        """
        with _CONFIG_LOCK:
            if category not in _CONFIG_CACHE:
                _CONFIG_CACHE[category] = {}

            _CONFIG_CACHE[category][key] = value

        self.logger.info(f"Configuration updated: {category}.{key} = {value}")
        return True

    def reload(self) -> Dict[str, Any]:
        """Reload configuration from environment.

        Clears and reloads module-level cache.
        """
        global _CONFIG_LOADED

        self.logger.info("Reloading configuration from environment")

        with _CONFIG_LOCK:
            _CONFIG_CACHE.clear()
            _CONFIG_LOADED = False
            self._load_global_config()
            return _CONFIG_CACHE.copy()
```

### Example 2: Object Pool Factory

```python
"""
Object Pool Factory - Operations Domain

Uses module-level singleton pattern with thread-safe initialization.
"""

import threading
from typing import Any, Dict, Optional, Callable, List
import logging


class ObjectPoolFactory:
    """Factory for creating and managing object pools.

    Uses module-level singleton pattern.
    """

    # Module-level singleton state
    _instance: Optional["ObjectPoolFactory"] = None
    _lock = threading.Lock()  # Class-level lock for singleton

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize object pool factory."""
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Instance-level state (not shared)
        self._pools: Dict[str, ObjectPool] = {}
        self._default_max_size = 10
        self._lock = threading.RLock()  # Instance-level lock for pools

    @classmethod
    def get_instance(
        cls,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ) -> "ObjectPoolFactory":
        """Get singleton instance of pool factory.

        Thread-safe double-checked locking pattern.
        """
        if cls._instance is None:
            with cls._lock:  # Class-level lock
                if cls._instance is None:
                    cls._instance = cls(logger, metrics, call_operation)
        return cls._instance

    def create_pool(self, name: str, factory_func: Callable, max_size: int = 10) -> bool:
        """Create new object pool.

        Uses instance-level lock for thread safety.
        """
        with self._lock:  # Instance-level lock
            if name in self._pools:
                self.logger.warning(f"Pool already exists: {name}")
                return False

            config = PoolConfig(
                max_size=max_size,
                factory_func=factory_func,
            )

            pool = ObjectPool(name, config)
            self._pools[name] = pool

            self.logger.info(f"Pool created: {name} (max_size={max_size})")
            return True
```

### Example 3: Connection Pool with Module State

```python
"""
Database connection pool with module-level persistence.
"""

import threading
from typing import Optional
import logging


# Module-level state
_connection_pool: Optional[ConnectionPool] = None
_pool_lock = threading.RLock()
_pool_initialized = False


def get_connection_pool(
    host: str = "localhost",
    port: int = 5432,
    max_connections: int = 10
) -> ConnectionPool:
    """Get or create connection pool.

    Pool persists across multiple calls.
    Thread-safe initialization.
    """
    global _connection_pool, _pool_initialized

    with _pool_lock:
        if _pool_initialized:
            return _connection_pool

        # Create pool on first access
        _connection_pool = ConnectionPool(
            host=host,
            port=port,
            max_connections=max_connections
        )
        _pool_initialized = True

        logging.info(f"Created connection pool: {host}:{port}")
        return _connection_pool


def reset_connection_pool() -> None:
    """Reset connection pool.

    Useful for testing or configuration changes.
    """
    global _connection_pool, _pool_initialized

    with _pool_lock:
        if _connection_pool is not None:
            _connection_pool.close()
            _connection_pool = None
        _pool_initialized = False
```

## When to Use Module-Level State

### Good Use Cases

1. **Caches**: Configuration, compiled regex patterns, parsed schemas
2. **Pools**: Database connections, thread pools, object pools
3. **Registries**: Plugin registries, type registries, handler mappings
4. **Singletons**: Global services, logging systems, metrics collectors
5. **Process-wide Resources**: File handles, network sockets, shared memory

### Bad Use Cases

1. **Request-specific Data**: User sessions, request contexts (use threading.local)
2. **Mutable Default Arguments**: Function default arguments (use None and create new)
3. **Instance-specific State**: Data that should vary per object instance

## Thread Safety Guidelines

### 1. Use RLock for Reentrant Locking

```python
# GOOD - RLock allows same thread to acquire multiple times
_lock = threading.RLock()

def method1(self):
    with _lock:
        self.method2()  # Won't deadlock

def method2(self):
    with _lock:
        # Critical section
        pass

# BAD - Lock would deadlock in reentrant scenario
_lock = threading.Lock()
```

### 2. Minimize Lock Scope

```python
# GOOD - Minimal lock scope
with _lock:
    value = _cache.get(key)
# Process value outside lock
result = process_value(value)

# BAD - Holding lock during expensive operation
with _lock:
    value = _cache.get(key)
    result = expensive_computation(value)  # Blocks other threads
```

### 3. Copy on Read

```python
# GOOD - Return copy to avoid external mutations
with _lock:
    return config.copy()

# BAD - Returning internal mutable state
with _lock:
    return config  # Caller can modify internal state
```

### 4. Double-Checked Locking for Singletons

```python
# GOOD - Double-checked locking
if cls._instance is None:
    with cls._lock:
        if cls._instance is None:
            cls._instance = cls()

return cls._instance
```

## Lock Types Comparison

| Lock Type | Reentrant | Use Case |
|-----------|-----------|----------|
| `threading.Lock` | No | Simple mutual exclusion |
| `threading.RLock` | Yes | Reentrant locking (most common) |
| `threading.Semaphore` | N/A | Limiting concurrent access |
| `threading.Event` | N/A | Signaling between threads |

## Testing Considerations

### Reset Module State in Tests

```python
import mymodule

def setup_function():
    """Reset module state before each test."""
    mymodule._STATE_CACHE.clear()
    mymodule._STATE_INITIALIZED = False

def test_with_clean_state():
    """Test with known initial state."""
    assert mymodule.get_state("key") is None
    mymodule.set_state("key", "value")
    assert mymodule.get_state("key") == "value"
```

### Use Mocks for Locks

```python
from unittest.mock import patch, MagicMock

def test_thread_safety():
    """Test that locks are used correctly."""
    with patch('mymodule.threading.RLock') as mock_lock:
        lock_instance = MagicMock()
        mock_lock.return_value.__enter__ = MagicMock()
        mock_lock.return_value.__exit__ = MagicMock()

        importlib.reload(mymodule)

        # Verify lock was created
        mock_lock.assert_called_once()
```

## Common Pitfalls

### Pitfall 1: Import-Time Side Effects

```python
# BAD - Side effect at import time
_CACHE = load_expensive_data()  # Runs on every import

# GOOD - Lazy initialization
_CACHE = None
_CACHE_LOCK = threading.RLock()

def get_cache():
    global _CACHE
    with _CACHE_LOCK:
        if _CACHE is None:
            _CACHE = load_expensive_data()
    return _CACHE
```

### Pitfall 2: Mutable Global State

```python
# BAD - Direct access to global
_GLOBAL_CONFIG = {}

def set_config(key, value):
    _GLOBAL_CONFIG[key] = value  # Not thread-safe

# GOOD - Protected access
_GLOBAL_CONFIG = {}
_CONFIG_LOCK = threading.RLock()

def set_config(key, value):
    with _CONFIG_LOCK:
        _GLOBAL_CONFIG[key] = value
```

### Pitfall 3: Circular Imports

```python
# Module A
from module_b import SomeClass
_STATE = SomeClass()  # Runs at import time

# Module B
from module_a import _STATE  # Circular import!
```

**Solution:** Use lazy imports or defer initialization.

## Cross-References

- **DEC-PY-01**: Combine with Protocol-based dependency injection
- **DEC-PY-02**: Use `from __future__ import annotations` for type hints
- **Generic Principles**: Singleton Pattern, Thread Safety, Separation of Concerns

## Examples from EE Codebase

**Location:** `d:\Code\Project\EE\foundation\config\config_factory.py`

```python
# Module-level configuration cache (shared across all instances)
_CONFIG_CACHE: Dict[str, Any] = {}
_CONFIG_LOCK = threading.RLock()
_CONFIG_LOADED = False

class ConfigFactory:
    def __init__(self, logger=None, metrics=None, call_operation=None):
        # Load global config if not already loaded
        _load_global_config()

    def get(self, category: str, key: Optional[str] = None, default: Any = None):
        with _CONFIG_LOCK:
            config = _CONFIG_CACHE.get(category)
            # ...
```

**Location:** `d:\Code\Project\EE\operations\object_pool\object_pool_factory.py`

```python
class ObjectPoolFactory:
    # Module-level singleton state
    _instance: Optional["ObjectPoolFactory"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, logger=None, metrics=None, call_operation=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(logger, metrics, call_operation)
        return cls._instance
```

## References

- Python threading module documentation
- "The Python Cookbook" - Chapter on Threads and Processes
- https://docs.python.org/3/library/threading.html
