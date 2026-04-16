"""ha_sonos.py - Sonos Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_sonos import ha_sonos_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _SonosRouter(BaseSimpleDispatchRouter):
    """Router for Sonos interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Sonos",
            core_module=ha_sonos_core,
            dispatch_map={
                "snapshot": ha_sonos_core.snapshot_impl,
                "restore": ha_sonos_core.restore_impl,
                "set_sleep_timer": ha_sonos_core.set_sleep_timer_impl,
                "clear_sleep_timer": ha_sonos_core.clear_sleep_timer_impl,
                "play_queue": ha_sonos_core.play_queue_impl,
                "remove_from_queue": ha_sonos_core.remove_from_queue_impl,
                "get_queue": ha_sonos_core.get_queue_impl,
                "update_alarm": ha_sonos_core.update_alarm_impl,
            }
        )


_sonos_router = _SonosRouter()


def execute_sonos_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Sonos interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _sonos_router.execute(operation, **kwargs)
