"""ha_icloud.py - iCloud Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_icloud import ha_icloud_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _IcloudRouter(BaseSimpleDispatchRouter):
    """Router for iCloud interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="iCloud",
            core_module=ha_icloud_core,
            dispatch_map={
                "update": ha_icloud_core.update_impl,
                "play_sound": ha_icloud_core.play_sound_impl,
                "display_message": ha_icloud_core.display_message_impl,
                "lost_device": ha_icloud_core.lost_device_impl,
            }
        )


_icloud_router = _IcloudRouter()


def execute_icloud_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch iCloud interface operations using DD-1 pattern."""
    return _icloud_router.execute(operation, **kwargs)
