"""
gateway/wrappers/gateway_wrappers_metrics.py

Version: 2025-12-11_1
Purpose: METRICS interface gateway wrappers
Project: LEE
License: Apache 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation
# NEW: Add debug system for exact failure point identification
from debug import debug_log, debug_timing, generate_correlation_id


def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, correlation_id: str = None, **kwargs) -> bool:
    """Record metric value."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_metric called", name=name, value=value, has_dimensions=dimensions is not None)

    with debug_timing(correlation_id, "METRICS", "record_metric", name=name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record', name=name, value=value, dimensions=dimensions, **kwargs)
            debug_log(correlation_id, "METRICS", "record_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def increment_counter(name: str, value: int = 1, correlation_id: str = None, **kwargs) -> int:
    """Increment counter."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "increment_counter called", name=name, value=value)

    with debug_timing(correlation_id, "METRICS", "increment_counter", name=name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'increment', name=name, value=value, **kwargs)
            debug_log(correlation_id, "METRICS", "increment_counter completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "increment_counter failed", error_type=type(e).__name__, error=str(e))
            raise


def get_metrics_stats(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get metrics statistics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_metrics_stats called")

    with debug_timing(correlation_id, "METRICS", "get_metrics_stats"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_stats', **kwargs)
            debug_log(correlation_id, "METRICS", "get_metrics_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_metrics_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def record_operation_metric(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, correlation_id: str = None, **kwargs) -> bool:
    """Record operation metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_operation_metric called", operation_name=operation_name, success=success, duration_ms=duration_ms)

    with debug_timing(correlation_id, "METRICS", "record_operation_metric", operation_name=operation_name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_operation', operation_name=operation_name, success=success, duration_ms=duration_ms, error_type=error_type, **kwargs)
            debug_log(correlation_id, "METRICS", "record_operation_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_operation_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_error_metric(error_type: str, severity: str = 'medium', category: str = 'internal', correlation_id: str = None, **kwargs) -> bool:
    """Record error metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_error_metric called", error_type=error_type, severity=severity, category=category)

    with debug_timing(correlation_id, "METRICS", "record_error_metric", error_type=error_type):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, severity=severity, category=category, **kwargs)
            debug_log(correlation_id, "METRICS", "record_error_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_error_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_cache_metric(operation_name: str, hit: bool = False, miss: bool = False, duration_ms: float = 0, correlation_id: str = None, **kwargs) -> bool:
    """Record cache metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_cache_metric called", operation_name=operation_name, hit=hit, miss=miss, duration_ms=duration_ms)

    with debug_timing(correlation_id, "METRICS", "record_cache_metric", operation_name=operation_name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_cache', operation_name=operation_name, hit=hit, miss=miss, duration_ms=duration_ms, **kwargs)
            debug_log(correlation_id, "METRICS", "record_cache_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_cache_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_api_metric(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0, status_code: Optional[int] = None, correlation_id: str = None, **kwargs) -> bool:
    """Record API metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_api_metric called", api_name=api_name, success=success, duration_ms=duration_ms)

    with debug_timing(correlation_id, "METRICS", "record_api_metric", api_name=api_name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_api', api_name=api_name, endpoint=endpoint, success=success, duration_ms=duration_ms, status_code=status_code, **kwargs)
            debug_log(correlation_id, "METRICS", "record_api_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_api_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_response_metric(response_type: str, success: bool = True, error_type: Optional[str] = None, correlation_id: str = None, **kwargs) -> bool:
    """Record response metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_response_metric called", response_type=response_type, success=success)

    with debug_timing(correlation_id, "METRICS", "record_response_metric", response_type=response_type):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_response', response_type=response_type, success=success, error_type=error_type, **kwargs)
            debug_log(correlation_id, "METRICS", "record_response_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_response_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_http_metric(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0, correlation_id: str = None, **kwargs) -> bool:
    """Record HTTP metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_http_metric called", method=method, status_code=status_code, duration_ms=duration_ms)

    with debug_timing(correlation_id, "METRICS", "record_http_metric", method=method):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_http', method=method, url=url, status_code=status_code, duration_ms=duration_ms, response_size=response_size, **kwargs)
            debug_log(correlation_id, "METRICS", "record_http_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_http_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def record_circuit_breaker_metric(circuit_name: str, event_type: str, success: bool = True, correlation_id: str = None, **kwargs) -> bool:
    """Record circuit breaker metric."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_circuit_breaker_metric called", circuit_name=circuit_name, event_type=event_type, success=success)

    with debug_timing(correlation_id, "METRICS", "record_circuit_breaker_metric", circuit_name=circuit_name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_circuit_breaker', circuit_name=circuit_name, event_type=event_type, success=success, **kwargs)
            debug_log(correlation_id, "METRICS", "record_circuit_breaker_metric completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_circuit_breaker_metric failed", error_type=type(e).__name__, error=str(e))
            raise


def get_response_metrics(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get response metrics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_response_metrics called")

    with debug_timing(correlation_id, "METRICS", "get_response_metrics"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_response_metrics', **kwargs)
            debug_log(correlation_id, "METRICS", "get_response_metrics completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_response_metrics failed", error_type=type(e).__name__, error=str(e))
            raise


def get_http_metrics(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get HTTP metrics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_http_metrics called")

    with debug_timing(correlation_id, "METRICS", "get_http_metrics"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_http_metrics', **kwargs)
            debug_log(correlation_id, "METRICS", "get_http_metrics completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_http_metrics failed", error_type=type(e).__name__, error=str(e))
            raise


def get_circuit_breaker_metrics(circuit_name: Optional[str] = None, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get circuit breaker metrics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics called", circuit_name=circuit_name)

    with debug_timing(correlation_id, "METRICS", "get_circuit_breaker_metrics"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_circuit_breaker_metrics', circuit_name=circuit_name, **kwargs)
            debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_circuit_breaker_metrics failed", error_type=type(e).__name__, error=str(e))
            raise


def record_dispatcher_timing(interface_name: str, operation_name: str, duration_ms: float, correlation_id: str = None, **kwargs) -> bool:
    """Record dispatcher timing."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "record_dispatcher_timing called", interface_name=interface_name, operation_name=operation_name, duration_ms=duration_ms)

    with debug_timing(correlation_id, "METRICS", "record_dispatcher_timing", interface_name=interface_name):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'record_dispatcher_timing', interface_name=interface_name, operation_name=operation_name, duration_ms=duration_ms, **kwargs)
            debug_log(correlation_id, "METRICS", "record_dispatcher_timing completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "record_dispatcher_timing failed", error_type=type(e).__name__, error=str(e))
            raise


def get_dispatcher_stats(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get dispatcher stats."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_dispatcher_stats called")

    with debug_timing(correlation_id, "METRICS", "get_dispatcher_stats"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_dispatcher_stats', **kwargs)
            debug_log(correlation_id, "METRICS", "get_dispatcher_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_dispatcher_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def get_operation_metrics(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get operation metrics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_operation_metrics called")

    with debug_timing(correlation_id, "METRICS", "get_operation_metrics"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_operation_metrics', **kwargs)
            debug_log(correlation_id, "METRICS", "get_operation_metrics completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_operation_metrics failed", error_type=type(e).__name__, error=str(e))
            raise


def get_performance_report(slow_threshold_ms: float = 100.0, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "get_performance_report called", slow_threshold_ms=slow_threshold_ms)

    with debug_timing(correlation_id, "METRICS", "get_performance_report"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'get_performance_report', slow_threshold_ms=slow_threshold_ms, **kwargs)
            debug_log(correlation_id, "METRICS", "get_performance_report completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "get_performance_report failed", error_type=type(e).__name__, error=str(e))
            raise


def reset_metrics(correlation_id: str = None, **kwargs) -> bool:
    """Reset all metrics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "METRICS", "reset_metrics called")

    with debug_timing(correlation_id, "METRICS", "reset_metrics"):
        try:
            result = execute_operation(GatewayInterface.METRICS, 'reset', **kwargs)
            debug_log(correlation_id, "METRICS", "reset_metrics completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "METRICS", "reset_metrics failed", error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'record_response_metric',
    'record_http_metric',
    'record_circuit_breaker_metric',
    'get_response_metrics',
    'get_http_metrics',
    'get_circuit_breaker_metrics',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_performance_report',
    'reset_metrics',
]
