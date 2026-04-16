"""ha_script.py - Router for Script Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ScriptRouter(BaseFallbackRouter):
    """Router for Script interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Script",
            import_path="lee.home_assistant.ha_script.ha_script_core",
            function_names=[]
        )


_ha_script_router = _ScriptRouter()


def execute_ha_script_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Script interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_script_router.execute(operation, **kwargs)


def list_ha_script_operations() -> list[str]:
    """List all available Script operations.

    Returns:
        List of operation names
    """
    return _ha_script_router.list_operations()


__all__ = [
    "execute_ha_script_operation",
    "list_ha_script_operations",
]
