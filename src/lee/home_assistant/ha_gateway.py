# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_gateway.py - Home Assistant SUGA Gateway (Main Entry Point)
Version: 2025-12-17_1
Purpose: Single entry point for all Home Assistant operations (HA-SUGA)

This is the main entry point for Home Assistant operations, equivalent to
gateway.py for LEE. All HA operations should route through this gateway.

Architecture:
- HA Gateway = ISP (Internet Service Provider)
- HA Interfaces = Routers
- HA Cores = Local Networks

Cross-interface calls to LEE use: gateway.execute_operation()
Internal HA calls use: ha_gateway.ha_execute_operation()

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core imports - Re-export main functionality
# Import from automation_tools module
from lee.home_assistant.ha_gateway_automation_tools import (
    ha_calendar_create_event,
    ha_calendar_list,
    ha_camera_disable_motion_detection,
    ha_camera_enable_motion_detection,
    ha_camera_list,
    ha_camera_play_stream,
    ha_camera_record,
    ha_camera_snapshot,
    ha_camera_turn_off,
    ha_camera_turn_on,
    ha_conversation_hass_agent_debug,
    ha_conversation_hass_agent_language_scores,
    ha_conversation_list_agents,
    ha_conversation_list_sentences,
    ha_conversation_prepare,
    ha_conversation_process,
    ha_conversation_subscribe_chat_log,
    ha_conversation_subscribe_chat_log_index,
    ha_esphome_get_encryption_key,
    ha_hardware_get_info,
    ha_image_processing_scan,
    ha_logger_get_info,
    ha_logger_set_integration_level,
    ha_logger_set_module_level,
    ha_mobile_app_confirm_push_notification,
    ha_mobile_app_register_push_channel,
    ha_notify_send_message,
    ha_number_get_device_class_units,
    ha_persistent_dismiss_notification,
    ha_persistent_get_notifications,
    ha_remote_delete_command,
    ha_remote_learn_command,
    ha_remote_list,
    ha_remote_send_command,
    ha_remote_toggle,
    ha_remote_turn_off,
    ha_remote_turn_on,
    ha_scene_activate,
    ha_scene_apply,
    ha_scene_create,
    ha_scene_list,
    ha_scene_reload,
    ha_scene_turn_on,
    ha_script_run,
    ha_sensor_get_device_class_units,
    ha_sensor_get_numeric_device_classes,
    ha_siren_list,
    ha_siren_toggle,
    ha_siren_turn_off,
    ha_siren_turn_on,
    ha_tts_say,
    ha_tts_speak,
    ha_update_install,
    ha_update_list,
    ha_update_skip,
)

# Import from convenience module
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
    ha_metrics_put,
    ha_validate_string,
)
from lee.gateway.decorators import cached_gateway_operation
from lee.home_assistant.ha_gateway_core import (
    clear_ha_fast_path_cache,
    disable_ha_fast_path,
    enable_ha_fast_path,
    get_ha_gateway_stats,
    ha_execute_operation,
    reset_ha_gateway_state,
)

# Import from entities module
from lee.home_assistant.ha_gateway_entities import (
    ha_alarm_control_panel_alarm_arm_away,
    ha_alarm_control_panel_alarm_arm_custom_bypass,
    ha_alarm_control_panel_alarm_arm_home,
    ha_alarm_control_panel_alarm_arm_night,
    ha_alarm_control_panel_alarm_disarm,
    ha_alarm_control_panel_alarm_trigger,
    ha_alarm_control_panel_list_alarm_control_panels,
    ha_binary_sensor_list_binary_sensors,
    ha_binary_sensor_reload_binary_sensors,
    ha_button_list_buttons,
    ha_button_press,
    ha_climate_list_climates,
    ha_climate_set_hvac_mode,
    ha_climate_set_preset_mode,
    ha_climate_set_temperature,
    ha_climate_turn_off,
    ha_climate_turn_on,
    ha_counter_increment_counter,
    ha_counter_list_counters,
    ha_counter_reset_counter,
    ha_cover_close,
    ha_cover_list_covers,
    ha_cover_open,
    ha_cover_set_position,
    ha_cover_stop,
    ha_cover_toggle,
    ha_fan_increase_speed,
    ha_fan_list_fans,
    ha_fan_set_percentage,
    ha_fan_set_speed,
    ha_fan_toggle,
    ha_fan_turn_off,
    ha_fan_turn_on,
    ha_group_list_groups,
    ha_group_reload,
    ha_group_set,
    ha_humidifier_list_humidifiers,
    ha_humidifier_set_humidity,
    ha_humidifier_set_mode,
    ha_humidifier_toggle,
    ha_humidifier_turn_off,
    ha_humidifier_turn_on,
    ha_input_boolean_list_input_booleans,
    ha_input_boolean_reload,
    ha_input_boolean_toggle,
    ha_input_boolean_turn_off,
    ha_input_boolean_turn_on,
    ha_input_button_list_input_buttons,
    ha_input_button_press,
    ha_input_button_reload,
    ha_input_datetime_list_input_datetimes,
    ha_input_datetime_reload,
    ha_input_datetime_set_datetime,
    ha_input_number_decrement,
    ha_input_number_increment,
    ha_input_number_list_input_numbers,
    ha_input_number_reload,
    ha_input_number_set_value,
    ha_input_select_list_input_selects,
    ha_input_select_reload,
    ha_input_select_select_first_option,
    ha_input_select_select_last_option,
    ha_input_select_select_next_option,
    ha_input_select_select_option,
    ha_input_select_select_previous_option,
    ha_input_select_set_options,
    ha_input_text_list_input_texts,
    ha_input_text_reload,
    ha_input_text_set_value,
    ha_light_list_lights,
    ha_light_set_brightness,
    ha_light_set_color_temp,
    ha_light_set_rgb_color,
    ha_light_toggle,
    ha_light_turn_off,
    ha_light_turn_on,
    ha_lock_list_locks,
    ha_lock_lock,
    ha_lock_open,
    ha_lock_unlock,
    ha_media_player_list_media_players,
    ha_media_player_pause,
    ha_media_player_play_media,
    ha_media_player_stop,
    ha_media_player_turn_off,
    ha_media_player_turn_on,
    ha_media_player_volume_set,
    ha_person_list_persons,
    ha_person_reload,
    ha_switch_list_switches,
    ha_switch_toggle,
    ha_switch_turn_off,
    ha_switch_turn_on,
    ha_timer_cancel_timer,
    ha_timer_change_timer,
    ha_timer_finish_timer,
    ha_timer_list_timers,
    ha_timer_pause_timer,
    ha_timer_start_timer,
    ha_vacuum_clean_spot,
    ha_vacuum_list_vacuums,
    ha_vacuum_locate,
    ha_vacuum_pause,
    ha_vacuum_return_to_base,
    ha_vacuum_start,
    ha_vacuum_stop,
    ha_water_heater_list_water_heaters,
    ha_water_heater_set_away_mode,
    ha_water_heater_set_operation_mode,
    ha_water_heater_set_temperature,
    ha_water_heater_turn_off,
    ha_water_heater_turn_on,
    ha_weather_get_forecast,
    ha_weather_get_forecasts,
    ha_weather_list_weather_entities,
    ha_zone_get_zone,
    ha_zone_list_zones,
    ha_zone_update_zone,
)

# Enum imports
from lee.home_assistant.ha_gateway_enums import (
    HAGatewayInterface,
    get_core_interfaces,
    get_infrastructure_interfaces,
    get_interface_description,
    get_voice_interfaces,
    list_all_interfaces,
)

# Import from infrastructure module
from lee.home_assistant.ha_gateway_infrastructure import (
    ha_automation_disable_automation,
    ha_automation_enable_automation,
    ha_automation_get_automation,
    ha_automation_get_script,
    ha_automation_list_automations,
    ha_automation_list_scripts,
    ha_automation_list_triggers,
    ha_automation_reload_automations,
    ha_automation_reload_scripts,
    ha_automation_run_script,
    ha_automation_trigger_automation,
    ha_blueprint_delete_blueprint,
    ha_blueprint_import_blueprint,
    ha_blueprint_list_blueprints,
    ha_blueprint_save_blueprint,
    ha_blueprint_substitute_blueprint,
    ha_config_get_ha_config,
    ha_config_get_ha_entities,
    ha_health_check_lee_connectivity,
    ha_health_check_system,
    ha_registry_create_area,
    ha_registry_delete_area,
    ha_registry_delete_device,
    ha_registry_get_area,
    ha_registry_get_device,
    ha_registry_get_entity,
    ha_registry_list_areas,
    ha_registry_list_categories,
    ha_registry_list_devices,
    ha_registry_list_entities,
    ha_registry_remove_entity,
    ha_registry_update_area,
    ha_registry_update_device,
    ha_registry_update_entity,
    ha_supervisor_get_addon_info,
    ha_supervisor_get_core_info,
    ha_supervisor_get_host_info,
    ha_supervisor_get_info,
    ha_supervisor_get_os_info,
    ha_supervisor_list_addons,
    ha_supervisor_restart_addon,
    ha_supervisor_start_addon,
    ha_supervisor_stop_addon,
)

# Import from monitoring module
from lee.home_assistant.ha_gateway_monitoring import (
    ha_backup_create,
    ha_backup_delete,
    ha_backup_get_details,
    ha_backup_get_info,
    ha_backup_restore,
    ha_camera_get_capabilities,
    ha_camera_get_info,
    ha_camera_get_stream_url,
    ha_camera_list_cameras,
    ha_camera_take_snapshot,
    ha_energy_get_fossil_energy_consumption,
    ha_energy_get_info,
    ha_energy_get_preferences,
    ha_energy_get_solar_forecast,
    ha_energy_save_preferences,
    ha_energy_validate_config,
    ha_history_get_during_period,
    ha_logbook_get_events,
    ha_repairs_get_issue_data,
    ha_repairs_ignore_issue,
    ha_repairs_list_issues,
    ha_statistics_adjust_sum_statistics,
    ha_statistics_change_statistics_unit,
    ha_statistics_clear_statistics,
    ha_statistics_get_statistic_during_period,
    ha_statistics_get_statistics_during_period,
    ha_statistics_get_statistics_metadata,
    ha_statistics_import_statistics,
    ha_statistics_list_statistic_ids,
    ha_statistics_update_statistics_issues,
    ha_statistics_update_statistics_metadata,
    ha_statistics_validate_statistics,
    ha_timed_backup_create_backup,
    ha_timed_backup_delete_backup,
    ha_timed_backup_list_backups,
    ha_timed_backup_restore_backup,
)


# Voice interface functions (Alexa and Assist)
def ha_alexa_process_directive(event: dict, **kwargs) -> dict:
    """Process Alexa directive through HA-SUGA gateway.

    Args:
        event: Alexa directive event payload from Alexa Smart Home API
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Response dictionary from Alexa interface containing directive processing results

    Example:
        >>> event = {"directive": {"header": {"name": "TurnOn"}, ...}}
        >>> result = ha_alexa_process_directive(event)
    """
    return ha_execute_operation(HAGatewayInterface.ALEXA, "process_directive", event=event, **kwargs)

def ha_alexa_handle_discovery(request: dict, **kwargs) -> dict:
    """Handle Alexa device discovery request through HA-SUGA gateway.

    Args:
        request: Alexa discovery request payload
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Discovery response dictionary with all discoverable Home Assistant devices

    Example:
        >>> request = {"directive": {"header": {"name": "Discovery"}, ...}}
        >>> result = ha_alexa_handle_discovery(request)
    """
    return ha_execute_operation(HAGatewayInterface.ALEXA, "handle_discovery", request=request, **kwargs)

@cached_gateway_operation(ttl_seconds=5)
def ha_devices_get_states(**kwargs) -> list:
    """Retrieve all device states from Home Assistant through HA-SUGA gateway.

    Args:
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id, use_cache)

    Returns:
        List of all device state dictionaries from Home Assistant

    Example:
        >>> states = ha_devices_get_states()
        >>> for state in states:
        ...     print(f"{state['entity_id']}: {state['state']}")
    """
    return ha_execute_operation(HAGatewayInterface.DEVICES, "get_states", **kwargs)

def ha_devices_get_by_id(entity_id: str, **kwargs) -> dict:
    """Retrieve specific device state by entity ID through HA-SUGA gateway.

    Args:
        entity_id: Home Assistant entity ID (e.g., "light.bubs_bedroom_inside_light_switch_1", "switch.living_room")
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id, use_cache)

    Returns:
        Device state dictionary for the requested entity

    Raises:
        KeyError: If entity_id not found in Home Assistant

    Example:
        >>> state = ha_devices_get_by_id("light.bubs_bedroom_inside_light_switch_1")
        >>> print(f"Light is {state['state']}")
    """
    return ha_execute_operation(HAGatewayInterface.DEVICES, "get_by_id", entity_id=entity_id, **kwargs)

def ha_devices_call_service(domain: str, service: str, service_data: dict = None, **kwargs) -> any:
    """Call Home Assistant service through HA-SUGA gateway.

    Args:
        domain: Service domain (e.g., "light", "switch", "cover")
        service: Service name (e.g., "turn_on", "turn_off", "toggle")
        service_data: Service parameters (e.g., {"entity_id": "light.bubs_bedroom_inside_light_switch_1", "brightness": 255})
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Service call response from Home Assistant

    Example:
        >>> result = ha_devices_call_service("light", "turn_on",
        ...                                    service_data={"entity_id": "light.bubs_bedroom_inside_light_switch_1"})
    """
    return ha_execute_operation(HAGatewayInterface.DEVICES, "call_service", domain=domain, service=service, service_data=service_data, **kwargs)

def ha_devices_get_states_batch(entity_ids: list, use_cache: bool = True, **kwargs) -> dict:
    """Retrieve multiple device states efficiently through HA-SUGA gateway.

    Args:
        entity_ids: List of entity IDs to retrieve (e.g., ["light.bubs_bedroom_inside_light_switch_1", "switch.living_room"])
        use_cache: Whether to use cached values (default: True for performance)
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Dictionary mapping entity_id to state dictionary

    Example:
        >>> states = ha_devices_get_states_batch(["light.bubs_bedroom_inside_light_switch_1", "switch.living_room"])
        >>> print(states["light.bubs_bedroom_inside_light_switch_1"]["state"])
    """
    return ha_execute_operation(HAGatewayInterface.DEVICES, "get_states_batch", entity_ids=entity_ids, use_cache=use_cache, **kwargs)

def ha_devices_call_service_batch(domain: str, service: str, entity_ids: list, service_data: dict = None, **kwargs) -> dict:
    """Call service on multiple devices efficiently through HA-SUGA gateway.

    Args:
        domain: Service domain (e.g., "light", "switch")
        service: Service name (e.g., "turn_on", "turn_off")
        entity_ids: List of entity IDs to call service on
        service_data: Service parameters to apply to all entities
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Dictionary mapping entity_id to service call result

    Example:
        >>> result = ha_devices_call_service_batch("light", "turn_on",
        ...                                          entity_ids=["light.bubs_bedroom_inside_light_switch_1", "light.kitchen"])
    """
    return ha_execute_operation(HAGatewayInterface.DEVICES, "call_service_batch", domain=domain, service=service, entity_ids=entity_ids, service_data=service_data, **kwargs)

def ha_assist_send_message(message: str, **kwargs) -> dict:
    """Send message to Home Assistant Assist through HA-SUGA gateway.

    Args:
        message: Message text to send to Assist conversation agent
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Assist response dictionary with conversation agent reply

    Example:
        >>> response = ha_assist_send_message("Turn on the office lights")
    """
    return ha_execute_operation(HAGatewayInterface.ASSIST, "send_message", message=message, **kwargs)

def ha_assist_process_conversation(text: str, **kwargs) -> dict:
    """Process conversation text with Home Assistant Assist through HA-SUGA gateway.

    Args:
        text: Conversation text to process (can include multi-turn context)
        **kwargs: Additional parameters for gateway operation (e.g., correlation_id)

    Returns:
        Assist response dictionary with processed conversation result

    Example:
        >>> response = ha_assist_process_conversation("What's the temperature?")
    """
    return ha_execute_operation(HAGatewayInterface.ASSIST, "process_conversation", text=text, **kwargs)

# ===== INITIALIZATION =====
def initialize_ha_gateway() -> dict:
    """Initialize HA gateway with mode-aware settings and return status."""
    # pylint: disable=import-outside-toplevel
    from lee.home_assistant.ha_deployment_mode import get_deployment_mode

    # Detect deployment mode
    mode = get_deployment_mode()

    # Log deployment mode
    ha_log_info(
        message=f'HA Gateway initialized in {mode.value} mode',
        corr_id='ha_init'
    )

    ha_stats = get_ha_gateway_stats()
    lee_health = ha_health_check_lee_connectivity()

    return {
        "ha_gateway_initialized": True,
        "ha_stats": ha_stats,
        "lee_connectivity": lee_health,
        "interfaces_count": len(list_all_interfaces()),
        "voice_interfaces": [i.value for i in get_voice_interfaces()],
        "core_interfaces": [i.value for i in get_core_interfaces()],
        "infrastructure_interfaces": [i.value for i in get_infrastructure_interfaces()],
        "deployment_mode": mode.value,
    }

# ===== EXPORTS =====

__all__ = [
    # Core gateway functions
    "ha_execute_operation",
    "get_ha_gateway_stats",
    "reset_ha_gateway_state",
    "enable_ha_fast_path",
    "disable_ha_fast_path",
    "clear_ha_fast_path_cache",

    # Enums and utilities
    "HAGatewayInterface",
    "get_interface_description",
    "list_all_interfaces",
    "get_voice_interfaces",
    "get_core_interfaces",
    "get_infrastructure_interfaces",

    "ha_alarm_control_panel_alarm_arm_away",
    "ha_alarm_control_panel_alarm_arm_custom_bypass",
    "ha_alarm_control_panel_alarm_arm_home",
    "ha_alarm_control_panel_alarm_arm_night",
    "ha_alarm_control_panel_alarm_disarm",
    "ha_alarm_control_panel_alarm_trigger",
    "ha_alarm_control_panel_list_alarm_control_panels",
    "ha_alexa_handle_discovery",
    "ha_alexa_process_directive",
    "ha_assist_process_conversation",
    "ha_assist_send_message",
    "ha_automation_disable_automation",
    "ha_automation_enable_automation",
    "ha_automation_get_automation",
    "ha_automation_get_script",
    "ha_automation_list_automations",
    "ha_automation_list_scripts",
    "ha_automation_list_triggers",
    "ha_automation_reload_automations",
    "ha_automation_reload_scripts",
    "ha_automation_run_script",
    "ha_automation_trigger_automation",
    "ha_backup_create",
    "ha_backup_delete",
    "ha_backup_get_details",
    "ha_backup_get_info",
    "ha_backup_restore",
    "ha_binary_sensor_list_binary_sensors",
    "ha_binary_sensor_reload_binary_sensors",
    "ha_blueprint_delete_blueprint",
    "ha_blueprint_import_blueprint",
    "ha_blueprint_list_blueprints",
    "ha_blueprint_save_blueprint",
    "ha_blueprint_substitute_blueprint",
    "ha_button_list_buttons",
    "ha_button_press",
    "ha_calendar_create_event",
    "ha_calendar_list",
    "ha_camera_disable_motion_detection",
    "ha_camera_enable_motion_detection",
    "ha_camera_get_capabilities",
    "ha_camera_get_info",
    "ha_camera_get_stream_url",
    "ha_camera_list",
    "ha_camera_list_cameras",
    "ha_camera_play_stream",
    "ha_camera_record",
    "ha_camera_snapshot",
    "ha_camera_take_snapshot",
    "ha_camera_turn_off",
    "ha_camera_turn_on",
    "ha_climate_list_climates",
    "ha_climate_set_hvac_mode",
    "ha_climate_set_preset_mode",
    "ha_climate_set_temperature",
    "ha_climate_turn_off",
    "ha_climate_turn_on",
    "ha_config_get_ha_config",
    "ha_config_get_ha_entities",
    "ha_conversation_hass_agent_debug",
    "ha_conversation_hass_agent_language_scores",
    "ha_conversation_list_agents",
    "ha_conversation_list_sentences",
    "ha_conversation_prepare",
    "ha_conversation_process",
    "ha_conversation_subscribe_chat_log",
    "ha_conversation_subscribe_chat_log_index",
    "ha_counter_increment_counter",
    "ha_counter_list_counters",
    "ha_counter_reset_counter",
    "ha_cover_close",
    "ha_cover_list_covers",
    "ha_cover_open",
    "ha_cover_set_position",
    "ha_cover_stop",
    "ha_cover_toggle",
    "ha_devices_call_service",
    "ha_devices_call_service_batch",
    "ha_devices_get_by_id",
    "ha_devices_get_states",
    "ha_devices_get_states_batch",
    "ha_energy_get_fossil_energy_consumption",
    "ha_energy_get_info",
    "ha_energy_get_preferences",
    "ha_energy_get_solar_forecast",
    "ha_energy_save_preferences",
    "ha_energy_validate_config",
    "ha_esphome_get_encryption_key",
    "ha_fan_increase_speed",
    "ha_fan_list_fans",
    "ha_fan_set_percentage",
    "ha_fan_set_speed",
    "ha_fan_toggle",
    "ha_fan_turn_off",
    "ha_fan_turn_on",
    "ha_generate_correlation_id",
    "ha_group_list_groups",
    "ha_group_reload",
    "ha_group_set",
    "ha_hardware_get_info",
    "ha_health_check_lee_connectivity",
    "ha_health_check_system",
    "ha_history_get_during_period",
    "ha_humidifier_list_humidifiers",
    "ha_humidifier_set_humidity",
    "ha_humidifier_set_mode",
    "ha_humidifier_toggle",
    "ha_humidifier_turn_off",
    "ha_humidifier_turn_on",
    "ha_image_processing_scan",
    "ha_input_boolean_list_input_booleans",
    "ha_input_boolean_reload",
    "ha_input_boolean_toggle",
    "ha_input_boolean_turn_off",
    "ha_input_boolean_turn_on",
    "ha_input_button_list_input_buttons",
    "ha_input_button_press",
    "ha_input_button_reload",
    "ha_input_datetime_list_input_datetimes",
    "ha_input_datetime_reload",
    "ha_input_datetime_set_datetime",
    "ha_input_number_decrement",
    "ha_input_number_increment",
    "ha_input_number_list_input_numbers",
    "ha_input_number_reload",
    "ha_input_number_set_value",
    "ha_input_select_list_input_selects",
    "ha_input_select_reload",
    "ha_input_select_select_first_option",
    "ha_input_select_select_last_option",
    "ha_input_select_select_next_option",
    "ha_input_select_select_option",
    "ha_input_select_select_previous_option",
    "ha_input_select_set_options",
    "ha_input_text_list_input_texts",
    "ha_input_text_reload",
    "ha_input_text_set_value",
    "ha_light_list_lights",
    "ha_light_set_brightness",
    "ha_light_set_color_temp",
    "ha_light_set_rgb_color",
    "ha_light_toggle",
    "ha_light_turn_off",
    "ha_light_turn_on",
    "ha_lock_list_locks",
    "ha_lock_lock",
    "ha_lock_open",
    "ha_lock_unlock",
    "ha_log_error",
    "ha_log_info",
    "ha_logbook_get_events",
    "ha_logger_get_info",
    "ha_logger_set_integration_level",
    "ha_logger_set_module_level",
    "ha_media_player_list_media_players",
    "ha_media_player_pause",
    "ha_media_player_play_media",
    "ha_media_player_stop",
    "ha_media_player_turn_off",
    "ha_media_player_turn_on",
    "ha_media_player_volume_set",
    "ha_metrics_put",
    "ha_mobile_app_confirm_push_notification",
    "ha_mobile_app_register_push_channel",
    "ha_notify_send_message",
    "ha_number_get_device_class_units",
    "ha_persistent_dismiss_notification",
    "ha_persistent_get_notifications",
    "ha_person_list_persons",
    "ha_person_reload",
    "ha_registry_create_area",
    "ha_registry_delete_area",
    "ha_registry_delete_device",
    "ha_registry_get_area",
    "ha_registry_get_device",
    "ha_registry_get_entity",
    "ha_registry_list_areas",
    "ha_registry_list_categories",
    "ha_registry_list_devices",
    "ha_registry_list_entities",
    "ha_registry_remove_entity",
    "ha_registry_update_area",
    "ha_registry_update_device",
    "ha_registry_update_entity",
    "ha_remote_delete_command",
    "ha_remote_learn_command",
    "ha_remote_list",
    "ha_remote_send_command",
    "ha_remote_toggle",
    "ha_remote_turn_off",
    "ha_remote_turn_on",
    "ha_repairs_get_issue_data",
    "ha_repairs_ignore_issue",
    "ha_repairs_list_issues",
    "ha_scene_activate",
    "ha_scene_apply",
    "ha_scene_create",
    "ha_scene_list",
    "ha_scene_reload",
    "ha_scene_turn_on",
    "ha_script_run",
    "ha_sensor_get_device_class_units",
    "ha_sensor_get_numeric_device_classes",
    "ha_siren_list",
    "ha_siren_toggle",
    "ha_siren_turn_off",
    "ha_siren_turn_on",
    "ha_statistics_adjust_sum_statistics",
    "ha_statistics_change_statistics_unit",
    "ha_statistics_clear_statistics",
    "ha_statistics_get_statistic_during_period",
    "ha_statistics_get_statistics_during_period",
    "ha_statistics_get_statistics_metadata",
    "ha_statistics_import_statistics",
    "ha_statistics_list_statistic_ids",
    "ha_statistics_update_statistics_issues",
    "ha_statistics_update_statistics_metadata",
    "ha_statistics_validate_statistics",
    "ha_supervisor_get_addon_info",
    "ha_supervisor_get_core_info",
    "ha_supervisor_get_host_info",
    "ha_supervisor_get_info",
    "ha_supervisor_get_os_info",
    "ha_supervisor_list_addons",
    "ha_supervisor_restart_addon",
    "ha_supervisor_start_addon",
    "ha_supervisor_stop_addon",
    "ha_switch_list_switches",
    "ha_switch_toggle",
    "ha_switch_turn_off",
    "ha_switch_turn_on",
    "ha_timed_backup_create_backup",
    "ha_timed_backup_delete_backup",
    "ha_timed_backup_list_backups",
    "ha_timed_backup_restore_backup",
    "ha_timer_cancel_timer",
    "ha_timer_change_timer",
    "ha_timer_finish_timer",
    "ha_timer_list_timers",
    "ha_timer_pause_timer",
    "ha_timer_start_timer",
    "ha_tts_say",
    "ha_tts_speak",
    "ha_update_install",
    "ha_update_list",
    "ha_update_skip",
    "ha_vacuum_clean_spot",
    "ha_vacuum_list_vacuums",
    "ha_vacuum_locate",
    "ha_vacuum_pause",
    "ha_vacuum_return_to_base",
    "ha_vacuum_start",
    "ha_vacuum_stop",
    "ha_validate_string",
    "ha_water_heater_list_water_heaters",
    "ha_water_heater_set_away_mode",
    "ha_water_heater_set_operation_mode",
    "ha_water_heater_set_temperature",
    "ha_water_heater_turn_off",
    "ha_water_heater_turn_on",
    "ha_weather_get_forecast",
    "ha_weather_get_forecasts",
    "ha_weather_list_weather_entities",
    "ha_zone_get_zone",
    "ha_zone_list_zones",
    "ha_zone_update_zone",
    "initialize_ha_gateway",
]
