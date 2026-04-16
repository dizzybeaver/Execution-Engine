"""ha_hardware.py - Router for Hardware Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _HardwareRouter(BaseFallbackRouter):
    """Router for Hardware interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Hardware",
            import_path="lee.home_assistant.ha_hardware.ha_hardware_core",
            function_names=[]
        )


_ha_hardware_router = _HardwareRouter()


def execute_ha_hardware_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Hardware interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_hardware_router.execute(operation, **kwargs)


def list_ha_hardware_operations() -> list[str]:
    """List all available Hardware operations.

    Returns:
        List of operation names
    """
    return _ha_hardware_router.list_operations()


__all__ = [
    "execute_ha_hardware_operation",
    "list_ha_hardware_operations",
]
