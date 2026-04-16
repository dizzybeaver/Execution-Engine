"""ha_climate.py - Climate Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ClimateRouter(BaseFallbackRouter):
    """Router for Climate interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Climate",
            import_path="lee.home_assistant.ha_climate.ha_climate_core",
            function_names=[
                "list_climates_impl",
                "set_temperature_climate_impl",
                "set_preset_mode_climate_impl",
                "set_hvac_mode_climate_impl",
                "turn_on_climate_impl",
                "turn_off_climate_impl",
            ]
        )


_climate_router = _ClimateRouter()


def execute_climate_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Climate interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _climate_router.execute(operation, **kwargs)
