"""ha_wemo.py - WeMo Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_wemo import ha_wemo_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _WemoRouter(BaseSimpleDispatchRouter):
    """Router for WeMo interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="WeMo",
            core_module=ha_wemo_core,
            dispatch_map={
                "set_humidity": ha_wemo_core.set_humidity_impl,
                "reset_filter_life": ha_wemo_core.reset_filter_life_impl,
            }
        )


_wemo_router = _WemoRouter()


def execute_wemo_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch WeMo interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _wemo_router.execute(operation, **kwargs)
