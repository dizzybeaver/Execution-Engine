"""ha_automation.py - Router for Automation Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AutomationRouter(BaseFallbackRouter):
    """Router for Automation interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Automation",
            import_path="lee.home_assistant.ha_automation.ha_automation_core",
            function_names=[]
        )


_automation_router = _AutomationRouter()


def execute_automation_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Automation interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _automation_router.execute(operation, **kwargs)


def list_automation_operations() -> list[str]:
    """List all available Automation operations.

    Returns:
        List of operation names
    """
    return _automation_router.list_operations()


__all__ = [
    "execute_automation_operation",
    "list_automation_operations",
]
