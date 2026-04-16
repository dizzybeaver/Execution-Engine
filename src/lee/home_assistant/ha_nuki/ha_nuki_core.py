"""ha_nuki_core.py - Nuki Smart Lock Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def lock_n_go_impl(
    entity_id=None, unlatch=None, ha_config=None, correlation_id=None, **kwargs
):
    """Lock Nuki and go.

    Args:
        entity_id: Nuki lock entity ID (required)
        unlatch: Also unlatch door (optional, default false)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    if unlatch is not None:
        service_data["unlatch"] = unlatch

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="nuki",
            service="lock_n_go",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }


def set_continuous_mode_impl(
    entity_id=None, enable=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set Nuki continuous mode.

    Args:
        entity_id: Nuki lock entity ID (required)
        enable: Enable continuous mode (optional, default false)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    if enable is not None:
        service_data["enable"] = enable

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="nuki",
            service="set_continuous_mode",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }
