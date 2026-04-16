"""ha_wake_on_lan.py - WAKE_ON_LAN Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_wake_on_lan import ha_wake_on_lan_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _WakeOnLanRouter(BaseSimpleDispatchRouter):
    """Router for WAKE_ON_LAN interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="WAKE_ON_LAN",
            core_module=ha_wake_on_lan_core,
            dispatch_map={
                "send_magic_packet": ha_wake_on_lan_core.send_magic_packet_impl,
            }
        )


_wake_on_lan_router = _WakeOnLanRouter()


def execute_wake_on_lan_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch WAKE_ON_LAN interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _wake_on_lan_router.execute(operation, **kwargs)
