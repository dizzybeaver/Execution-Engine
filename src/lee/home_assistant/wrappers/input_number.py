"""Input Number Wrapper Functions Namespace

Provides direct access to input_number device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import input_number

    # Get all input numbers
    numbers = input_number.get_input_numbers()

    # Set value
    input_number.set_value(entity_id='input_number.target_temp', value=22)

    # Increment value
    input_number.increment(entity_id='input_number.target_temp')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for input_number operations
get_input_numbers = LazyFunctionProxy('interface.ha_input_number', 'list_input_numbers')
set_value = LazyFunctionProxy('interface.ha_input_number', 'set_value')
increment = LazyFunctionProxy('interface.ha_input_number', 'increment')
decrement = LazyFunctionProxy('interface.ha_input_number', 'decrement')
reload = LazyFunctionProxy('interface.ha_input_number', 'reload')

__all__ = [
    'get_input_numbers',
    'set_value',
    'increment',
    'decrement',
    'reload',
]
