"""ha_touch_panel_core.py - Touch Panel Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def navigate_impl(
    device_id=None,
    card_id=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Navigate touch panel to screen.

    Args:
        device_id: Touch panel device ID
        card_id: Target card ID to navigate to
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not device_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id is required",
        }

    if not card_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "card_id is required",
        }

    service_data = {"device_id": device_id, "card_id": card_id}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="touch_panel",
        service="navigate",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def set_brightness_impl(
    device_id=None,
    brightness=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Set touch panel screen brightness.

    Args:
        device_id: Touch panel device ID
        brightness: Brightness level (typically 0-255)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not device_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id is required",
        }

    if brightness is None:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "brightness is required",
        }

    service_data = {"device_id": device_id, "brightness": brightness}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="touch_panel",
        service="set_brightness",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
