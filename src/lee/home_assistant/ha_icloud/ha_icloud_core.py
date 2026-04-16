"""ha_icloud_core.py - iCloud Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def update_impl(
    account=None, ha_config=None, correlation_id=None, **kwargs
):
    """Update iCloud account.

    Args:
        account: iCloud account (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not account:
        return missing_parameter("account")

    service_data = {"account": account}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="icloud", service="update",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def play_sound_impl(
    account=None, device_name=None, ha_config=None, correlation_id=None, **kwargs
):
    """Play sound on iCloud device.

    Args:
        account: iCloud account (required)
        device_name: Device name (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not account or not device_name:
        return {
            "success": False, "error_code": "MISSING_PARAMETER",
            "error_message": "account and device_name are required"
        }

    service_data = {"account": account, "device_name": device_name}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="icloud", service="play_sound",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def display_message_impl(
    account=None, device_name=None, message=None, sound=None, ha_config=None, correlation_id=None, **kwargs
):
    """Display message on iCloud device.

    Args:
        account: iCloud account (required)
        device_name: Device name (required)
        message: Message content (required)
        sound: Play sound (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not account or not device_name or not message:
        return {
            "success": False, "error_code": "MISSING_PARAMETER",
            "error_message": "account, device_name, and message are required"
        }

    service_data = {"account": account, "device_name": device_name, "message": message}

    if sound is not None:
        service_data["sound"] = sound

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="icloud", service="display_message",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def lost_device_impl(
    account=None, device_name=None, number=None, message=None, ha_config=None, correlation_id=None, **kwargs
):
    """Mark iCloud device as lost.

    Args:
        account: iCloud account (required)
        device_name: Device name (required)
        number: Phone number (required)
        message: Message (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not account or not device_name or not number or not message:
        return {
            "success": False, "error_code": "MISSING_PARAMETER",
            "error_message": "account, device_name, number, and message are required"
        }

    service_data = {"account": account, "device_name": device_name, "number": number, "message": message}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="icloud", service="lost_device",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
