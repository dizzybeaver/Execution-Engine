"""
Object Pool Factory - Operations Domain

Generic object pooling for resource management implementation.

Merges functionality from:
- EE/src/operations/object_pool/
- EE/src/object_pool/

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

from collections import deque
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
from time import time
import logging
import threading


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PoolConfig:
    """Configuration for object pool."""
    max_size: int = 10
    initial_size: int = 0
    factory_func: Optional[Callable] = None
    reset_func: Optional[Callable] = None
    validate_func: Optional[Callable] = None
    cleanup_func: Optional[Callable] = None
    enable_stats: bool = True


@dataclass
class PoolEntry:
    """Entry in the object pool."""
    obj: Any
    created_at: float = field(default_factory=time)
    last_used: float = field(default_factory=time)
    use_count: int = 0
    is_valid: bool = True


@dataclass
class PoolStats:
    """Statistics for object pool."""
    total_created: int = 0
    total_acquired: int = 0
    total_released: int = 0
    total_invalidated: int = 0
    current_size: int = 0
    in_use: int = 0
    available: int = 0
    hit_rate: float = 0.0


# =============================================================================
# Object Pool Class
# =============================================================================

class ObjectPool:
    """Generic object pool (Lambda-optimized, single-threaded).

    UG-ISP Compliant: All debug via call_operation callback.
    NO internal debug helper functions.

    Usage:
        def create_connection():
            return SomeConnection()

        pool = ObjectPool("connections", PoolConfig(
            factory_func=create_connection,
            max_size=5
        ))

        # Acquire object
        conn = pool.acquire()

        # Use object
        conn.do_something()

        # Release object
        pool.release(conn)
    """

    def __init__(self, name: str, config: PoolConfig):
        """Initialize object pool.

        Args:
            name: Pool name
            config: Pool configuration
        """
        self.name = name
        self.config = config
        self._available: deque = deque()
        self._in_use: List[Any] = []
        self._stats = PoolStats()
        self._lock = threading.RLock()

        # Pre-warm pool if specified
        if config.initial_size > 0:
            self._warm_pool(config.initial_size)

    def _warm_pool(self, count: int):
        """Warm pool with initial objects."""
        with self._lock:
            created = 0
            for _ in range(count):
                if len(self._available) + len(self._in_use) >= self.config.max_size:
                    break
                obj = self._create_object()
                if obj is not None:
                    self._available.append(obj)
                    created += 1

            self._stats.available = len(self._available)

    def _create_object(self) -> Optional[PoolEntry]:
        """Create new pool entry."""
        if self.config.factory_func is None:
            return None

        try:
            obj = self.config.factory_func()
            entry = PoolEntry(obj=obj)
            self._stats.total_created += 1
            return entry
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Failed to create object for pool {self.name}: {e}"
            )
            return None

    def acquire(self) -> Optional[Any]:
        """Acquire object from pool.

        Returns:
            Object from pool or None if pool is empty and cannot create
        """
        with self._lock:
            # Try to get from available pool
            if self._available:
                entry = self._available.popleft()
            else:
                # Create new object if under limit
                if len(self._in_use) < self.config.max_size:
                    entry = self._create_object()
                    if entry is None:
                        return None
                else:
                    logging.getLogger(__name__).warning(
                        f"Pool {self.name} exhausted (max_size={self.config.max_size})"
                    )
                    return None

            # Validate if validation function provided
            if self.config.validate_func and not self.config.validate_func(entry.obj):
                self._stats.total_invalidated += 1
                entry = self._create_object()
                if entry is None:
                    return None

            # Update entry and track
            entry.last_used = time()
            entry.use_count += 1
            self._in_use.append(entry)

            # Update stats
            self._stats.total_acquired += 1
            self._stats.in_use = len(self._in_use)
            self._stats.available = len(self._available)
            self._stats.hit_rate = (
                self._stats.total_acquired / max(1, self._stats.total_created)
            )

            return entry.obj

    def release(self, obj: Any) -> bool:
        """Release object back to pool.

        Args:
            obj: Object to release

        Returns:
            True if released successfully, False otherwise
        """
        with self._lock:
            # Find entry in use
            entry = None
            for i, used_entry in enumerate(self._in_use):
                if used_entry.obj is obj:
                    entry = self._in_use.pop(i)
                    break

            if entry is None:
                logging.getLogger(__name__).warning(
                    f"Object not found in pool {self.name}"
                )
                return False

            # Reset object if reset function provided
            if self.config.reset_func:
                try:
                    self.config.reset_func(obj)
                except Exception as e:
                    logging.getLogger(__name__).error(
                        f"Reset failed for pool {self.name}: {e}"
                    )
                    # Don't return invalid object to pool
                    self._cleanup_entry(entry)
                    self._stats.total_invalidated += 1
                    self._update_stats()
                    return False

            # Return to available pool
            self._available.append(entry)
            self._stats.total_released += 1
            self._update_stats()
            return True

    def _cleanup_entry(self, entry: PoolEntry):
        """Clean up pool entry."""
        if self.config.cleanup_func and entry.obj is not None:
            try:
                self.config.cleanup_func(entry.obj)
            except Exception:
                pass  # Cleanup failure is non-critical

    def _update_stats(self):
        """Update pool statistics."""
        self._stats.in_use = len(self._in_use)
        self._stats.available = len(self._available)
        self._stats.current_size = self._stats.in_use + self._stats.available

    def clear(self) -> int:
        """Clear all objects from pool.

        Returns:
            Number of objects cleared
        """
        with self._lock:
            cleared = 0

            # Clear available objects
            while self._available:
                entry = self._available.popleft()
                self._cleanup_entry(entry)
                cleared += 1

            # Clear in-use objects (force cleanup)
            for entry in self._in_use:
                self._cleanup_entry(entry)
                cleared += 1
            self._in_use.clear()

            self._update_stats()
            return cleared

    def stats(self) -> Dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        with self._lock:
            if not self.config.enable_stats:
                return {"stats_enabled": False}

            return {
                "name": self.name,
                "max_size": self.config.max_size,
                "total_created": self._stats.total_created,
                "total_acquired": self._stats.total_acquired,
                "total_released": self._stats.total_released,
                "total_invalidated": self._stats.total_invalidated,
                "current_size": self._stats.current_size,
                "in_use": self._stats.in_use,
                "available": self._stats.available,
                "hit_rate": round(self._stats.hit_rate, 2),
            }

    def resize(self, new_size: int) -> bool:
        """Resize pool.

        Args:
            new_size: New maximum pool size

        Returns:
            True if resized successfully
        """
        with self._lock:
            old_size = self.config.max_size
            self.config.max_size = max(1, new_size)

            # Trim excess available objects
            while len(self._available) > self.config.max_size:
                entry = self._available.pop()
                self._cleanup_entry(entry)

            self._update_stats()
            return True

    def warm(self, count: int) -> int:
        """Warm pool with additional objects.

        Args:
            count: Number of objects to create

        Returns:
            Number of objects actually created
        """
        with self._lock:
            created = 0
            target = min(count, self.config.max_size - len(self._available) - len(self._in_use))

            for _ in range(target):
                entry = self._create_object()
                if entry is not None:
                    self._available.append(entry)
                    created += 1

            self._update_stats()
            return created


# =============================================================================
# Object Pool Factory
# =============================================================================

class ObjectPoolFactory:
    """Factory for creating and managing object pools.

    Merges functionality from both src/operations/object_pool and src/object_pool.

    UG-ISP Compliant: All debug via call_operation callback.
    NO internal debug helper functions.

    Usage:
        factory = ObjectPoolFactory.get_instance()

        # Create pool
        factory.create_pool(
            name="connections",
            factory_func=lambda: Connection(),
            max_size=10
        )

        # Acquire from pool
        obj = factory.acquire("connections")

        # Release to pool
        factory.release("connections", obj)

        # Get pool stats
        stats = factory.get_stats("connections")
    """

    _instance: Optional["ObjectPoolFactory"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize object pool factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation
        self._pools: Dict[str, ObjectPool] = {}
        self._default_max_size = 10
        self._lock = threading.RLock()

    @classmethod
    def get_instance(
        cls,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ) -> "ObjectPoolFactory":
        """Get singleton instance of pool factory.

        Returns:
            Global ObjectPoolFactory instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(logger, metrics, call_operation)
        return cls._instance

    def create_pool(
        self,
        name: str,
        factory_func: Callable,
        max_size: int = 10,
        initial_size: int = 0,
        reset_func: Optional[Callable] = None,
        validate_func: Optional[Callable] = None,
        cleanup_func: Optional[Callable] = None,
        enable_stats: bool = True,
        **kwargs
    ) -> bool:
        """Create new object pool.

        Args:
            name: Unique pool name
            factory_func: Function to create new objects
            max_size: Maximum pool size
            initial_size: Initial pool size (pre-warm)
            reset_func: Function to reset objects before reuse
            validate_func: Function to validate objects
            cleanup_func: Function to cleanup objects when discarded
            enable_stats: Enable statistics collection
            **kwargs: Additional parameters

        Returns:
            True if pool created successfully
        """
        with self._lock:
            if name in self._pools:
                self.logger.warning(f"Pool already exists: {name}")
                return False

            config = PoolConfig(
                max_size=max_size,
                initial_size=initial_size,
                factory_func=factory_func,
                reset_func=reset_func,
                validate_func=validate_func,
                cleanup_func=cleanup_func,
                enable_stats=enable_stats,
            )

            pool = ObjectPool(name, config)
            self._pools[name] = pool

            self.logger.info(
                f"Pool created: {name} (max_size={max_size}, initial_size={initial_size})"
            )
            return True

    def acquire(self, name: str, **kwargs) -> Optional[Any]:
        """Acquire object from pool.

        Args:
            name: Pool name
            **kwargs: Additional parameters

        Returns:
            Object from pool or None if pool not found or empty
        """
        pool = self._pools.get(name)
        if pool is None:
            self.logger.warning(f"Pool not found: {name}")
            return None

        return pool.acquire()

    def release(self, name: str, obj: Any, **kwargs) -> bool:
        """Release object to pool.

        Args:
            name: Pool name
            obj: Object to release
            **kwargs: Additional parameters

        Returns:
            True if released successfully
        """
        pool = self._pools.get(name)
        if pool is None:
            self.logger.warning(f"Pool not found: {name}")
            return False

        return pool.release(obj)

    def get_stats(self, name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get pool statistics.

        Args:
            name: Pool name
            **kwargs: Additional parameters

        Returns:
            Pool statistics or None if pool not found
        """
        pool = self._pools.get(name)
        if pool is None:
            return None

        return pool.stats()

    def clear_pool(self, name: str, **kwargs) -> bool:
        """Clear pool.

        Args:
            name: Pool name
            **kwargs: Additional parameters

        Returns:
            True if cleared successfully
        """
        pool = self._pools.get(name)
        if pool is None:
            return False

        pool.clear()
        self.logger.info(f"Pool cleared: {name}")
        return True

    def delete_pool(self, name: str, **kwargs) -> bool:
        """Delete pool.

        Args:
            name: Pool name
            **kwargs: Additional parameters

        Returns:
            True if deleted successfully
        """
        with self._lock:
            if name not in self._pools:
                return False

            pool = self._pools.pop(name)
            pool.clear()

            self.logger.info(f"Pool deleted: {name}")
            return True

    def resize_pool(self, name: str, new_size: int, **kwargs) -> bool:
        """Resize pool.

        Args:
            name: Pool name
            new_size: New maximum size
            **kwargs: Additional parameters

        Returns:
            True if resized successfully
        """
        pool = self._pools.get(name)
        if pool is None:
            return False

        return pool.resize(new_size)

    def warm_pool(self, name: str, count: int, **kwargs) -> int:
        """Warm pool with additional objects.

        Args:
            name: Pool name
            count: Number of objects to create
            **kwargs: Additional parameters

        Returns:
            Number of objects created
        """
        pool = self._pools.get(name)
        if pool is None:
            return 0

        return pool.warm(count)

    def list_pools(self, **kwargs) -> List[str]:
        """List all pool names.

        Returns:
            List of pool names
        """
        return list(self._pools.keys())


__all__ = [
    "ObjectPoolFactory",
    "ObjectPool",
    "PoolConfig",
    "PoolEntry",
    "PoolStats",
]
