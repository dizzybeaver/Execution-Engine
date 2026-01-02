"""
metrics/metrics_core.py

Version: 2025-12-11_1
Purpose: Core metrics implementation with debug integration
Project: LEE
License: Apache 2.0

MODIFIED: Added debug calls throughout
MODIFIED: Refactored to metrics/ subdirectory
"""

from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from metrics.metrics_types import ResponseMetrics, HTTPClientMetrics, CircuitBreakerMetrics


class MetricsCore:
    """Core metrics manager - singleton."""

    def __init__(self, correlation_id: str = None, **kwargs):
        # NEW: Add debug tracing for exact failure point identification
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "MetricsCore.__init__ called")

        with debug_timing(correlation_id, "METRICS", "MetricsCore.__init__"):
            try:
                self._metrics = defaultdict(float)
                self._counters = defaultdict(int)
                self._gauges = defaultdict(float)
                self._histograms = defaultdict(list)
                self._response_metrics = ResponseMetrics()
                self._http_metrics = HTTPClientMetrics()
                self._circuit_breaker_metrics = {}
                self._dispatcher_timings = defaultdict(list)
                self._dispatcher_call_counts = defaultdict(int)
                self._operation_metrics = defaultdict(lambda: {'count': 0, 'total_ms': 0, 'durations': []})

                debug_log(correlation_id, "METRICS", "MetricsCore.__init__ completed", success=True)
            except Exception as e:
                debug_log(correlation_id, "METRICS", "MetricsCore.__init__ failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None,
                     correlation_id: str = None, **kwargs) -> bool:
        """Record metric value."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_metric called",
                 name=name, value=value, has_dimensions=dimensions is not None)

        with debug_timing(correlation_id, "METRICS", "record_metric",
                         name=name, value=value, has_dimensions=dimensions is not None):
            try:
                # FIXED: Add validation for LOW-001
                from gateway import validate_string, validate_number_range, validate_data_structure

                validate_string(name, min_length=1, max_length=200, name="metric name")
                validate_number_range(value, min_val=-1e20, max_val=1e20, name="metric value")

                if dimensions is not None:
                    validate_data_structure(dimensions, dict, "dimensions")
                    # Validate dimension keys and values
                    for key, val in dimensions.items():
                        validate_string(key, min_length=1, max_length=100, name="dimension key")
                        validate_string(val, min_length=0, max_length=200, name="dimension value")

                key = self._build_metric_key(name, dimensions)
                self._metrics[key] = value
                debug_log(correlation_id, "METRICS", "record_metric completed",
                         success=True, metric_key=key)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def increment_counter(self, name: str, value: int = 1, correlation_id: str = None, **kwargs) -> int:
        """Increment counter."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "increment_counter called",
                 name=name, value=value)

        with debug_timing(correlation_id, "METRICS", "increment_counter",
                         name=name, value=value):
            try:
                self._counters[name] += value
                result = self._counters[name]
                debug_log(correlation_id, "METRICS", "increment_counter completed",
                         success=True, new_count=result)
                return result
            except Exception as e:
                debug_log(correlation_id, "METRICS", "increment_counter failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_stats(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get all statistics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_stats called")

        with debug_timing(correlation_id, "METRICS", "get_stats"):
            try:
                stats = {
                    'metrics': dict(self._metrics),
                    'counters': dict(self._counters),
                    'gauges': dict(self._gauges),
                    'histograms': {k: list(v) for k, v in self._histograms.items()}
                }

                debug_log(correlation_id, "METRICS", "get_stats completed",
                         success=True, metrics_count=len(stats['metrics']),
                         counters_count=len(stats['counters']))
                return stats
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_stats failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_operation_metric(self, operation_name: str, success: bool, duration_ms: float,
                               error_type: Optional[str], correlation_id: str = None, **kwargs) -> bool:
        """Record operation metric."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_operation_metric called",
                 operation_name=operation_name, success=success, duration_ms=duration_ms,
                 has_error=error_type is not None)

        with debug_timing(correlation_id, "METRICS", "record_operation_metric",
                         operation_name=operation_name, success=success, duration_ms=duration_ms):
            try:
                dimensions = {'operation': operation_name, 'success': str(success)}
                if error_type:
                    dimensions['error_type'] = error_type
                self.record_metric(f'operation.{operation_name}.count', 1.0, dimensions)
                if duration_ms > 0:
                    self.record_metric(f'operation.{operation_name}.duration_ms', duration_ms, dimensions)
                    op_key = operation_name
                    self._operation_metrics[op_key]['count'] += 1
                    self._operation_metrics[op_key]['total_ms'] += duration_ms
                    self._operation_metrics[op_key]['durations'].append(duration_ms)
                debug_log(correlation_id, "METRICS", "record_operation_metric completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_operation_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_error_response(self, error_type: str, severity: str, category: str,
                             correlation_id: str = None, **kwargs) -> bool:
        """Record error response."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_error_response called",
                 error_type=error_type, severity=severity, category=category)

        with debug_timing(correlation_id, "METRICS", "record_error_response",
                         error_type=error_type, severity=severity, category=category):
            try:
                dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
                self.record_metric('error.response.count', 1.0, dimensions)
                debug_log(correlation_id, "METRICS", "record_error_response completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_error_response failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str:
        """Build metric key from name and dimensions."""
        if not dimensions:
            return name
        dim_str = ','.join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dim_str}]"


# SINGLETON instance
_MANAGER = MetricsCore()


__all__ = [
    'MetricsCore',
    '_MANAGER',
]

# EOF