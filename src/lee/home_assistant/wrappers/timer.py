"""Timer Wrapper Functions Namespace

Provides direct access to timer device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import timer

    # Get all timers
    timers = timer.get_timers()

    # Start timer
    timer.start(entity_id='timer.coffee_timer')

    # Cancel timer
    timer.cancel(entity_id='timer.coffee_timer')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for timer operations
get_timers = LazyFunctionProxy('interface.ha_timer', 'list_timers')
start = LazyFunctionProxy('interface.ha_timer', 'start')
pause = LazyFunctionProxy('interface.ha_timer', 'pause')
cancel = LazyFunctionProxy('interface.ha_timer', 'cancel')
finish = LazyFunctionProxy('interface.ha_timer', 'finish')
change = LazyFunctionProxy('interface.ha_timer', 'change')

__all__ = [
    'get_timers',
    'start',
    'pause',
    'cancel',
    'finish',
    'change',
]
