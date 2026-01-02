"""
metrics/metrics_operations.py

Version: 2025-12-11_1
Purpose: Metrics operations with debug tracing - split from metrics_core.py
Project: LEE
License: Apache 2.0

MODIFIED: Added debug calls throughout
MODIFIED: Refactored to metrics/ subdirectory
"""

from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from metrics.metrics_types import ResponseMetrics, HTTPClientMetrics, CircuitBreakerMetrics

# Import the MetricsCore class from metrics_core
from metrics.metrics_core import MetricsCore


class MetricsCoreOperations(MetricsCore):
    """Extended metrics operations with debug tracing."""

    def record_cache_metric(self, operation_name: str, hit: bool, miss: bool, duration_ms: float,
                           correlation_id: str = None, **kwargs) -> bool:
        """Record cache metric."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_cache_metric called",
                 operation_name=operation_name, hit=hit, miss=miss, duration_ms=duration_ms)

        with debug_timing(correlation_id, "METRICS", "record_cache_metric",
                         operation_name=operation_name, hit=hit, miss=miss):
            try:
                dimensions = {'operation': operation_name, 'hit': str(hit), 'miss': str(miss)}
                self.record_metric(f'cache.{operation_name}.count', 1.0, dimensions)
                if duration_ms > 0:
                    self.record_metric(f'cache.{operation_name}.duration_ms', duration_ms, dimensions)
                debug_log(correlation_id, "METRICS", "record_cache_metric completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_cache_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_api_metric(self, api_name: str, endpoint: str, success: bool, duration_ms: float,
                         status_code: Optional[int], correlation_id: str = None, **kwargs) -> bool:
        """Record API metric."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_api_metric called",
                 api_name=api_name, endpoint=endpoint, success=success, duration_ms=duration_ms,
                 has_status_code=status_code is not None)

        with debug_timing(correlation_id, "METRICS", "record_api_metric",
                         api_name=api_name, endpoint=endpoint, success=success, duration_ms=duration_ms):
            try:
                dimensions = {'api': api_name, 'endpoint': endpoint, 'success': str(success)}
                if status_code:
                    dimensions['status_code'] = str(status_code)
                self.record_metric(f'api.{api_name}.count', 1.0, dimensions)
                if duration_ms > 0:
                    self.record_metric(f'api.{api_name}.duration_ms', duration_ms, dimensions)
                debug_log(correlation_id, "METRICS", "record_api_metric completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_api_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_response_metric(self, response_type: str, success: bool, error_type: Optional[str],
                              correlation_id: str = None, **kwargs) -> bool:
        """Record response metric."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_response_metric called",
                 response_type=response_type, success=success, has_error=error_type is not None)

        with debug_timing(correlation_id, "METRICS", "record_response_metric",
                         response_type=response_type, success=success):
            try:
                dimensions = {'response_type': response_type, 'success': str(success)}
                if error_type:
                    dimensions['error_type'] = error_type
                self.record_metric('response.count', 1.0, dimensions)
                debug_log(correlation_id, "METRICS", "record_response_metric completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_response_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_http_metric(self, method: str, url: str, status_code: int, duration_ms: float,
                          response_size: int, correlation_id: str = None, **kwargs) -> bool:
        """Record HTTP metric."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_http_metric called",
                 method=method, url=url, status_code=status_code, duration_ms=duration_ms,
                 response_size=response_size)

        with debug_timing(correlation_id, "METRICS", "record_http_metric",
                         method=method, url=url, status_code=status_code, duration_ms=duration_ms):
            try:
                self._http_metrics.total_requests += 1
                if 200 <= status_code < 300:
                    self._http_metrics.successful_requests += 1
                else:
                    self._http_metrics.failed_requests += 1
                self._http_metrics.requests_by_method[method] += 1
                self._http_metrics.requests_by_status[status_code] += 1
                self._http_metrics.total_response_time_ms += duration_ms
                self._http_metrics.avg_response_time_ms = self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
                debug_log(correlation_id, "METRICS", "record_http_metric completed",
                         success=True, success_rate=self._http_metrics.avg_response_time_ms)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_http_metric failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool,
                                     correlation_id: str = None, **kwargs) -> bool:
        """Record circuit breaker event."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_circuit_breaker_event called",
                 circuit_name=circuit_name, event_type=event_type, success=success)

        with debug_timing(correlation_id, "METRICS", "record_circuit_breaker_event",
                         circuit_name=circuit_name, event_type=event_type, success=success):
            try:
                if circuit_name not in self._circuit_breaker_metrics:
                    self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics(circuit_name=circuit_name)
                metrics = self._circuit_breaker_metrics[circuit_name]
                metrics.total_calls += 1
                if success:
                    metrics.successful_calls += 1
                else:
                    metrics.failed_calls += 1
                if event_type == 'open':
                    metrics.circuit_opens += 1
                elif event_type == 'half_open':
                    metrics.half_open_attempts += 1
                debug_log(correlation_id, "METRICS", "record_circuit_breaker_event completed",
                         success=True, total_calls=metrics.total_calls)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_circuit_breaker_event failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_response_metrics(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get response metrics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_response_metrics called")

        with debug_timing(correlation_id, "METRICS", "get_response_metrics"):
            try:
                result = {
                    'total_responses': self._response_metrics.total_responses,
                    'successful_responses': self._response_metrics.successful_responses,
                    'error_responses': self._response_metrics.error_responses,
                    'success_rate': self._response_metrics.success_rate()
                }
                debug_log(correlation_id, "METRICS", "get_response_metrics completed",
                         success=True, total_responses=result['total_responses'])
                return result
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_response_metrics failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_http_metrics(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get HTTP metrics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_http_metrics called")

        with debug_timing(correlation_id, "METRICS", "get_http_metrics"):
            try:
                result = {
                    'total_requests': self._http_metrics.total_requests,
                    'successful_requests': self._http_metrics.successful_requests,
                    'failed_requests': self._http_metrics.failed_requests,
                    'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
                    'requests_by_method': dict(self._http_metrics.requests_by_method),
                    'requests_by_status': dict(self._http_metrics.requests_by_status)
                }
                debug_log(correlation_id, "METRICS", "get_http_metrics completed",
                         success=True, total_requests=result['total_requests'])
                return result
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_http_metrics failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None,
                                    correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics called",
                 has_circuit_name=circuit_name is not None)

        with debug_timing(correlation_id, "METRICS", "get_circuit_breaker_metrics"):
            try:
                if circuit_name:
                    if circuit_name in self._circuit_breaker_metrics:
                        metrics = self._circuit_breaker_metrics[circuit_name]
                        result = {
                            'circuit_name': metrics.circuit_name,
                            'total_calls': metrics.total_calls,
                            'successful_calls': metrics.successful_calls,
                            'failed_calls': metrics.failed_calls,
                            'circuit_opens': metrics.circuit_opens,
                            'half_open_attempts': metrics.half_open_attempts
                        }
                    else:
                        result = {}
                    debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics completed",
                             success=True, circuit_name=circuit_name)
                    return result
                return {name: self.get_circuit_breaker_metrics(name) for name in self._circuit_breaker_metrics.keys()}
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float,
                                correlation_id: str = None, **kwargs) -> bool:
        """Record dispatcher timing."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "record_dispatcher_timing called",
                 interface_name=interface_name, operation_name=operation_name, duration_ms=duration_ms)

        with debug_timing(correlation_id, "METRICS", "record_dispatcher_timing",
                         interface_name=interface_name, operation_name=operation_name):
            try:
                key = f"{interface_name}.{operation_name}"
                self._dispatcher_timings[key].append(duration_ms)
                self._dispatcher_call_counts[key] += 1
                debug_log(correlation_id, "METRICS", "record_dispatcher_timing completed",
                         success=True, call_count=self._dispatcher_call_counts[key])
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "record_dispatcher_timing failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_dispatcher_stats(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get dispatcher stats."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_dispatcher_stats called")

        with debug_timing(correlation_id, "METRICS", "get_dispatcher_stats"):
            try:
                stats = {}
                for key, timings in self._dispatcher_timings.items():
                    if timings:
                        stats[key] = {
                            'count': self._dispatcher_call_counts[key],
                            'avg_ms': sum(timings) / len(timings),
                            'min_ms': min(timings),
                            'max_ms': max(timings)
                        }
                debug_log(correlation_id, "METRICS", "get_dispatcher_stats completed",
                         success=True, interface_count=len(stats))
                return stats
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_dispatcher_stats failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_operation_metrics(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get operation metrics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_operation_metrics called")

        with debug_timing(correlation_id, "METRICS", "get_operation_metrics"):
            try:
                result = {op: {
                    'count': data['count'],
                    'avg_ms': data['total_ms'] / data['count'] if data['count'] > 0 else 0,
                    'total_ms': data['total_ms']
                } for op, data in self._operation_metrics.items()}
                debug_log(correlation_id, "METRICS", "get_operation_metrics completed",
                         success=True, operation_count=len(result))
                return result
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_operation_metrics failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_performance_report(self, slow_threshold_ms: float = 100.0,
                               correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get performance report."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "get_performance_report called",
                 slow_threshold_ms=slow_threshold_ms)

        with debug_timing(correlation_id, "METRICS", "get_performance_report",
                         slow_threshold_ms=slow_threshold_ms):
            try:
                from metrics.metrics_helper import calculate_percentiles
                operations = {}
                for op, data in self._operation_metrics.items():
                    if data['durations']:
                        percentiles = calculate_percentiles(data['durations'])
                        operations[op] = {
                            'count': data['count'],
                            'avg_ms': data['total_ms'] / data['count'],
                            'min_ms': min(data['durations']),
                            'max_ms': max(data['durations']),
                            'p50_ms': percentiles['p50'],
                            'p95_ms': percentiles['p95'],
                            'p99_ms': percentiles['p99']
                        }
                slow_operations = [
                    {'operation': op, 'p95_ms': metrics['p95_ms'], 'max_ms': metrics['max_ms']}
                    for op, metrics in operations.items()
                    if metrics['p95_ms'] > slow_threshold_ms
                ]
                result = {
                    'timestamp': datetime.now().isoformat(),
                    'metrics_version': '2025-12-11_1',
                    'slow_threshold_ms': slow_threshold_ms,
                    'operations': operations,
                    'slow_operations': slow_operations,
                    'slow_operation_count': len(slow_operations)
                }
                debug_log(correlation_id, "METRICS", "get_performance_report completed",
                         success=True, slow_operation_count=len(slow_operations))
                return result
            except Exception as e:
                debug_log(correlation_id, "METRICS", "get_performance_report failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def reset_metrics(self, correlation_id: str = None, **kwargs) -> bool:
        """Reset all metrics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "METRICS", "reset_metrics called")

        with debug_timing(correlation_id, "METRICS", "reset_metrics"):
            try:
                self._metrics.clear()
                self._counters.clear()
                self._gauges.clear()
                self._histograms.clear()
                self._response_metrics = ResponseMetrics()
                self._http_metrics = HTTPClientMetrics()
                self._circuit_breaker_metrics.clear()
                self._dispatcher_timings.clear()
                self._dispatcher_call_counts.clear()
                self._operation_metrics.clear()
                debug_log(correlation_id, "METRICS", "reset_metrics completed",
                         success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "METRICS", "reset_metrics failed",
                         error_type=type(e).__name__, error=str(e))
                raise


# SINGLETON instance
_MANAGER = MetricsCoreOperations()


# PUBLIC API - Interface layer uses these
def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    return _MANAGER.record_metric(name, value, dimensions, **kwargs)

def increment_counter(name: str, value: int = 1, **kwargs) -> int:
    return _MANAGER.increment_counter(name, value, **kwargs)

def get_stats(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_stats(**kwargs)

def record_operation_metric(operation_name: str, success: bool = True, duration_ms: float = 0,
                           error_type: Optional[str] = None, **kwargs) -> bool:
    return _MANAGER.record_operation_metric(operation_name, success, duration_ms, error_type, **kwargs)

def record_error_response(error_type: str, severity: str = 'medium', category: str = 'internal', **kwargs) -> bool:
    return _MANAGER.record_error_response(error_type, severity, category, **kwargs)

def record_cache_metric(operation_name: str, hit: bool = False, miss: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    return _MANAGER.record_cache_metric(operation_name, hit, miss, duration_ms, **kwargs)

def record_api_metric(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0,
                     status_code: Optional[int] = None, **kwargs) -> bool:
    return _MANAGER.record_api_metric(api_name, endpoint, success, duration_ms, status_code, **kwargs)

def record_response_metric(response_type: str, success: bool = True, error_type: Optional[str] = None, **kwargs) -> bool:
    return _MANAGER.record_response_metric(response_type, success, error_type, **kwargs)

def record_http_metric(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0, **kwargs) -> bool:
    return _MANAGER.record_http_metric(method, url, status_code, duration_ms, response_size, **kwargs)

def record_circuit_breaker_event(circuit_name: str, event_type: str, success: bool = True, **kwargs) -> bool:
    return _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success, **kwargs)

def get_response_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_response_metrics(**kwargs)

def get_http_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_http_metrics(**kwargs)

def get_circuit_breaker_metrics(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    return _MANAGER.get_circuit_breaker_metrics(circuit_name, **kwargs)

def record_dispatcher_timing(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    return _MANAGER.record_dispatcher_timing(interface_name, operation_name, duration_ms, **kwargs)

def get_dispatcher_stats(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_dispatcher_stats(**kwargs)

def get_operation_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_operation_metrics(**kwargs)

def get_performance_report(slow_threshold_ms: float = 100.0, **kwargs) -> Dict[str, Any]:
    return _MANAGER.get_performance_report(slow_threshold_ms, **kwargs)

def reset_metrics(**kwargs) -> bool:
    return _MANAGER.reset_metrics(**kwargs)


__all__ = [
    'MetricsCoreOperations',
    '_MANAGER',
    'record_metric',
    'increment_counter',
    'get_stats',
    'record_operation_metric',
    'record_error_response',
    'record_cache_metric',
    'record_api_metric',
    'record_response_metric',
    'record_http_metric',
    'record_circuit_breaker_event',
    'get_response_metrics',
    'get_http_metrics',
    'get_circuit_breaker_metrics',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_performance_report',
    'reset_metrics',
]

# EOF