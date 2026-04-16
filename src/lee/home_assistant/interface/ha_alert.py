"""ha_alert.py - Router for Alert Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AlertRouter(BaseFallbackRouter):
    """Router for Alert interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Alert",
            import_path="lee.home_assistant.ha_alert.ha_alert_core",
            function_names=[]
        )


_alert_router = _AlertRouter()


def execute_alert_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Alert interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _alert_router.execute(operation, **kwargs)


def list_alert_operations() -> list[str]:
    """List all available Alert operations.

    Returns:
        List of operation names
    """
    return _alert_router.list_operations()


__all__ = [
    "execute_alert_operation",
    "list_alert_operations",
]
