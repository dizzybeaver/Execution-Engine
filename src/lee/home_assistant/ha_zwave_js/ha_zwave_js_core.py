"""ha_zwave_js_core.py - Z-Wave JS Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def clear_lock_usercode_impl(entity_id=None, code_slot=None, ha_config=None, correlation_id=None, **kwargs):
    """Clear Z-Wave lock usercode.

    Args:
        entity_id: Z-Wave lock entity ID
        code_slot: Code slot number to clear
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not code_slot:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and code_slot are required",
        }

    service_data = {"entity_id": entity_id, "code_slot": code_slot}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zwave_js",
        service="clear_lock_usercode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def get_lock_usercode_impl(entity_id=None, code_slot=None, ha_config=None, correlation_id=None, **kwargs):
    """Get Z-Wave lock usercode.

    Args:
        entity_id: Z-Wave lock entity ID
        code_slot: Code slot number (optional, gets all if not specified)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if code_slot is not None:
        service_data["code_slot"] = code_slot

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zwave_js",
        service="get_lock_usercode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def set_lock_usercode_impl(entity_id=None, code_slot=None, usercode=None, ha_config=None, correlation_id=None, **kwargs):
    """Set Z-Wave lock usercode.

    Args:
        entity_id: Z-Wave lock entity ID
        code_slot: Code slot number to set
        usercode: Usercode value to set
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not code_slot or not usercode:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id, code_slot, and usercode are required",
        }

    service_data = {"entity_id": entity_id, "code_slot": code_slot, "usercode": usercode}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zwave_js",
        service="set_lock_usercode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
