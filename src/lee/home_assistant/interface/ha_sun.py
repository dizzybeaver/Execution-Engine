"""ha_sun.py - Router for Sun Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _SunRouter(BaseFallbackRouter):
    """Router for Sun interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Sun",
            import_path="lee.home_assistant.ha_sun.ha_sun_core",
            function_names=[]
        )


_ha_sun_router = _SunRouter()


def execute_ha_sun_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Sun interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_sun_router.execute(operation, **kwargs)


def list_ha_sun_operations() -> list[str]:
    """List all available Sun operations.

    Returns:
        List of operation names
    """
    return _ha_sun_router.list_operations()


__all__ = [
    "execute_ha_sun_operation",
    "list_ha_sun_operations",
]
