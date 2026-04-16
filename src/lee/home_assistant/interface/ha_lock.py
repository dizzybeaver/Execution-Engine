"""ha_lock.py - Router for Lock Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _LockRouter(BaseFallbackRouter):
    """Router for Lock interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Lock",
            import_path="lee.home_assistant.ha_lock.ha_lock_core",
            function_names=[]
        )


_ha_lock_router = _LockRouter()


def execute_ha_lock_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Lock interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_lock_router.execute(operation, **kwargs)


def list_ha_lock_operations() -> list[str]:
    """List all available Lock operations.

    Returns:
        List of operation names
    """
    return _ha_lock_router.list_operations()


__all__ = [
    "execute_ha_lock_operation",
    "list_ha_lock_operations",
]
