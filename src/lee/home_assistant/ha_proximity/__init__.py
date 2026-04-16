"""ha_proximity - Proximity integration for Home Assistant.

Provides proximity zone tracking and distance monitoring.
"""

from lee.home_assistant.ha_proximity.ha_proximity_core import (
    get_proximity_state_impl,
    list_proximity_zones_impl,
    set_proximity_zone_impl,
)

__all__ = [
    "get_proximity_state_impl",
    "list_proximity_zones_impl",
    "set_proximity_zone_impl",
]
