"""ha_fan.py - Router for Fan Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _FanRouter(BaseFallbackRouter):
    """Router for Fan interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Fan",
            import_path="lee.home_assistant.ha_fan.ha_fan_core",
            function_names=[]
        )


_ha_fan_router = _FanRouter()


def execute_ha_fan_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Fan interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_fan_router.execute(operation, **kwargs)


def list_ha_fan_operations() -> list[str]:
    """List all available Fan operations.

    Returns:
        List of operation names
    """
    return _ha_fan_router.list_operations()


__all__ = [
    "execute_ha_fan_operation",
    "list_ha_fan_operations",
]
