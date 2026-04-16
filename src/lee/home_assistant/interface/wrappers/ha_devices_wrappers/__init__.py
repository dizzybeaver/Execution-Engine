"""ha_devices_wrappers package
Version: 2026-04-11
Purpose: Device interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Devices router.
External modules MUST use execute_devices_operation() instead of importing
directly.

This package provides backward compatibility by re-exporting all wrapper
functions.

The original 1,878-line file has been split into focused domain modules:
- ha_devices_core.py: Core operations (factory-generated, batch, cache, config)
- ha_state_management.py: State management operations
- ha_service_calls.py: Service call operations
- ha_device_management.py: Device and entity management
- ha_utilities.py: Utility and validation operations
- device_helpers.py: Helper functions and factory pattern
- device_factory.py: Factory-generated wrappers

All functions are re-exported here for backward compatibility.
"""

# Import from core module (factory-generated, batch, cache, config)
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.ha_devices_core import (  # noqa: F401
    get_states,
    get_by_id,
    find_fuzzy,
    update_state,
    call_service,
    list_by_domain,
    check_status,
    call_ha_api,
    get_ha_config,
    warm_cache,
    invalidate_entity_cache,
    invalidate_domain_cache,
    get_performance_report,
    get_diagnostic_info,
    get_states_batch,
    call_service_batch,
)

# Import from state management module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.ha_state_management import (  # noqa: F401
    get_state,
    get_by_type,
    get_by_domain,
    refresh_state,
    subscribe_to_events,
    unsubscribe_from_events,
    get_history,
)

# Import from service calls module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.ha_service_calls import (  # noqa: F401
    batch_call,
    async_call_service,
    turn_on,
    turn_off,
    toggle,
    set_value,
    get_available_services,
    get_service_schema,
    validate_service_call,
    call_service_with_response,
)

# Import from device management module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.ha_device_management import (  # noqa: F401
    get_all_entities,
    get_entity_attributes,
    get_entity_capabilities,
    get_device_info,
    get_device_registry,
    get_area_devices,
    get_entity_registry,
    update_entity_registry,
    remove_entity_registry,
    get_device_by_id,
    get_device_by_name,
    get_devices_by_area,
    get_area_by_id,
    get_all_areas,
    get_floor_info,
)

# Import from utilities module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.ha_utilities import (  # noqa: F401
    validate_entity_id,
    validate_device_id,
    get_device_config,
    set_device_config,
    get_entity_config,
    set_entity_config,
    get_integration_info,
    reload_integration,
)

__all__ = [
    # Core module
    "get_states",
    "get_by_id",
    "find_fuzzy",
    "update_state",
    "call_service",
    "list_by_domain",
    "check_status",
    "call_ha_api",
    "get_ha_config",
    "warm_cache",
    "invalidate_entity_cache",
    "invalidate_domain_cache",
    "get_performance_report",
    "get_diagnostic_info",
    "get_states_batch",
    "call_service_batch",
    # State management
    "get_state",
    "get_by_type",
    "get_by_domain",
    "refresh_state",
    "subscribe_to_events",
    "unsubscribe_from_events",
    "get_history",
    # Service calls
    "batch_call",
    "async_call_service",
    "turn_on",
    "turn_off",
    "toggle",
    "set_value",
    "get_available_services",
    "get_service_schema",
    "validate_service_call",
    "call_service_with_response",
    # Device management
    "get_all_entities",
    "get_entity_attributes",
    "get_entity_capabilities",
    "get_device_info",
    "get_device_registry",
    "get_area_devices",
    "get_entity_registry",
    "update_entity_registry",
    "remove_entity_registry",
    "get_device_by_id",
    "get_device_by_name",
    "get_devices_by_area",
    "get_area_by_id",
    "get_all_areas",
    "get_floor_info",
    # Utilities
    "validate_entity_id",
    "validate_device_id",
    "get_device_config",
    "set_device_config",
    "get_entity_config",
    "set_entity_config",
    "get_integration_info",
    "reload_integration",
]
