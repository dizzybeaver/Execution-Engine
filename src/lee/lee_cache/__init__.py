"""cache/__init__.py
Version: 2025-03-02_1
Purpose: Cache interface package exports
License: Apache 2.0
"""

from lee.lee_cache.cache_batch_operations import (
    MultiGetOperations,
    cache_mdelete,
    cache_mget,
    cache_mget_metadata,
    cache_mset,
)
from lee.lee_cache.cache_compression import (
    CacheCompressor,
    CompressionConfig,
    CompressionMetadata,
    CompressionStatistics,
    get_cache_compressor,
)
from lee.lee_cache.cache_enums import (
    DEFAULT_CACHE_TTL,
    MAX_CACHE_BYTES,
    RATE_LIMIT_MAX_OPS,
    RATE_LIMIT_WINDOW_MS,
    CacheEntry,
    CacheOperation,
)
from lee.lee_cache.cache_generic import (
    LUGSIntegratedCache,
)

# Phase 3: Event-Driven Invalidation, Cache Warming, Observability
from lee.lee_cache.cache_invalidation import (
    CacheInvalidator,
    DependencyGraph,
    InvalidationResult,
    TagRegistry,
    get_cache_invalidator,
)
from lee.lee_cache.cache_l2_disk import (
    L2CacheConfig,
    L2DiskCache,
    get_l2_cache,
)
from lee.lee_cache.cache_observability import (
    CacheHealthStatus,
    CacheMetricsCollector,
    CacheObservability,
    KeyStatistics,
    get_cache_observability,
)
from lee.lee_cache.cache_operations import (
    cache_cleanup_expired,
    cache_clear,
    cache_delete,
    cache_exists,
    cache_get,
    cache_get_many,
    cache_get_metadata,
    cache_get_module_dependencies,
    cache_get_stats,
    cache_increment,
    cache_items,
    cache_keys,
    cache_pop,
    cache_reset,
    cache_set,
    cache_set_many,
    cache_touch,
    cache_update,
    cache_values,
)
from lee.lee_cache.cache_warming import (
    CacheWarmer,
    get_cache_warmer,
    get_cache_warming_stats,
    record_access,
    warm_alexa_capacities,
    warm_alexa_discovery_data,
    warm_alexa_entity_states,
    warm_predictive_data,
    warm_static_data,
    warm_trace_based,
)

# Phase 1: Stampede Protection & Stale-While-Revalidate
from lee.lee_cache.lee_stampede_protection import (
    StampedeProtection,
    StampedeProtectionConfig,
    get_stampede_protection,
    stampede_protected,
)
from lee.lee_cache.stale_while_revalidate import (
    StaleWhileRevalidate,
    StaleWhileRevalidateConfig,
    get_stale_while_revalidate,
)

# Note: execute_cache_operation is provided by interface.interface_cache

__all__ = [
    # Enums and types
    "CacheOperation",
    "CacheEntry",

    # Constants
    "DEFAULT_CACHE_TTL",
    "MAX_CACHE_BYTES",
    "RATE_LIMIT_WINDOW_MS",
    "RATE_LIMIT_MAX_OPS",

    # Main class
    "LUGSIntegratedCache",

    # Operations
    "cache_get",
    "cache_set",
    "cache_exists",
    "cache_delete",
    "cache_clear",
    "cache_reset",
    "cache_cleanup_expired",
    "cache_get_stats",
    "cache_get_metadata",
    "cache_get_module_dependencies",
    "cache_keys",
    "cache_values",
    "cache_items",
    "cache_pop",
    "cache_update",
    "cache_touch",
    "cache_increment",
    "cache_get_many",
    "cache_set_many",

    # Batch operations
    "cache_mget",
    "cache_mset",
    "cache_mdelete",
    "cache_mget_metadata",
    "MultiGetOperations",

    # Phase 2: Compression
    "CacheCompressor",
    "CompressionConfig",
    "CompressionMetadata",
    "CompressionStatistics",
    "get_cache_compressor",

    # Phase 2: L2 Disk Cache
    "L2DiskCache",
    "L2CacheConfig",
    "get_l2_cache",

    # Phase 3: Invalidation
    "CacheInvalidator",
    "TagRegistry",
    "DependencyGraph",
    "InvalidationResult",
    "get_cache_invalidator",

    # Phase 3: Warming
    "CacheWarmer",
    "get_cache_warmer",
    "warm_static_data",
    "warm_predictive_data",
    "warm_trace_based",
    "record_access",
    "get_cache_warming_stats",
    "warm_alexa_discovery_data",
    "warm_alexa_entity_states",
    "warm_alexa_capacities",

    # Phase 3: Observability
    "CacheObservability",
    "CacheMetricsCollector",
    "KeyStatistics",
    "CacheHealthStatus",
    "get_cache_observability",

    # Phase 1: Stampede Protection
    "StampedeProtection",
    "StampedeProtectionConfig",
    "get_stampede_protection",
    "stampede_protected",

    # Phase 1: Stale-While-Revalidate
    "StaleWhileRevalidate",
    "StaleWhileRevalidateConfig",
    "get_stale_while_revalidate",

    # Interface (provided by interface.interface_cache)
    # 'execute_cache_operation',
]

# EOF
