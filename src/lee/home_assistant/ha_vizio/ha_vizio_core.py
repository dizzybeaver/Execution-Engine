"""ha_vizio_core.py - Vizio TV Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def update_setting_impl(
    entity_id=None,
    setting_type=None,
    setting_name=None,
    new_value=None,
    ha_config=None,
    correlation_id=None,
    **kwargs,
):
    """Update Vizio TV setting.

    Args:
        entity_id: Vizio media player entity ID (required)
        setting_type: Setting type (required)
        setting_name: Setting name (required)
        new_value: New value (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not setting_type or not setting_name or not new_value:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id, setting_type, setting_name, and new_value are required",
        }

    service_data = {
        "entity_id": entity_id,
        "setting_type": setting_type,
        "setting_name": setting_name,
        "new_value": new_value,
    }

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="vizio",
            service="update_setting",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {e}",
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": str(e),
        }
