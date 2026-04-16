"""ha_ffmpeg.py - FFmpeg Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _FfmpegRouter(BaseFallbackRouter):
    """Router for FFmpeg interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="FFmpeg",
            import_path="lee.home_assistant.ha_ffmpeg.ha_ffmpeg_core",
            function_names=[
                "restart_impl",
                "start_impl",
                "stop_impl",
            ]
        )


_ffmpeg_router = _FfmpegRouter()


def execute_ffmpeg_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch FFmpeg interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ffmpeg_router.execute(operation, **kwargs)
