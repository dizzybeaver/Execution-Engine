"""Sensor Wrapper Functions Namespace

5 functions for sensor entity metadata.

Usage:
    from lee.home_assistant.wrappers import sensor

    # Get sensor state
    state = sensor.get_state(entity_id='sensor.temperature_123')

    # Get sensor value
    value = sensor.get_value(entity_id='sensor.temperature_123')

    # Get device class units
    units = sensor.get_device_class_units(device_class='temperature')

    # Get numeric device classes
    classes = sensor.get_numeric_device_classes()

    # List sensors
    sensors = sensor.list_sensors()
"""

# Import all sensor wrapper functions
from lee.home_assistant.interface.wrappers.ha_sensor_wrappers import (
    get_device_class_units,
    get_numeric_device_classes,
    get_state,
    get_value,
    list_sensors,
)

__all__ = [
    'get_device_class_units',
    'get_numeric_device_classes',
    'get_state',
    'get_value',
    'list_sensors',
]
