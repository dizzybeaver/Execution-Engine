"""Cache Observability System for LEE

Provides comprehensive metrics collection, health monitoring, and CloudWatch integration.
Tracks performance, hit rates, latency percentiles, and per-key statistics.

Split into modules for better maintainability:
- enums: MetricType, HealthStatus
- key_statistics: KeyStatistics dataclass
- metrics_collector: CacheMetricsCollector class
- health_models: HealthRecommendation, CacheHealthStatus
- observability: CacheObservability main class
"""

# Import all classes and functions from split modules
from lee.lee_cache.cache_observability_split.enums import (
    MetricType,
    HealthStatus,
    MAX_KEY_STATS,
)
from lee.lee_cache.cache_observability_split.key_statistics import KeyStatistics
from lee.lee_cache.cache_observability_split.metrics_collector import CacheMetricsCollector
from lee.lee_cache.cache_observability_split.health_models import (
    HealthRecommendation,
    CacheHealthStatus,
)
from lee.lee_cache.cache_observability_split.observability import (
    CacheObservability,
    get_cache_observability,
)

__all__ = [
    # Enums
    "MetricType",
    "HealthStatus",
    "MAX_KEY_STATS",

    # Data models
    "KeyStatistics",
    "HealthRecommendation",
    "CacheHealthStatus",

    # Metrics
    "CacheMetricsCollector",

    # Main observability
    "CacheObservability",
    "get_cache_observability",
]
