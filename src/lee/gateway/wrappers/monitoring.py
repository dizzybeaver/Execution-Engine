"""Monitoring Wrapper Functions

Direct access to monitoring and health check operations (5 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import monitoring

    # Perform health check
    health = monitoring.health_check()

    # Get system metrics
    metrics = monitoring.get_system_metrics()

    # Check alerts
    alerts = monitoring.check_alerts()
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def monitoring_health_check(**kwargs: Any) -> dict[str, Any]:
    """Perform system health check.

    Args:
        **kwargs: Additional options

    Returns:
        Health check result with status and details
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'health_check', **kwargs)


def monitoring_record_health_check(source: str, status: str, **kwargs: Any) -> dict[str, Any]:
    """Record health check result.

    Args:
        source: Source of health check
        status: Health status
        **kwargs: Additional options

    Returns:
        Recording confirmation
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'record_health_check', source=source, status=status, **kwargs)


def monitoring_get_system_metrics(**kwargs: Any) -> dict[str, Any]:
    """Get system performance metrics.

    Args:
        **kwargs: Additional options

    Returns:
        System metrics dictionary
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'get_system_metrics', **kwargs)


def monitoring_check_alerts(**kwargs: Any) -> list[dict[str, Any]]:
    """Check and trigger alerts.

    Args:
        **kwargs: Additional options (filters, etc.)

    Returns:
        List of active alerts
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'check_alerts', **kwargs)


def monitoring_get_alerts(**kwargs: Any) -> list[dict[str, Any]]:
    """Get all or filtered alerts.

    Args:
        **kwargs: Additional options (severity, component, etc.)

    Returns:
        List of alerts
    """
    return execute_operation(GatewayInterface.OBSERVABILITY, 'get_alerts', **kwargs)


# Convenience aliases
health_check = monitoring_health_check
record_health_check = monitoring_record_health_check
get_system_metrics = monitoring_get_system_metrics
check_alerts = monitoring_check_alerts
get_alerts = monitoring_get_alerts


__all__ = [
    'monitoring_health_check',
    'monitoring_record_health_check',
    'monitoring_get_system_metrics',
    'monitoring_check_alerts',
    'monitoring_get_alerts',
    # Convenience aliases
    'health_check',
    'record_health_check',
    'get_system_metrics',
    'check_alerts',
    'get_alerts',
]
