"""Input Boolean Wrapper Functions Namespace

Provides direct access to input_boolean device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import input_boolean

    # Get all input booleans
    booleans = input_boolean.get_input_booleans()

    # Turn on input boolean
    input_boolean.turn_on(entity_id='input_boolean.guest_mode')

    # Toggle input boolean
    input_boolean.toggle(entity_id='input_boolean.guest_mode')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for input_boolean operations
get_input_booleans = LazyFunctionProxy('interface.ha_input_boolean', 'list_input_booleans')
turn_on = LazyFunctionProxy('interface.ha_input_boolean', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_input_boolean', 'turn_off')
toggle = LazyFunctionProxy('interface.ha_input_boolean', 'toggle')
reload = LazyFunctionProxy('interface.ha_input_boolean', 'reload')

__all__ = [
    'get_input_booleans',
    'turn_on',
    'turn_off',
    'toggle',
    'reload',
]
