"""ha_persistent.py - Persistent Notification Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _PersistentRouter(BaseFallbackRouter):
    """Router for Persistent Notification interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Persistent",
            import_path="lee.home_assistant.ha_persistent.ha_persistent_core",
            function_names=[
                "list_notifications_impl",
                "create_notification_impl",
                "dismiss_notification_impl",
            ]
        )


_persistent_router = _PersistentRouter()


def execute_persistent_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Persistent Notification interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _persistent_router.execute(operation, **kwargs)
