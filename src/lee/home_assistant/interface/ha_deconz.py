"""ha_deconz.py - deCONZ Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _DeconzRouter(BaseFallbackRouter):
    """Router for deCONZ interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="deCONZ",
            import_path="lee.home_assistant.ha_deconz.ha_deconz_core",
            function_names=[
                "configure_impl",
                "device_refresh_impl",
                "remove_orphaned_entries_impl",
            ]
        )


_deconz_router = _DeconzRouter()


def execute_deconz_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch deCONZ interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _deconz_router.execute(operation, **kwargs)
