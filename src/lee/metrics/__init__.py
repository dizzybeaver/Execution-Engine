"""metrics/__init__.py

Version: 2025-12-11_1
Purpose: Metrics module initialization - exports public API with lazy imports
Project: LEE

Cycle 8: Lazy imports to break circular dependency
"""

# Public API exports - interface layer uses these
# Lazy imports via __getattr__ to break circular dependency
_metrics_operations_module = None

def _get_metrics_operations():  # pylint: disable=global-statement
    """Lazy load metrics_operations module to break circular dependency."""
    global _metrics_operations_module
    if _metrics_operations_module is None:
        from lee.metrics import metrics_operations  # pylint: disable=import-outside-toplevel
        _metrics_operations_module = metrics_operations
    return _metrics_operations_module

def __getattr__(name: str):  # pylint: disable=undefined-all-variable
    """Lazy import metrics operations to break circular dependency.

    This function is called when an attribute is accessed but not found.
    It lazily imports from metrics_operations module on first access.
    """
    if name in [
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
    ]:
        module = _get_metrics_operations()
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
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
