"""ha_flux_led.py - Flux LED Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _FluxLedRouter(BaseFallbackRouter):
    """Router for Flux LED interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Flux LED",
            import_path="lee.home_assistant.ha_flux_led.ha_flux_led_core",
            function_names=[
                "set_custom_effect_impl",
                "set_zones_impl",
                "set_music_mode_impl",
            ]
        )


_flux_led_router = _FluxLedRouter()


def execute_flux_led_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Flux LED interface operations using DD-1 pattern."""
    return _flux_led_router.execute(operation, **kwargs)
