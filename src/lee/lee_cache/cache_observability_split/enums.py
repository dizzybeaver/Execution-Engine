"""cache_observability_split/enums.py

Enums and constants for cache observability.
Split from cache_observability.py (lines 1-48).
"""

from enum import Enum

# Memory limits for key statistics (2026-03-29 fix)
MAX_KEY_STATS = 10000


class MetricType(Enum):
    """Types of cache metrics."""

    HIT = "hit"
    MISS = "miss"
    EVICTION = "eviction"
    ERROR = "error"
    LATENCY = "latency"
    COMPRESSION = "compression"
    COMPRESSION_SKIP = "compression_skip"
    L1_HIT = "l1_hit"
    L1_MISS = "l1_miss"
    L2_HIT = "l2_hit"
    L2_MISS = "l2_miss"


class HealthStatus(Enum):
    """Cache health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
