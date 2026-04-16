"""ha_blue_current.py - Blue Current Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BlueCurrentRouter(BaseFallbackRouter):
    """Router for Blue Current interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Blue Current",
            import_path="lee.home_assistant.ha_blue_current.ha_blue_current_core",
            function_names=[
                "start_charge_session_impl",
            ]
        )


_blue_current_router = _BlueCurrentRouter()


def execute_blue_current_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Blue Current interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _blue_current_router.execute(operation, **kwargs)
