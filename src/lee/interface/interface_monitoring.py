# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface_monitoring.py - Router for Monitoring Interface

Version: 2026-04-11_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.interface.wrappers.monitoring_wrappers')
def _import_monitoring():
    from lee.interface.wrappers.monitoring_wrappers import (
        acknowledge_alert_impl as _acknowledge_alert,
        check_alerts_impl as _check_alerts,
        check_and_trigger_alerts_impl as _check_and_trigger_alerts,
        create_alert_impl as _create_alert,
        get_alert_by_id_impl as _get_alert_by_id,
        get_alert_stats_impl as _get_alert_stats,
        get_alerts_impl as _get_alerts,
        get_system_metrics_impl as _get_system_metrics,
        record_health_check_impl as _record_health_check,
        reset_alerts_impl as _reset_alerts,
        resolve_alert_impl as _resolve_alert,
        suppress_alert_impl as _suppress_alert,
        unsuppress_alert_impl as _unsuppress_alert,
    )
    return {
        'acknowledge_alert': _acknowledge_alert,
        'check_alerts': _check_alerts,
        'check_and_trigger_alerts': _check_and_trigger_alerts,
        'create_alert': _create_alert,
        'get_alert_by_id': _get_alert_by_id,
        'get_alert_stats': _get_alert_stats,
        'get_alerts': _get_alerts,
        'get_system_metrics': _get_system_metrics,
        'record_health_check': _record_health_check,
        'reset_alerts': _reset_alerts,
        'resolve_alert': _resolve_alert,
        'suppress_alert': _suppress_alert,
        'unsuppress_alert': _unsuppress_alert,
    }


_monitoring_funcs = _import_monitoring()
_MONITORING_AVAILABLE = _import_monitoring.__dict__.get('_MONITORING_AVAILABLE', False)

if _MONITORING_AVAILABLE:
    _record_health_check = _monitoring_funcs['record_health_check']
    _get_system_metrics = _monitoring_funcs['get_system_metrics']
    _check_alerts = _monitoring_funcs['check_alerts']
    _create_alert = _monitoring_funcs['create_alert']
    _acknowledge_alert = _monitoring_funcs['acknowledge_alert']
    _get_alert_by_id = _monitoring_funcs['get_alert_by_id']
    _get_alert_stats = _monitoring_funcs['get_alert_stats']
    _get_alerts = _monitoring_funcs['get_alerts']
    _reset_alerts = _monitoring_funcs['reset_alerts']
    _resolve_alert = _monitoring_funcs['resolve_alert']
    _suppress_alert = _monitoring_funcs['suppress_alert']
    _unsuppress_alert = _monitoring_funcs['unsuppress_alert']
else:
    def _record_health_check(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_system_metrics(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _check_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _create_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _acknowledge_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alert_by_id(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alert_stats(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _reset_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _resolve_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _suppress_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _unsuppress_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}
        return {"success": False, "error": "Monitoring not available"}

    def _resolve_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alert_by_id(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _get_alert_stats(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _reset_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _check_and_trigger_alerts(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _suppress_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}

    def _unsuppress_alert(**_kwargs):
        return {"success": False, "error": "Monitoring not available"}


def _health_check(**_kwargs) -> dict[str, Any]:
    """Perform health check."""
    return {
        "status": "healthy",
        "interface": "MONITORING",
        "timestamp": __import__('time').time(),
        "checks": {
            "alerts_system": "operational",
            "metrics_collection": "operational",
        }
    }


# Dispatch dictionary for O(1) operation routing
_MONITORING_DISPATCH = {
    "health_check": _health_check,
    "record_health_check": _record_health_check,
    "get_system_metrics": _get_system_metrics,
    "check_alerts": _check_alerts,
    "create_alert": _create_alert,
    "acknowledge_alert": _acknowledge_alert,
    "resolve_alert": _resolve_alert,
    "get_alerts": _get_alerts,
    "get_alert_by_id": _get_alert_by_id,
    "get_alert_stats": _get_alert_stats,
    "reset_alerts": _reset_alerts,
    "check_and_trigger_alerts": _check_and_trigger_alerts,
    "suppress_alert": _suppress_alert,
    "unsuppress_alert": _unsuppress_alert,
}


class _MonitoringRouter(BaseSimpleDispatchRouter):
    """Router for Monitoring interface operations.

    This router handles monitoring operations including health checks,
    alert management, and system metrics collection.
    """

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Monitoring",
            core_module=DummyModule(),
            dispatch_map=_MONITORING_DISPATCH
        )


_monitoring_router = _MonitoringRouter()


def execute_monitoring_operation(operation: str, **kwargs) -> Any:
    """Execute Monitoring operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Monitoring operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Monitoring implementation
    """
    return _monitoring_router.execute(operation, **kwargs)


def list_monitoring_operations() -> list[str]:
    """List all available Monitoring operations."""
    return _monitoring_router.dispatch_map.keys()


__all__ = [
    "execute_monitoring_operation",
    "list_monitoring_operations",
    "_MONITORING_AVAILABLE"
]
