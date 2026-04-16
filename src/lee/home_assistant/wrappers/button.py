"""Button Wrapper Functions Namespace

Provides direct access to button device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import button

    # Get all buttons
    buttons = button.get_buttons()

    # Press button
    button.press(entity_id='button.garage_door_opener')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for button operations
get_buttons = LazyFunctionProxy('interface.ha_button', 'list_buttons')
press = LazyFunctionProxy('interface.ha_button', 'press')

__all__ = [
    'get_buttons',
    'press',
]
