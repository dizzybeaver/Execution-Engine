"""ha_energy.py - Router for Energy Interface

Version: 2026-04-02_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal implementations (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.ha_energy.ha_energy_core import (
        get_energy_info_impl as _get_energy_info_impl,
    )
    from lee.home_assistant.ha_energy.ha_energy_core import (
        get_energy_preferences_impl as _get_energy_preferences_impl,
    )
    from lee.home_assistant.ha_energy.ha_energy_core import (
        get_fossil_energy_consumption_impl as _get_fossil_energy_consumption_impl,
    )
    from lee.home_assistant.ha_energy.ha_energy_core import (
        get_solar_forecast_impl as _get_solar_forecast_impl,
    )
    from lee.home_assistant.ha_energy.ha_energy_core import (
        save_energy_preferences_impl as _save_energy_preferences_impl,
    )
    from lee.home_assistant.ha_energy.ha_energy_core import (
        validate_energy_config_impl as _validate_energy_config_impl,
    )
    _ENERGY_AVAILABLE = True
except ImportError:
    _ENERGY_AVAILABLE = False

    # Create stub implementations
    def _get_energy_preferences_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

    def _save_energy_preferences_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

    def _get_energy_info_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

    def _validate_energy_config_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

    def _get_solar_forecast_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

    def _get_fossil_energy_consumption_impl(**kwargs):
        return {"success": False, "error": "ENERGY not available"}

# Dispatch dictionary for O(1) operation routing
_ENERGY_DISPATCH = {
    "get_energy_preferences": _get_energy_preferences_impl,
    "save_energy_preferences": _save_energy_preferences_impl,
    "get_energy_info": _get_energy_info_impl,
    "validate_energy_config": _validate_energy_config_impl,
    "get_solar_forecast": _get_solar_forecast_impl,
    "get_fossil_energy_consumption": _get_fossil_energy_consumption_impl,
}


class _EnergyRouter(BaseSimpleDispatchRouter):
    """Router for Energy interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Energy",
            core_module=DummyModule(),
            dispatch_map=_ENERGY_DISPATCH
        )


_ha_energy_router = _EnergyRouter()


def execute_ha_energy_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Execute Energy operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Energy operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Energy implementation
    """
    return _ha_energy_router.execute(operation, **kwargs)


def list_ha_energy_operations() -> list[str]:
    """List all available Energy operations."""
    return _ha_energy_router.dispatch_map.keys()


__all__ = [
    "execute_ha_energy_operation",
    "list_ha_energy_operations",
    "_ENERGY_AVAILABLE"
]
