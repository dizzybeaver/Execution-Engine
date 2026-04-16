"""ha_proximity.py - Proximity Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ProximityRouter(BaseFallbackRouter):
    """Router for Proximity interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Proximity",
            import_path="lee.home_assistant.ha_proximity.ha_proximity_core",
            function_names=[
                "list_proximity_zones_impl",
                "get_proximity_state_impl",
                "set_proximity_zone_impl",
            ]
        )


_proximity_router = _ProximityRouter()


def execute_proximity_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Proximity interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _proximity_router.execute(operation, **kwargs)
