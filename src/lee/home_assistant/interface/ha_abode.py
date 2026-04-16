"""ha_abode.py - Router for Abode Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AbodeRouter(BaseFallbackRouter):
    """Router for Abode interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Abode",
            import_path="lee.home_assistant.ha_abode.ha_abode_core",
            function_names=[]
        )


_abode_router = _AbodeRouter()


def execute_abode_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Abode interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _abode_router.execute(operation, **kwargs)


def list_abode_operations() -> list[str]:
    """List all available Abode operations.

    Returns:
        List of operation names
    """
    return _abode_router.list_operations()


__all__ = [
    "execute_abode_operation",
    "list_abode_operations",
]
