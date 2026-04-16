# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_energy - Home Assistant Energy Interface

This module provides energy management operations including:
- Energy preferences management
- Energy information and validation
- Solar forecasting
- Fossil fuel energy consumption tracking

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_energy.ha_energy_core import (
    get_energy_info_impl,
    get_energy_preferences_impl,
    get_fossil_energy_consumption_impl,
    get_solar_forecast_impl,
    save_energy_preferences_impl,
    validate_energy_config_impl,
)

__all__ = [
    "get_energy_preferences_impl",
    "save_energy_preferences_impl",
    "get_energy_info_impl",
    "validate_energy_config_impl",
    "get_solar_forecast_impl",
    "get_fossil_energy_consumption_impl",
]
