"""ha_squeezebox_core.py - Squeezebox Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def call_method_impl(
    entity_id=None,
    method=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Call Squeezebox player method.

    Args:
        entity_id: Squeezebox media player entity ID
        method: Player method to call
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

    if not method:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "method is required",
        }

    service_data = {"entity_id": entity_id, "method": method}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="squeezebox",
        service="call_method",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def play_path_impl(
    entity_id=None,
    path=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Play URL path on Squeezebox.

    Args:
        entity_id: Squeezebox media player entity ID
        path: URL path to play
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

    if not path:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "path is required",
        }

    service_data = {"entity_id": entity_id, "path": path}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="squeezebox",
        service="play_path",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
