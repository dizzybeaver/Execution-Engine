"""ha_alarmdecoder.py - Router for Alarmdecoder Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AlarmdecoderRouter(BaseFallbackRouter):
    """Router for Alarmdecoder interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Alarmdecoder",
            import_path="lee.home_assistant.ha_alarmdecoder.ha_alarmdecoder_core",
            function_names=[]
        )


_alarmdecoder_router = _AlarmdecoderRouter()


def execute_alarmdecoder_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Alarmdecoder interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _alarmdecoder_router.execute(operation, **kwargs)


def list_alarmdecoder_operations() -> list[str]:
    """List all available Alarmdecoder operations.

    Returns:
        List of operation names
    """
    return _alarmdecoder_router.list_operations()


__all__ = [
    "execute_alarmdecoder_operation",
    "list_alarmdecoder_operations",
]
