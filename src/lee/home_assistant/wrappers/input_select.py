"""Input Select Wrapper Functions Namespace

Provides direct access to input_select device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import input_select

    # Get all input selects
    selects = input_select.get_input_selects()

    # Select option
    input_select.select_option(entity_id='input_select.mode', option='Home')

    # Navigate options
    input_select.previous_option(entity_id='input_select.mode')
    input_select.next_option(entity_id='input_select.mode')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for input_select operations
get_input_selects = LazyFunctionProxy('interface.ha_input_select', 'list_input_selects')
select_option = LazyFunctionProxy('interface.ha_input_select', 'select_option')
previous_option = LazyFunctionProxy('interface.ha_input_select', 'select_previous_option')
next_option = LazyFunctionProxy('interface.ha_input_select', 'select_next_option')
reload = LazyFunctionProxy('interface.ha_input_select', 'reload_input_selects')

__all__ = [
    'get_input_selects',
    'select_option',
    'previous_option',
    'next_option',
    'reload',
]
