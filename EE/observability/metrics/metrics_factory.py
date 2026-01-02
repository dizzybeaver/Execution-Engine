"""
Metrics Factory - Observability Domain

Performance metrics and CloudWatch metrics implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside observability domain (except stdlib)
- All cross-domain calls via call_operation callback
- Module-level state for persistence across instances
"""

import time
import threading
from typing import Any, Dict, Optional, Callable, List
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# Module-level metrics state (shared across all instances)
# =============================================================================

_METRICS_LOCK = threading.RLock()
_COUNTERS: Dict[str, int] = defaultdict(int)
_GAUGES: Dict[str, float] = {}
_TIMINGS: Dict[str, List[float]] = defaultdict(list)
_HISTOGRAMS: Dict[str, List[float]] = defaultdict(list)
_CLOUDWATCH_ENABLED = False


# =============================================================================
# Metric data classes
# =============================================================================

@dataclass
class MetricSnapshot:
    """Snapshot of a metric value."""
    name: str
    value: Any
    timestamp: float = field(default_factory=time.time)


@dataclass
class TimingSnapshot:
    """Snapshot of timing metrics."""
    name: str
    count: int
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float


# =============================================================================
# Metrics Factory Class
# =============================================================================

class MetricsFactory:
    """Performance metrics factory.

    Provides comprehensive metrics capabilities with CloudWatch integration:
    - Counters (increment, decrement)
    - Gauges (set absolute value)
    - Timings (measure duration)
    - Histograms (distribution tracking)
    - CloudWatch integration

    UG-ISP Compliance:
    - Cross-domain calls via call_operation callback
    - Uses module-level state for persistence
    - No direct imports outside observability domain
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize metrics factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance (for external metrics system)
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger
        self.metrics = metrics
        self.call_operation = call_operation

    def increment(
        self,
        metric_name: str,
        value: int = 1,
        dimensions: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> int:
        """Increment counter metric.

        Args:
            metric_name: Metric name
            value: Value to increment by (default: 1)
            dimensions: Optional CloudWatch dimensions
            **kwargs: Additional parameters

        Returns:
            New counter value
        """
        with _METRICS_LOCK:
            _COUNTERS[metric_name] += value
            new_value = _COUNTERS[metric_name]

        # Log metric change
        if self.logger:
            self.logger.debug(
                f"Metric increment: {metric_name} += {value} = {new_value}"
            )

        # Send to CloudWatch if enabled
        if _CLOUDWATCH_ENABLED:
            self._send_to_cloudwatch(metric_name, new_value, dimensions)

        return new_value

    def decrement(
        self,
        metric_name: str,
        value: int = 1,
        dimensions: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> int:
        """Decrement counter metric.

        Args:
            metric_name: Metric name
            value: Value to decrement by (default: 1)
            dimensions: Optional CloudWatch dimensions
            **kwargs: Additional parameters

        Returns:
            New counter value
        """
        with _METRICS_LOCK:
            _COUNTERS[metric_name] -= value
            new_value = _COUNTERS[metric_name]

        # Log metric change
        if self.logger:
            self.logger.debug(
                f"Metric decrement: {metric_name} -= {value} = {new_value}"
            )

        # Send to CloudWatch if enabled
        if _CLOUDWATCH_ENABLED:
            self._send_to_cloudwatch(metric_name, new_value, dimensions)

        return new_value

    def gauge(
        self,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> float:
        """Set gauge metric value.

        Args:
            metric_name: Metric name
            value: Gauge value
            dimensions: Optional CloudWatch dimensions
            **kwargs: Additional parameters

        Returns:
            Gauge value
        """
        with _METRICS_LOCK:
            _GAUGES[metric_name] = value

        # Log metric change
        if self.logger:
            self.logger.debug(f"Metric gauge: {metric_name} = {value}")

        # Send to CloudWatch if enabled
        if _CLOUDWATCH_ENABLED:
            self._send_to_cloudwatch(metric_name, value, dimensions)

        return value

    def timing(
        self,
        metric_name: str,
        value_ms: float,
        dimensions: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> bool:
        """Record timing metric.

        Args:
            metric_name: Metric name
            value_ms: Timing value in milliseconds
            dimensions: Optional CloudWatch dimensions
            **kwargs: Additional parameters

        Returns:
            True if recorded successfully
        """
        with _METRICS_LOCK:
            _TIMINGS[metric_name].append(value_ms)

            # Keep only last 1000 timings per metric
            if len(_TIMINGS[metric_name]) > 1000:
                _TIMINGS[metric_name] = _TIMINGS[metric_name][-1000:]

        # Log timing
        if self.logger:
            self.logger.debug(f"Metric timing: {metric_name} = {value_ms}ms")

        # Send to CloudWatch if enabled (send average)
        if _CLOUDWATCH_ENABLED:
            stats = self._get_timing_stats(metric_name)
            self._send_to_cloudwatch(metric_name, stats.avg, dimensions)

        return True

    def histogram(
        self,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> bool:
        """Record histogram value.

        Args:
            metric_name: Metric name
            value: Histogram value
            dimensions: Optional CloudWatch dimensions
            **kwargs: Additional parameters

        Returns:
            True if recorded successfully
        """
        with _METRICS_LOCK:
            _HISTOGRAMS[metric_name].append(value)

            # Keep only last 1000 values per histogram
            if len(_HISTOGRAMS[metric_name]) > 1000:
                _HISTOGRAMS[metric_name] = _HISTOGRAMS[metric_name][-1000:]

        # Log histogram
        if self.logger:
            self.logger.debug(f"Metric histogram: {metric_name} = {value}")

        # Send to CloudWatch if enabled (send average)
        if _CLOUDWATCH_ENABLED:
            stats = self._get_histogram_stats(metric_name)
            self._send_to_cloudwatch(metric_name, stats.avg, dimensions)

        return True

    def flush(self, **kwargs) -> bool:
        """Flush all metrics to CloudWatch.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not _CLOUDWATCH_ENABLED:
            if self.logger:
                self.logger.warning("CloudWatch is disabled, flush skipped")
            return False

        # Flush all counters
        with _METRICS_LOCK:
            for name, value in _COUNTERS.items():
                self._send_to_cloudwatch(name, value, {})

            for name, value in _GAUGES.items():
                self._send_to_cloudwatch(name, value, {})

        if self.logger:
            self.logger.info("Metrics flushed to CloudWatch")

        return True

    def get_metrics(self, **kwargs) -> Dict[str, Any]:
        """Get all metrics.

        Args:
            **kwargs: Additional parameters

        Returns:
            Dictionary of all metrics
        """
        with _METRICS_LOCK:
            result = {
                'counters': dict(_COUNTERS),
                'gauges': dict(_GAUGES),
                'timings': {},
                'histograms': {},
            }

            # Calculate timing stats
            for name in _TIMINGS:
                result['timings'][name] = self._get_timing_stats_dict(name)

            # Calculate histogram stats
            for name in _HISTOGRAMS:
                result['histograms'][name] = self._get_histogram_stats_dict(name)

        return result

    def reset(self, **kwargs) -> bool:
        """Reset all metrics.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _COUNTERS, _GAUGES, _TIMINGS, _HISTOGRAMS

        with _METRICS_LOCK:
            _COUNTERS.clear()
            _GAUGES.clear()
            _TIMINGS.clear()
            _HISTOGRAMS.clear()

        if self.logger:
            self.logger.info("All metrics reset")

        return True

    def enable_cloudwatch(self, **kwargs) -> bool:
        """Enable CloudWatch integration.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _CLOUDWATCH_ENABLED

        _CLOUDWATCH_ENABLED = True

        if self.logger:
            self.logger.info("CloudWatch metrics enabled")

        return True

    def disable_cloudwatch(self, **kwargs) -> bool:
        """Disable CloudWatch integration.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _CLOUDWATCH_ENABLED

        _CLOUDWATCH_ENABLED = False

        if self.logger:
            self.logger.info("CloudWatch metrics disabled")

        return True

    # ========================================================================
    # Private helper methods
    # ========================================================================

    def _get_timing_stats(self, metric_name: str) -> TimingSnapshot:
        """Get timing statistics for a metric.

        Args:
            metric_name: Metric name

        Returns:
            TimingSnapshot with statistics
        """
        with _METRICS_LOCK:
            timings = _TIMINGS.get(metric_name, [])

            if not timings:
                return TimingSnapshot(
                    name=metric_name,
                    count=0,
                    min=0.0,
                    max=0.0,
                    avg=0.0,
                    p50=0.0,
                    p95=0.0,
                    p99=0.0
                )

            sorted_timings = sorted(timings)
            count = len(sorted_timings)

            return TimingSnapshot(
                name=metric_name,
                count=count,
                min=sorted_timings[0],
                max=sorted_timings[-1],
                avg=sum(sorted_timings) / count,
                p50=sorted_timings[int(count * 0.5)],
                p95=sorted_timings[int(count * 0.95)],
                p99=sorted_timings[int(count * 0.99)],
            )

    def _get_timing_stats_dict(self, metric_name: str) -> Dict[str, Any]:
        """Get timing statistics as dictionary.

        Args:
            metric_name: Metric name

        Returns:
            Dictionary with statistics
        """
        stats = self._get_timing_stats(metric_name)
        return {
            'count': stats.count,
            'min_ms': stats.min,
            'max_ms': stats.max,
            'avg_ms': stats.avg,
            'p50_ms': stats.p50,
            'p95_ms': stats.p95,
            'p99_ms': stats.p99,
        }

    def _get_histogram_stats(self, metric_name: str) -> TimingSnapshot:
        """Get histogram statistics for a metric.

        Args:
            metric_name: Metric name

        Returns:
            TimingSnapshot with statistics
        """
        with _METRICS_LOCK:
            values = _HISTOGRAMS.get(metric_name, [])

            if not values:
                return TimingSnapshot(
                    name=metric_name,
                    count=0,
                    min=0.0,
                    max=0.0,
                    avg=0.0,
                    p50=0.0,
                    p95=0.0,
                    p99=0.0
                )

            sorted_values = sorted(values)
            count = len(sorted_values)

            return TimingSnapshot(
                name=metric_name,
                count=count,
                min=sorted_values[0],
                max=sorted_values[-1],
                avg=sum(sorted_values) / count,
                p50=sorted_values[int(count * 0.5)],
                p95=sorted_values[int(count * 0.95)],
                p99=sorted_values[int(count * 0.99)],
            )

    def _get_histogram_stats_dict(self, metric_name: str) -> Dict[str, Any]:
        """Get histogram statistics as dictionary.

        Args:
            metric_name: Metric name

        Returns:
            Dictionary with statistics
        """
        stats = self._get_histogram_stats(metric_name)
        return {
            'count': stats.count,
            'min': stats.min,
            'max': stats.max,
            'avg': stats.avg,
            'p50': stats.p50,
            'p95': stats.p95,
            'p99': stats.p99,
        }

    def _send_to_cloudwatch(
        self,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]]
    ) -> None:
        """Send metric to CloudWatch.

        Args:
            metric_name: Metric name
            value: Metric value
            dimensions: CloudWatch dimensions
        """
        # Placeholder for CloudWatch integration
        # In production, this would use boto3 to send to CloudWatch
        if self.logger:
            self.logger.debug(
                f"CloudWatch: {metric_name}={value} "
                f"dimensions={dimensions}"
            )


__all__ = [
    "MetricsFactory",
    "MetricSnapshot",
    "TimingSnapshot",
]
