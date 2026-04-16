"""ha_cast.py - Router for Cast Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _CastRouter(BaseFallbackRouter):
    """Router for Cast interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Cast",
            import_path="lee.home_assistant.ha_cast.ha_cast_core",
            function_names=[]
        )


_cast_router = _CastRouter()


def execute_cast_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Cast interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _cast_router.execute(operation, **kwargs)


def list_cast_operations() -> list[str]:
    """List all available Cast operations.

    Returns:
        List of operation names
    """
    return _cast_router.list_operations()


__all__ = [
    "execute_cast_operation",
    "list_cast_operations",
]
