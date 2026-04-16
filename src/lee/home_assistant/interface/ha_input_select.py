"""ha_input_select.py - Input Select Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputSelectRouter(BaseFallbackRouter):
    """Router for Input Select interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputSelect",
            import_path="lee.home_assistant.ha_input_select.ha_input_select_core",
            function_names=[
                "list_input_selects_impl",
                "select_next_option_impl",
                "select_previous_option_impl",
                "select_first_option_impl",
                "select_last_option_impl",
                "select_option_impl",
                "set_options_impl",
                "reload_input_selects_impl",
            ]
        )


_input_select_router = _InputSelectRouter()


def execute_input_select_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input Select interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_select_router.execute(operation, **kwargs)
