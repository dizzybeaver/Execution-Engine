"""ha_tado.py - Tado° Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_tado import ha_tado_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _TadoRouter(BaseSimpleDispatchRouter):
    """Router for Tado° interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Tado°",
            core_module=ha_tado_core,
            dispatch_map={
                "set_climate_timer": ha_tado_core.set_climate_timer_impl,
                "set_water_heater_timer": ha_tado_core.set_water_heater_timer_impl,
                "set_climate_temperature_offset": ha_tado_core.set_climate_temperature_offset_impl,
                "add_meter_reading": ha_tado_core.add_meter_reading_impl,
            }
        )


_tado_router = _TadoRouter()


def execute_tado_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Tado° interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _tado_router.execute(operation, **kwargs)
