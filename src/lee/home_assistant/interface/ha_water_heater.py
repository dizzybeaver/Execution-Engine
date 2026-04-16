"""ha_water_heater.py - Router for WaterHeater Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _WaterHeaterRouter(BaseFallbackRouter):
    """Router for WaterHeater interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="WaterHeater",
            import_path="lee.home_assistant.ha_water_heater.ha_water_heater_core",
            function_names=[]
        )


_ha_water_heater_router = _WaterHeaterRouter()


def execute_ha_water_heater_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch WaterHeater interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_water_heater_router.execute(operation, **kwargs)


def list_ha_water_heater_operations() -> list[str]:
    """List all available WaterHeater operations.

    Returns:
        List of operation names
    """
    return _ha_water_heater_router.list_operations()


__all__ = [
    "execute_ha_water_heater_operation",
    "list_ha_water_heater_operations",
]
