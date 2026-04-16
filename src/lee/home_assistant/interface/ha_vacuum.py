"""ha_vacuum.py - Router for Vacuum Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _VacuumRouter(BaseFallbackRouter):
    """Router for Vacuum interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Vacuum",
            import_path="lee.home_assistant.ha_vacuum.ha_vacuum_core",
            function_names=[]
        )


_ha_vacuum_router = _VacuumRouter()


def execute_ha_vacuum_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Vacuum interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_vacuum_router.execute(operation, **kwargs)


def list_ha_vacuum_operations() -> list[str]:
    """List all available Vacuum operations.

    Returns:
        List of operation names
    """
    return _ha_vacuum_router.list_operations()


__all__ = [
    "execute_ha_vacuum_operation",
    "list_ha_vacuum_operations",
]
