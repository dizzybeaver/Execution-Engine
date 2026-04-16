"""ha_file.py - File Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _FileRouter(BaseFallbackRouter):
    """Router for File interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="File",
            import_path="lee.home_assistant.ha_file.ha_file_core",
            function_names=[
                "read_file_impl",
            ]
        )


_file_router = _FileRouter()


def execute_file_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch File interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _file_router.execute(operation, **kwargs)
