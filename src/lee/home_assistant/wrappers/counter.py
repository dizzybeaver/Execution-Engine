"""Counter Wrapper Functions Namespace

Provides direct access to counter device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import counter

    # Get all counters
    counters = counter.get_counters()

    # Increment counter
    counter.increment(entity_id='counter.cycle_count')

    # Reset counter
    counter.reset(entity_id='counter.cycle_count')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for counter operations
get_counters = LazyFunctionProxy('interface.ha_counter', 'list')
increment = LazyFunctionProxy('interface.ha_counter', 'increment')
reset = LazyFunctionProxy('interface.ha_counter', 'reset')

__all__ = [
    'get_counters',
    'increment',
    'reset',
]
