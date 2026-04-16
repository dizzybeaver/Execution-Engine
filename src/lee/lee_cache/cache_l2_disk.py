"""L2 Disk Cache for Lambda Cold Start Persistence

Implementation of persistent disk cache for AWS Lambda using /tmp directory.
Provides data persistence across Lambda cold starts while maintaining thread safety.

Split into modules for better maintainability:
- models: L2CacheEntry, L2CacheConfig
- l2_disk_cache: L2DiskCache class
- singleton: get_l2_cache singleton
- convenience: l2_* convenience functions
"""

from __future__ import annotations

from lee.lee_cache.cache_l2_disk_split.models import (
    L2CacheEntry,
    L2CacheConfig,
)
from lee.lee_cache.cache_l2_disk_split.l2_disk_cache import L2DiskCache
from lee.lee_cache.cache_l2_disk_split.singleton import get_l2_cache
from lee.lee_cache.cache_l2_disk_split.convenience import (
    l2_get,
    l2_set,
    l2_delete,
    l2_clear,
)

__all__ = [
    # Models
    "L2CacheEntry",
    "L2CacheConfig",

    # Main cache
    "L2DiskCache",

    # Singleton
    "get_l2_cache",

    # Convenience functions
    "l2_get",
    "l2_set",
    "l2_delete",
    "l2_clear",
]
