"""cache_operations_split/cache_functions.py

Standalone cache functions.
"""
from __future__ import annotations

import os

from typing import Any, Optional

from lee.lee_cache.cache_operations_split.standalone_functions import _get_cache_instance
from lee.lee_cache.cache_enums import _CACHE_MISS, DEFAULT_CACHE_TTL

_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"


def _is_cache_disabled() -> bool:
    """Check if caching is disabled via environment variable.

    Returns:
        True if LEE_CACHE_DISABLED=true, False otherwise
    """
    return os.environ.get("LEE_CACHE_DISABLED", "false").lower() == "true"


def _debug_cache_log(message: str) -> None:
    """Log debug message for cache operations if LEE_DEBUG is enabled.

    Args:
        message: Debug message to log
    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=message,
                         scope='CACHE_FUNCTIONS')

def cache_get(key: str, default: Any = _CACHE_MISS, **kwargs) -> Any:
    """Get cached value if exists and not expired."""
    if _is_cache_disabled():
        _debug_cache_log(f"CACHE DISABLED: cache_get('{key}') returning default")
        return default
    cache = _get_cache_instance()
    result = cache.get(key, **kwargs)
    return default if result is _CACHE_MISS else result

def cache_set(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL,
               source_module: Optional[str] = None, **kwargs) -> None:
    """Set value in cache with optional TTL."""
    if _is_cache_disabled():
        _debug_cache_log(f"CACHE DISABLED: cache_set('{key}') skipped")
        return
    cache = _get_cache_instance()
    cache.set(key, value, ttl=ttl, source_module=source_module, **kwargs)

def cache_exists(key: str, **kwargs) -> bool:
    """Check if key exists and is not expired."""
    if _is_cache_disabled():
        _debug_cache_log(f"CACHE DISABLED: cache_exists('{key}') returning False")
        return False
    cache = _get_cache_instance()
    return cache.exists(key, **kwargs)

def cache_delete(key: str, **kwargs) -> bool:
    """Delete cache entry if it exists."""
    if _is_cache_disabled():
        _debug_cache_log(f"CACHE DISABLED: cache_delete('{key}') returning False")
        return False
    cache = _get_cache_instance()
    return cache.delete(key, **kwargs)

def cache_clear(**kwargs) -> int:
    """Clear all cache entries. Returns count of cleared entries."""
    if _is_cache_disabled():
        _debug_cache_log("CACHE DISABLED: cache_clear() returning 0")
        return 0
    cache = _get_cache_instance()
    return cache.clear(**kwargs)

def cache_reset(**kwargs) -> bool:
    """Reset cache to initial state."""
    if _is_cache_disabled():
        _debug_cache_log("CACHE DISABLED: cache_reset() returning True")
        return True
    cache = _get_cache_instance()
    return cache.reset(**kwargs)

def cache_cleanup_expired(**kwargs) -> int:
    """Remove all expired entries. Returns count of cleaned entries."""
    cache = _get_cache_instance()
    return cache.cleanup_expired(**kwargs)

def cache_get_stats(**kwargs) -> dict[str, Any]:
    """Get cache statistics."""
    cache = _get_cache_instance()
    return cache.get_stats(**kwargs)

def cache_get_metadata(key: str, **kwargs) -> Optional[dict[str, Any]]:
    """Get cache entry metadata without accessing value."""
    cache = _get_cache_instance()
    return cache.get_metadata(key, **kwargs)

def cache_get_module_dependencies(**kwargs) -> set[str]:
    """Get set of all module names that have cache dependencies."""
    cache = _get_cache_instance()
    return cache.get_module_dependencies(**kwargs)

def cache_keys(**kwargs) -> list[str]:
    """Get all non-expired cache keys."""
    cache = _get_cache_instance()
    return cache.keys(**kwargs)

def cache_values(**kwargs) -> list[Any]:
    """Get all non-expired cache values."""
    cache = _get_cache_instance()
    return cache.values(**kwargs)

def cache_items(**kwargs) -> dict[str, Any]:
    """Get all non-expired cache key-value pairs."""
    cache = _get_cache_instance()
    return cache.items(**kwargs)

def cache_pop(key: str, default: Any = None, **kwargs) -> Any:
    """Remove and return value if exists and not expired."""
    cache = _get_cache_instance()
    return cache.pop(key, default=default, **kwargs)

def cache_update(items: dict[str, Any], ttl: int = DEFAULT_CACHE_TTL,
                source_module: Optional[str] = None, **kwargs) -> int:
    """Update cache with multiple key-value pairs."""
    cache = _get_cache_instance()
    return cache.update(items, ttl=ttl, source_module=source_module, **kwargs)

def cache_touch(key: str, ttl: Optional[int] = None, **kwargs) -> bool:
    """Reset TTL for a key without changing its value."""
    cache = _get_cache_instance()
    return cache.touch(key, ttl=ttl, **kwargs)

def cache_increment(key: str, delta: int = 1, ttl: int = DEFAULT_CACHE_TTL, **kwargs) -> int:
    """Increment a counter value in cache."""
    cache = _get_cache_instance()
    return cache.increment(key, delta=delta, ttl=ttl, **kwargs)

def cache_get_many(keys: list[str], **kwargs) -> dict[str, Any]:
    """Convenience alias for batch get operations."""
    from lee.lee_cache.cache_batch_operations import _get_batch_cache_instance  # pylint: disable=import-outside-toplevel
    cache = _get_batch_cache_instance(**kwargs)
    return cache.mget(keys, **kwargs)

def cache_set_many(items: dict[str, Any], ttl: int = DEFAULT_CACHE_TTL, **kwargs) -> int:
    """Convenience alias for batch set operations."""
    from lee.lee_cache.cache_batch_operations import _get_batch_cache_instance  # pylint: disable=import-outside-toplevel
    cache = _get_batch_cache_instance(**kwargs)
    return cache.mset(items, ttl=ttl, **kwargs)
