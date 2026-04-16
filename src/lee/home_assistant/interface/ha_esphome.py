"""ha_esphome.py - Router for Esphome Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _EsphomeRouter(BaseFallbackRouter):
    """Router for Esphome interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Esphome",
            import_path="lee.home_assistant.ha_esphome.ha_esphome_core",
            function_names=[]
        )


_ha_esphome_router = _EsphomeRouter()


def execute_ha_esphome_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Esphome interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_esphome_router.execute(operation, **kwargs)


def list_ha_esphome_operations() -> list[str]:
    """List all available Esphome operations.

    Returns:
        List of operation names
    """
    return _ha_esphome_router.list_operations()


# Alias for gateway compatibility
execute_esphome_operation = execute_ha_esphome_operation


__all__ = [
    "execute_ha_esphome_operation",
    "execute_esphome_operation",
    "list_ha_esphome_operations",
]
