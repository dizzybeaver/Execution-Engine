"""cache_observability_split/observability.py

CacheObservability main class for cache observability.
"""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from threading import RLock
from typing import Any, Optional

from lee.lee_cache.cache_observability_split.enums import MetricType, HealthStatus, MAX_KEY_STATS
from lee.lee_cache.cache_observability_split.key_statistics import KeyStatistics
from lee.lee_cache.cache_observability_split.metrics_collector import CacheMetricsCollector
from lee.lee_cache.cache_observability_split.health_models import HealthRecommendation, CacheHealthStatus

class CacheObservability:  # pylint: disable=too-many-public-methods
    """Cache observability orchestrator.

    Provides comprehensive metrics collection, health monitoring, and CloudWatch export.

    Thread-safe singleton implementation.
    """

    _instance: Optional[CacheObservability] = None
    _initialized: bool = False
    _lock = RLock()

    def __new__(cls) -> CacheObservability:
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize cache observability (only once)."""
        if self._initialized:
            return

        self._metrics = CacheMetricsCollector()
        # Use OrderedDict for LRU eviction
        self._key_stats: OrderedDict[str, KeyStatistics] = OrderedDict()
        self._cloudwatch_enabled: bool = False
        self._cloudwatch_namespace: str = "LEE/Cache"
        self._initialized = True

    def enable_cloudwatch(self, enabled: bool = True, namespace: str = "LEE/Cache") -> None:
        """Enable or disable CloudWatch metrics export.

            enabled: Whether to enable CloudWatch export
            namespace: CloudWatch namespace for metrics

        """
        self._cloudwatch_enabled = enabled
        self._cloudwatch_namespace = namespace

    def record_hit(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record a cache hit.

            key: Cache key that was hit
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.HIT, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(True, latency_ms)

    def record_miss(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record a cache miss.

            key: Cache key that was missed
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.MISS, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(False, latency_ms)

    def record_error(self, key: str, error: Exception, correlation_id: Optional[str] = None) -> None:
        """Record a cache operation error.

            key: Cache key that caused the error
            error: Exception that occurred
            correlation_id: Optional correlation ID for tracking

        """
        _ = key  # Unused parameter for interface consistency
        _ = error  # Error type logged but not used
        self._metrics.record_metric(MetricType.ERROR, correlation_id=correlation_id)

    def record_eviction(self, key: str, correlation_id: Optional[str] = None) -> None:
        """Record a cache eviction.

            key: Cache key that was evicted
            correlation_id: Optional correlation ID for tracking

        """
        _ = key  # Unused parameter for interface consistency
        self._metrics.record_metric(MetricType.EVICTION, correlation_id=correlation_id)

    def update_key_size(self, key: str, size_bytes: int) -> None:
        """Update the size of a cached value.

            key: Cache key
            size_bytes: Size in bytes

        """
        stats = self._get_or_create_key_stats(key)
        stats.size_bytes = size_bytes
        stats.last_update = datetime.now()

    def update_key_ttl(self, key: str, ttl_seconds: int) -> None:
        """Update the TTL for a cache key.

            key: Cache key
            ttl_seconds: TTL in seconds (0 for no TTL)

        """
        stats = self._get_or_create_key_stats(key)
        stats.ttl_seconds = ttl_seconds

    def record_compression(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        key: str,
        compression_ratio: float,
        compression_time_ms: float,
        bytes_saved: int,
        original_bytes: int,
        compressed_bytes: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Record a cache compression operation.

            key: Cache key that was compressed
            compression_ratio: Compression ratio achieved
            compression_time_ms: Time taken to compress in milliseconds
            bytes_saved: Bytes saved from compression
            original_bytes: Original bytes before compression
            compressed_bytes: Compressed bytes after compression
            correlation_id: Optional correlation ID for tracking

        """
        _ = key  # Unused parameter for interface consistency
        self._metrics.record_metric(
            MetricType.COMPRESSION,
            latency_ms=compression_time_ms,
            correlation_id=correlation_id,
            compression_ratio=compression_ratio,
            bytes_saved=bytes_saved,
            original_bytes=original_bytes,
            compressed_bytes=compressed_bytes,
        )

    def record_compression_skip(self, key: str, correlation_id: Optional[str] = None) -> None:
        """Record a cache compression skip (value too small).

            key: Cache key that was skipped
            correlation_id: Optional correlation ID for tracking

        """
        _ = key  # Unused parameter for interface consistency
        self._metrics.record_metric(MetricType.COMPRESSION_SKIP, correlation_id=correlation_id)

    def get_compression_metrics(self) -> dict[str, Any]:
        """Get compression-specific metrics.

            Dict with compression statistics

        """
        return self._metrics.get_compression_stats()

    def _get_or_create_key_stats(self, key: str) -> KeyStatistics:
        """Get or create statistics for a key.

            key: Cache key

            KeyStatistics for the key

        """
        if key not in self._key_stats:
            # Enforce size limit with LRU eviction
            if len(self._key_stats) >= MAX_KEY_STATS:
                # Evict oldest entry (OrderedDict maintains insertion order)
                self._key_stats.popitem(last=False)
            self._key_stats[key] = KeyStatistics(key=key)
        else:
            # Move to end to mark as recently used (LRU)
            self._key_stats.move_to_end(key)
        return self._key_stats[key]

    def get_metrics(self) -> dict[str, Any]:
        """Get overall cache metrics.

            Dict with comprehensive metrics

        """
        return self._metrics.get_metrics_summary()

    def get_key_statistics(self, key: str) -> Optional[dict[str, Any]]:
        """Get statistics for a specific key.

            key: Cache key to query

            Dict with key statistics or None if key not tracked

        """
        if key not in self._key_stats:
            return None
        return self._key_stats[key].to_dict()

    # Sort dispatch for top keys (O(1) lookup)
    @staticmethod
    def _sort_access_count(s):
        """Sort key function for access_count."""
        return s.access_count

    @staticmethod
    def _sort_hit_count(s):
        """Sort key function for hit_count."""
        return s.hit_count

    @staticmethod
    def _sort_miss_count(s):
        """Sort key function for miss_count."""
        return s.miss_count

    @staticmethod
    def _sort_hit_rate(s):
        """Sort key function for hit_rate."""
        return s.hit_rate

    @staticmethod
    def _sort_size_bytes(s):
        """Sort key function for size_bytes."""
        return s.size_bytes

    # Dispatch dictionary for sort options (O(1) lookup)
    _SORT_DISPATCH = {
        "access_count": _sort_access_count,
        "hit_count": _sort_hit_count,
        "miss_count": _sort_miss_count,
        "hit_rate": _sort_hit_rate,
        "size_bytes": _sort_size_bytes,
    }

    def get_top_keys(self, count: int = 10, sort_by: str = "access_count") -> list[dict[str, Any]]:
        """Get top cache keys by various metrics.

            count: Maximum number of keys to return
            sort_by: Metric to sort by (access_count, hit_count, miss_count, hit_rate, size_bytes)

            List of key statistics sorted by the specified metric

        """
        all_stats = list(self._key_stats.values())

        # Dictionary dispatch for sort function (O(1) lookup)
        sort_func = self._SORT_DISPATCH.get(sort_by, self._sort_access_count)
        all_stats.sort(key=sort_func, reverse=True)

        return [s.to_dict() for s in all_stats[:count]]

    def record_l1_hit(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record an L1 cache hit.

            key: Cache key that was hit
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.L1_HIT, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(True, latency_ms)

    def record_l1_miss(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record an L1 cache miss.

            key: Cache key that was missed
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.L1_MISS, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(False, latency_ms)

    def record_l2_hit(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record an L2 cache hit.

            key: Cache key that was hit
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.L2_HIT, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(True, latency_ms)

    def record_l2_miss(self, key: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        """Record an L2 cache miss.

            key: Cache key that was missed
            latency_ms: Access latency in milliseconds
            correlation_id: Optional correlation ID for tracking

        """
        self._metrics.record_metric(MetricType.L2_MISS, latency_ms, correlation_id=correlation_id)
        self._get_or_create_key_stats(key).record_access(False, latency_ms)

    def record_operation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        operation_type: str,
        hit: bool = False,
        miss: bool = False,
        latency_ms: float = 0.0,
        key: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Record a cache operation by type.

            operation_type: Type of operation (get, set, delete, exists, mget, mset)
            hit: Whether this was a hit
            miss: Whether this was a miss
            latency_ms: Operation latency in milliseconds
            key: Optional cache key
            correlation_id: Optional correlation ID for tracking

        """
        _ = correlation_id  # Reserved for future tracking
        self._metrics.record_operation_metric(operation_type, hit, miss, latency_ms)

        # Also record in key stats if key provided
        if key:
            self._get_or_create_key_stats(key).record_access(hit, latency_ms)

    def get_l1_metrics(self) -> dict[str, Any]:
        """Get L1 cache metrics.

            Dict with L1 cache statistics

        """
        return self._metrics.get_l1_metrics()

    def get_l2_metrics(self) -> dict[str, Any]:
        """Get L2 cache metrics.

            Dict with L2 cache statistics

        """
        return self._metrics.get_l2_metrics()

    def get_operation_type_metrics(self) -> dict[str, Any]:
        """Get metrics by operation type.

            Dict with metrics per operation type

        """
        return self._metrics.get_operation_type_metrics()

    def get_slow_operations(self, threshold_ms: float = 10.0) -> list[dict[str, Any]]:
        """Get slow cache operations above threshold.

            threshold_ms: Latency threshold in milliseconds

            List of slow operation statistics

        """
        return self._metrics.get_slow_operations(threshold_ms)

    def check_health(self) -> CacheHealthStatus:
        """Perform comprehensive health check.

        Evaluates:
        - Hit rate (target: 70%+)
        - Error rate (max: 1%)
        - Latency (P95 target: <10ms)
        - Operation volume

            CacheHealthStatus with health assessment and recommendations

        """
        metrics = self._metrics.get_metrics_summary()
        warnings = []
        recommendations = []

        # Hit rate check
        hit_rate = metrics["hit_rate"]
        if hit_rate < CacheMetricsCollector.TARGET_HIT_RATE:
            warnings.append(f"Low hit rate: {hit_rate:.1f}% (target: {CacheMetricsCollector.TARGET_HIT_RATE}%)")
            recommendations.append(HealthRecommendation(
                severity="warning",
                category="performance",
                message=f"Cache hit rate is below target of {CacheMetricsCollector.TARGET_HIT_RATE}%",
                action="Consider increasing cache size or adjusting TTL values",
            ))

        # Error rate check
        error_rate = metrics["error_rate"]
        if error_rate > CacheMetricsCollector.MAX_ERROR_RATE:
            warnings.append(f"High error rate: {error_rate:.1f}% (max: {CacheMetricsCollector.MAX_ERROR_RATE}%)")
            recommendations.append(HealthRecommendation(
                severity="critical",
                category="reliability",
                message=f"Cache error rate exceeds {CacheMetricsCollector.MAX_ERROR_RATE}%",
                action="Check cache backend connectivity and error logs",
            ))

        # Latency check
        p95_latency = metrics["latency_ms"]["p95"]
        if p95_latency > CacheMetricsCollector.MAX_P95_LATENCY_MS:
            warnings.append(f"High P95 latency: {p95_latency:.1f}ms (target: <{CacheMetricsCollector.MAX_P95_LATENCY_MS}ms)")
            recommendations.append(HealthRecommendation(
                severity="warning",
                category="performance",
                message=f"P95 latency exceeds {CacheMetricsCollector.MAX_P95_LATENCY_MS}ms",
                action="Check cache backend performance and network latency",
            ))

        # Operation volume check
        if metrics["total_operations"] < 100:
            recommendations.append(HealthRecommendation(
                severity="info",
                category="volume",
                message="Low operation volume detected",
                action="Health metrics may not be statistically significant yet",
            ))

        # Calculate overall health score (0-100)
        score = 100.0

        # Hit rate impact (40% weight)
        if hit_rate < CacheMetricsCollector.TARGET_HIT_RATE:
            score -= 40 * (1 - hit_rate / CacheMetricsCollector.TARGET_HIT_RATE)

        # Error rate impact (30% weight)
        if error_rate > CacheMetricsCollector.MAX_ERROR_RATE:
            score -= 30 * (error_rate / CacheMetricsCollector.MAX_ERROR_RATE)

        # Latency impact (30% weight)
        if p95_latency > CacheMetricsCollector.MAX_P95_LATENCY_MS:
            score -= 30 * (p95_latency / CacheMetricsCollector.MAX_P95_LATENCY_MS)

        score = max(0.0, min(100.0, score))

        # Determine health status
        if score >= 80:
            status = HealthStatus.HEALTHY
        elif score >= 50:
            status = HealthStatus.DEGRADED
        elif score > 0:
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.UNKNOWN

        return CacheHealthStatus(
            status=status,
            score=score,
            warnings=warnings,
            recommendations=recommendations,
            metrics_snapshot=metrics,
        )

    def export_to_cloudwatch(self, metrics: Optional[dict[str, Any]] = None) -> bool:
        """Export metrics to AWS CloudWatch.

        Requires boto3 and proper AWS credentials.

            metrics: Optional metrics dict to export (uses current metrics if None)

            True if export successful, False otherwise

        """
        if not self._cloudwatch_enabled:
            return False

        try:
            import boto3  # pylint: disable=import-outside-toplevel

            if metrics is None:
                metrics = self._metrics.get_metrics_summary()

            cloudwatch = boto3.client("cloudwatch")

            # Prepare metric data
            metric_data = [
                {
                    "MetricName": "HitRate",
                    "Value": metrics["hit_rate"],
                    "Unit": "Percent",
                },
                {
                    "MetricName": "MissRate",
                    "Value": metrics["miss_rate"],
                    "Unit": "Percent",
                },
                {
                    "MetricName": "ErrorRate",
                    "Value": metrics["error_rate"],
                    "Unit": "Percent",
                },
                {
                    "MetricName": "TotalOperations",
                    "Value": metrics["total_operations"],
                    "Unit": "Count",
                },
                {
                    "MetricName": "LatencyP50",
                    "Value": metrics["latency_ms"]["p50"],
                    "Unit": "Milliseconds",
                },
                {
                    "MetricName": "LatencyP95",
                    "Value": metrics["latency_ms"]["p95"],
                    "Unit": "Milliseconds",
                },
                {
                    "MetricName": "LatencyP99",
                    "Value": metrics["latency_ms"]["p99"],
                    "Unit": "Milliseconds",
                },
            ]

            # Send to CloudWatch
            cloudwatch.put_metric_data(
                Namespace=self._cloudwatch_namespace,
                MetricData=metric_data,
            )

            return True

        except ImportError:
            # boto3 not available
            return False
        except (ConnectionError, OSError):
            # CloudWatch export failed (network error or I/O error)
            return False

    def reset_metrics(self) -> None:
        """Reset all metrics and key statistics."""
        self._metrics.reset()
        self._key_stats.clear()

    def get_statistics_summary(self) -> dict[str, Any]:
        """Get comprehensive statistics summary.

            Dict with metrics, key statistics, and health status

        """
        health = self.check_health()

        return {
            "metrics": self._metrics.get_metrics_summary(),
            "total_tracked_keys": len(self._key_stats),
            "health": health.to_dict(),
            "cloudwatch_enabled": self._cloudwatch_enabled,
        }


def get_cache_observability() -> CacheObservability:
    """Get singleton CacheObservability instance.

        CacheObservability singleton instance

    """
    return CacheObservability()
