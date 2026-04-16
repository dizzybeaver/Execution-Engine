"""ha_input_datetime.py - Input DateTime Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _InputDateTimeRouter(BaseFallbackRouter):
    """Router for Input DateTime interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="InputDateTime",
            import_path="lee.home_assistant.ha_input_datetime.ha_input_datetime_core",
            function_names=[
                "list_input_datetimes_impl",
                "set_datetime_impl",
                "reload_input_datetimes_impl",
            ]
        )


_input_datetime_router = _InputDateTimeRouter()


def execute_input_datetime_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Input DateTime interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _input_datetime_router.execute(operation, **kwargs)
