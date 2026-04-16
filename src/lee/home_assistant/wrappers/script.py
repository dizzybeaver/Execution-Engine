"""Script Wrapper Functions Namespace

Provides direct access to script device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import script

    # Get all scripts
    scripts = script.get_scripts()

    # Execute script
    script.turn_on(entity_id='script.good_night')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for script operations
get_scripts = LazyFunctionProxy('interface.ha_script', 'list')
turn_on = LazyFunctionProxy('interface.ha_script', 'turn_on')
reload = LazyFunctionProxy('interface.ha_script', 'reload')

__all__ = [
    'get_scripts',
    'turn_on',
    'reload',
]
