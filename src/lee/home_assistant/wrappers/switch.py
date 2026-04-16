"""Switch Wrapper Functions Namespace

Provides direct access to switch device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import switch

    # Get all switches
    switches = switch.get_switches()

    # Turn on switch
    switch.turn_on(entity_id='switch.plug')

    # Toggle switch
    switch.toggle(entity_id='switch.plug')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for switch operations
get_switches = LazyFunctionProxy('interface.ha_switch', 'get_switches')
turn_on = LazyFunctionProxy('interface.ha_switch', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_switch', 'turn_off')
toggle = LazyFunctionProxy('interface.ha_switch', 'toggle')

__all__ = [
    'get_switches',
    'turn_on',
    'turn_off',
    'toggle',
]
