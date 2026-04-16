"""ha_button.py - Button Interface Router

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ButtonRouter(BaseFallbackRouter):
    """Router for Button interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Button",
            import_path="lee.home_assistant.button.ha_button_core",
            function_names=[
                "list_buttons_impl",
                "press_button_impl",
            ]
        )


_button_router = _ButtonRouter()


def execute_button_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Execute Button operation through dispatch dictionary.

    Args:
        operation: The operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Dict with success status and operation result
    """
    return _button_router.execute(operation, **kwargs)


def list_button_operations() -> list[str]:
    """List all available Button operations.

    Returns:
        List of operation names
    """
    return _button_router.list_operations()


__all__ = [
    "execute_button_operation",
    "list_button_operations",
]
