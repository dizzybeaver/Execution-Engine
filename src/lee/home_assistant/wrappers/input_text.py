"""Input Text Wrapper Functions Namespace

Provides direct access to input_text device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import input_text

    # Get all input texts
    texts = input_text.get_input_texts()

    # Set value
    input_text.set_value(entity_id='input_text.message', value='Hello World')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for input_text operations
get_input_texts = LazyFunctionProxy('interface.ha_input_text', 'list')
set_value = LazyFunctionProxy('interface.ha_input_text', 'set_value')
reload = LazyFunctionProxy('interface.ha_input_text', 'reload')

__all__ = [
    'get_input_texts',
    'set_value',
    'reload',
]
