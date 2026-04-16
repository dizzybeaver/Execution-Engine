"""ha_health.py - Router for Health Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.home_assistant.ha_health.ha_health_generic import check_system_health_impl


class _HealthRouter(BaseSimpleDispatchRouter):
    """Router for Health interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Health",
            core_module=None,
            dispatch_map={
                "check_system_health": check_system_health_impl,
            }
        )


_ha_health_router = _HealthRouter()


def execute_ha_health_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Health interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_health_router.execute(operation, **kwargs)


def list_ha_health_operations() -> list[str]:
    """List all available Health operations.

    Returns:
        List of operation names
    """
    return _ha_health_router.list_operations()


__all__ = [
    "execute_ha_health_operation",
    "list_ha_health_operations",
]
