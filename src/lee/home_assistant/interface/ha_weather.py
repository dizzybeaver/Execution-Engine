"""ha_weather.py - Router for Weather Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _WeatherRouter(BaseFallbackRouter):
    """Router for Weather interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Weather",
            import_path="lee.home_assistant.ha_weather.ha_weather_core",
            function_names=[]
        )


_ha_weather_router = _WeatherRouter()


def execute_ha_weather_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Weather interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_weather_router.execute(operation, **kwargs)


def list_ha_weather_operations() -> list[str]:
    """List all available Weather operations.

    Returns:
        List of operation names
    """
    return _ha_weather_router.list_operations()


__all__ = [
    "execute_ha_weather_operation",
    "list_ha_weather_operations",
]
