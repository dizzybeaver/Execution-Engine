"""ha_alexa_devices.py - Alexa Devices Router

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_alexa_devices import ha_alexa_devices_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Dispatch dictionary for O(1) operation routing
_ALEXA_DEVICES_DISPATCH = {
    "send_text_command": ha_alexa_devices_core.send_text_command_impl,
    "send_sound": ha_alexa_devices_core.send_sound_impl,
    "send_info_skill": ha_alexa_devices_core.send_info_skill_impl,
    "discover_devices": ha_alexa_devices_core.discover_alexa_devices_impl,
    "get_device_state": ha_alexa_devices_core.get_alexa_device_state_impl,
}


class _AlexaDevicesRouter(BaseSimpleDispatchRouter):
    """Router for Alexa Devices interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Alexa Devices",
            core_module=DummyModule(),
            dispatch_map=_ALEXA_DEVICES_DISPATCH
        )


_alexa_devices_router = _AlexaDevicesRouter()


def execute_alexa_devices_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Alexa Devices operation using dispatch dictionary.

    Args:
        operation: Operation name from ALEXA_DEVICES_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function
    """
    return _alexa_devices_router.execute(operation, **kwargs)


__all__ = ["execute_alexa_devices_operation"]
