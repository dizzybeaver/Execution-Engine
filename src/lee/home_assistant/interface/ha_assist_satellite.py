"""ha_assist_satellite.py - Router for AssistSatellite Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AssistSatelliteRouter(BaseFallbackRouter):
    """Router for AssistSatellite interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AssistSatellite",
            import_path="lee.home_assistant.ha_assist_satellite.ha_assist_satellite_core",
            function_names=[]
        )


_assist_satellite_router = _AssistSatelliteRouter()


def execute_assist_satellite_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch AssistSatellite interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _assist_satellite_router.execute(operation, **kwargs)


def list_assist_satellite_operations() -> list[str]:
    """List all available AssistSatellite operations.

    Returns:
        List of operation names
    """
    return _assist_satellite_router.list_operations()


__all__ = [
    "execute_assist_satellite_operation",
    "list_assist_satellite_operations",
]
