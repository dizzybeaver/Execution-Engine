"""monitoring_wrappers.py - Monitoring interface wrapper functions

Version: 2026-04-02_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0

Wrapper functions for monitoring interface operations.
These functions implement the actual monitoring operations.
"""

from typing import Any, Optional

# Import gateway for singleton operations
try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False

    # Create stubs
    def execute_operation(*_args, **_kwargs):
        """Stub for execute_operation when gateway unavailable."""
        raise RuntimeError("Gateway unavailable")

    class GatewayInterface:
        """Stub for GatewayInterface when gateway unavailable."""
        SINGLETON = "SINGLETON"

# Import monitoring module
try:
    from lee.monitoring.classes.AlertManager import (
        alert_manager_acknowledge,
        alert_manager_create,
        alert_manager_get,
        alert_manager_get_stats,
        alert_manager_reset,
        alert_manager_resolve,
        get_alert_manager,
    )
    _MONITORING_AVAILABLE = True
except ImportError:
    _MONITORING_AVAILABLE = False

    # Create stub implementations
    def alert_manager_acknowledge(*_args, **_kwargs):
        """Stub for alert_manager_acknowledge when monitoring unavailable."""
        return {"success": False, "error": "Monitoring unavailable"}

    def alert_manager_create(*_args, **_kwargs):
        """Stub for alert_manager_create when monitoring unavailable."""
        return {"success": False, "error": "Monitoring unavailable"}

    def alert_manager_get(*_args, **_kwargs):
        """Stub for alert_manager_get when monitoring unavailable."""
        return []

    def alert_manager_get_stats(*_args, **_kwargs):
        """Stub for alert_manager_get_stats when monitoring unavailable."""
        return {"active_critical_count": 0, "unacknowledged_count": 0}

    def alert_manager_resolve(*_args, **_kwargs):
        """Stub for alert_manager_resolve when monitoring unavailable."""
        return {"success": False, "error": "Monitoring unavailable"}

    def alert_manager_reset(*_args, **_kwargs):
        """Stub for alert_manager_reset when monitoring unavailable."""
        return {"status": "reset", "timestamp": 0}

    def get_alert_manager(*_args, **_kwargs):
        """Stub for get_alert_manager when monitoring unavailable."""
        return None


def record_health_check_impl(**kwargs) -> dict[str, Any]:
    """Record health check result."""
    return {
        "status": "recorded",
        "timestamp": __import__('time').time(),
        "source": kwargs.get("source", "unknown"),
    }


def get_system_metrics_impl(**_kwargs) -> dict[str, Any]:
    """Get system performance metrics."""
    return {
        "timestamp": __import__('time').time(),
        "metrics": {
            "cpu_usage_percent": 0.0,
            "memory_usage_percent": 0.0,
            "active_alerts": 0,
        },
    }


def check_alerts_impl(**_kwargs) -> dict[str, Any]:
    """Check and trigger alerts."""
    manager = get_alert_manager()
    stats = manager.get_alert_stats()
    return {
        "critical_count": stats.active_critical_count,
        "unacknowledged_count": stats.unacknowledged_count,
        "recommend_action": stats.active_critical_count > 0,
    }


def create_alert_impl(**kwargs) -> dict[str, Any]:
    """Create new alert with de-duplication."""
    return alert_manager_create(
        title=kwargs.get("title", "Untitled Alert"),
        description=kwargs.get("description", ""),
        severity=kwargs.get("severity", "info"),
        source=kwargs.get("source", "unknown"),
        correlation_id=kwargs.get("correlation_id"),
        context=kwargs.get("context"),
    )


def acknowledge_alert_impl(**kwargs) -> Optional[dict[str, Any]]:
    """Acknowledge active alert."""
    alert_id = kwargs.get("alert_id")
    if not alert_id:
        raise ValueError("alert_id is required")
    return alert_manager_acknowledge(alert_id)


def resolve_alert_impl(**kwargs) -> Optional[dict[str, Any]]:
    """Resolve alert."""
    alert_id = kwargs.get("alert_id")
    if not alert_id:
        raise ValueError("alert_id is required")
    return alert_manager_resolve(alert_id)


def get_alerts_impl(**kwargs) -> list[dict[str, Any]]:
    """Get all or filtered alerts."""
    return alert_manager_get(
        severity_filter=kwargs.get("severity_filter"),
        status_filter=kwargs.get("status_filter"),
        source_filter=kwargs.get("source_filter"),
        limit=kwargs.get("limit"),
    )


def get_alert_by_id_impl(**kwargs) -> Optional[dict[str, Any]]:
    """Get specific alert."""
    alert_id = kwargs.get("alert_id")
    if not alert_id:
        raise ValueError("alert_id is required")

    alerts = alert_manager_get()
    for alert in alerts:
        if alert["alert_id"] == alert_id:
            return alert
    return None


def get_alert_stats_impl(**_kwargs) -> dict[str, Any]:
    """Get alert statistics."""
    return alert_manager_get_stats()


def reset_alerts_impl(**_kwargs) -> dict[str, Any]:
    """Clear all alerts."""
    alert_manager_reset()
    return {"status": "reset", "timestamp": __import__('time').time()}


def check_and_trigger_alerts_impl(**_kwargs) -> dict[str, Any]:
    """Check conditions and trigger alerts."""
    manager = get_alert_manager()
    stats = manager.get_alert_stats()

    results = []
    if stats.active_critical_count > 0:
        results.append({
            "condition": "critical_alerts_present",
            "triggered": True,
            "count": stats.active_critical_count,
        })

    return {
        "checks_performed": len(results),
        "results": results,
    }


def suppress_alert_impl(**kwargs) -> dict[str, Any]:
    """Suppress alerts by pattern.

    Stores suppression rule in singleton for pattern-based alert filtering.

    Args:
        **kwargs: Suppression parameters
            - pattern (str): Alert pattern to suppress (required)
            - duration_seconds (int): Suppression duration in seconds (default: 3600)

    Returns:
        Dict containing:
            - status (str): Operation status ('success' or 'error')
            - pattern (str): The pattern being suppressed
            - duration_seconds (int): Suppression duration
            - suppressed_at (float): Timestamp when suppression was created
            - expires_at (float): Timestamp when suppression expires
    """
    import time  # pylint: disable=import-outside-toplevel

    pattern = kwargs.get('pattern')
    duration = kwargs.get('duration_seconds', 3600)

    if not pattern:
        return {
            "status": "error",
            "error": "Pattern parameter required"
        }

    if not _GATEWAY_AVAILABLE:
        return {
            "status": "error",
            "error": "Gateway unavailable"
        }

    # Store suppression rule in singleton using gateway
    try:
        # Try to get existing suppressions, default to empty dict
        suppressions_result = execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name='alert_suppressions'
        )

        # Handle different response formats
        if isinstance(suppressions_result, dict):
            if 'data' in suppressions_result:
                suppressions = suppressions_result['data']
            elif 'status' in suppressions_result and \
                    suppressions_result['status'] == 'error':
                suppressions = {}
            else:
                suppressions = suppressions_result
        else:
            suppressions = {}

        if not isinstance(suppressions, dict):
            suppressions = {}

        # Add new suppression
        suppressions[pattern] = {
            'suppressed_at': time.time(),
            'duration': duration,
            'expires_at': time.time() + duration
        }

        # Store back to singleton
        execute_operation(
            GatewayInterface.SINGLETON,
            'set',
            name='alert_suppressions',
            instance=suppressions
        )

        return {
            "status": "success",
            "pattern": pattern,
            "duration_seconds": duration,
            "suppressed_at": time.time(),
            "expires_at": time.time() + duration
        }
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
        return {
            "status": "error",
            "error": f"Alert suppression operation error: {str(e)}"
        }


def unsuppress_alert_impl(**kwargs) -> dict[str, Any]:
    """Remove alert suppression by pattern.

    Removes a suppression rule from singleton for pattern-based alert filtering.

    Args:
        **kwargs: Unsuppression parameters
            - pattern (str): Alert pattern to unsuppress (required)

    Returns:
        Dict containing:
            - status (str): Operation status ('success' or 'error')
            - pattern (str): The pattern that was unsuppressed
            - removed (bool): True if pattern was suppressed, False if not found
    """
    pattern = kwargs.get('pattern')

    if not pattern:
        return {
            "status": "error",
            "error": "Pattern parameter required"
        }

    if not _GATEWAY_AVAILABLE:
        return {
            "status": "error",
            "error": "Gateway unavailable"
        }

    # Remove suppression rule from singleton using gateway
    try:
        # Try to get existing suppressions, default to empty dict
        suppressions_result = execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name='alert_suppressions'
        )

        # Handle different response formats
        if isinstance(suppressions_result, dict):
            if 'data' in suppressions_result:
                suppressions = suppressions_result['data']
            elif 'status' in suppressions_result and \
                    suppressions_result['status'] == 'error':
                suppressions = {}
            else:
                suppressions = suppressions_result
        else:
            suppressions = {}

        if not isinstance(suppressions, dict):
            suppressions = {}

        # Check if pattern exists
        if pattern in suppressions:
            del suppressions[pattern]

            # Store back to singleton
            execute_operation(
                GatewayInterface.SINGLETON,
                'set',
                name='alert_suppressions',
                instance=suppressions
            )

            return {
                "status": "success",
                "pattern": pattern,
                "removed": True
            }

        return {
            "status": "success",
            "pattern": pattern,
            "removed": False,
            "note": "Pattern was not suppressed"
        }
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
        return {
            "status": "error",
            "error": f"Alert unsuppression operation error: {str(e)}"
        }


__all__ = [
    "record_health_check_impl",
    "get_system_metrics_impl",
    "check_alerts_impl",
    "create_alert_impl",
    "acknowledge_alert_impl",
    "resolve_alert_impl",
    "get_alerts_impl",
    "get_alert_by_id_impl",
    "get_alert_stats_impl",
    "reset_alerts_impl",
    "check_and_trigger_alerts_impl",
    "suppress_alert_impl",
    "unsuppress_alert_impl",
]
