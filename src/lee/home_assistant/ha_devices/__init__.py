# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Home Assistant Devices module with batch operations

"""ha_devices - Home Assistant Devices module

Provides device state management and service call operations with
batch support for multiple operations in single HA requests.
"""

from lee.home_assistant.ha_devices.ha_devices_generic import (
    call_service_batch_impl,
    call_service_impl,
    check_status_impl,
    find_fuzzy_impl,
    get_by_id_impl,
    get_states_batch_impl,
    get_states_impl,
    list_by_domain_impl,
    update_state_impl,
)

__all__ = [
    "call_service_batch_impl",
    "call_service_impl",
    "check_status_impl",
    "find_fuzzy_impl",
    "get_by_id_impl",
    "get_states_batch_impl",
    "get_states_impl",
    "list_by_domain_impl",
    "update_state_impl",
]
