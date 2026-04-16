"""Cache Wrapper Functions

Direct access to cache operations (23 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import cache

    # Get value (returns None if not found)
    value = cache.get(key='device:light:office')

    # Set value with 5-minute TTL
    cache.set(key='device:light:office', value={'state': 'on'}, ttl=300)

    # Check if key exists
    exists = cache.exists(key='device:light:office')

    # Delete key
    cache.delete(key='device:light:office')

    # Clear all cache
    cache.clear()
"""

from collections.abc import Callable
from typing import Any, Optional

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def cache_get(key: str, default: Any = None, **kwargs: Any) -> Any:
    """Get cached value.

    Args:
        key: Cache key
        default: Default value if key not found
        **kwargs: Additional cache options

    Returns:
        Cached value or default if not found
    """
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default=default, **kwargs)


def cache_set(key: str, value: Any, ttl: Optional[float] = None, **kwargs: Any) -> None:
    """Set cached value.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time-to-live in seconds (optional)
        **kwargs: Additional cache options
    """
    execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl, **kwargs)


def cache_exists(key: str, **kwargs: Any) -> bool:
    """Check if cache key exists.

    Args:
        key: Cache key
        **kwargs: Additional cache options

    Returns:
        True if key exists, False otherwise
    """
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key, **kwargs)


def cache_delete(key: str, **kwargs: Any) -> bool:
    """Delete cache key.

    Args:
        key: Cache key
        **kwargs: Additional cache options

    Returns:
        True if key was deleted, False if not found
    """
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key, **kwargs)


def cache_clear(**kwargs: Any) -> None:
    """Clear all cache entries.

    Args:
        **kwargs: Additional cache options
    """
    execute_operation(GatewayInterface.CACHE, 'clear', **kwargs)


def cache_stats(**kwargs: Any) -> dict[str, Any]:
    """Get cache statistics.

    Args:
        **kwargs: Additional cache options

    Returns:
        Dictionary with cache stats (hits, misses, size, etc.)
    """
    return execute_operation(GatewayInterface.CACHE, 'stats', **kwargs)


def cache_get_l2_cache(**kwargs: Any) -> Any:
    """Get L2 disk cache instance.

    Args:
        **kwargs: Additional cache options

    Returns:
        L2 cache instance
    """
    return execute_operation(GatewayInterface.CACHE, 'get_l2_cache', **kwargs)


def cache_get_with_grace_period(key: str, grace_period: float = 300, **kwargs: Any) -> Any:
    """Get value with grace period on expiration.

    Args:
        key: Cache key
        grace_period: Grace period in seconds (default 5 minutes)
        **kwargs: Additional cache options

    Returns:
        Cached value or None if not found and expired
    """
    return execute_operation(GatewayInterface.CACHE, 'get_with_grace_period', key=key, grace_period=grace_period, **kwargs)


def cache_get_or_compute(key: str, compute_fn: Callable[[], Any], ttl: Optional[float] = None, **kwargs: Any) -> Any:
    """Get value or compute if not found.

    Args:
        key: Cache key
        compute_fn: Function to compute value if not cached
        ttl: Time-to-live in seconds (optional)
        **kwargs: Additional cache options

    Returns:
        Cached or computed value
    """
    return execute_operation(GatewayInterface.CACHE, 'get_or_compute', key=key, compute_fn=compute_fn, ttl=ttl, **kwargs)


def cache_process_pending_refreshes(**kwargs: Any) -> int:
    """Process pending cache refreshes.

    Args:
        **kwargs: Additional cache options

    Returns:
        Number of refreshes processed
    """
    return execute_operation(GatewayInterface.CACHE, 'process_pending_refreshes', **kwargs)


def cache_mget_wrapper(keys: list[str], **kwargs: Any) -> dict[str, Any]:
    """Multi-get cache values.

    Args:
        keys: List of cache keys
        **kwargs: Additional cache options

    Returns:
        Dictionary mapping keys to values
    """
    return execute_operation(GatewayInterface.CACHE, 'mget', keys=keys, **kwargs)


def cache_mset_wrapper(items: dict[str, Any], ttl: Optional[float] = None, **kwargs: Any) -> None:
    """Multi-set cache values.

    Args:
        items: Dictionary of key-value pairs to cache
        ttl: Time-to-live in seconds (optional)
        **kwargs: Additional cache options
    """
    execute_operation(GatewayInterface.CACHE, 'mset', items=items, ttl=ttl, **kwargs)


def cache_mdelete_wrapper(keys: list[str], **kwargs: Any) -> int:
    """Multi-delete cache keys.

    Args:
        keys: List of cache keys to delete
        **kwargs: Additional cache options

    Returns:
        Number of keys deleted
    """
    return execute_operation(GatewayInterface.CACHE, 'mdelete', keys=keys, **kwargs)


def cache_mget_metadata_wrapper(keys: list[str], **kwargs: Any) -> dict[str, Any]:
    """Multi-get cache metadata.

    Args:
        keys: List of cache keys
        **kwargs: Additional cache options

    Returns:
        Dictionary mapping keys to metadata
    """
    return execute_operation(GatewayInterface.CACHE, 'mget_metadata', keys=keys, **kwargs)


def cache_get_compressor(**kwargs: Any) -> Any:
    """Get cache compressor instance.

    Args:
        **kwargs: Additional cache options

    Returns:
        Cache compressor instance
    """
    return execute_operation(GatewayInterface.CACHE, 'get_compressor', **kwargs)


def cache_get_invalidator(**kwargs: Any) -> Any:
    """Get cache invalidator instance.

    Args:
        **kwargs: Additional cache options

    Returns:
        Cache invalidator instance
    """
    return execute_operation(GatewayInterface.CACHE, 'get_invalidator', **kwargs)


def cache_get_warmer(**kwargs: Any) -> Any:
    """Get cache warmer instance.

    Args:
        **kwargs: Additional cache options

    Returns:
        Cache warmer instance
    """
    return execute_operation(GatewayInterface.CACHE, 'get_warmer', **kwargs)


def cache_get_observability(**kwargs: Any) -> Any:
    """Get cache observability instance.

    Args:
        **kwargs: Additional cache options

    Returns:
        Cache observability instance
    """
    return execute_operation(GatewayInterface.CACHE, 'get_observability', **kwargs)


def cache_warm_static(patterns: list[str], **kwargs: Any) -> int:
    """Warm cache with static patterns.

    Args:
        patterns: List of key patterns to warm
        **kwargs: Additional cache options

    Returns:
        Number of keys warmed
    """
    return execute_operation(GatewayInterface.CACHE, 'warm_static', patterns=patterns, **kwargs)


def cache_warm_predictive(count: int = 100, **kwargs: Any) -> int:
    """Warm cache with predictive algorithm.

    Args:
        count: Number of keys to warm
        **kwargs: Additional cache options

    Returns:
        Number of keys warmed
    """
    return execute_operation(GatewayInterface.CACHE, 'warm_predictive', count=count, **kwargs)


def cache_warm_trace_based(trace_file: str, **kwargs: Any) -> int:
    """Warm cache based on trace file.

    Args:
        trace_file: Path to trace file
        **kwargs: Additional cache options

    Returns:
        Number of keys warmed
    """
    return execute_operation(GatewayInterface.CACHE, 'warm_trace_based', trace_file=trace_file, **kwargs)


def cache_record_access(key: str, **kwargs: Any) -> None:
    """Record cache access for warming algorithms.

    Args:
        key: Cache key that was accessed
        **kwargs: Additional cache options
    """
    execute_operation(GatewayInterface.CACHE, 'record_access', key=key, **kwargs)


def cache_get_warming_stats(**kwargs: Any) -> dict[str, Any]:
    """Get cache warming statistics.

    Args:
        **kwargs: Additional cache options

    Returns:
        Dictionary with warming stats
    """
    return execute_operation(GatewayInterface.CACHE, 'get_warming_stats', **kwargs)


# Convenience aliases without cache_ prefix
get = cache_get  # pylint: disable=redefined-builtin
set = cache_set  # pylint: disable=redefined-builtin
exists = cache_exists
delete = cache_delete
clear = cache_clear
stats = cache_stats


__all__ = [
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    'cache_get_l2_cache',
    'cache_get_with_grace_period',
    'cache_get_or_compute',
    'cache_process_pending_refreshes',
    'cache_mget_wrapper',
    'cache_mset_wrapper',
    'cache_mdelete_wrapper',
    'cache_mget_metadata_wrapper',
    'cache_get_compressor',
    'cache_get_invalidator',
    'cache_get_warmer',
    'cache_get_observability',
    'cache_warm_static',
    'cache_warm_predictive',
    'cache_warm_trace_based',
    'cache_record_access',
    'cache_get_warming_stats',
    # Convenience aliases
    'get',
    'set',
    'exists',
    'delete',
    'clear',
    'stats',
]
