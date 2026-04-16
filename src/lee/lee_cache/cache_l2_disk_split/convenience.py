"""cache_l2_disk_split/convenience.py

Convenience functions for L2 disk cache.
"""

from __future__ import annotations

from typing import Any, Optional

from lee.lee_cache.cache_l2_disk_split.models import L2CacheConfig, L2CacheEntry
from lee.lee_cache.cache_l2_disk_split.l2_disk_cache import L2DiskCache
from lee.lee_cache.cache_l2_disk_split.singleton import get_l2_cache

def l2_get(key: str, default: Any = None, correlation_id: str = None) -> Any:
    """Get value from L2 cache with default and circuit breaker protection."""
    cache = get_l2_cache()
    result = cache.get(key, correlation_id)
    return result if result is not None else default


def l2_set(key: str, value: Any, ttl: Optional[int] = None, correlation_id: str = None) -> bool:
    """Set value in L2 cache with circuit breaker protection."""
    cache = get_l2_cache()
    return cache.set(key, value, ttl, correlation_id)


def l2_delete(key: str, correlation_id: str = None) -> bool:
    """Delete entry from L2 cache with circuit breaker protection."""
    cache = get_l2_cache()
    return cache.delete(key, correlation_id)


def l2_clear(correlation_id: str = None) -> bool:
    """Clear all L2 cache entries with circuit breaker protection."""
    cache = get_l2_cache()
    return cache.clear(correlation_id)


__all__ = [
    "L2CacheConfig",
    "L2CacheEntry",
    "L2DiskCache",
    "get_l2_cache",
    "l2_clear",
    "l2_delete",
    "l2_get",
    "l2_set",
]
