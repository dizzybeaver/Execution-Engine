"""ha_amcrest.py - Router for Amcrest Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AmcrestRouter(BaseFallbackRouter):
    """Router for Amcrest interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Amcrest",
            import_path="lee.home_assistant.ha_amcrest.ha_amcrest_core",
            function_names=[]
        )


_amcrest_router = _AmcrestRouter()


def execute_amcrest_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Amcrest interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _amcrest_router.execute(operation, **kwargs)


def list_amcrest_operations() -> list[str]:
    """List all available Amcrest operations.

    Returns:
        List of operation names
    """
    return _amcrest_router.list_operations()


__all__ = [
    "execute_amcrest_operation",
    "list_amcrest_operations",
]
