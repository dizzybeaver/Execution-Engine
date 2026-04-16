"""Metrics Wrapper Functions

Direct access to metrics operations (5 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import metrics

    # Record metric
    metrics.record_metric(name='operation.duration', value=123.45)

    # Increment counter
    metrics.increment_counter(name='api.calls', value=1)

    # Record timing
    metrics.record_timing(name='database.query', duration_ms=45.6)
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def metrics_record_metric(name: str, value: float, **kwargs: Any) -> None:
    """Record a metric value.

    Args:
        name: Metric name
        value: Metric value
        **kwargs: Additional options (dimensions, unit, etc.)
    """
    execute_operation(GatewayInterface.OBSERVABILITY, 'record_metric', name=name, value=value, **kwargs)


def metrics_increment_counter(name: str, value: int = 1, **kwargs: Any) -> None:
    """Increment a counter metric.

    Args:
        name: Counter name
        value: Increment amount (default: 1)
        **kwargs: Additional options (dimensions, etc.)
    """
    execute_operation(GatewayInterface.OBSERVABILITY, 'increment_counter', name=name, value=value, **kwargs)


def metrics_record_timing(name: str, duration_ms: float, **kwargs: Any) -> None:
    """Record a timing metric.

    Args:
        name: Timing metric name
        duration_ms: Duration in milliseconds
        **kwargs: Additional options (dimensions, etc.)
    """
    execute_operation(GatewayInterface.OBSERVABILITY, 'record_timing', name=name, duration_ms=duration_ms, **kwargs)


def metrics_get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get metrics statistics.

    Args:
        **kwargs: Additional options

    Returns:
        Statistics dictionary
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'get_stats', **kwargs)


def metrics_reset(**kwargs: Any) -> None:
    """Reset all metrics.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.OBSERVABILITY, 'reset', **kwargs)


# Convenience aliases without metrics_ prefix
record_metric = metrics_record_metric
increment_counter = metrics_increment_counter
record_timing = metrics_record_timing
get_stats = metrics_get_stats
reset = metrics_reset


__all__ = [
    'metrics_record_metric',
    'metrics_increment_counter',
    'metrics_record_timing',
    'metrics_get_stats',
    'metrics_reset',
    # Convenience aliases
    'record_metric',
    'increment_counter',
    'record_timing',
    'get_stats',
    'reset',
]
