"""ha_mobile_app.py - Router for MobileApp Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _MobileAppRouter(BaseFallbackRouter):
    """Router for MobileApp interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="MobileApp",
            import_path="lee.home_assistant.ha_mobile_app.ha_mobile_app_core",
            function_names=[]
        )


_ha_mobile_app_router = _MobileAppRouter()


def execute_ha_mobile_app_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch MobileApp interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_mobile_app_router.execute(operation, **kwargs)


def list_ha_mobile_app_operations() -> list[str]:
    """List all available MobileApp operations.

    Returns:
        List of operation names
    """
    return _ha_mobile_app_router.list_operations()


__all__ = [
    "execute_ha_mobile_app_operation",
    "list_ha_mobile_app_operations",
]
