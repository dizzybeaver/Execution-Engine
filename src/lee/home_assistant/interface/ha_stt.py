"""ha_stt.py - Router for Stt Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _SttRouter(BaseFallbackRouter):
    """Router for Stt interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Stt",
            import_path="lee.home_assistant.ha_stt.ha_stt_core",
            function_names=[]
        )


_ha_stt_router = _SttRouter()


def execute_ha_stt_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Stt interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_stt_router.execute(operation, **kwargs)


def list_ha_stt_operations() -> list[str]:
    """List all available Stt operations.

    Returns:
        List of operation names
    """
    return _ha_stt_router.list_operations()


__all__ = [
    "execute_ha_stt_operation",
    "list_ha_stt_operations",
]
