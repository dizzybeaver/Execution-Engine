"""ha_light.py - Router for Light Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _LightRouter(BaseFallbackRouter):
    """Router for Light interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Light",
            import_path="lee.home_assistant.ha_light.ha_light_core",
            function_names=[]
        )


_ha_light_router = _LightRouter()


def execute_ha_light_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Light interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_light_router.execute(operation, **kwargs)


def list_ha_light_operations() -> list[str]:
    """List all available Light operations.

    Returns:
        List of operation names
    """
    return _ha_light_router.list_operations()


__all__ = [
    "execute_ha_light_operation",
    "list_ha_light_operations",
]
