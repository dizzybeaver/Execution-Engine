"""ha_siren.py - Router for Siren Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _SirenRouter(BaseFallbackRouter):
    """Router for Siren interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Siren",
            import_path="lee.home_assistant.ha_siren.ha_siren_core",
            function_names=[]
        )


_ha_siren_router = _SirenRouter()


def execute_ha_siren_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Siren interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_siren_router.execute(operation, **kwargs)


def list_ha_siren_operations() -> list[str]:
    """List all available Siren operations.

    Returns:
        List of operation names
    """
    return _ha_siren_router.list_operations()


__all__ = [
    "execute_ha_siren_operation",
    "list_ha_siren_operations",
]
