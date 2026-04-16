"""Input DateTime Wrapper Functions Namespace

Provides direct access to input_datetime device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import input_datetime

    # Get all input datetimes
    datetimes = input_datetime.get_input_datetimes()

    # Set datetime
    input_datetime.set_datetime(entity_id='input_datetime.alarm_time', datetime='2026-03-23T07:00:00')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for input_datetime operations
get_input_datetimes = LazyFunctionProxy('interface.ha_input_datetime', 'list')
set_datetime = LazyFunctionProxy('interface.ha_input_datetime', 'set_datetime')
reload = LazyFunctionProxy('interface.ha_input_datetime', 'reload')

__all__ = [
    'get_input_datetimes',
    'set_datetime',
    'reload',
]
