"""ha_ecovacs.py - Ecovacs Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _EcovacsRouter(BaseFallbackRouter):
    """Router for Ecovacs interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Ecovacs",
            import_path="lee.home_assistant.ha_ecovacs.ha_ecovacs_core",
            function_names=[
                "raw_get_positions_impl",
            ]
        )


_ecovacs_router = _EcovacsRouter()


def execute_ecovacs_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Ecovacs interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ecovacs_router.execute(operation, **kwargs)
