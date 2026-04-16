"""ha_supervisor.py - Router for Supervisor Interface

Version: 2026-04-02_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        get_addon_info_impl as _get_addon_info_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        get_core_info_impl as _get_core_info_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        get_host_info_impl as _get_host_info_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        get_os_info_impl as _get_os_info_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        get_supervisor_info_impl as _get_supervisor_info_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        list_addons_impl as _list_addons_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        restart_addon_impl as _restart_addon_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        start_addon_impl as _start_addon_impl,
    )
    from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
        stop_addon_impl as _stop_addon_impl,
    )
    _SUPERVISOR_AVAILABLE = True
except ImportError:
    _SUPERVISOR_AVAILABLE = False

    # Create stub implementations
    def _get_supervisor_info_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _get_host_info_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _get_core_info_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _get_os_info_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _list_addons_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _get_addon_info_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _start_addon_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _stop_addon_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

    def _restart_addon_impl(**kwargs):
        return {"success": False, "error": "SUPERVISOR not available"}

# Dispatch dictionary for O(1) operation routing
_SUPERVISOR_DISPATCH = {
    "get_supervisor_info": _get_supervisor_info_impl,
    "get_host_info": _get_host_info_impl,
    "get_core_info": _get_core_info_impl,
    "get_os_info": _get_os_info_impl,
    "list_addons": _list_addons_impl,
    "get_addon_info": _get_addon_info_impl,
    "start_addon": _start_addon_impl,
    "stop_addon": _stop_addon_impl,
    "restart_addon": _restart_addon_impl,
}


class _SupervisorRouter(BaseSimpleDispatchRouter):
    """Router for Supervisor interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Supervisor",
            core_module=DummyModule(),
            dispatch_map=_SUPERVISOR_DISPATCH
        )


_supervisor_router = _SupervisorRouter()


def execute_ha_supervisor_operation(operation: str, **kwargs) -> Any:
    """Execute Supervisor operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Supervisor operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Supervisor implementation
    """
    return _supervisor_router.execute(operation, **kwargs)


def list_ha_supervisor_operations() -> list[str]:
    """List all available Supervisor operations."""
    return _supervisor_router.dispatch_map.keys()


# Backward compatibility alias for ha_gateway_generic
execute_supervisor_operation = execute_ha_supervisor_operation


__all__ = [
    "execute_ha_supervisor_operation",
    "execute_supervisor_operation",
    "list_ha_supervisor_operations",
    "_SUPERVISOR_AVAILABLE"
]
