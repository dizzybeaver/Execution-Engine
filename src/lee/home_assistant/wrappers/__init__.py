"""HA Wrapper Functions - Lazy-Loaded User API

Provides categorized access to all HA wrapper functions.

Usage:
    from lee.home_assistant.wrappers import devices, alexa, assist, light, switch

    # Device operations
    states = devices.get_states(domain='light')
    devices.call_service('light', 'turn_on', entity_id='light.bubs_bedroom_inside_light_switch_1')

    # Light operations
    light.turn_on(entity_id='light.bubs_bedroom_inside_light_switch_1')
    light.set_brightness(entity_id='light.bubs_bedroom_inside_light_switch_1', brightness=255)

    # Switch operations
    switch.turn_on(entity_id='switch.plug')

    # Climate operations
    climate.set_temperature(entity_id='climate.thermostat', temperature=22)
"""

# Import all category namespaces
from lee.home_assistant.wrappers import (
    alarm_control_panel,
    assist,
    binary_sensor,
    button,
    camera,
    climate,
    counter,
    cover,
    devices,
    fan,
    group,
    health,
    humidifier,
    input_boolean,
    input_datetime,
    input_number,
    input_select,
    input_text,
    light,
    lock,
    media_player,
    person,
    remote,
    scene,
    script,
    sensor,
    siren,
    sun,
    switch,
    timer,
    vacuum,
    water_heater,
    weather,
    websocket,
    zone,
)

__all__ = [
    'devices',
    'assist',
    'sensor',
    'binary_sensor',
    'weather',
    'websocket',
    'health',
    'light',
    'switch',
    'climate',
    'lock',
    'cover',
    'media_player',
    'vacuum',
    'fan',
    'alarm_control_panel',
    'scene',
    'script',
    'group',
    'timer',
    'input_boolean',
    'humidifier',
    'input_number',
    'input_select',
    'input_text',
    'input_datetime',
    'water_heater',
    'sun',
    'person',
    'camera',
    'button',
    'counter',
    'zone',
    'siren',
    'remote',
]
