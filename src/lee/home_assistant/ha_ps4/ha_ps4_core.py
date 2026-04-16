"""ha_ps4_core.py - PlayStation 4 Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def send_command_impl(
    entity_id=None, command=None, ha_config=None, correlation_id=None, **kwargs
):
    """Send command to PS4.

    Args:
        entity_id: PS4 media player entity ID (required)
        command: Command to send (required) - back, down, enter, left, option, ps_hold, ps, right, up
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not command:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and command are required",
        }

    service_data = {"entity_id": entity_id, "command": command}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="ps4",
            service="send_command",
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
