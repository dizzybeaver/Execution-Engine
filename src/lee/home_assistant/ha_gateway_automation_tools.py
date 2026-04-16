# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Extracted automation tools from ha_gateway.py

"""ha_gateway_automation_tools.py - Automation Tools for HA Gateway
Version: 2026-04-01
Purpose: Scene, script, notify, remote, and other automation-related interfaces

This module contains functions for automation tools:
- Scene management
- Script execution
- Notifications
- Remote controls
- Siren, update, calendar, TTS, camera, mobile app, logger, hardware
- Sensor, number, persistent notification, conversation
- Zone, counter, timer, input boolean

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Optional

# Core imports
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface

# ===== SCENE CONVENIENCE FUNCTIONS =====

def ha_scene_list(**kwargs) -> dict:
    """List all scenes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "list_scenes", **kwargs)

def ha_scene_turn_on(entity_id: str, transition: Optional[int] = None, **kwargs) -> dict:
    """Turn on a scene through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "turn_on", entity_id=entity_id, transition=transition, **kwargs)

def ha_scene_reload(**kwargs) -> dict:
    """Reload all scenes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "reload", **kwargs)

def ha_scene_apply(entities: dict, transition: Optional[int] = None, **kwargs) -> dict:
    """Apply scene state to entities through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "apply", entities=entities, transition=transition, **kwargs)

def ha_scene_create(scene_id: str, entities: Optional[dict] = None, snapshot_entities: Optional[list[str]] = None, **kwargs) -> dict:
    """Create a new scene through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "create", scene_id=scene_id, entities=entities, snapshot_entities=snapshot_entities, **kwargs)

def ha_scene_activate(entity_id: str, transition: Optional[float] = None, **kwargs) -> dict:
    """Activate a scene through HA gateway (legacy - use ha_scene_turn_on)."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCENE, "activate_scene", entity_id=entity_id, transition=transition, **kwargs)


# ===== SCRIPT CONVENIENCE FUNCTIONS =====

def ha_script_run(entity_id: str, variables: Optional[dict] = None, **kwargs) -> dict:
    """Run a script through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SCRIPT, "run_script", entity_id=entity_id, variables=variables, **kwargs)


# ===== NOTIFY CONVENIENCE FUNCTIONS =====

def ha_notify_send_message(target: str, message: str, title: Optional[str] = None, data: Optional[dict] = None, **kwargs) -> dict:
    """Send a notification through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.NOTIFY, "send_message", target=target, message=message, title=title, data=data, **kwargs)


# ===== ESPHOME CONVENIENCE FUNCTIONS =====

def ha_esphome_get_encryption_key(entry_id: str, **kwargs) -> dict:
    """Get ESPHome encryption key through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ESPHOME, "get_encryption_key", entry_id=entry_id, **kwargs)


# ===== REMOTE CONVENIENCE FUNCTIONS =====

def ha_remote_list(**kwargs) -> dict:
    """List all remotes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "list_remotes", **kwargs)

def ha_remote_turn_on(entity_id: str, activity: Optional[str] = None, **kwargs) -> dict:
    """Turn on remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "turn_on", entity_id=entity_id, activity=activity, **kwargs)

def ha_remote_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "toggle", entity_id=entity_id, **kwargs)

def ha_remote_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn off remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "turn_off", entity_id=entity_id, **kwargs)

def ha_remote_send_command(entity_id: str, command: dict, device: Optional[str] = None, num_repeats: Optional[int] = None, delay_secs: Optional[float] = None, hold_secs: Optional[float] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments
    """Send command to remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "send_command", entity_id=entity_id, command=command, device=device, num_repeats=num_repeats, delay_secs=delay_secs, hold_secs=hold_secs, **kwargs)

def ha_remote_learn_command(entity_id: str, device: str, command: dict, command_type: Optional[str] = None, alternative: Optional[bool] = None, timeout: Optional[int] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments
    """Learn command on remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "learn_command", entity_id=entity_id, device=device, command=command, command_type=command_type, alternative=alternative, timeout=timeout, **kwargs)

def ha_remote_delete_command(entity_id: str, device: str, command: dict, **kwargs) -> dict:
    """Delete command from remote through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REMOTE, "delete_command", entity_id=entity_id, device=device, command=command, **kwargs)


# ===== SIREN CONVENIENCE FUNCTIONS =====

def ha_siren_list(**kwargs) -> dict:
    """List all sirens through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SIREN, "list_sirens", **kwargs)

def ha_siren_turn_on(entity_id: str, tone: Optional[str] = None, volume_level: Optional[float] = None, duration: Optional[int] = None, **kwargs) -> dict:
    """Turn on siren through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SIREN, "turn_on", entity_id=entity_id, tone=tone, volume_level=volume_level, duration=duration, **kwargs)

def ha_siren_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn off siren through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SIREN, "turn_off", entity_id=entity_id, **kwargs)

def ha_siren_toggle(entity_id: str, **kwargs) -> dict:
    """Toggle siren through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SIREN, "toggle", entity_id=entity_id, **kwargs)


# ===== UPDATE CONVENIENCE FUNCTIONS =====

def ha_update_list(**kwargs) -> dict:
    """List all updates through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.UPDATE, "list_updates", **kwargs)

def ha_update_install(entity_id: str, version: Optional[str] = None, backup: Optional[bool] = None, **kwargs) -> dict:
    """Install update through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.UPDATE, "install", entity_id=entity_id, version=version, backup=backup, **kwargs)

def ha_update_skip(entity_id: str, **kwargs) -> dict:
    """Skip update through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.UPDATE, "skip", entity_id=entity_id, **kwargs)


# ===== CALENDAR CONVENIENCE FUNCTIONS =====

def ha_calendar_list(**kwargs) -> dict:
    """List all calendars through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CALENDAR, "list_calendars", **kwargs)

def ha_calendar_create_event(entity_id: str, summary: str, description: Optional[str] = None, start_date_time: Optional[str] = None, end_date_time: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, in_param: Optional[dict] = None, location: Optional[str] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments
    """Create calendar event through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CALENDAR, "create_event", entity_id=entity_id, summary=summary, description=description, start_date_time=start_date_time, end_date_time=end_date_time, start_date=start_date, end_date=end_date, in_param=in_param, location=location, **kwargs)


# ===== IMAGE PROCESSING CONVENIENCE FUNCTIONS =====

def ha_image_processing_scan(entity_id: str, **kwargs) -> dict:
    """Scan image through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.IMAGE_PROCESSING, "scan", entity_id=entity_id, **kwargs)


# ===== TTS CONVENIENCE FUNCTIONS =====

def ha_tts_say(entity_id: str, message: str, cache: Optional[bool] = None, language: Optional[str] = None, options: Optional[dict] = None, **kwargs) -> dict:
    """Text-to-speech through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TTS, "say", entity_id=entity_id, message=message, cache=cache, language=language, options=options, **kwargs)

def ha_tts_speak(entity_id: str, media_player_entity_id: str, message: Optional[str] = None, **kwargs) -> dict:
    """Speak through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TTS, "speak", entity_id=entity_id, media_player_entity_id=media_player_entity_id, message=message, **kwargs)


# ===== CAMERA CONVENIENCE FUNCTIONS =====

def ha_camera_list(**kwargs) -> dict:
    """List all cameras through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "list_cameras", **kwargs)

def ha_camera_turn_on(entity_id: str, **kwargs) -> dict:
    """Turn on camera through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "turn_on", entity_id=entity_id, **kwargs)

def ha_camera_turn_off(entity_id: str, **kwargs) -> dict:
    """Turn off camera through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "turn_off", entity_id=entity_id, **kwargs)

def ha_camera_enable_motion_detection(entity_id: str, **kwargs) -> dict:
    """Enable motion detection on camera through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "enable_motion_detection", entity_id=entity_id, **kwargs)

def ha_camera_disable_motion_detection(entity_id: str, **kwargs) -> dict:
    """Disable motion detection on camera through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "disable_motion_detection", entity_id=entity_id, **kwargs)

def ha_camera_snapshot(entity_id: str, filename: str, **kwargs) -> dict:
    """Take camera snapshot through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "snapshot", entity_id=entity_id, filename=filename, **kwargs)

def ha_camera_play_stream(entity_id: str, media_player: str, format_param: Optional[str] = None, **kwargs) -> dict:
    """Play camera stream through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "play_stream", entity_id=entity_id, media_player=media_player, format=format_param, **kwargs)

def ha_camera_record(entity_id: str, filename: str, duration: Optional[int] = None, lookback: Optional[int] = None, **kwargs) -> dict:
    """Record camera video through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "record", entity_id=entity_id, filename=filename, duration=duration, lookback=lookback, **kwargs)


# ===== MOBILE APP CONVENIENCE FUNCTIONS =====

def ha_mobile_app_register_push_channel(webhook_id: str, support_confirm: bool = False, **kwargs) -> dict:
    """Register mobile app push notification channel through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MOBILE_APP, "register_push_channel", webhook_id=webhook_id, support_confirm=support_confirm, **kwargs)

def ha_mobile_app_confirm_push_notification(webhook_id: str, confirm_id: str, **kwargs) -> dict:
    """Confirm mobile app push notification delivery through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.MOBILE_APP, "confirm_push_notification", webhook_id=webhook_id, confirm_id=confirm_id, **kwargs)


# ===== LOGGER CONVENIENCE FUNCTIONS =====

def ha_logger_get_info(**kwargs) -> dict:
    """Get logger information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOGGER, "get_log_info", **kwargs)

def ha_logger_set_integration_level(integration: str, level: str, persistence: bool = False, **kwargs) -> dict:
    """Set integration log level through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOGGER, "set_integration_log_level", integration=integration, level=level, persistence=persistence, **kwargs)

def ha_logger_set_module_level(module: str, level: str, persistence: bool = False, **kwargs) -> dict:
    """Set module log level through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOGGER, "set_module_log_level", module=module, level=level, persistence=persistence, **kwargs)


# ===== HARDWARE CONVENIENCE FUNCTIONS =====

def ha_hardware_get_info(**kwargs) -> dict:
    """Get hardware information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HARDWARE, "get_hardware_info", **kwargs)


# ===== SENSOR CONVENIENCE FUNCTIONS =====

def ha_sensor_get_device_class_units(device_class: str, **kwargs) -> dict:
    """Get convertible units for sensor device class through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SENSOR, "get_device_class_units", device_class=device_class, **kwargs)

def ha_sensor_get_numeric_device_classes(**kwargs) -> dict:
    """Get numeric sensor device classes through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SENSOR, "get_numeric_device_classes", **kwargs)


# ===== NUMBER CONVENIENCE FUNCTIONS =====

def ha_number_get_device_class_units(device_class: str, **kwargs) -> dict:
    """Get convertible units for number device class through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.NUMBER, "get_device_class_units", device_class=device_class, **kwargs)


# ===== PERSISTENT NOTIFICATION CONVENIENCE FUNCTIONS =====

def ha_persistent_get_notifications(**kwargs) -> dict:
    """Get persistent notifications through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.PERSISTENT, "get_notifications", **kwargs)


def ha_persistent_dismiss_notification(notification_id: str, **kwargs) -> dict:
    """Dismiss persistent notification through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.PERSISTENT, "dismiss_notification", notification_id=notification_id, **kwargs)


# ===== CONVERSATION CONVENIENCE FUNCTIONS =====

def ha_conversation_process(text: str, **kwargs) -> dict:
    """Process text through conversation agent through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "process", text=text, **kwargs)


def ha_conversation_prepare(**kwargs) -> dict:
    """Prepare/reload conversation agent through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "prepare", **kwargs)


def ha_conversation_list_agents(**kwargs) -> dict:
    """List conversation agents through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "list_agents", **kwargs)


def ha_conversation_list_sentences(language: str, **kwargs) -> dict:
    """List training sentences through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "list_sentences", language=language, **kwargs)


def ha_conversation_hass_agent_debug(text: str, **kwargs) -> dict:
    """Debug HassAgent through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "hass_agent_debug", text=text, **kwargs)


def ha_conversation_hass_agent_language_scores(text: str, **kwargs) -> dict:
    """Get language detection scores through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "hass_agent_language_scores", text=text, **kwargs)


def ha_conversation_subscribe_chat_log(**kwargs) -> dict:
    """Subscribe to chat log through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "subscribe_chat_log", **kwargs)


def ha_conversation_subscribe_chat_log_index(**kwargs) -> dict:
    """Subscribe to chat log index through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONVERSATION, "subscribe_chat_log_index", **kwargs)