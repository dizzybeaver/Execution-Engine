"""ha_binary_sensor.py - Binary Sensor Interface Router
Version: 2026-04-01_6
Description: Interface router for Binary Sensor integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_binary_sensor_wrappers import (
        get_state as _get_state_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_binary_sensor_wrappers import (
        list_binary_sensors as _list_binary_sensors_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_binary_sensor_wrappers import (
        reload_binary_sensors as _reload_binary_sensors_impl,
    )
    _BINARY_SENSOR_AVAILABLE = True
except ImportError:
    _BINARY_SENSOR_AVAILABLE = False

    # Create stub implementations
    def _list_binary_sensors_impl(**kwargs):
        return {"success": False, "error": "Binary Sensor not available"}

    def _reload_binary_sensors_impl(**kwargs):
        return {"success": False, "error": "Binary Sensor not available"}

    def _get_state_impl(**kwargs):
        return {"success": False, "error": "Binary Sensor not available"}

# Dispatch dictionary for O(1) operation routing
_BINARY_SENSOR_DISPATCH = {
    "list": _list_binary_sensors_impl,
    "reload": _reload_binary_sensors_impl,
    "get_state": _get_state_impl,
}


class _BinarySensorRouter(BaseSimpleDispatchRouter):
    """Router for Binary Sensor interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Binary Sensor",
            core_module=DummyModule(),
            dispatch_map=_BINARY_SENSOR_DISPATCH
        )


_binary_sensor_router = _BinarySensorRouter()


def execute_binary_sensor_operation(operation: str, **kwargs) -> Any:
    """Execute Binary Sensor operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Binary Sensor operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Binary Sensor implementation
    """
    return _binary_sensor_router.execute(operation, **kwargs)


__all__ = ["execute_binary_sensor_operation"]
