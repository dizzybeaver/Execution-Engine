"""Devices Wrapper Functions Namespace

59 functions for device state management and control.
All functions load lazily via LazyFunctionProxy.

Usage:
    from lee.home_assistant.wrappers import devices

    # Get all states
    states = devices.get_states(domain='light')

    # Get specific entity
    state = devices.get_by_id('light.bubs_bedroom_inside_light_switch_1')

    # Call service
    devices.call_service('light', 'turn_on', entity_id='light.bubs_bedroom_inside_light_switch_1')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Core device operations
get_states = LazyFunctionProxy('interface.ha_devices', 'get_states')
get_by_id = LazyFunctionProxy('interface.ha_devices', 'get_by_id')
call_service = LazyFunctionProxy('interface.ha_devices', 'call_service')

# Convenience functions
turn_on = LazyFunctionProxy('interface.ha_devices', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_devices', 'turn_off')
toggle = LazyFunctionProxy('interface.ha_devices', 'toggle')

# Batch operations
batch_call = LazyFunctionProxy('interface.ha_devices', 'batch_call')

# Service call with response
call_service_with_response = LazyFunctionProxy('interface.ha_devices', 'call_service_with_response')

# Status and discovery
check_status = LazyFunctionProxy('interface.ha_devices', 'check_status')

__all__ = [
    'get_states',
    'get_by_id',
    'call_service',
    'turn_on',
    'turn_off',
    'toggle',
    'batch_call',
    'call_service_with_response',
    'check_status',
]
