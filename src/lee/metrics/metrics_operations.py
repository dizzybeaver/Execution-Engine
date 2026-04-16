"""metrics/metrics_operations.py

Version: 2026-04-11_1
Purpose: Public API wrapper for metrics operations
Project: LEE
License: Apache 2.0

REFACTORED: Split into multiple files for AWS Lambda 350-line limit
- metrics_operations_core.py - Core recording operations
- metrics_operations_retrieval.py - Retrieval operations
- metrics_operations.py - Public API wrapper (this file)

REFACTORED: 2026-04-11 - Consolidated wrapper functions
- Created base _call() function to eliminate duplicate wrapper code
- Reduced from 18 wrapper functions to streamlined implementation
- Eliminated ~60 lines while maintaining full backward compatibility
"""

from typing import Any

from lee.metrics.metrics_operations_retrieval import MetricsRetrievalOperations

# SINGLETON instance
_MANAGER = MetricsRetrievalOperations()


def _call(method_name: str, *args, **kwargs):
    """Base function for calling manager methods.

    Eliminates duplicate wrapper code by providing single call-through point.
    Maintains full backward compatibility while reducing maintenance burden.
    """
    return getattr(_MANAGER, method_name)(*args, **kwargs)


# PUBLIC API - Interface layer uses these
def record_metric(
    name: str, value: float, dimensions: dict[str, str] | None = None, **kwargs
) -> bool:
    """Record a metric value with optional dimensions."""
    return _call("record_metric", name, value, dimensions, **kwargs)


def increment_counter(name: str | None = None, value: int = 1, **kwargs) -> int:
    """Increment a counter by specified value."""
    if name is None and "metric_name" in kwargs:
        name = kwargs.pop("metric_name")
    elif name is None:
        raise ValueError(
            "increment_counter requires either 'name' or 'metric_name' parameter"
        )
    return _call("increment_counter", name, value, **kwargs)


def get_stats(**kwargs) -> dict[str, Any]:
    """Get current statistics."""
    return _call("get_stats", **kwargs)


def record_operation_metric(
    operation_name: str,
    success: bool = True,
    duration_ms: float = 0,
    error_type: str | None = None,
    **kwargs,
) -> bool:
    """Record operation metric with timing and error info."""
    return _call(
        "record_operation_metric",
        operation_name,
        success,
        duration_ms,
        error_type,
        **kwargs,
    )


def record_error_response(
    error_type: str, severity: str = "medium", category: str = "internal", **kwargs
) -> bool:
    """Record error response metric."""
    return _call("record_error_response", error_type, severity, category, **kwargs)


def record_cache_metric(
    operation_name: str,
    hit: bool = False,
    miss: bool = False,
    duration_ms: float = 0,
    **kwargs,
) -> bool:
    """Record cache metric."""
    return _call(
        "record_cache_metric", operation_name, hit, miss, duration_ms, **kwargs
    )


def record_api_metric(
    api_name: str,
    endpoint: str,
    success: bool = True,
    duration_ms: float = 0,
    status_code: int | None = None,
    **kwargs,
) -> bool:
    """Record API metric."""
    return _call(
        "record_api_metric",
        api_name,
        endpoint,
        success,
        duration_ms,
        status_code,
        **kwargs,
    )


def record_response_metric(
    response_type: str, success: bool = True, error_type: str | None = None, **kwargs
) -> bool:
    """Record response metric."""
    return _call("record_response_metric", response_type, success, error_type, **kwargs)


def record_http_metric(
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    response_size: int = 0,
    **kwargs,
) -> bool:
    """Record HTTP metric."""
    return _call(
        "record_http_metric",
        method,
        url,
        status_code,
        duration_ms,
        response_size,
        **kwargs,
    )


def record_circuit_breaker_event(
    circuit_name: str, event_type: str, success: bool = True, **kwargs
) -> bool:
    """Record circuit breaker event."""
    return _call(
        "record_circuit_breaker_event", circuit_name, event_type, success, **kwargs
    )


def get_response_metrics(**kwargs) -> dict[str, Any]:
    """Get response metrics."""
    return _call("get_response_metrics", **kwargs)


def get_http_metrics(**kwargs) -> dict[str, Any]:
    """Get HTTP metrics."""
    return _call("get_http_metrics", **kwargs)


def get_circuit_breaker_metrics(
    circuit_name: str | None = None, **kwargs
) -> dict[str, Any]:
    """Get circuit breaker metrics."""
    return _call("get_circuit_breaker_metrics", circuit_name, **kwargs)


def record_dispatcher_timing(
    interface_name: str, operation_name: str, duration_ms: float, **kwargs
) -> bool:
    """Record dispatcher timing."""
    return _call(
        "record_dispatcher_timing",
        interface_name,
        operation_name,
        duration_ms,
        **kwargs,
    )


def get_dispatcher_stats(**kwargs) -> dict[str, Any]:
    """Get dispatcher statistics."""
    return _call("get_dispatcher_stats", **kwargs)


def get_operation_metrics(**kwargs) -> dict[str, Any]:
    """Get operation metrics."""
    return _call("get_operation_metrics", **kwargs)


def get_performance_report(
    slow_threshold_ms: float = 100.0, **kwargs
) -> dict[str, Any]:
    """Get performance report."""
    return _call("get_performance_report", slow_threshold_ms, **kwargs)


def reset_metrics(**kwargs) -> bool:
    """Reset all metrics."""
    return _call("reset_metrics", **kwargs)


__all__ = [
    "_MANAGER",
    "MetricsRetrievalOperations",
    "get_circuit_breaker_metrics",
    "get_dispatcher_stats",
    "get_http_metrics",
    "get_operation_metrics",
    "get_performance_report",
    "get_response_metrics",
    "get_stats",
    "increment_counter",
    "record_api_metric",
    "record_cache_metric",
    "record_circuit_breaker_event",
    "record_dispatcher_timing",
    "record_error_response",
    "record_http_metric",
    "record_metric",
    "record_operation_metric",
    "record_response_metric",
    "reset_metrics",
]


# EOF
