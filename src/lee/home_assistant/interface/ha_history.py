"""ha_history.py - Router for History Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _HistoryRouter(BaseFallbackRouter):
    """Router for History interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="History",
            import_path="lee.home_assistant.ha_history.ha_history_core",
            function_names=[]
        )


_ha_history_router = _HistoryRouter()


def execute_ha_history_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch History interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_history_router.execute(operation, **kwargs)


def list_ha_history_operations() -> list[str]:
    """List all available History operations.

    Returns:
        List of operation names
    """
    return _ha_history_router.list_operations()


__all__ = [
    "execute_ha_history_operation",
    "list_ha_history_operations",
]
