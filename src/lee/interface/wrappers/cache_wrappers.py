"""cache_wrappers.py
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Purpose: Cache interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the cache router.
External modules MUST use gateway.execute_operation() instead of importing directly.

CONSOLIDATION:
- Removed duplicate correlation_id decorator implementation
- Uses base_wrapper.with_correlation_id
- Reduced code by ~5 lines
"""

from typing import Any, Optional

# Import correlation ID decorator from base_wrapper
from lee.interface.wrappers.base_wrapper import with_correlation_id

# Import protection - only work if cache core is available
try:
    # Phase 2: Batch operations
    from lee.lee_cache.cache_batch_operations import (
        cache_mdelete,
        cache_mget,
        cache_mget_metadata,
        cache_mset,
    )

    # Phase 2: Compression
    from lee.lee_cache.cache_compression import (
        get_cache_compressor,
    )

    # Phase 3: Invalidation, Warming, Observability
    from lee.lee_cache.cache_invalidation import (
        get_cache_invalidator,
    )

    # Phase 2: L2 Disk Cache
    from lee.lee_cache.cache_l2_disk import (
        get_l2_cache,
    )
    from lee.lee_cache.cache_observability import (
        get_cache_observability,
    )
    from lee.lee_cache.cache_operations import (
        _execute_clear_implementation,
        _execute_delete_implementation,
        _execute_exists_implementation,
        _execute_get_implementation,
        _execute_get_or_compute_implementation,
        _execute_get_stats_implementation,
        # Phase 1: Stampede Protection & Stale-While-Revalidate
        _execute_get_with_grace_period_implementation,
        _execute_process_pending_refreshes_implementation,
        _execute_set_implementation,
    )
    from lee.lee_cache.cache_warming import (
        get_cache_warmer,
    )

    _CACHE_AVAILABLE = True
    _CACHE_IMPORT_ERROR = None
except ImportError as e:
    _CACHE_AVAILABLE = False
    _CACHE_IMPORT_ERROR = str(e)


@with_correlation_id(scope_prefix="cache")
def cache_get(key: str, correlation_id: str = None) -> Any:
    """Get cached value - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_get_implementation(key=key, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache")
def cache_set(key: str, value: Any, ttl: Optional[float] = None, correlation_id: str = None, **kwargs) -> None:
    """Set cached value - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_set_implementation(key=key, value=value, ttl=ttl, correlation_id=correlation_id, **kwargs)


@with_correlation_id(scope_prefix="cache")
def cache_exists(key: str, correlation_id: str = None) -> bool:
    """Check if cache key exists - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_exists_implementation(key=key, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache")
def cache_delete(key: str, correlation_id: str = None) -> bool:
    """Delete cache key - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_delete_implementation(key=key, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache")
def cache_clear(correlation_id: str = None) -> None:
    """Clear all cache - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_clear_implementation(correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache")
def cache_stats(correlation_id: str = None) -> dict[str, Any]:
    """Get cache statistics - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_get_stats_implementation(correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache")
def cache_get_l2_cache(correlation_id: str = None, **kwargs):  # pylint: disable=unused-argument
    """Get L2 cache singleton - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return get_l2_cache()


@with_correlation_id(scope_prefix="cache")
def cache_get_with_grace_period(
    key: str,
    factory,
    ttl: int = 300,
    grace_period: int = 30,
    correlation_id: str = None,
    **kwargs,
) -> tuple:
    """Get value with stale-while-revalidate grace period - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_get_with_grace_period_implementation(
        key=key,
        factory=factory,
        ttl=ttl,
        grace_period=grace_period,
        correlation_id=correlation_id,
        **kwargs,
    )


@with_correlation_id(scope_prefix="cache")
def cache_get_or_compute(
    key: str,
    factory,
    ttl: int = 300,
    correlation_id: str = None,
    **kwargs,
) -> Any:
    """Get value with stampede protection (request coalescing) - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_get_or_compute_implementation(
        key=key,
        factory=factory,
        ttl=ttl,
        correlation_id=correlation_id,
        **kwargs,
    )


@with_correlation_id(scope_prefix="cache")
def cache_process_pending_refreshes(correlation_id: str = None, **kwargs) -> int:
    """Process pending async refreshes - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return _execute_process_pending_refreshes_implementation(
        correlation_id=correlation_id,
        **kwargs,
    )


# Phase 2: Batch operations wrappers

@with_correlation_id(scope_prefix="cache")
def cache_mget_wrapper(keys: list, correlation_id: str = None, **kwargs) -> dict:
    """Batch get multiple keys - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return cache_mget(keys=keys, correlation_id=correlation_id, **kwargs)


@with_correlation_id(scope_prefix="cache")
def cache_mset_wrapper(items: dict, ttl: int = None, correlation_id: str = None, **kwargs) -> int:
    """Batch set multiple items - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return cache_mset(items=items, ttl=ttl, correlation_id=correlation_id, **kwargs)


@with_correlation_id(scope_prefix="cache")
def cache_mdelete_wrapper(keys: list, correlation_id: str = None, **kwargs) -> int:
    """Batch delete multiple keys - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return cache_mdelete(keys=keys, correlation_id=correlation_id, **kwargs)


@with_correlation_id(scope_prefix="cache")
def cache_mget_metadata_wrapper(keys: list, correlation_id: str = None, **kwargs) -> dict:
    """Batch get metadata for multiple keys - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return cache_mget_metadata(keys=keys, correlation_id=correlation_id, **kwargs)


# Phase 2 & 3: Singleton access wrappers

@with_correlation_id(scope_prefix="cache")
def cache_get_compressor(correlation_id: str = None, **kwargs):  # pylint: disable=unused-argument
    """Get cache compressor singleton - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return get_cache_compressor()


@with_correlation_id(scope_prefix="cache")
def cache_get_invalidator(correlation_id: str = None, **kwargs):  # pylint: disable=unused-argument
    """Get cache invalidator singleton - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return get_cache_invalidator()


@with_correlation_id(scope_prefix="cache")
def cache_get_warmer(correlation_id: str = None, **kwargs):  # pylint: disable=unused-argument
    """Get cache warmer singleton - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return get_cache_warmer()


@with_correlation_id(scope_prefix="cache")
def cache_get_observability(correlation_id: str = None, **kwargs):  # pylint: disable=unused-argument
    """Get cache observability singleton - INTERNAL wrapper."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    return get_cache_observability()


# Phase 3: Cache warming operations
@with_correlation_id(scope_prefix="cache_warm")
def cache_warm_static(keys: list, factory: callable, correlation_id: str = None) -> int:
    """Warm static cache entries - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    warmer = get_cache_warmer()
    return warmer.warm_static_data(keys=keys, factory=factory, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache_warm")
def cache_warm_predictive(user_id: str, context: dict = None, correlation_id: str = None) -> int:
    """Warm predictive cache entries - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    warmer = get_cache_warmer()
    return warmer.warm_predictive_data(user_id=user_id, context=context, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache_warm")
def cache_warm_trace_based(trace_size: int = 100, correlation_id: str = None) -> int:
    """Warm trace-based cache entries - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    warmer = get_cache_warmer()
    return warmer.warm_trace_based(trace_size=trace_size, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache_access")
def cache_record_access(key: str, user_id: str = None, correlation_id: str = None) -> None:
    """Record cache access - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    warmer = get_cache_warmer()
    warmer.record_access(key=key, user_id=user_id, correlation_id=correlation_id)


@with_correlation_id(scope_prefix="cache_stats")
def cache_get_warming_stats(correlation_id: str = None) -> dict:
    """Get cache warming statistics - INTERNAL wrapper for cache router."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(f"Cache unavailable: {_CACHE_IMPORT_ERROR}")
    warmer = get_cache_warmer()
    return warmer.get_stats()


__all__ = [
    "cache_get",
    "cache_set",
    "cache_exists",
    "cache_delete",
    "cache_clear",
    "cache_stats",
    # Phase 1: Stampede Protection & Stale-While-Revalidate
    "cache_get_with_grace_period",
    "cache_get_or_compute",
    "cache_process_pending_refreshes",
    # Phase 2: Batch operations
    "cache_mget_wrapper",
    "cache_mset_wrapper",
    "cache_mdelete_wrapper",
    "cache_mget_metadata_wrapper",
    # Phase 2 & 3: Singleton access
    "cache_get_compressor",
    "cache_get_l2_cache",
    "cache_get_invalidator",
    "cache_get_warmer",
    "cache_get_observability",
    # Phase 3: Cache warming operations
    "cache_warm_static",
    "cache_warm_predictive",
    "cache_warm_trace_based",
    "cache_record_access",
    "cache_get_warming_stats",
]

# EOF
