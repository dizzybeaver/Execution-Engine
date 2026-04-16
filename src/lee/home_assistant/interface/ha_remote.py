"""ha_remote.py - Remote Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _RemoteRouter(BaseFallbackRouter):
    """Router for Remote interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Remote",
            import_path="lee.home_assistant.ha_remote.ha_remote_core",
            function_names=[
                "list_remotes_impl",
                "turn_on_remote_impl",
                "toggle_remote_impl",
                "turn_off_remote_impl",
                "send_command_impl",
                "learn_command_impl",
                "delete_command_impl",
            ]
        )


_remote_router = _RemoteRouter()


def execute_remote_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Remote interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _remote_router.execute(operation, **kwargs)
