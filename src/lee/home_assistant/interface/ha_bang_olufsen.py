"""ha_bang_olufsen.py - Router for BangOlufsen Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BangOlufsenRouter(BaseFallbackRouter):
    """Router for BangOlufsen interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="BangOlufsen",
            import_path="lee.home_assistant.ha_bang_olufsen.ha_bang_olufsen_core",
            function_names=[]
        )


_bang_olufsen_router = _BangOlufsenRouter()


def execute_bang_olufsen_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch BangOlufsen interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _bang_olufsen_router.execute(operation, **kwargs)


def list_bang_olufsen_operations() -> list[str]:
    """List all available BangOlufsen operations.

    Returns:
        List of operation names
    """
    return _bang_olufsen_router.list_operations()


__all__ = [
    "execute_bang_olufsen_operation",
    "list_bang_olufsen_operations",
]
