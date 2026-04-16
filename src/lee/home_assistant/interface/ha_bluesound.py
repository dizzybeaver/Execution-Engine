"""ha_bluesound.py - Bluesound Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BluesoundRouter(BaseFallbackRouter):
    """Router for Bluesound interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Bluesound",
            import_path="lee.home_assistant.ha_bluesound.ha_bluesound_core",
            function_names=[
                "join_impl",
                "unjoin_impl",
            ]
        )


_bluesound_router = _BluesoundRouter()


def execute_bluesound_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Bluesound interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _bluesound_router.execute(operation, **kwargs)
