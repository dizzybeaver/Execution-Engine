"""ha_tplink.py - TP-Link Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_tplink import ha_tplink_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _TplinkRouter(BaseSimpleDispatchRouter):
    """Router for TP-Link interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="TP-Link",
            core_module=ha_tplink_core,
            dispatch_map={
                "sequence_effect": ha_tplink_core.sequence_effect_impl,
                "random_effect": ha_tplink_core.random_effect_impl,
            }
        )


_tplink_router = _TplinkRouter()


def execute_tplink_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch TP-Link interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _tplink_router.execute(operation, **kwargs)
