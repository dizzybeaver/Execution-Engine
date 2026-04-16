"""ha_hue - Philips Hue Interface.

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_hue.ha_hue_core import (
    activate_scene_impl,
    hue_activate_scene_impl,
)

__all__ = [
    "activate_scene_impl",
    "hue_activate_scene_impl",
]
