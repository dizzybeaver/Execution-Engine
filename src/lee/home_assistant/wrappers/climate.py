"""Climate Wrapper Functions Namespace

Provides direct access to climate/HVAC device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import climate

    # Get all climate devices
    climates = climate.get_climates()

    # Set temperature
    climate.set_temperature(entity_id='climate.thermostat', temperature=22)

    # Set preset mode
    climate.set_preset_mode(entity_id='climate.thermostat', preset_mode='home')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for climate operations
get_climates = LazyFunctionProxy('interface.ha_climate', 'get_climates')
set_temperature = LazyFunctionProxy('interface.ha_climate', 'set_temperature')
set_preset_mode = LazyFunctionProxy('interface.ha_climate', 'set_preset_mode')
set_hvac_mode = LazyFunctionProxy('interface.ha_climate', 'set_hvac_mode')
turn_on = LazyFunctionProxy('interface.ha_climate', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_climate', 'turn_off')

__all__ = [
    'get_climates',
    'set_temperature',
    'set_preset_mode',
    'set_hvac_mode',
    'turn_on',
    'turn_off',
]
