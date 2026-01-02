"""
interface_metrics.py

Version: 2025-12-11_1
Purpose: Metrics interface router (SUGA pattern)
Project: LEE
License: Apache 2.0

MODIFIED: Refactored to use metrics module
"""

from typing import Any, Dict, Optional


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Execute metrics operation via SUGA pattern.
    
    Pattern: Interface → Core (lazy import)
    
    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: Unknown operation
    """
    import metrics
    
    DISPATCH = {
        'record': metrics.record_metric,
        'record_metric': metrics.record_metric,
        'increment': metrics.increment_counter,
        'increment_counter': metrics.increment_counter,
        'get_stats': metrics.get_stats,
        'record_operation': metrics.record_operation_metric,
        'record_operation_metric': metrics.record_operation_metric,
        'record_error': metrics.record_error_response,
        'record_error_response': metrics.record_error_response,
        'record_cache': metrics.record_cache_metric,
        'record_cache_metric': metrics.record_cache_metric,
        'record_api': metrics.record_api_metric,
        'record_api_metric': metrics.record_api_metric,
        'record_response': metrics.record_response_metric,
        'record_response_metric': metrics.record_response_metric,
        'record_http': metrics.record_http_metric,
        'record_http_metric': metrics.record_http_metric,
        'record_circuit_breaker': metrics.record_circuit_breaker_event,
        'record_circuit_breaker_metric': metrics.record_circuit_breaker_event,
        'get_response_metrics': metrics.get_response_metrics,
        'get_http_metrics': metrics.get_http_metrics,
        'get_circuit_breaker_metrics': metrics.get_circuit_breaker_metrics,
        'record_dispatcher_timing': metrics.record_dispatcher_timing,
        'get_dispatcher_stats': metrics.get_dispatcher_stats,
        'get_dispatcher_metrics': metrics.get_dispatcher_stats,
        'get_operation_metrics': metrics.get_operation_metrics,
        'get_performance_report': metrics.get_performance_report,
        'reset': metrics.reset_metrics,
        'reset_metrics': metrics.reset_metrics,
    }
    
    handler = DISPATCH.get(operation)
    if not handler:
        raise ValueError(
            f"Unknown metrics operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(set(DISPATCH.keys())))}"
        )
    
    return handler(**kwargs)


__all__ = ['execute_metrics_operation']
