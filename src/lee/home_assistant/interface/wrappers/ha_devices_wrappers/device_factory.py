"""device_factory.py
Version: 2026-04-06
Purpose: Factory-generated device wrappers
License: Apache 2.0

This module contains factory-generated wrapper functions that eliminate code duplication.
"""

# Import helper functions
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.device_helpers import (
    _create_device_wrapper,
)

# Import implementation functions
try:
    from lee.home_assistant.ha_devices.ha_devices_generic import (
        get_states_impl,
        get_by_id_impl,
        update_state_impl,
        call_service_impl,
        list_by_domain_impl,
    )
except ImportError:
    pass

# Factory-generated wrapper for get_states
get_states = _create_device_wrapper(
    get_states_impl,
    "get_states",
    log_params=["entity_ids", "use_cache"]
)
get_states.__doc__ = """Get entity states."""
get_states.__annotations__ = {
    "entity_ids": "Optional[list[str]]",
    "use_cache": "bool",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}

# Factory-generated wrapper for get_by_id
get_by_id = _create_device_wrapper(
    get_by_id_impl,
    "get_by_id",
    log_params=["entity_id"]
)
get_by_id.__doc__ = """Get device by ID."""
get_by_id.__annotations__ = {
    "entity_id": "str",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}

# Factory-generated wrapper for update_state
update_state = _create_device_wrapper(
    update_state_impl,
    "update_state",
    log_params=["entity_id"]
)
update_state.__doc__ = """Update device state."""
update_state.__annotations__ = {
    "entity_id": "str",
    "state_data": "dict[str, Any]",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}

# Factory-generated wrapper for call_service
call_service = _create_device_wrapper(
    call_service_impl,
    "call_service",
    log_params=["domain", "service", "entity_id"]
)
call_service.__doc__ = """Call HA service."""
call_service.__annotations__ = {
    "domain": "str",
    "service": "str",
    "entity_id": "Optional[str]",
    "service_data": "Optional[dict]",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}

# Factory-generated wrapper for list_by_domain
list_by_domain = _create_device_wrapper(
    list_by_domain_impl,
    "list_by_domain",
    log_params=["domain"]
)
list_by_domain.__doc__ = """List devices by domain."""
list_by_domain.__annotations__ = {
    "domain": "str",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}
