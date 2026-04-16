"""ha_amberelectric.py - Router for Amberelectric Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AmberelectricRouter(BaseFallbackRouter):
    """Router for Amberelectric interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Amberelectric",
            import_path="lee.home_assistant.ha_amberelectric.ha_amberelectric_core",
            function_names=[]
        )


_amberelectric_router = _AmberelectricRouter()


def execute_amberelectric_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Amberelectric interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _amberelectric_router.execute(operation, **kwargs)


def list_amberelectric_operations() -> list[str]:
    """List all available Amberelectric operations.

    Returns:
        List of operation names
    """
    return _amberelectric_router.list_operations()


__all__ = [
    "execute_amberelectric_operation",
    "list_amberelectric_operations",
]
