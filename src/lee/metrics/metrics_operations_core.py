"""metrics/metrics_operations_core.py

Version: 2025-12-23_2
Purpose: Core metrics recording operations with SUGA-ISP compliant debug tracing
Project: LEE
License: Apache 2.0

SPLIT FROM: metrics_operations.py (>350 lines)
CONTAINS: Metrics recording operations (record_* functions)

REFACTOR: Eliminated 360 lines of duplicate code (60 lines repeated 6 times)
by extracting common debug tracing/error handling pattern into _with_debug_tracing decorator.
"""

from contextlib import nullcontext
from functools import wraps
from typing import TypeVar, Optional
from collections.abc import Callable

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.metrics.metrics_generic import MetricsCore
from lee.metrics.metrics_types import (
    CircuitBreakerMetrics,
    HTTPClientMetrics,
    ResponseMetrics,
)

T = TypeVar('T')


def _with_debug_tracing(operation_name: str) -> Callable:
    """Decorator to add debug tracing and error handling to metrics operations.

    This eliminates 360 lines of duplicate code (60 lines repeated 6 times).

    Args:
        operation_name: Name of the metric operation being traced

    Returns:
        Decorated function with debug tracing, timing, and error handling
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            # Get or generate correlation ID
            correlation_id = kwargs.get('correlation_id')
            if correlation_id is None:
                correlation_id = generate_correlation_id("met")
                kwargs['correlation_id'] = correlation_id

            # Log operation entry with function-specific context
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="METRICS",
                                 message=f"{operation_name} called")
            except ImportError:
                pass  # Optional dependency

            # Set up timing context
            try:
                timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                             corr_id=correlation_id, scope="METRICS",
                                             operation_name=operation_name)
            except ImportError:
                timing_ctx = nullcontext()

            with timing_ctx:
                try:
                    # Call the actual function
                    result = func(self, *args, **kwargs)

                    # Log success
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="METRICS",
                                         message=f"{operation_name} completed", success=True)
                    except ImportError:
                        pass

                    return result

                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    # Expected error types - log and re-raise
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="METRICS",
                                         message=f"{operation_name} failed",
                                         error_type=type(e).__name__, error=str(e))
                    except ImportError:
                        pass
                    raise

                except Exception as e:
                    # Unexpected error - log and re-raise
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="METRICS",
                                         message=f"{operation_name} failed with unexpected error",
                                         error_type=type(e).__name__, error=str(e))
                    except ImportError:
                        pass
                    raise

        return wrapper
    return decorator


class MetricsCoreOperations(MetricsCore):
    """Extended metrics operations with debug tracing."""

    @_with_debug_tracing("record_cache_metric")
    def record_cache_metric(self, operation_name: str, hit: bool, miss: bool, duration_ms: float,
                           correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record cache metric."""
        dimensions = {"operation": operation_name, "hit": str(hit), "miss": str(miss)}
        self.record_metric(f"cache.{operation_name}.count", 1.0, dimensions)
        if duration_ms > 0:
            self.record_metric(f"cache.{operation_name}.duration_ms", duration_ms, dimensions)
        return True

    @_with_debug_tracing("record_api_metric")
    def record_api_metric(self, api_name: str, endpoint: str, success: bool, duration_ms: float,
                         status_code: Optional[int], correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record API metric."""
        dimensions = {"api": api_name, "endpoint": endpoint, "success": str(success)}
        if status_code:
            dimensions["status_code"] = str(status_code)
        self.record_metric(f"api.{api_name}.count", 1.0, dimensions)
        if duration_ms > 0:
            self.record_metric(f"api.{api_name}.duration_ms", duration_ms, dimensions)
        return True

    @_with_debug_tracing("record_response_metric")
    def record_response_metric(self, response_type: str, success: bool, error_type: Optional[str],
                              correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record response metric."""
        dimensions = {"response_type": response_type, "success": str(success)}
        if error_type:
            dimensions["error_type"] = error_type
        self.record_metric("response.count", 1.0, dimensions)
        return True

    @_with_debug_tracing("record_http_metric")
    def record_http_metric(self, method: str, url: str, status_code: int, duration_ms: float,
                          response_size: int, correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record HTTP metric."""
        self._http_metrics.total_requests += 1
        if 200 <= status_code < 300:
            self._http_metrics.successful_requests += 1
        else:
            self._http_metrics.failed_requests += 1
        self._http_metrics.requests_by_method[method] += 1
        self._http_metrics.requests_by_status[status_code] += 1
        self._http_metrics.total_response_time_ms += duration_ms
        self._http_metrics.avg_response_time_ms = self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
        return True

    @_with_debug_tracing("record_circuit_breaker_event")
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool,
                                     correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record circuit breaker event."""
        if circuit_name not in self._circuit_breaker_metrics:
            self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics(circuit_name=circuit_name)
        metrics = self._circuit_breaker_metrics[circuit_name]
        metrics.total_calls += 1
        if success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
        if event_type == "open":
            metrics.circuit_opens += 1
        elif event_type == "half_open":
            metrics.half_open_attempts += 1
        return True

    @_with_debug_tracing("record_dispatcher_timing")
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float,
                                correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Record dispatcher timing."""
        key = f"{interface_name}.{operation_name}"
        self._dispatcher_timings[key].append(duration_ms)
        self._dispatcher_call_counts[key] += 1
        return True

    @_with_debug_tracing("reset_metrics")
    def reset_metrics(self, correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=W0613
        """Reset all metrics."""
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
        return True


__all__ = [
    "MetricsCoreOperations",
]
