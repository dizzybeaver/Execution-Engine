"""ha_statistics.py - Router for Statistics Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _StatisticsRouter(BaseFallbackRouter):
    """Router for Statistics interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Statistics",
            import_path="lee.home_assistant.ha_statistics.ha_statistics_core",
            function_names=[]
        )


_ha_statistics_router = _StatisticsRouter()


def execute_ha_statistics_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Statistics interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_statistics_router.execute(operation, **kwargs)


def list_ha_statistics_operations() -> list[str]:
    """List all available Statistics operations.

    Returns:
        List of operation names
    """
    return _ha_statistics_router.list_operations()


__all__ = [
    "execute_ha_statistics_operation",
    "list_ha_statistics_operations",
]
