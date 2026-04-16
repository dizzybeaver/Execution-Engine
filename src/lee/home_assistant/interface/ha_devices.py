"""ha_devices.py - Devices Interface Router
Version: 2026-04-01_6
Description: Router for Devices operations

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        call_ha_api as _call_ha_api_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        call_service as _call_service_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        call_service_batch as _call_service_batch_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        check_status as _check_status_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        find_fuzzy as _find_fuzzy_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_by_domain as _get_by_domain_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_by_id as _get_by_id_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_by_type as _get_by_type_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_diagnostic_info as _get_diagnostic_info_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_ha_config as _get_ha_config_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_performance_report as _get_performance_report_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_state as _get_state_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_states as _get_states_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        get_states_batch as _get_states_batch_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        invalidate_domain_cache as _invalidate_domain_cache_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        invalidate_entity_cache as _invalidate_entity_cache_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        list_by_domain as _list_by_domain_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        refresh_state as _refresh_state_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        update_state as _update_state_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_devices_wrappers import (
        warm_cache as _warm_cache_impl,
    )
    _DEVICES_AVAILABLE = True
except ImportError:
    _DEVICES_AVAILABLE = False

    # Create stub implementations
    def _get_states_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_by_id_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _find_fuzzy_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _update_state_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _call_service_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _list_by_domain_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _check_status_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _call_ha_api_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_ha_config_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _warm_cache_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _invalidate_entity_cache_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _invalidate_domain_cache_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_performance_report_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_diagnostic_info_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_states_batch_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _call_service_batch_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_state_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_by_type_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _get_by_domain_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

    def _refresh_state_impl(**kwargs):
        return {"success": False, "error": "Devices not available"}

# Dispatch dictionary for O(1) operation routing
_DEVICES_DISPATCH = {
    "get_states": _get_states_impl,
    "get_by_id": _get_by_id_impl,
    "find_fuzzy": _find_fuzzy_impl,
    "update_state": _update_state_impl,
    "call_service": _call_service_impl,
    "list_by_domain": _list_by_domain_impl,
    "check_status": _check_status_impl,
    "call_ha_api": _call_ha_api_impl,
    "get_ha_config": _get_ha_config_impl,
    "warm_cache": _warm_cache_impl,
    "invalidate_entity_cache": _invalidate_entity_cache_impl,
    "invalidate_domain_cache": _invalidate_domain_cache_impl,
    "get_performance_report": _get_performance_report_impl,
    "get_diagnostic_info": _get_diagnostic_info_impl,
    "get_states_batch": _get_states_batch_impl,
    "call_service_batch": _call_service_batch_impl,
    "get_state": _get_state_impl,
    "get_by_type": _get_by_type_impl,
    "get_by_domain": _get_by_domain_impl,
    "refresh_state": _refresh_state_impl,
}


class _DevicesRouter(BaseSimpleDispatchRouter):
    """Router for Devices interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Devices",
            core_module=DummyModule(),
            dispatch_map=_DEVICES_DISPATCH
        )


_devices_router = _DevicesRouter()


def execute_devices_operation(operation: str, **kwargs) -> Any:
    """Execute Devices operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Devices operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Devices implementation
    """
    return _devices_router.execute(operation, **kwargs)


__all__ = ["execute_devices_operation"]
