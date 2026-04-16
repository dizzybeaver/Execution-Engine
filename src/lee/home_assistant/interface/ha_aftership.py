"""ha_aftership.py - Router for Aftership Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AftershipRouter(BaseFallbackRouter):
    """Router for Aftership interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Aftership",
            import_path="lee.home_assistant.ha_aftership.ha_aftership_core",
            function_names=[]
        )


_aftership_router = _AftershipRouter()


def execute_aftership_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Aftership interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _aftership_router.execute(operation, **kwargs)


def list_aftership_operations() -> list[str]:
    """List all available Aftership operations.

    Returns:
        List of operation names
    """
    return _aftership_router.list_operations()


__all__ = [
    "execute_aftership_operation",
    "list_aftership_operations",
]
