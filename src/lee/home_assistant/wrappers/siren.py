"""Siren Wrapper Functions Namespace

Provides direct access to siren device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import siren

    # Get all sirens
    sirens = siren.get_sirens()

    # Turn on siren
    siren.turn_on(entity_id='siren.alarm')

    # Toggle siren
    siren.toggle(entity_id='siren.alarm')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for siren operations
get_sirens = LazyFunctionProxy('interface.ha_siren', 'list_sirens')
turn_on = LazyFunctionProxy('interface.ha_siren', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_siren', 'turn_off')
toggle = LazyFunctionProxy('interface.ha_siren', 'toggle')

__all__ = [
    'get_sirens',
    'turn_on',
    'turn_off',
    'toggle',
]
