"""ha_input_number.py - Input Number Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputNumberRouter(BaseFallbackRouter):
    """Router for Input Number interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputNumber",
            import_path="lee.home_assistant.ha_input_number.ha_input_number_core",
            function_names=[
                "list_input_numbers_impl",
                "decrement_input_number_impl",
                "increment_input_number_impl",
                "set_value_input_number_impl",
                "reload_input_numbers_impl",
            ]
        )


_input_number_router = _InputNumberRouter()


def execute_input_number_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input Number interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_number_router.execute(operation, **kwargs)
