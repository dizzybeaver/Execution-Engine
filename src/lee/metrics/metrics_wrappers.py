"""metrics/metrics_wrappers.py

Version: 2025-12-11_1
Purpose: Module-level wrapper functions for metrics - SUGA-ISP compliant
Project: LEE
License: Apache 2.0

SPLIT FROM: metrics_generic.py (exceeded 350-line limit)
FIXED: SUGA-ISP compliance - removed direct imports, use gateway routing
"""

from lee.metrics.metrics_generic import _get_management

# Get singleton instance
_MANAGER = _get_management()


# Module-level wrapper functions for interface compatibility
def record_operation_metric(operation_name: str, success: bool = True,
                          duration_ms: float = 0, error_type: str = None,
                          **kwargs) -> None:
    """Record an operation metric (module-level wrapper)."""
    return _MANAGER.record_operation_metric(
        operation_name=operation_name,
        success=success,
        duration_ms=duration_ms,
        error_type=error_type,
        **kwargs,
    )


def record_error_response(error_type: str, error_code: str, entity_id: str = None,
                         user_id: str = None, **kwargs) -> None:
    """Record an error response metric (module-level wrapper)."""
    return _MANAGER.record_error_response(
        error_type=error_type,
        error_code=error_code,
        entity_id=entity_id,
        user_id=user_id,
        **kwargs,
    )


def record_cache_metric(operation_name: str, hit: bool = False,
                        miss: bool = False, duration_ms: float = 0,
                        **kwargs) -> None:
    """Record a cache metric (module-level wrapper)."""
    return _MANAGER.record_cache_metric(
        operation_name=operation_name,
        hit=hit,
        miss=miss,
        duration_ms=duration_ms,
        **kwargs,
    )


def record_api_metric(api_name: str, endpoint: str, success: bool = True,
                     duration_ms: float = 0, status_code: int = None,
                     **kwargs) -> None:
    """Record an API metric (module-level wrapper)."""
    return _MANAGER.record_api_metric(
        api_name=api_name,
        endpoint=endpoint,
        success=success,
        duration_ms=duration_ms,
        status_code=status_code,
        **kwargs,
    )


def record_response_metric(response_time_ms: float, status: str = None,
                          error_code: str = None, entity_id: str = None, **kwargs) -> None:
    """Record a response metric (module-level wrapper)."""
    return _MANAGER.record_response_metric(
        response_time_ms=response_time_ms,
        status=status,
        error_code=error_code,
        entity_id=entity_id,
        **kwargs,
    )


def record_http_metric(method: str, url: str, status_code: int,
                      response_time_ms: float, **kwargs) -> None:
    """Record HTTP client metric (module-level wrapper)."""
    return _MANAGER.record_http_metric(
        method=method,
        url=url,
        status_code=status_code,
        response_time_ms=response_time_ms,
        **kwargs,
    )


def record_circuit_breaker_event(circuit_name: str, event_type: str,
                                 success: bool = True, **kwargs) -> None:
    """Record circuit breaker event (module-level wrapper)."""
    return _MANAGER.record_circuit_breaker_event(
        circuit_name=circuit_name,
        event_type=event_type,
        success=success,
        **kwargs,
    )


def get_response_metrics(**kwargs):
    """Get response metrics (module-level wrapper)."""
    return _MANAGER.get_response_metrics(**kwargs)


def get_http_metrics(**kwargs):
    """Get HTTP metrics (module-level wrapper)."""
    return _MANAGER.get_http_metrics(**kwargs)


def get_circuit_breaker_metrics(**kwargs):
    """Get circuit breaker metrics (module-level wrapper)."""
    return _MANAGER.get_circuit_breaker_metrics(**kwargs)


def record_dispatcher_timing(interface_name: str, operation_name: str,
                            duration_ms: float, **kwargs) -> None:
    """Record dispatcher timing (module-level wrapper)."""
    return _MANAGER.record_dispatcher_timing(
        interface_name=interface_name,
        operation_name=operation_name,
        duration_ms=duration_ms,
        **kwargs,
    )


def get_dispatcher_stats(**kwargs) -> dict:
    """Get dispatcher statistics (module-level wrapper)."""
    return _MANAGER.get_dispatcher_stats(**kwargs)


def get_operation_metrics(operation_name: str = None, **kwargs) -> dict:
    """Get operation metrics (module-level wrapper)."""
    return _MANAGER.get_operation_metrics(operation_name=operation_name, **kwargs)


def get_performance_report(**kwargs) -> dict:
    """Get performance report (module-level wrapper)."""
    return _MANAGER.get_performance_report(**kwargs)


def reset_metrics(**kwargs) -> None:
    """Reset all metrics (module-level wrapper)."""
    return _MANAGER.reset_metrics(**kwargs)


__all__ = [
    "get_circuit_breaker_metrics",
    "get_dispatcher_stats",
    "get_http_metrics",
    "get_operation_metrics",
    "get_performance_report",
    "get_response_metrics",
    "record_api_metric",
    "record_cache_metric",
    "record_circuit_breaker_event",
    "record_dispatcher_timing",
    "record_error_response",
    "record_http_metric",
    "record_operation_metric",
    "record_response_metric",
    "reset_metrics",
]


# EOF
