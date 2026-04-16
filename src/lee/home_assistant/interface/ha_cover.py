"""ha_cover.py - Cover Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _CoverRouter(BaseFallbackRouter):
    """Router for Cover interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Cover",
            import_path="lee.home_assistant.ha_cover.ha_cover_core",
            function_names=[
                "list_covers_impl",
                "open_cover_impl",
                "close_cover_impl",
                "toggle_cover_impl",
                "set_cover_position_impl",
                "stop_cover_impl",
            ]
        )


_cover_router = _CoverRouter()


def execute_cover_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Cover interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _cover_router.execute(operation, **kwargs)
