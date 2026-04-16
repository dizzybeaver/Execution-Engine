"""ha_input_button.py - Input Button Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputButtonRouter(BaseFallbackRouter):
    """Router for Input Button interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputButton",
            import_path="lee.home_assistant.ha_input_button.ha_input_button_core",
            function_names=[
                "list_input_buttons_impl",
                "press_input_button_impl",
                "reload_input_buttons_impl",
            ]
        )


_input_button_router = _InputButtonRouter()


def execute_input_button_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input Button interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_button_router.execute(operation, **kwargs)
