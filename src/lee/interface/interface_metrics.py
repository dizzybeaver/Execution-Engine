# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_metrics.py

Version: 2026-04-11_2
Purpose: Metrics interface router (BaseSimpleDispatchRouter pattern)
Project: LEE
License: Apache 2.0

CHANGES (2026-04-11_2):
- Refactored to use @graceful_import decorator
- Simplified import protection code
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.metrics')
def _import_metrics():
    from lee.metrics import (
        get_circuit_breaker_metrics,
        get_dispatcher_stats,
        get_http_metrics,
        get_operation_metrics,
        get_performance_report,
        get_response_metrics,
        get_stats,
        increment_counter,
        record_api_metric,
        record_cache_metric,
        record_circuit_breaker_event,
        record_dispatcher_timing,
        record_error_response,
        record_http_metric,
        record_metric,
        record_operation_metric,
        record_response_metric,
        reset_metrics,
    )
    return {
        'get_circuit_breaker_metrics': get_circuit_breaker_metrics,
        'get_dispatcher_stats': get_dispatcher_stats,
        'get_http_metrics': get_http_metrics,
        'get_operation_metrics': get_operation_metrics,
        'get_performance_report': get_performance_report,
        'get_response_metrics': get_response_metrics,
        'get_stats': get_stats,
        'increment_counter': increment_counter,
        'record_api_metric': record_api_metric,
        'record_cache_metric': record_cache_metric,
        'record_circuit_breaker_event': record_circuit_breaker_event,
        'record_dispatcher_timing': record_dispatcher_timing,
        'record_error_response': record_error_response,
        'record_http_metric': record_http_metric,
        'record_metric': record_metric,
        'record_operation_metric': record_operation_metric,
        'record_response_metric': record_response_metric,
        'reset_metrics': reset_metrics,
    }


_metrics_funcs = _import_metrics()
_METRICS_AVAILABLE = _import_metrics.__dict__.get('_METRICS_AVAILABLE', False)

if _METRICS_AVAILABLE:
    get_circuit_breaker_metrics = _metrics_funcs['get_circuit_breaker_metrics']
    get_dispatcher_stats = _metrics_funcs['get_dispatcher_stats']
    get_http_metrics = _metrics_funcs['get_http_metrics']
    get_operation_metrics = _metrics_funcs['get_operation_metrics']
    get_performance_report = _metrics_funcs['get_performance_report']
    get_response_metrics = _metrics_funcs['get_response_metrics']
    get_stats = _metrics_funcs['get_stats']
    increment_counter = _metrics_funcs['increment_counter']
    record_api_metric = _metrics_funcs['record_api_metric']
    record_cache_metric = _metrics_funcs['record_cache_metric']
    record_circuit_breaker_event = _metrics_funcs['record_circuit_breaker_event']
    record_dispatcher_timing = _metrics_funcs['record_dispatcher_timing']
    record_error_response = _metrics_funcs['record_error_response']
    record_http_metric = _metrics_funcs['record_http_metric']
    record_metric = _metrics_funcs['record_metric']
    record_operation_metric = _metrics_funcs['record_operation_metric']
    record_response_metric = _metrics_funcs['record_response_metric']
    reset_metrics = _metrics_funcs['reset_metrics']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        return {"success": False, "error": "Metrics interface unavailable"}

    get_circuit_breaker_metrics = _stub_unavailable
    get_dispatcher_stats = _stub_unavailable
    get_http_metrics = _stub_unavailable
    get_operation_metrics = _stub_unavailable
    get_performance_report = _stub_unavailable
    get_response_metrics = _stub_unavailable
    get_stats = _stub_unavailable
    increment_counter = _stub_unavailable
    record_api_metric = _stub_unavailable
    record_cache_metric = _stub_unavailable
    record_circuit_breaker_event = _stub_unavailable
    record_dispatcher_timing = _stub_unavailable
    record_error_response = _stub_unavailable
    record_http_metric = _stub_unavailable
    record_metric = _stub_unavailable
    record_operation_metric = _stub_unavailable
    record_response_metric = _stub_unavailable
    reset_metrics = _stub_unavailable


# Dispatch dictionary for O(1) operation routing
_METRICS_DISPATCH = {
    "record": record_metric,
    "record_metric": record_metric,
    "increment": increment_counter,
    "increment_counter": increment_counter,
    "get_stats": get_stats,
    "record_operation": record_operation_metric,
    "record_operation_metric": record_operation_metric,
    "record_error": record_error_response,
    "record_error_response": record_error_response,
    "record_cache": record_cache_metric,
    "record_cache_metric": record_cache_metric,
    "record_api": record_api_metric,
    "record_api_metric": record_api_metric,
    "record_response": record_response_metric,
    "record_response_metric": record_response_metric,
    "record_http": record_http_metric,
    "record_http_metric": record_http_metric,
    "record_circuit_breaker": record_circuit_breaker_event,
    "record_circuit_breaker_metric": record_circuit_breaker_event,
    "get_response_metrics": get_response_metrics,
    "get_http_metrics": get_http_metrics,
    "get_circuit_breaker_metrics": get_circuit_breaker_metrics,
    "record_dispatcher_timing": record_dispatcher_timing,
    "get_dispatcher_stats": get_dispatcher_stats,
    "get_dispatcher_metrics": get_dispatcher_stats,
    "get_operation_metrics": get_operation_metrics,
    "get_performance_report": get_performance_report,
    "reset": reset_metrics,
    "reset_metrics": reset_metrics,
}


class _MetricsRouter(BaseSimpleDispatchRouter):
    """Router for Metrics interface operations.

    This router handles all metrics recording and retrieval operations
    including counters, timers, circuit breaker metrics, and performance reports.
    """

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Metrics",
            core_module=DummyModule(),
            dispatch_map=_METRICS_DISPATCH
        )


_metrics_router = _MetricsRouter()


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """Execute metrics operation via dispatch.

    Args:
        operation: The metrics operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from metrics implementation
    """
    return _metrics_router.execute(operation, **kwargs)


def list_metrics_operations() -> list[str]:
    """List all available metrics operations."""
    return list(_metrics_router.dispatch_map.keys())


__all__ = [
    "execute_metrics_operation",
    "list_metrics_operations",
    "_METRICS_AVAILABLE"
]
