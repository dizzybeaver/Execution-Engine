"""ha_timer.py - Router for Timer Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _TimerRouter(BaseFallbackRouter):
    """Router for Timer interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Timer",
            import_path="lee.home_assistant.ha_timer.ha_timer_core",
            function_names=[]
        )


_ha_timer_router = _TimerRouter()


def execute_ha_timer_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Timer interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_timer_router.execute(operation, **kwargs)


def list_ha_timer_operations() -> list[str]:
    """List all available Timer operations.

    Returns:
        List of operation names
    """
    return _ha_timer_router.list_operations()


__all__ = [
    "execute_ha_timer_operation",
    "list_ha_timer_operations",
]
