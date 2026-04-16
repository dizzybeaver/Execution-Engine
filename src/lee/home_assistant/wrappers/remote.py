"""Remote Wrapper Functions Namespace

Provides direct access to remote device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import remote

    # Get all remotes
    remotes = remote.get_remotes()

    # Send command
    remote.send_command(entity_id='remote.tv', command='power')

    # Learn command
    remote.learn_command(entity_id='remote.tv', command='volume_up')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for remote operations
get_remotes = LazyFunctionProxy('interface.ha_remote', 'list')
turn_on = LazyFunctionProxy('interface.ha_remote', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_remote', 'turn_off')
send_command = LazyFunctionProxy('interface.ha_remote', 'send_command')
learn_command = LazyFunctionProxy('interface.ha_remote', 'learn_command')
delete_command = LazyFunctionProxy('interface.ha_remote', 'delete_command')

__all__ = [
    'get_remotes',
    'turn_on',
    'turn_off',
    'send_command',
    'learn_command',
    'delete_command',
]
