"""
cache/__init__.py
Version: 2025-12-08_1
Purpose: Cache interface package exports
License: Apache 2.0
"""

from cache.cache_enums import (
    CacheOperation,
    CacheEntry,
    DEFAULT_CACHE_TTL,
    MAX_CACHE_BYTES,
    RATE_LIMIT_WINDOW_MS,
    RATE_LIMIT_MAX_OPS,
)

from cache.cache_core import (
    LUGSIntegratedCache,
)

from cache.cache_operations import (
    cache_get,
    cache_set,
    cache_exists,
    cache_delete,
    cache_clear,
    cache_reset,
    cache_cleanup_expired,
    cache_get_stats,
    cache_get_metadata,
    cache_get_module_dependencies,
)

from cache.interface_cache import (
    execute_cache_operation,
)

__all__ = [
    # Enums and types
    'CacheOperation',
    'CacheEntry',
    
    # Constants
    'DEFAULT_CACHE_TTL',
    'MAX_CACHE_BYTES',
    'RATE_LIMIT_WINDOW_MS',
    'RATE_LIMIT_MAX_OPS',
    
    # Main class
    'LUGSIntegratedCache',
    
    # Operations
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_reset',
    'cache_cleanup_expired',
    'cache_get_stats',
    'cache_get_metadata',
    'cache_get_module_dependencies',
    
    # Interface
    'execute_cache_operation',
]

# EOF
