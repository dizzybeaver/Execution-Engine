"""Humidifier Wrapper Functions Namespace

Provides direct access to humidifier device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import humidifier

    # Get all humidifiers
    humidifiers = humidifier.get_humidifiers()

    # Set humidity
    humidifier.set_humidity(entity_id='humidifier.living_room', humidity=45)

    # Turn on humidifier
    humidifier.turn_on(entity_id='humidifier.living_room')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for humidifier operations
get_humidifiers = LazyFunctionProxy('interface.ha_humidifier', 'list_humidifiers')
turn_on = LazyFunctionProxy('interface.ha_humidifier', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_humidifier', 'turn_off')
set_humidity = LazyFunctionProxy('interface.ha_humidifier', 'set_humidity')
set_mode = LazyFunctionProxy('interface.ha_humidifier', 'set_mode')
toggle = LazyFunctionProxy('interface.ha_humidifier', 'toggle')

__all__ = [
    'get_humidifiers',
    'turn_on',
    'turn_off',
    'set_humidity',
    'set_mode',
    'toggle',
]
