"""Cache interface router (UG-ISP Router).

Simple LRU cache for scanner operations.
NO debug/logging calls - pure cache implementation.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

from typing import Any, Optional
from functools import lru_cache


# Simple in-memory cache implementation (Local Network)
class _ScannerCache:
    """Simple LRU cache for scanner operations.

    No external dependencies, no logging, pure cache implementation.
    """

    def __init__(self, maxsize: int = 128):
        """Initialize cache.

        Args:
            maxsize: Maximum number of cached items
        """
        self._cache = {}
        self._maxsize = maxsize

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Simple LRU: if cache full, clear oldest item
        if len(self._cache) >= self._maxsize and key not in self._cache:
            # Remove first item (oldest)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        return {
            'size': len(self._cache),
            'maxsize': self._maxsize,
            'keys': list(self._cache.keys())
        }


# Global cache instance
_cache_instance = _ScannerCache()


# Dispatch dictionary - O(1) operation routing
_CACHE_DISPATCH = {
    'get': lambda **kw: _cache_instance.get(kw.get('key')),
    'set': lambda **kw: _cache_instance.set(kw.get('key'), kw.get('value')),
    'delete': lambda **kw: _cache_instance.delete(kw.get('key')),
    'clear': lambda **kw: _cache_instance.clear(),
    'get_stats': lambda **kw: _cache_instance.get_stats(),
}


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """Route cache operation requests to implementation functions.

    UG-ISP: This is the Router's execute operation function, called by
    the Gateway (ISP) to route operations to the Local Network (implementation).

    Args:
        operation: The cache operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown

    Example:
        # Called by Gateway via execute_operation()
        result = execute_cache_operation('get', key='ast_cache:file.py')
    """
    if operation not in _CACHE_DISPATCH:
        raise ValueError(
            f"Unknown cache operation: '{operation}'. "
            f"Valid: {', '.join(_CACHE_DISPATCH.keys())}"
        )

    # Execute operation through dispatch handler (O(1) lookup)
    handler = _CACHE_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_cache_operation']
