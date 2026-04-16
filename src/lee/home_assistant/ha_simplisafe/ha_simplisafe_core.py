"""ha_simplisafe_core.py - SimpliSafe Security Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def remove_pin_impl(
    device_id=None, label_or_pin=None, ha_config=None, correlation_id=None, **kwargs
):
    """Remove PIN from SimpliSafe security system.

    Args:
        device_id: SimpliSafe device ID (required)
        label_or_pin: PIN label or PIN value to remove (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not device_id or not label_or_pin:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id and label_or_pin are required",
        }

    service_data = {"device_id": device_id, "label_or_pin": label_or_pin}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="simplisafe", service="remove_pin",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def set_pin_impl(
    device_id=None, label=None, pin=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set PIN on SimpliSafe security system.

    Args:
        device_id: SimpliSafe device ID (required)
        label: PIN label (required)
        pin: PIN value (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not device_id or not label or not pin:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id, label, and pin are required",
        }

    service_data = {"device_id": device_id, "label": label, "pin": pin}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="simplisafe", service="set_pin",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def set_system_properties_impl(
    device_id=None, alarm_duration=None, alarm_volume=None, chime_volume=None,
    entry_delay_away=None, entry_delay_home=None, exit_delay_away=None,
    exit_delay_home=None, light=None, voice_prompt_volume=None,
    ha_config=None, correlation_id=None, **kwargs
):
    """Set system properties on SimpliSafe security system.

    Args:
        device_id: SimpliSafe device ID (required)
        alarm_duration: Alarm duration 30-480 seconds (optional)
        alarm_volume: Alarm volume - low, medium, high, off (optional)
        chime_volume: Chime volume - low, medium, high, off (optional)
        entry_delay_away: Entry delay away mode 30-255 seconds (optional)
        entry_delay_home: Entry delay home mode 0-255 seconds (optional)
        exit_delay_away: Exit delay away mode 45-255 seconds (optional)
        exit_delay_home: Exit delay home mode 0-255 seconds (optional)
        light: Light on/off (optional)
        voice_prompt_volume: Voice prompt volume - low, medium, high, off (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not device_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id is required",
        }

    service_data = {"device_id": device_id}

    if alarm_duration is not None:
        service_data["alarm_duration"] = alarm_duration
    if alarm_volume is not None:
        service_data["alarm_volume"] = alarm_volume
    if chime_volume is not None:
        service_data["chime_volume"] = chime_volume
    if entry_delay_away is not None:
        service_data["entry_delay_away"] = entry_delay_away
    if entry_delay_home is not None:
        service_data["entry_delay_home"] = entry_delay_home
    if exit_delay_away is not None:
        service_data["exit_delay_away"] = exit_delay_away
    if exit_delay_home is not None:
        service_data["exit_delay_home"] = exit_delay_home
    if light is not None:
        service_data["light"] = light
    if voice_prompt_volume is not None:
        service_data["voice_prompt_volume"] = voice_prompt_volume

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="simplisafe", service="set_system_properties",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
