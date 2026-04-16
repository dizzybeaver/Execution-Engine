"""ha_shopping_list.py - Router for ShoppingList Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ShoppingListRouter(BaseFallbackRouter):
    """Router for ShoppingList interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="ShoppingList",
            import_path="lee.home_assistant.ha_shopping_list.ha_shopping_list_core",
            function_names=[]
        )


_ha_shopping_list_router = _ShoppingListRouter()


def execute_ha_shopping_list_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch ShoppingList interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_shopping_list_router.execute(operation, **kwargs)


def list_ha_shopping_list_operations() -> list[str]:
    """List all available ShoppingList operations.

    Returns:
        List of operation names
    """
    return _ha_shopping_list_router.list_operations()


__all__ = [
    "execute_ha_shopping_list_operation",
    "list_ha_shopping_list_operations",
]
