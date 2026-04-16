"""ha_notify.py - Router for Notify Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _NotifyRouter(BaseFallbackRouter):
    """Router for Notify interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Notify",
            import_path="lee.home_assistant.ha_notify.ha_notify_core",
            function_names=[]
        )


_ha_notify_router = _NotifyRouter()


def execute_ha_notify_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Notify interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_notify_router.execute(operation, **kwargs)


def list_ha_notify_operations() -> list[str]:
    """List all available Notify operations.

    Returns:
        List of operation names
    """
    return _ha_notify_router.list_operations()


__all__ = [
    "execute_ha_notify_operation",
    "list_ha_notify_operations",
]
