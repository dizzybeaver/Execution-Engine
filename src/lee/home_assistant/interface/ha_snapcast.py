"""ha_snapcast.py - Snapcast Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_snapcast import ha_snapcast_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _SnapcastRouter(BaseSimpleDispatchRouter):
    """Router for Snapcast interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Snapcast",
            core_module=ha_snapcast_core,
            dispatch_map={
                "snapshot": ha_snapcast_core.snapshot_impl,
                "restore": ha_snapcast_core.restore_impl,
                "set_latency": ha_snapcast_core.set_latency_impl,
            }
        )


_snapcast_router = _SnapcastRouter()


def execute_snapcast_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Snapcast interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _snapcast_router.execute(operation, **kwargs)
