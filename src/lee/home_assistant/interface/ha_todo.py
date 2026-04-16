"""ha_todo.py - Router for Todo Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _TodoRouter(BaseFallbackRouter):
    """Router for Todo interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Todo",
            import_path="lee.home_assistant.ha_todo.ha_todo_core",
            function_names=[]
        )


_ha_todo_router = _TodoRouter()


def execute_ha_todo_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Todo interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_todo_router.execute(operation, **kwargs)


def list_ha_todo_operations() -> list[str]:
    """List all available Todo operations.

    Returns:
        List of operation names
    """
    return _ha_todo_router.list_operations()


__all__ = [
    "execute_ha_todo_operation",
    "list_ha_todo_operations",
]
