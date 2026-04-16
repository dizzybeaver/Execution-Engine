"""Lock Wrapper Functions Namespace

Provides direct access to lock device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import lock

    # Get all locks
    locks = lock.get_locks()

    # Lock door
    lock.lock_door(entity_id='lock.front_door')

    # Unlock door
    lock.unlock_door(entity_id='lock.front_door')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for lock operations
get_locks = LazyFunctionProxy('interface.ha_lock', 'get_locks')
lock_door = LazyFunctionProxy('interface.ha_lock', 'lock')
unlock_door = LazyFunctionProxy('interface.ha_lock', 'unlock')
open_lock = LazyFunctionProxy('interface.ha_lock', 'open')

__all__ = [
    'get_locks',
    'lock_door',
    'unlock_door',
    'open_lock',
]
