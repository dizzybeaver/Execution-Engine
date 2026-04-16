"""ha_ecobee.py - Ecobee Thermostat Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _EcobeeRouter(BaseFallbackRouter):
    """Router for Ecobee thermostat interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Ecobee",
            import_path="lee.home_assistant.ha_ecobee.ha_ecobee_core",
            function_names=[
                "create_vacation_impl",
                "delete_vacation_impl",
                "resume_program_impl",
                "set_fan_min_on_time_impl",
                "set_dst_mode_impl",
                "set_mic_mode_impl",
                "set_occupancy_modes_impl",
                "set_sensors_used_in_climate_impl",
            ]
        )


_ecobee_router = _EcobeeRouter()


def execute_ecobee_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Ecobee thermostat interface operations using DD-1 pattern."""
    return _ecobee_router.execute(operation, **kwargs)
