"""Binary Sensor Wrapper Functions Namespace

3 functions for binary sensor operations.

Usage:
    from lee.home_assistant.wrappers import binary_sensor

    # Get binary sensor state
    state = binary_sensor.get_state(entity_id='binary_sensor.motion_123')

    # List binary sensors
    sensors = binary_sensor.list_binary_sensors()

    # Reload binary sensors
    binary_sensor.reload_binary_sensors()
"""

# Import all binary sensor wrapper functions
from lee.home_assistant.interface.wrappers.ha_binary_sensor_wrappers import (
    get_state,
    list_binary_sensors,
    reload_binary_sensors,
)

__all__ = [
    'get_state',
    'list_binary_sensors',
    'reload_binary_sensors',
]
