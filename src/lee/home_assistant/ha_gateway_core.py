# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_gateway_core.py - Home Assistant Gateway Core (Alias)
Version: 2025-03-02_1
Purpose: Core gateway implementation - re-exports from ha_gateway_generic

This file serves as an alias/re-export layer for the HA gateway core implementation.
The actual implementation is in ha_gateway_generic.py.

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

# Re-export all core functionality from ha_gateway_generic
from lee.home_assistant.ha_gateway_generic import (
    _INTERFACE_ROUTERS,
    HAGatewayInterface,
    clear_ha_fast_path_cache,
    disable_ha_fast_path,
    enable_ha_fast_path,
    get_ha_gateway_stats,
    ha_execute_operation,
    reset_ha_gateway_state,
)

__all__ = [
    "_INTERFACE_ROUTERS",
    "HAGatewayInterface",
    "clear_ha_fast_path_cache",
    "disable_ha_fast_path",
    "enable_ha_fast_path",
    "get_ha_gateway_stats",
    "ha_execute_operation",
    "reset_ha_gateway_state",
]

# EOF
