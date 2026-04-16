"""ha_vizio.py - Vizio TV Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_vizio import ha_vizio_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _VizioRouter(BaseSimpleDispatchRouter):
    """Router for Vizio interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Vizio",
            core_module=ha_vizio_core,
            dispatch_map={
                "update_setting": ha_vizio_core.update_setting_impl,
            }
        )


_vizio_router = _VizioRouter()


def execute_vizio_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Vizio interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _vizio_router.execute(operation, **kwargs)
