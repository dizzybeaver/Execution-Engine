"""Group Wrapper Functions Namespace

Provides direct access to group device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import group

    # Get all groups
    groups = group.get_groups()

    # Set group state
    group.set(entity_id='group.all_lights', state='on')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for group operations
get_groups = LazyFunctionProxy('interface.ha_group', 'list_groups')
set = LazyFunctionProxy('interface.ha_group', 'set')  # pylint: disable=redefined-builtin
reload = LazyFunctionProxy('interface.ha_group', 'reload')

__all__ = [
    'get_groups',
    'set',
    'reload',
]
