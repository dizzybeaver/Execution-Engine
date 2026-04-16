"""ha_sun - Sun integration for Home Assistant.

Provides sun position and timing data for automation.
"""

from lee.home_assistant.ha_sun.ha_sun_core import (
    get_sun_state_impl,
    get_sunrise_time_impl,
    get_sunset_time_impl,
)

__all__ = [
    "get_sun_state_impl",
    "get_sunrise_time_impl",
    "get_sunset_time_impl",
]
