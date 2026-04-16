# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Extracted entity interfaces from ha_gateway.py

"""ha_gateway_entities.py - Domain Entity Interfaces for HA Gateway
Version: 2026-04-01
Purpose: All domain-specific entity interfaces (light, switch, climate, etc.)

This module contains domain-specific entity interfaces:
- Input Button, Input DateTime, Input Number, Input Select, Input Text
- Switch, Light, Climate, Cover, Lock, Media Player
- Binary Sensor, Vacuum, Fan, Humidifier, Water Heater
- Alarm Control Panel, Button, Group, Weather, Person

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Optional

# Core imports
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface

# ===== ZONE CONVENIENCE FUNCTIONS =====

def ha_zone_list_zones(**kwargs) -> dict:
    """List all zones through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ZONE, "list_zones", **kwargs)


def ha_zone_get_zone(zone_id: str, **kwargs) -> dict:
    """Get zone by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ZONE, "get_zone", zone_id=zone_id, **kwargs)


def ha_zone_update_zone(zone_id: str, **kwargs) -> dict:
    """Update zone through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ZONE, "update_zone", zone_id=zone_id, **kwargs)


# ===== COUNTER CONVENIENCE FUNCTIONS =====

def ha_counter_list_counters(**kwargs) -> dict:
    """List all counters through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COUNTER, "list_counters", **kwargs)


def ha_counter_increment_counter(entity_id: str, **kwargs) -> dict:
    """Increment counter through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COUNTER, "increment_counter", entity_id=entity_id, **kwargs)


def ha_counter_reset_counter(entity_id: str, **kwargs) -> dict:
    """Reset counter through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COUNTER, "reset_counter", entity_id=entity_id, **kwargs)


# ===== TIMER CONVENIENCE FUNCTIONS =====

def ha_timer_list_timers(**kwargs) -> dict:
    """List all timers through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "list_timers", **kwargs)


def ha_timer_start_timer(entity_id: str, **kwargs) -> dict:
    """Start timer through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "start_timer", entity_id=entity_id, **kwargs)


def ha_timer_pause_timer(entity_id: str, **kwargs) -> dict:
    """Pause timer through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "pause_timer", entity_id=entity_id, **kwargs)


def ha_timer_cancel_timer(entity_id: str, **kwargs) -> dict:
    """Cancel timer through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "cancel_timer", entity_id=entity_id, **kwargs)


def ha_timer_finish_timer(entity_id: str, **kwargs) -> dict:
    """Finish timer through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "finish_timer", entity_id=entity_id, **kwargs)


def ha_timer_change_timer(entity_id: str, **kwargs) -> dict:
    """Change timer duration through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMER, "change_timer", entity_id=entity_id, **kwargs)


# ===== INPUT BOOLEAN CONVENIENCE FUNCTIONS =====

def ha_input_boolean_list_input_booleans(**kwargs) -> dict:
    """List all input booleans through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BOOLEAN, "list_input_booleans", **kwargs)


def ha_input_boolean_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn on input boolean through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BOOLEAN, "turn_on_input_boolean", entity_id=entity_id, **kwargs)


def ha_input_boolean_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn off input boolean through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BOOLEAN, "turn_off_input_boolean", entity_id=entity_id, **kwargs)


def ha_input_boolean_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle input boolean through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BOOLEAN, "toggle_input_boolean", entity_id=entity_id, **kwargs)


def ha_input_boolean_reload(**kwargs) -> dict:
    """Reload input booleans through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BOOLEAN, "reload_input_booleans", **kwargs)


# INPUT_BUTTON Interface
def ha_input_button_list_input_buttons(**kwargs) -> dict:
    """List input buttons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BUTTON, "list_input_buttons", **kwargs)


def ha_input_button_press(entity_id: str, **kwargs) -> dict:
    """Press input button through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BUTTON, "press_input_button", entity_id=entity_id, **kwargs)


def ha_input_button_reload(**kwargs) -> dict:
    """Reload input buttons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_BUTTON, "reload_input_buttons", **kwargs)


# INPUT_DATETIME Interface
def ha_input_datetime_list_input_datetimes(**kwargs) -> dict:
    """List input datetimes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_DATETIME, "list_input_datetimes", **kwargs)


def ha_input_datetime_set_datetime(entity_id: str, **kwargs) -> dict:
    """Set input datetime through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_DATETIME, "set_datetime", entity_id=entity_id, **kwargs)


def ha_input_datetime_reload(**kwargs) -> dict:
    """Reload input datetimes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_DATETIME, "reload_input_datetimes", **kwargs)


# INPUT_NUMBER Interface
def ha_input_number_list_input_numbers(**kwargs) -> dict:
    """List input numbers through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_NUMBER, "list_input_numbers", **kwargs)


def ha_input_number_decrement(entity_id: str, **kwargs) -> dict:
    """Decrement input number through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_NUMBER, "decrement_input_number", entity_id=entity_id, **kwargs)


def ha_input_number_increment(entity_id: str, **kwargs) -> dict:
    """Increment input number through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_NUMBER, "increment_input_number", entity_id=entity_id, **kwargs)


def ha_input_number_set_value(entity_id: str, value: float | int, **kwargs) -> dict:
    """Set input number value through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_NUMBER, "set_value_input_number", entity_id=entity_id, value=value, **kwargs)


def ha_input_number_reload(**kwargs) -> dict:
    """Reload input numbers through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_NUMBER, "reload_input_numbers", **kwargs)


# INPUT_SELECT Interface
def ha_input_select_list_input_selects(**kwargs) -> dict:
    """List input selects through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "list_input_selects", **kwargs)


def ha_input_select_select_next_option(entity_id: str, cycle: bool = True, **kwargs) -> dict:
    """Select next option through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "select_next_option", entity_id=entity_id, cycle=cycle, **kwargs)


def ha_input_select_select_previous_option(entity_id: str, cycle: bool = True, **kwargs) -> dict:
    """Select previous option through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "select_previous_option", entity_id=entity_id, cycle=cycle, **kwargs)


def ha_input_select_select_first_option(entity_id: str, **kwargs) -> dict:
    """Select first option through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "select_first_option", entity_id=entity_id, **kwargs)


def ha_input_select_select_last_option(entity_id: str, **kwargs) -> dict:
    """Select last option through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "select_last_option", entity_id=entity_id, **kwargs)


def ha_input_select_select_option(entity_id: str, option: str, **kwargs) -> dict:
    """Select specific option through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "select_option", entity_id=entity_id, option=option, **kwargs)


def ha_input_select_set_options(entity_id: str, options: list[str], **kwargs) -> dict:
    """Set options through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "set_options", entity_id=entity_id, options=options, **kwargs)


def ha_input_select_reload(**kwargs) -> dict:
    """Reload input selects through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_SELECT, "reload_input_selects", **kwargs)


# INPUT_TEXT Interface
def ha_input_text_list_input_texts(**kwargs) -> dict:
    """List input texts through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_TEXT, "list_input_texts", **kwargs)


def ha_input_text_set_value(entity_id: str, value: str, **kwargs) -> dict:
    """Set input text value through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_TEXT, "set_value_input_text", entity_id=entity_id, value=value, **kwargs)


def ha_input_text_reload(**kwargs) -> dict:
    """Reload input texts through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.INPUT_TEXT, "reload_input_texts", **kwargs)


# SWITCH Interface
def ha_switch_list_switches(**kwargs) -> dict:
    """List switches through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SWITCH, "list_switches", **kwargs)


def ha_switch_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn switch on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SWITCH, "turn_on", entity_id=entity_id, **kwargs)


def ha_switch_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn switch off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SWITCH, "turn_off", entity_id=entity_id, **kwargs)


def ha_switch_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle switch through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SWITCH, "toggle", entity_id=entity_id, **kwargs)


# LIGHT Interface
def ha_light_list_lights(**kwargs) -> dict:
    """List lights through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "list_lights", **kwargs)


def ha_light_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn light on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "turn_on", entity_id=entity_id, **kwargs)


def ha_light_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn light off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "turn_off", entity_id=entity_id, **kwargs)


def ha_light_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle light through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "toggle", entity_id=entity_id, **kwargs)


def ha_light_set_brightness(entity_id: str, brightness: int, **kwargs) -> dict:
    """Set light brightness through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "set_brightness", entity_id=entity_id, brightness=brightness, **kwargs)


def ha_light_set_color_temp(entity_id: str, color_temp: int, **kwargs) -> dict:
    """Set light color temperature through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "set_color_temp", entity_id=entity_id, color_temp=color_temp, **kwargs)


def ha_light_set_rgb_color(entity_id: str, rgb_color: list[int], **kwargs) -> dict:
    """Set light RGB color through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LIGHT, "set_rgb_color", entity_id=entity_id, rgb_color=rgb_color, **kwargs)


# CLIMATE Interface
def ha_climate_list_climates(**kwargs) -> dict:
    """List climates through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "list_climates", **kwargs)


def ha_climate_set_temperature(entity_id: str, temperature: float, **kwargs) -> dict:
    """Set climate temperature through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "set_temperature", entity_id=entity_id, temperature=temperature, **kwargs)


def ha_climate_set_preset_mode(entity_id: str, preset_mode: str, **kwargs) -> dict:
    """Set climate preset mode through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "set_preset_mode", entity_id=entity_id, preset_mode=preset_mode, **kwargs)


def ha_climate_set_hvac_mode(entity_id: str, hvac_mode: str, **kwargs) -> dict:
    """Set climate HVAC mode through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "set_hvac_mode", entity_id=entity_id, hvac_mode=hvac_mode, **kwargs)


def ha_climate_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn climate on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "turn_on", entity_id=entity_id, **kwargs)


def ha_climate_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn climate off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CLIMATE, "turn_off", entity_id=entity_id, **kwargs)


# COVER Interface
def ha_cover_list_covers(**kwargs) -> dict:
    """List covers through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "list_covers", **kwargs)


def ha_cover_open(entity_id: str, **kwargs) -> dict:
    """Open cover through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "open_cover", entity_id=entity_id, **kwargs)


def ha_cover_close(entity_id: str, **kwargs) -> dict:
    """Close cover through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "close_cover", entity_id=entity_id, **kwargs)


def ha_cover_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle cover through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "toggle_cover", entity_id=entity_id, **kwargs)


def ha_cover_set_position(entity_id: str, position: int, **kwargs) -> dict:
    """Set cover position through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "set_cover_position", entity_id=entity_id, position=position, **kwargs)


def ha_cover_stop(entity_id: str, **kwargs) -> dict:
    """Stop cover through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.COVER, "stop_cover", entity_id=entity_id, **kwargs)


# LOCK Interface
def ha_lock_list_locks(**kwargs) -> dict:
    """List locks through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOCK, "list_locks", **kwargs)


def ha_lock_lock(entity_id: str, **kwargs) -> dict:
    """Lock through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOCK, "lock", entity_id=entity_id, **kwargs)


def ha_lock_unlock(entity_id: str, **kwargs) -> dict:
    """Unlock through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOCK, "unlock", entity_id=entity_id, **kwargs)


def ha_lock_open(entity_id: str, **kwargs) -> dict:
    """Open lock through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOCK, "open", entity_id=entity_id, **kwargs)


# MEDIA_PLAYER Interface
def ha_media_player_list_media_players(**kwargs) -> dict:
    """List media players through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "list_media_players", **kwargs)


def ha_media_player_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn media player on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "turn_on", entity_id=entity_id, **kwargs)


def ha_media_player_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn media player off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "turn_off", entity_id=entity_id, **kwargs)


def ha_media_player_play_media(entity_id: str, media_content_id: str, **kwargs) -> dict:
    """Play media through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "play_media", entity_id=entity_id, media_content_id=media_content_id, **kwargs)


def ha_media_player_pause(entity_id: str, **kwargs) -> dict:
    """Pause media through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "media_pause", entity_id=entity_id, **kwargs)


def ha_media_player_stop(entity_id: str, **kwargs) -> dict:
    """Stop media through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "media_stop", entity_id=entity_id, **kwargs)


def ha_media_player_volume_set(entity_id: str, volume_level: float, **kwargs) -> dict:
    """Set volume through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MEDIA_PLAYER, "volume_set", entity_id=entity_id, volume_level=volume_level, **kwargs)


# BINARY_SENSOR Interface
def ha_binary_sensor_list_binary_sensors(**kwargs) -> dict:
    """List binary sensors through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BINARY_SENSOR, "list_binary_sensors", **kwargs)


def ha_binary_sensor_reload_binary_sensors(**kwargs) -> dict:
    """Reload binary sensors through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BINARY_SENSOR, "reload_binary_sensors", **kwargs)


# VACUUM Interface
def ha_vacuum_list_vacuums(**kwargs) -> dict:
    """List vacuums through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "list_vacuums", **kwargs)


def ha_vacuum_start(entity_id: str, **kwargs) -> dict:
    """Start vacuum through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "start", entity_id=entity_id, **kwargs)


def ha_vacuum_pause(entity_id: str, **kwargs) -> dict:
    """Pause vacuum through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "pause", entity_id=entity_id, **kwargs)


def ha_vacuum_stop(entity_id: str, **kwargs) -> dict:
    """Stop vacuum through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "stop", entity_id=entity_id, **kwargs)


def ha_vacuum_return_to_base(entity_id: str, **kwargs) -> dict:
    """Return vacuum to base through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "return_to_base", entity_id=entity_id, **kwargs)


def ha_vacuum_clean_spot(entity_id: str, **kwargs) -> dict:
    """Clean spot through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "clean_spot", entity_id=entity_id, **kwargs)


def ha_vacuum_locate(entity_id: str, **kwargs) -> dict:
    """Locate vacuum through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.VACUUM, "locate", entity_id=entity_id, **kwargs)


# FAN Interface
def ha_fan_list_fans(**kwargs) -> dict:
    """List fans through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "list_fans", **kwargs)


def ha_fan_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn fan on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "turn_on", entity_id=entity_id, **kwargs)


def ha_fan_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn fan off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "turn_off", entity_id=entity_id, **kwargs)


def ha_fan_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle fan through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "toggle", entity_id=entity_id, **kwargs)


def ha_fan_set_speed(entity_id: str, speed: str, **kwargs) -> dict:
    """Set fan speed through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "set_speed", entity_id=entity_id, speed=speed, **kwargs)


def ha_fan_set_percentage(entity_id: str, percentage: int, **kwargs) -> dict:
    """Set fan percentage through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "set_percentage", entity_id=entity_id, percentage=percentage, **kwargs)


def ha_fan_increase_speed(entity_id: str, **kwargs) -> dict:
    """Increase fan speed through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.FAN, "increase_speed", entity_id=entity_id, **kwargs)


# HUMIDIFIER Interface
def ha_humidifier_list_humidifiers(**kwargs) -> dict:
    """List humidifiers through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "list_humidifiers", **kwargs)


def ha_humidifier_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn humidifier on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "turn_on", entity_id=entity_id, **kwargs)


def ha_humidifier_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn humidifier off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "turn_off", entity_id=entity_id, **kwargs)


def ha_humidifier_set_humidity(entity_id: str, humidity: int, **kwargs) -> dict:
    """Set humidifier target humidity through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "set_humidity", entity_id=entity_id, humidity=humidity, **kwargs)


def ha_humidifier_set_mode(entity_id: str, mode: str, **kwargs) -> dict:
    """Set humidifier mode through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "set_mode", entity_id=entity_id, mode=mode, **kwargs)


def ha_humidifier_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle humidifier through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HUMIDIFIER, "toggle", entity_id=entity_id, **kwargs)


# WATER_HEATER Interface
def ha_water_heater_list_water_heaters(**kwargs) -> dict:
    """List water heaters through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "list_water_heaters", **kwargs)


def ha_water_heater_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn water heater on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "turn_on", entity_id=entity_id, **kwargs)


def ha_water_heater_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn water heater off through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "turn_off", entity_id=entity_id, **kwargs)


def ha_water_heater_set_temperature(entity_id: str, temperature: float, **kwargs) -> dict:
    """Set water heater temperature through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "set_temperature", entity_id=entity_id, temperature=temperature, **kwargs)


def ha_water_heater_set_operation_mode(entity_id: str, operation_mode: str, **kwargs) -> dict:
    """Set water heater operation mode through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "set_operation_mode", entity_id=entity_id, operation_mode=operation_mode, **kwargs)


def ha_water_heater_set_away_mode(entity_id: str, mode: str, **kwargs) -> dict:
    """Set water heater away mode through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WATER_HEATER, "set_away_mode", entity_id=entity_id, mode=mode, **kwargs)


# ALARM_CONTROL_PANEL Interface
def ha_alarm_control_panel_list_alarm_control_panels(**kwargs) -> dict:
    """List alarm control panels through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "list_alarm_control_panels", **kwargs)


def ha_alarm_control_panel_alarm_arm_away(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Arm alarm away through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_arm_away", entity_id=entity_id, code=code, **kwargs)


def ha_alarm_control_panel_alarm_arm_home(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Arm alarm home through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_arm_home", entity_id=entity_id, code=code, **kwargs)


def ha_alarm_control_panel_alarm_arm_night(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Arm alarm night through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_arm_night", entity_id=entity_id, code=code, **kwargs)


def ha_alarm_control_panel_alarm_arm_custom_bypass(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Arm alarm with custom bypass through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_arm_custom_bypass", entity_id=entity_id, code=code, **kwargs)


def ha_alarm_control_panel_alarm_disarm(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Disarm alarm through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_disarm", entity_id=entity_id, code=code, **kwargs)


def ha_alarm_control_panel_alarm_trigger(entity_id: str, code: Optional[str] = None, **kwargs) -> dict:
    """Trigger alarm through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ALARM_CONTROL_PANEL, "alarm_trigger", entity_id=entity_id, code=code, **kwargs)


# BUTTON Interface
def ha_button_list_buttons(**kwargs) -> dict:
    """List buttons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BUTTON, "list_buttons", **kwargs)


def ha_button_press(entity_id: str, **kwargs) -> dict:
    """Press button through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BUTTON, "press", entity_id=entity_id, **kwargs)


# GROUP Interface
def ha_group_list_groups(**kwargs) -> dict:
    """List groups through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.GROUP, "list_groups", **kwargs)


def ha_group_reload(**kwargs) -> dict:
    """Reload groups through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.GROUP, "reload", **kwargs)


def ha_group_set(object_id: str, name: Optional[str] = None, icon: Optional[str] = None, entities: Optional[list[str]] = None, add_entities: Optional[list[str]] = None, remove_entities: Optional[list[str]] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments
    """Set group through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.GROUP, "set", object_id=object_id, name=name, icon=icon, entities=entities, add_entities=add_entities, remove_entities=remove_entities, **kwargs)


# WEATHER Interface
def ha_weather_list_weather_entities(**kwargs) -> dict:
    """List weather entities through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WEATHER, "list_weather_entities", **kwargs)


def ha_weather_get_forecast(entity_id: str, forecast_type: str, **kwargs) -> dict:
    """Get weather forecast through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WEATHER, "get_forecast", entity_id=entity_id, forecast_type=forecast_type, **kwargs)


def ha_weather_get_forecasts(entity_id: str, **kwargs) -> dict:
    """Get weather forecasts through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.WEATHER, "get_forecasts", entity_id=entity_id, **kwargs)


# PERSON Interface
def ha_person_list_persons(**kwargs) -> dict:
    """List persons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.PERSON, "list_persons", **kwargs)


def ha_person_reload(**kwargs) -> dict:
    """Reload persons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.PERSON, "reload", **kwargs)
