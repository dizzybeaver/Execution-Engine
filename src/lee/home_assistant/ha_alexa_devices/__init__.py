# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_alexa_devices - Alexa Devices module

Version: 2026-03-25_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0

This module provides Alexa device discovery and control functionality.
"""

from lee.home_assistant.ha_alexa_devices.ha_alexa_devices_core import (
    AlexaDevicesCore,
    discover_alexa_devices_impl,
    get_alexa_device_state_impl,
    send_info_skill_impl,
    send_sound_impl,
    send_text_command_impl,
)

__all__ = [
    "AlexaDevicesCore",
    "send_text_command_impl",
    "send_sound_impl",
    "send_info_skill_impl",
    "discover_alexa_devices_impl",
    "get_alexa_device_state_impl",
]
