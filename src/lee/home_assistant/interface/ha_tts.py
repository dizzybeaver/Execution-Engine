"""ha_tts.py - Router for Tts Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _TtsRouter(BaseFallbackRouter):
    """Router for Tts interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Tts",
            import_path="lee.home_assistant.ha_tts.ha_tts_core",
            function_names=[]
        )


_ha_tts_router = _TtsRouter()


def execute_ha_tts_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Tts interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_tts_router.execute(operation, **kwargs)


def list_ha_tts_operations() -> list[str]:
    """List all available Tts operations.

    Returns:
        List of operation names
    """
    return _ha_tts_router.list_operations()


__all__ = [
    "execute_ha_tts_operation",
    "list_ha_tts_operations",
]
