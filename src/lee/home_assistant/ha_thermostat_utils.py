# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Create shared thermostat utilities


"""ha_thermostat_utils.py - Thermostat Utilities

Version: 2026-04-10_1
Description: Shared utilities for thermostat operations across LEE.
Eliminates duplicate code between directive handlers and state reporting.

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Thermostat mode mapping constants
THERMOSTAT_MODE_MAP = {
    "heat": "HEAT",
    "cool": "COOL",
    "auto": "AUTO",
    "off": "OFF",
    "heat_cool": "AUTO",
}


def map_ha_to_alexa_thermostat_mode(ha_mode: str) -> str:
    """Map Home Assistant thermostat mode to Alexa mode.

    Args:
        ha_mode: Home Assistant thermostat mode

    Returns:
        Alexa thermostat mode
    """
    return THERMOSTAT_MODE_MAP.get(ha_mode, "OFF")


__all__ = [
    "THERMOSTAT_MODE_MAP",
    "map_ha_to_alexa_thermostat_mode",
]
