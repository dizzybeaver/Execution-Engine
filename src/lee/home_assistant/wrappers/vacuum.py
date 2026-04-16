"""Vacuum Wrapper Functions Namespace

Provides direct access to vacuum device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import vacuum

    # Get all vacuums
    vacuums = vacuum.get_vacuums()

    # Start cleaning
    vacuum.start(entity_id='vacuum.roborock')

    # Return to base
    vacuum.return_to_base(entity_id='vacuum.roborock')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for vacuum operations
get_vacuums = LazyFunctionProxy('interface.ha_vacuum', 'list_vacuums')
start = LazyFunctionProxy('interface.ha_vacuum', 'start')
pause = LazyFunctionProxy('interface.ha_vacuum', 'pause')
stop = LazyFunctionProxy('interface.ha_vacuum', 'stop')
return_to_base = LazyFunctionProxy('interface.ha_vacuum', 'return_to_base')
clean_spot = LazyFunctionProxy('interface.ha_vacuum', 'clean_spot')
locate = LazyFunctionProxy('interface.ha_vacuum', 'locate')

__all__ = [
    'get_vacuums',
    'start',
    'pause',
    'stop',
    'return_to_base',
    'clean_spot',
    'locate',
]
