"""ha_group.py - Router for Group Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _GroupRouter(BaseFallbackRouter):
    """Router for Group interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Group",
            import_path="lee.home_assistant.ha_group.ha_group_core",
            function_names=[]
        )


_ha_group_router = _GroupRouter()


def execute_ha_group_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Group interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_group_router.execute(operation, **kwargs)


def list_ha_group_operations() -> list[str]:
    """List all available Group operations.

    Returns:
        List of operation names
    """
    return _ha_group_router.list_operations()


__all__ = [
    "execute_ha_group_operation",
    "list_ha_group_operations",
]
