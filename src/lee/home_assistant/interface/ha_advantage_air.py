"""ha_advantage_air.py - Router for AdvantageAir Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AdvantageAirRouter(BaseFallbackRouter):
    """Router for AdvantageAir interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AdvantageAir",
            import_path="lee.home_assistant.ha_advantage_air.ha_advantage_air_core",
            function_names=[]
        )


_advantage_air_router = _AdvantageAirRouter()


def execute_advantage_air_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch AdvantageAir interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _advantage_air_router.execute(operation, **kwargs)


def list_advantage_air_operations() -> list[str]:
    """List all available AdvantageAir operations.

    Returns:
        List of operation names
    """
    return _advantage_air_router.list_operations()


__all__ = [
    "execute_advantage_air_operation",
    "list_advantage_air_operations",
]
