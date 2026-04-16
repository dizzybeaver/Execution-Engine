"""ha_switch.py - Router for Switch Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _SwitchRouter(BaseFallbackRouter):
    """Router for Switch interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Switch",
            import_path="lee.home_assistant.ha_switch.ha_switch_core",
            function_names=[]
        )


_ha_switch_router = _SwitchRouter()


def execute_ha_switch_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Switch interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_switch_router.execute(operation, **kwargs)


def list_ha_switch_operations() -> list[str]:
    """List all available Switch operations.

    Returns:
        List of operation names
    """
    return _ha_switch_router.list_operations()


__all__ = [
    "execute_ha_switch_operation",
    "list_ha_switch_operations",
]
