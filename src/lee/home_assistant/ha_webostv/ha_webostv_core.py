"""ha_webostv_core.py - LG webOS TV Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def button_impl(entity_id=None, button=None, ha_config=None, correlation_id=None, **kwargs):
    """Send button command to LG webOS TV.

    Args:
        entity_id: LG webOS TV media player entity ID
        button: Button to press (e.g., "HOME", "BACK", "LEFT", "RIGHT", "UP", "DOWN")
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not button:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and button are required",
        }

    service_data = {"entity_id": entity_id, "button": button}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="webostv",
        service="button",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def command_impl(entity_id=None, command=None, payload=None, ha_config=None, correlation_id=None, **kwargs):
    """Send command to LG webOS TV.

    Args:
        entity_id: LG webOS TV media player entity ID
        command: Command to send (e.g., "system.launcher/open")
        payload: Command payload (advanced)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not command:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and command are required",
        }

    service_data = {"entity_id": entity_id, "command": command}
    if payload is not None:
        service_data["payload"] = payload

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="webostv",
        service="command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def select_sound_output_impl(entity_id=None, sound_output=None, ha_config=None, correlation_id=None, **kwargs):
    """Select sound output on LG webOS TV.

    Args:
        entity_id: LG webOS TV media player entity ID
        sound_output: Sound output to select (e.g., "external_speaker", "tv_speaker")
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not sound_output:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and sound_output are required",
        }

    service_data = {"entity_id": entity_id, "sound_output": sound_output}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="webostv",
        service="select_sound_output",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
