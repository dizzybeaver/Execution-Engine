"""ha_input_boolean.py - Input Boolean Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputBooleanRouter(BaseFallbackRouter):
    """Router for Input Boolean interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputBoolean",
            import_path="lee.home_assistant.ha_input_boolean.ha_input_boolean_core",
            function_names=[
                "list_input_booleans_impl",
                "turn_on_input_boolean_impl",
                "turn_off_input_boolean_impl",
                "toggle_input_boolean_impl",
                "reload_input_booleans_impl",
            ]
        )


_input_boolean_router = _InputBooleanRouter()


def execute_input_boolean_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input Boolean interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_boolean_router.execute(operation, **kwargs)
