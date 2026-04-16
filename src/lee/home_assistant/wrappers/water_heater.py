"""Water Heater Wrapper Functions Namespace

Provides direct access to water_heater device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import water_heater

    # Get all water heaters
    heaters = water_heater.get_water_heaters()

    # Set temperature
    water_heater.set_temperature(entity_id='water_heater.hot_water', temperature=50)

    # Turn on water heater
    water_heater.turn_on(entity_id='water_heater.hot_water')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for water_heater operations
get_water_heaters = LazyFunctionProxy('interface.ha_water_heater', 'list')
turn_on = LazyFunctionProxy('interface.ha_water_heater', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_water_heater', 'turn_off')
set_temperature = LazyFunctionProxy('interface.ha_water_heater', 'set_temperature')
set_operation_mode = LazyFunctionProxy('interface.ha_water_heater', 'set_operation_mode')
set_away_mode = LazyFunctionProxy('interface.ha_water_heater', 'set_away_mode')

__all__ = [
    'get_water_heaters',
    'turn_on',
    'turn_off',
    'set_temperature',
    'set_operation_mode',
    'set_away_mode',
]
