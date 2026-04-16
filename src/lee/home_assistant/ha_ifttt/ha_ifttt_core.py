"""ha_ifttt_core.py - IFTTT Webhook Automation Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def push_alarm_state_impl(
    entity_id=None, state=None, ha_config=None, correlation_id=None, **kwargs
):
    """Push alarm state to IFTTT.

    Args:
        entity_id: Alarm control panel entity ID (required)
        state: Alarm state (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not state:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and state are required",
        }

    service_data = {"entity_id": entity_id, "state": state}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="ifttt", service="push_alarm_state",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def trigger_impl(
    event=None, value1=None, value2=None, value3=None, ha_config=None, correlation_id=None, **kwargs
):
    """Trigger IFTTT webhook event.

    Args:
        event: Event name (required)
        value1: First value (optional)
        value2: Second value (optional)
        value3: Third value (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not event:
        return missing_parameter("event")

    service_data = {"event": event}

    if value1 is not None:
        service_data["value1"] = value1
    if value2 is not None:
        service_data["value2"] = value2
    if value3 is not None:
        service_data["value3"] = value3

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="ifttt", service="trigger",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
