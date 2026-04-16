"""ha_logbook.py - Router for Logbook Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _LogbookRouter(BaseFallbackRouter):
    """Router for Logbook interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Logbook",
            import_path="lee.home_assistant.ha_logbook.ha_logbook_core",
            function_names=[]
        )


_ha_logbook_router = _LogbookRouter()


def execute_ha_logbook_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Logbook interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_logbook_router.execute(operation, **kwargs)


def list_ha_logbook_operations() -> list[str]:
    """List all available Logbook operations.

    Returns:
        List of operation names
    """
    return _ha_logbook_router.list_operations()


__all__ = [
    "execute_ha_logbook_operation",
    "list_ha_logbook_operations",
]
