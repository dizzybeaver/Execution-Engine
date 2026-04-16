"""Fan Wrapper Functions Namespace

Provides direct access to fan device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import fan

    # Get all fans
    fans = fan.get_fans()

    # Turn on fan
    fan.turn_on(entity_id='fan.living_room')

    # Set fan speed
    fan.set_speed(entity_id='fan.living_room', speed='high')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for fan operations
get_fans = LazyFunctionProxy('interface.ha_fan', 'list_fans')
turn_on = LazyFunctionProxy('interface.ha_fan', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_fan', 'turn_off')
toggle = LazyFunctionProxy('interface.ha_fan', 'toggle')
set_speed = LazyFunctionProxy('interface.ha_fan', 'set_speed')
set_percentage = LazyFunctionProxy('interface.ha_fan', 'set_percentage')
increase_speed = LazyFunctionProxy('interface.ha_fan', 'increase_speed')

__all__ = [
    'get_fans',
    'turn_on',
    'turn_off',
    'toggle',
    'set_speed',
    'set_percentage',
    'increase_speed',
]
