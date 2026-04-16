"""ha_camera.py - Camera Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _CameraRouter(BaseFallbackRouter):
    """Router for Camera interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Camera",
            import_path="lee.home_assistant.ha_camera.ha_camera_core",
            function_names=[
                "list_cameras_impl",
                "turn_on_camera_impl",
                "turn_off_camera_impl",
                "enable_motion_detection_impl",
                "disable_motion_detection_impl",
                "snapshot_impl",
                "play_stream_impl",
                "record_impl",
            ]
        )


_camera_router = _CameraRouter()


def execute_camera_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Camera interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _camera_router.execute(operation, **kwargs)
