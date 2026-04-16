"""ha_hue.py - Philips Hue Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_hue import ha_hue_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _HueRouter(BaseSimpleDispatchRouter):
    """Router for Philips Hue interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Philips Hue",
            core_module=ha_hue_core,
            dispatch_map={
                "hue_activate_scene": ha_hue_core.hue_activate_scene_impl,
                "activate_scene": ha_hue_core.activate_scene_impl,
            }
        )


_hue_router = _HueRouter()


def execute_hue_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Philips Hue interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _hue_router.execute(operation, **kwargs)
