"""cache_observability_split/key_statistics.py

KeyStatistics dataclass for per-key cache statistics.
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class KeyStatistics:
    """Statistics for a single cache key.

    Attributes:
        key: Cache key
        access_count: Total number of accesses
        hit_count: Number of cache hits
        miss_count: Number of cache misses
        size_bytes: Current size in bytes
        last_access: Most recent access timestamp
        last_update: Most recent value update timestamp
        created_at: When this key was first tracked
        ttl_seconds: Configured TTL (0 if no TTL)
        avg_latency_ms: Average access latency
        p50_latency_ms: 50th percentile latency
        p95_latency_ms: 95th percentile latency
        p99_latency_ms: 99th percentile latency

    """

    key: str
    access_count: int = 0
    hit_count: int = 0
    miss_count: int = 0
    size_bytes: int = 0
    last_access: Optional[datetime] = None
    last_update: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0

    # Internal latency tracking (not exported)
    _latencies: list[float] = field(default_factory=list, repr=False)

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as percentage (0-100)."""
        if self.access_count == 0:
            return 0.0
        return (self.hit_count / self.access_count) * 100

    @property
    def miss_rate(self) -> float:
        """Cache miss rate as percentage (0-100)."""
        return 100.0 - self.hit_rate

    def record_access(self, hit: bool, latency_ms: float) -> None:
        """Record a cache access.

            hit: Whether this was a hit
            latency_ms: Access latency in milliseconds

        """
        self.access_count += 1
        if hit:
            self.hit_count += 1
        else:
            self.miss_count += 1

        self.last_access = datetime.now()

        # Track latency (keep last 100 samples)
        if not hasattr(self, '_latencies'):
            self._latencies = []
        self._latencies.append(latency_ms)
        if len(self._latencies) > 100:
            self._latencies.pop(0)

        # Update percentile statistics
        self._update_latency_stats()

    def _update_latency_stats(self) -> None:
        """Update latency percentile statistics."""
        if not hasattr(self, '_latencies') or not self._latencies:
            return

        self.avg_latency_ms = statistics.mean(self._latencies)
        self.p50_latency_ms = statistics.median(self._latencies)

        # P95 and P99
        sorted_latencies = sorted(self._latencies)
        n = len(sorted_latencies)
        self.p95_latency_ms = sorted_latencies[int(n * 0.95)] if n >= 20 else 0
        self.p99_latency_ms = sorted_latencies[int(n * 0.99)] if n >= 100 else 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

            Dict representation of statistics

        """
        return {
            "key": self.key,
            "access_count": self.access_count,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": round(self.hit_rate, 2),
            "miss_rate": round(self.miss_rate, 2),
            "size_bytes": self.size_bytes,
            "last_access": self.last_access.isoformat() if self.last_access else None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            "ttl_seconds": self.ttl_seconds,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
        }

