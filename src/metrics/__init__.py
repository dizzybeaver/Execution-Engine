"""
metrics/__init__.py

Version: 2025-12-11_1
Purpose: Metrics module initialization - exports public API
Project: LEE
"""

# Public API exports - interface layer uses these
from metrics.metrics_core import (
    record_metric,
    increment_counter,
    get_stats,
    record_operation_metric,
    record_error_response,
    record_cache_metric,
    record_api_metric,
    record_response_metric,
    record_http_metric,
    record_circuit_breaker_event,
    get_response_metrics,
    get_http_metrics,
    get_circuit_breaker_metrics,
    record_dispatcher_timing,
    get_dispatcher_stats,
    get_operation_metrics,
    get_performance_report,
    reset_metrics,
)

__all__ = [
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
