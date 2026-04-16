"""ha_sensor.py - Sensor Interface Router
Version: 2026-04-01_6
Description: Interface router for Sensor integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
        get_device_class_units as _get_device_class_units_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
        get_numeric_device_classes as _get_numeric_device_classes_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
        get_state as _get_state_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
        get_value as _get_value_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
        list_sensors as _list_sensors_impl,
    )
    _SENSOR_AVAILABLE = True
except ImportError:
    _SENSOR_AVAILABLE = False

    # Create stub implementations
    def _get_device_class_units_impl(**kwargs):
        return {"success": False, "error": "Sensor not available"}

    def _get_numeric_device_classes_impl(**kwargs):
        return {"success": False, "error": "Sensor not available"}

    def _get_value_impl(**kwargs):
        return {"success": False, "error": "Sensor not available"}

    def _get_state_impl(**kwargs):
        return {"success": False, "error": "Sensor not available"}

    def _list_sensors_impl(**kwargs):
        return {"success": False, "error": "Sensor not available"}

# Dispatch dictionary for O(1) operation routing
_SENSOR_DISPATCH = {
    "get_device_class_units": _get_device_class_units_impl,
    "get_numeric_device_classes": _get_numeric_device_classes_impl,
    "get_value": _get_value_impl,
    "get_state": _get_state_impl,
    "list": _list_sensors_impl,
}


class _SensorRouter(BaseSimpleDispatchRouter):
    """Router for Sensor interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Sensor",
            core_module=DummyModule(),
            dispatch_map=_SENSOR_DISPATCH
        )


_sensor_router = _SensorRouter()


def execute_sensor_operation(operation: str, **kwargs) -> Any:
    """Execute Sensor operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Sensor operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Sensor implementation
    """
    return _sensor_router.execute(operation, **kwargs)


__all__ = ["execute_sensor_operation"]
