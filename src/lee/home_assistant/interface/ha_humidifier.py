"""ha_humidifier.py - Humidifier Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _HumidifierRouter(BaseFallbackRouter):
    """Router for Humidifier interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Humidifier",
            import_path="lee.home_assistant.ha_humidifier.ha_humidifier_core",
            function_names=[
                "list_humidifiers_impl",
                "turn_on_humidifier_impl",
                "turn_off_humidifier_impl",
                "set_humidity_impl",
                "set_mode_impl",
                "toggle_humidifier_impl",
            ]
        )


_humidifier_router = _HumidifierRouter()


def execute_humidifier_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Humidifier interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _humidifier_router.execute(operation, **kwargs)
