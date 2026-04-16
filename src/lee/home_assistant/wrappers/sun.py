"""Sun Wrapper Functions Namespace

Provides direct access to sun device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import sun

    # Get sun state
    state = sun.get_sun_state()

    # Get sunrise time
    sunrise = sun.get_sunrise_time()

    # Get sunset time
    sunset = sun.get_sunset_time()
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for sun operations
get_sun_state = LazyFunctionProxy('interface.ha_sun', 'get_sun_state')
get_sunrise_time = LazyFunctionProxy('interface.ha_sun', 'get_sunrise_time')
get_sunset_time = LazyFunctionProxy('interface.ha_sun', 'get_sunset_time')

__all__ = [
    'get_sun_state',
    'get_sunrise_time',
    'get_sunset_time',
]
