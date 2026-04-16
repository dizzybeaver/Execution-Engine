"""ha_androidtv.py - Router for Androidtv Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AndroidtvRouter(BaseFallbackRouter):
    """Router for Androidtv interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Androidtv",
            import_path="lee.home_assistant.ha_androidtv.ha_androidtv_core",
            function_names=[]
        )


_androidtv_router = _AndroidtvRouter()


def execute_androidtv_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Androidtv interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _androidtv_router.execute(operation, **kwargs)


def list_androidtv_operations() -> list[str]:
    """List all available Androidtv operations.

    Returns:
        List of operation names
    """
    return _androidtv_router.list_operations()


__all__ = [
    "execute_androidtv_operation",
    "list_androidtv_operations",
]
