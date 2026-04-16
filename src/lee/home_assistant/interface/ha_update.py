"""ha_update.py - Router for Update Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _UpdateRouter(BaseFallbackRouter):
    """Router for Update interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Update",
            import_path="lee.home_assistant.ha_update.ha_update_core",
            function_names=[]
        )


_ha_update_router = _UpdateRouter()


def execute_ha_update_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Update interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_update_router.execute(operation, **kwargs)


def list_ha_update_operations() -> list[str]:
    """List all available Update operations.

    Returns:
        List of operation names
    """
    return _ha_update_router.list_operations()


__all__ = [
    "execute_ha_update_operation",
    "list_ha_update_operations",
]
