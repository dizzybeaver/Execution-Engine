"""ha_number.py - Router for Number Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _NumberRouter(BaseFallbackRouter):
    """Router for Number interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Number",
            import_path="lee.home_assistant.ha_number.ha_number_core",
            function_names=["get_device_class_units_impl"]
        )


_ha_number_router = _NumberRouter()


def execute_ha_number_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Number interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_number_router.execute(operation, **kwargs)


def list_ha_number_operations() -> list[str]:
    """List all available Number operations.

    Returns:
        List of operation names
    """
    return _ha_number_router.list_operations()


# Export router availability flag
HAS_NUMBER = _ha_number_router.is_available()


__all__ = [
    "execute_ha_number_operation",
    "list_ha_number_operations",
    "HAS_NUMBER",
]
