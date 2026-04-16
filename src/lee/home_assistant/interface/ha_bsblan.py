"""ha_bsblan.py - BSBLan Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BsblanRouter(BaseFallbackRouter):
    """Router for BSBLan operations."""

    def __init__(self):
        super().__init__(
            interface_name="BSBLan",
            import_path="lee.home_assistant.ha_bsblan.ha_bsblan_core",
            function_names=[
                "sync_time_impl",
                "set_hot_water_schedule_impl",
            ]
        )


_bsblan_router = _BsblanRouter()


def execute_bsblan_operation(operation: str, **kwargs: Any) -> Any:
    """Execute BSBLan operation using dispatch dictionary.

    Args:
        operation: Operation name from BSBLAN_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _bsblan_router.execute(operation, **kwargs)
