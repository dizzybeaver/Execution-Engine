"""ha_blink.py - Blink Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BlinkRouter(BaseFallbackRouter):
    """Router for Blink interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Blink",
            import_path="lee.home_assistant.ha_blink.ha_blink_core",
            function_names=[
                "record_impl",
                "trigger_camera_impl",
                "save_video_impl",
                "save_recent_clips_impl",
                "send_pin_impl",
            ]
        )


_blink_router = _BlinkRouter()


def execute_blink_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Blink interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _blink_router.execute(operation, **kwargs)
