"""ha_bond.py - Bond Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BondRouter(BaseFallbackRouter):
    """Router for Bond operations."""

    def __init__(self):
        super().__init__(
            interface_name="Bond",
            import_path="lee.home_assistant.ha_bond.ha_bond_core",
            function_names=[
                "set_fan_speed_tracked_state_impl",
                "set_switch_power_tracked_state_impl",
                "set_light_power_tracked_state_impl",
                "set_light_brightness_tracked_state_impl",
                "start_increasing_brightness_impl",
                "start_decreasing_brightness_impl",
                "stop_impl",
            ]
        )


_bond_router = _BondRouter()


def execute_bond_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Bond operation using dispatch dictionary.

    Args:
        operation: Operation name from BOND_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _bond_router.execute(operation, **kwargs)
