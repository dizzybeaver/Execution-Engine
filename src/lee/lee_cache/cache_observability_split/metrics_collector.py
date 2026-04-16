"""cache_observability_split/metrics_collector.py

CacheMetricsCollector class for aggregating cache metrics.
"""

import statistics
from datetime import datetime
from threading import RLock
from typing import Any, Optional

from lee.lee_cache.cache_observability_split.enums import MetricType

class CacheMetricsCollector:  # pylint: disable=too-many-instance-attributes
    """Aggregates cache operation metrics across all keys.

    Tracks overall performance metrics with sliding windows.
    """

    # Metric thresholds
    TARGET_HIT_RATE = 70.0  # Target cache hit rate percentage
    MAX_P95_LATENCY_MS = 10.0  # Maximum acceptable P95 latency
    MAX_ERROR_RATE = 1.0  # Maximum acceptable error rate percentage

    # Sliding window parameters
    WINDOW_SIZE = 1000  # Number of operations to keep in window
    LATENCY_WINDOW_SIZE = 100  # Number of latencies to track

    def __init__(self):
        """Initialize metrics collector."""
        self._total_hits: int = 0
        self._total_misses: int = 0
        self._total_errors: int = 0
        self._total_evictions: int = 0

        # L1/L2 cache metrics
        self._l1_hits: int = 0
        self._l1_misses: int = 0
        self._l2_hits: int = 0
        self._l2_misses: int = 0

        # Operation type tracking
        self._operations_by_type: dict[str, dict[str, int]] = {
            "get": {"hits": 0, "misses": 0, "total_latency_ms": 0.0, "count": 0},
            "set": {"count": 0, "total_latency_ms": 0.0},
            "delete": {"count": 0, "total_latency_ms": 0.0},
            "exists": {"count": 0, "total_latency_ms": 0.0},
            "mget": {"hits": 0, "misses": 0, "total_latency_ms": 0.0, "count": 0},
            "mset": {"count": 0, "total_latency_ms": 0.0},
        }

        # Compression metrics
        self._total_compressions: int = 0
        self._total_compression_skips: int = 0
        self._compression_ratios: list[float] = []
        self._compression_overhead_ms: list[float] = []
        self._bytes_saved: int = 0
        self._original_bytes: int = 0
        self._compressed_bytes: int = 0

        self._latencies: list[float] = []
        self._operation_times: list[tuple[datetime, str]] = []

        self._lock = RLock()

    def record_metric(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-branches
        self,
        metric_type: MetricType,
        latency_ms: float = 0.0,
        correlation_id: Optional[str] = None,
        compression_ratio: float = 0.0,
        bytes_saved: int = 0,
        original_bytes: int = 0,
        compressed_bytes: int = 0,
    ) -> None:
        """Record a cache operation metric.

            metric_type: Type of metric (hit, miss, eviction, error, latency, compression)
            latency_ms: Operation latency in milliseconds
            correlation_id: Optional correlation ID for tracking
            compression_ratio: Compression ratio (compressed_size / original_size)
            bytes_saved: Bytes saved from compression
            original_bytes: Original bytes before compression
            compressed_bytes: Compressed bytes after compression

        """
        timestamp = datetime.now()

        with self._lock:
            # Dictionary dispatch for simple metric increments (O(1) lookup)
            if metric_type == MetricType.COMPRESSION:
                # Handle compression metrics separately (complex logic)
                self._total_compressions += 1
                if compression_ratio > 0:
                    self._compression_ratios.append(compression_ratio)
                    if len(self._compression_ratios) > 100:
                        self._compression_ratios.pop(0)
                # Track bytes saved
                if bytes_saved > 0:
                    self._bytes_saved += bytes_saved
                if original_bytes > 0:
                    self._original_bytes += original_bytes
                if compressed_bytes > 0:
                    self._compressed_bytes += compressed_bytes
                # Track compression overhead
                if latency_ms > 0:
                    self._compression_overhead_ms.append(latency_ms)
                    if len(self._compression_overhead_ms) > 100:
                        self._compression_overhead_ms.pop(0)
            else:
                # Simple metric increments using dictionary dispatch
                METRIC_HANDLERS = {
                    MetricType.HIT: lambda: setattr(self, '_total_hits', self._total_hits + 1),
                    MetricType.MISS: lambda: setattr(self, '_total_misses', self._total_misses + 1),
                    MetricType.ERROR: lambda: setattr(self, '_total_errors', self._total_errors + 1),
                    MetricType.EVICTION: lambda: setattr(self, '_total_evictions', self._total_evictions + 1),
                    MetricType.COMPRESSION_SKIP: lambda: setattr(self, '_total_compression_skips', self._total_compression_skips + 1),
                    MetricType.L1_HIT: lambda: (setattr(self, '_l1_hits', self._l1_hits + 1), setattr(self, '_total_hits', self._total_hits + 1)),
                    MetricType.L1_MISS: lambda: (setattr(self, '_l1_misses', self._l1_misses + 1), setattr(self, '_total_misses', self._total_misses + 1)),
                    MetricType.L2_HIT: lambda: (setattr(self, '_l2_hits', self._l2_hits + 1), setattr(self, '_total_hits', self._total_hits + 1)),
                    MetricType.L2_MISS: lambda: (setattr(self, '_l2_misses', self._l2_misses + 1), setattr(self, '_total_misses', self._total_misses + 1)),
                }
                handler = METRIC_HANDLERS.get(metric_type)
                if handler:
                    handler()

            if latency_ms > 0 and metric_type != MetricType.COMPRESSION:
                self._latencies.append(latency_ms)
                if len(self._latencies) > self.LATENCY_WINDOW_SIZE:
                    self._latencies.pop(0)

            self._operation_times.append((timestamp, metric_type.value))
            if len(self._operation_times) > self.WINDOW_SIZE:
                self._operation_times.pop(0)

    @property
    def total_operations(self) -> int:
        """Total number of cache operations."""
        with self._lock:
            return self._total_hits + self._total_misses

    @property
    def hit_rate(self) -> float:
        """Overall cache hit rate percentage."""
        with self._lock:
            total = self._total_hits + self._total_misses
            if total == 0:
                return 0.0
            return (self._total_hits / total) * 100

    @property
    def miss_rate(self) -> float:
        """Overall cache miss rate percentage."""
        return 100.0 - self.hit_rate

    @property
    def error_rate(self) -> float:
        """Error rate percentage."""
        with self._lock:
            total = self._total_hits + self._total_misses
            if total == 0:
                return 0.0
            return (self._total_errors / total) * 100

    def get_latency_percentiles(self) -> dict[str, float]:
        """Calculate latency percentiles.

            Dict with p50, p95, p99 latencies in milliseconds

        """
        with self._lock:
            if not self._latencies:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

            sorted_latencies = sorted(self._latencies)
            n = len(sorted_latencies)

            return {
                "p50": statistics.median(sorted_latencies),
                "p95": sorted_latencies[int(n * 0.95)] if n >= 20 else 0.0,
                "p99": sorted_latencies[int(n * 0.99)] if n >= 100 else 0.0,
            }

    @property
    def compression_rate(self) -> float:
        """Compression rate percentage (operations compressed / total operations)."""
        with self._lock:
            total_compression_ops = self._total_compressions + self._total_compression_skips
            if total_compression_ops == 0:
                return 0.0
            return (self._total_compressions / total_compression_ops) * 100

    def get_compression_stats(self) -> dict[str, Any]:
        """Get compression statistics.

            Dict with compression metrics

        """
        with self._lock:
            avg_ratio = 0.0
            if self._compression_ratios:
                avg_ratio = statistics.mean(self._compression_ratios)

            avg_compression_time = 0.0
            if self._compression_overhead_ms:
                avg_compression_time = statistics.mean(self._compression_overhead_ms)

            space_saving_rate = 0.0
            if self._original_bytes > 0:
                space_saving_rate = (self._bytes_saved / self._original_bytes) * 100

            skip_rate = 0.0
            total_attempts = self._total_compressions + self._total_compression_skips
            if total_attempts > 0:
                skip_rate = (self._total_compression_skips / total_attempts) * 100

            return {
                "total_compressions": self._total_compressions,
                "total_skips": self._total_compression_skips,
                "compression_rate": round(self.compression_rate, 2),
                "avg_compression_ratio": round(avg_ratio, 2),
                "compression_time_avg_ms": round(avg_compression_time, 2),
                "skip_rate": round(skip_rate, 2),
                "space_saving_rate": round(space_saving_rate, 2),
                "space_savings_percent": round((1 - avg_ratio) * 100, 2) if avg_ratio > 0 else 0.0,
                "bytes_saved": self._bytes_saved,
                "original_bytes": self._original_bytes,
                "compressed_bytes": self._compressed_bytes,
            }

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary.

            Dict with all metrics

        """
        with self._lock:
            latencies = self.get_latency_percentiles()
            compression_stats = self.get_compression_stats()

            return {
                "total_operations": self.total_operations,
                "total_hits": self._total_hits,
                "total_misses": self._total_misses,
                "total_errors": self._total_errors,
                "total_evictions": self._total_evictions,
                "hit_rate": round(self.hit_rate, 2),
                "miss_rate": round(self.miss_rate, 2),
                "error_rate": round(self.error_rate, 2),
                "latency_ms": {
                    "avg": round(statistics.mean(self._latencies), 2) if self._latencies else 0.0,
                    "p50": round(latencies["p50"], 2),
                    "p95": round(latencies["p95"], 2),
                    "p99": round(latencies["p99"], 2),
                },
                "compression": compression_stats,
                "l1_cache": self.get_l1_metrics(),
                "l2_cache": self.get_l2_metrics(),
                "operations_by_type": self.get_operation_type_metrics(),
            }

    def record_operation_metric(self, operation_type: str, hit: bool = False, miss: bool = False, latency_ms: float = 0.0) -> None:
        """Record a cache operation metric by type.

            operation_type: Type of operation (get, set, delete, exists, mget, mset)
            hit: Whether this was a hit
            miss: Whether this was a miss
            latency_ms: Operation latency in milliseconds

        """
        with self._lock:
            if operation_type in self._operations_by_type:
                op_metrics = self._operations_by_type[operation_type]
                op_metrics["count"] = op_metrics.get("count", 0) + 1

                if latency_ms > 0:
                    current_total = op_metrics.get("total_latency_ms", 0.0)
                    op_metrics["total_latency_ms"] = current_total + latency_ms

                if hit:
                    op_metrics["hits"] = op_metrics.get("hits", 0) + 1
                if miss:
                    op_metrics["misses"] = op_metrics.get("misses", 0) + 1

    def get_l1_metrics(self) -> dict[str, Any]:
        """Get L1 cache metrics.

            Dict with L1 cache statistics

        """
        with self._lock:
            total_l1_ops = self._l1_hits + self._l1_misses
            hit_rate = (self._l1_hits / total_l1_ops * 100) if total_l1_ops > 0 else 0.0

            return {
                "total_hits": self._l1_hits,
                "total_misses": self._l1_misses,
                "total_operations": total_l1_ops,
                "hit_rate": round(hit_rate, 2),
            }

    def get_l2_metrics(self) -> dict[str, Any]:
        """Get L2 cache metrics.

            Dict with L2 cache statistics

        """
        with self._lock:
            total_l2_ops = self._l2_hits + self._l2_misses
            hit_rate = (self._l2_hits / total_l2_ops * 100) if total_l2_ops > 0 else 0.0

            return {
                "total_hits": self._l2_hits,
                "total_misses": self._l2_misses,
                "total_operations": total_l2_ops,
                "hit_rate": round(hit_rate, 2),
            }

    def get_operation_type_metrics(self) -> dict[str, Any]:
        """Get metrics by operation type.

            Dict with metrics per operation type

        """
        with self._lock:
            result = {}
            for op_type, metrics in self._operations_by_type.items():
                count = metrics.get("count", 0)
                total_latency = metrics.get("total_latency_ms", 0.0)
                avg_latency = (total_latency / count) if count > 0 else 0.0

                hits = metrics.get("hits", 0)
                misses = metrics.get("misses", 0)
                total_accesses = hits + misses
                hit_rate = (hits / total_accesses * 100) if total_accesses > 0 else 0.0

                result[op_type] = {
                    "count": count,
                    "avg_latency_ms": round(avg_latency, 2),
                    "hits": hits,
                    "misses": misses,
                    "hit_rate": round(hit_rate, 2),
                }

            return result

    def get_slow_operations(self, threshold_ms: float = 10.0) -> list[dict[str, Any]]:
        """Get slow cache operations above threshold.

            threshold_ms: Latency threshold in milliseconds

            List of slow operation statistics

        """
        with self._lock:
            slow_ops = []
            for op_type, metrics in self._operations_by_type.items():
                count = metrics.get("count", 0)
                if count == 0:
                    continue

                total_latency = metrics.get("total_latency_ms", 0.0)
                avg_latency = (total_latency / count) if count > 0 else 0.0

                if avg_latency > threshold_ms:
                    slow_ops.append({
                        "operation_type": op_type,
                        "count": count,
                        "avg_latency_ms": round(avg_latency, 2),
                        "threshold_ms": threshold_ms,
                    })

            return sorted(slow_ops, key=lambda x: x["avg_latency_ms"], reverse=True)

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._total_hits = 0
            self._total_misses = 0
            self._total_errors = 0
            self._total_evictions = 0
            self._latencies.clear()
            self._operation_times.clear()
