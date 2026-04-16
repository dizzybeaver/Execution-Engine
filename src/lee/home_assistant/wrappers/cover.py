"""Cover Wrapper Functions Namespace

Provides direct access to cover/blinds device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import cover

    # Get all covers
    covers = cover.get_covers()

    # Open cover
    cover.open(entity_id='cover.living_room_blinds')

    # Set position
    cover.set_position(entity_id='cover.living_room_blinds', position=50)
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for cover operations
get_covers = LazyFunctionProxy('interface.ha_cover', 'get_covers')
open = LazyFunctionProxy('interface.ha_cover', 'open')  # pylint: disable=redefined-builtin
close = LazyFunctionProxy('interface.ha_cover', 'close')
toggle = LazyFunctionProxy('interface.ha_cover', 'toggle')
set_position = LazyFunctionProxy('interface.ha_cover', 'set_position')
stop = LazyFunctionProxy('interface.ha_cover', 'stop')

__all__ = [
    'get_covers',
    'open',
    'close',
    'toggle',
    'set_position',
    'stop',
]
