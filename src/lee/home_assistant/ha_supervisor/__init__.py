"""ha_supervisor - Home Assistant Supervisor Interface

This module provides supervisor management operations for Home Assistant OS.
"""

from lee.home_assistant.ha_supervisor.ha_supervisor_core import (
    get_addon_info_impl,
    get_core_info_impl,
    get_host_info_impl,
    get_os_info_impl,
    get_supervisor_info_impl,
    list_addons_impl,
    restart_addon_impl,
    start_addon_impl,
    stop_addon_impl,
)

__all__ = [
    "get_supervisor_info_impl",
    "get_host_info_impl",
    "get_core_info_impl",
    "get_os_info_impl",
    "list_addons_impl",
    "get_addon_info_impl",
    "start_addon_impl",
    "stop_addon_impl",
    "restart_addon_impl",
]
