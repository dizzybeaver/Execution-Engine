"""ha_input_text.py - Input Text Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputTextRouter(BaseFallbackRouter):
    """Router for Input Text interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputText",
            import_path="lee.home_assistant.ha_input_text.ha_input_text_core",
            function_names=[
                "list_input_texts_impl",
                "set_value_input_text_impl",
                "reload_input_texts_impl",
            ]
        )


_input_text_router = _InputTextRouter()


def execute_input_text_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input Text interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_text_router.execute(operation, **kwargs)
