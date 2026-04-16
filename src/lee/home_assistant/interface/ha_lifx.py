"""ha_lifx.py - LIFX LED Lighting Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_lifx import ha_lifx_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _LifxRouter(BaseSimpleDispatchRouter):
    """Router for LIFX LED lighting interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="LIFX",
            core_module=ha_lifx_core,
            dispatch_map={
                "effect_pulse": ha_lifx_core.effect_pulse_impl,
                "effect_stop": ha_lifx_core.effect_stop_impl,
            }
        )


_lifx_router = _LifxRouter()


def execute_lifx_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch LIFX LED lighting interface operations using DD-1 pattern."""
    return _lifx_router.execute(operation, **kwargs)
