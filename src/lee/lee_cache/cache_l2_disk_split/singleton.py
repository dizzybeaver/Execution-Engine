"""cache_l2_disk_split/singleton.py

Singleton accessor for L2 disk cache.
"""

from __future__ import annotations

from typing import Optional
import sys
import threading

from lee.lee_cache.cache_l2_disk_split.models import L2CacheConfig
from lee.lee_cache.cache_l2_disk_split.l2_disk_cache import L2DiskCache

# Singleton instance
_l2_cache_instance = None
_l2_cache_lock = threading.RLock()

def get_l2_cache(config: Optional[L2CacheConfig] = None) -> Optional[L2DiskCache]:
    """Get the L2 disk cache singleton instance, or None if disabled."""
    global _l2_cache_instance

    # Check if L2 cache is disabled
    if 'lambda_preload' in sys.modules:
        import lambda_preload
        if getattr(lambda_preload, 'cache_l2_disable', False):
            return None

    with _l2_cache_lock:
        if _l2_cache_instance is None:
            _l2_cache_instance = L2DiskCache(config)
        return _l2_cache_instance
