"""ha_zone.py - Router for Zone Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ZoneRouter(BaseFallbackRouter):
    """Router for Zone interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Zone",
            import_path="lee.home_assistant.ha_zone.ha_zone_core",
            function_names=[]
        )


_ha_zone_router = _ZoneRouter()


def execute_ha_zone_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Zone interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_zone_router.execute(operation, **kwargs)


def list_ha_zone_operations() -> list[str]:
    """List all available Zone operations.

    Returns:
        List of operation names
    """
    return _ha_zone_router.list_operations()


__all__ = [
    "execute_ha_zone_operation",
    "list_ha_zone_operations",
]
