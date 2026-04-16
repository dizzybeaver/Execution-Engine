"""ha_adguard.py - Router for Adguard Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AdguardRouter(BaseFallbackRouter):
    """Router for Adguard interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Adguard",
            import_path="lee.home_assistant.ha_adguard.ha_adguard_core",
            function_names=[]
        )


_adguard_router = _AdguardRouter()


def execute_adguard_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Adguard interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _adguard_router.execute(operation, **kwargs)


def list_adguard_operations() -> list[str]:
    """List all available Adguard operations.

    Returns:
        List of operation names
    """
    return _adguard_router.list_operations()


__all__ = [
    "execute_adguard_operation",
    "list_adguard_operations",
]
