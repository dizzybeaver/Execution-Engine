"""ha_shelly_core.py - Shelly Smart Home Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def get_kvs_value_impl(
    device_id=None, key=None, ha_config=None, correlation_id=None, **kwargs
):
    """Get key-value store value from Shelly device.

    Args:
        device_id: Shelly device ID (required)
        key: Key name to retrieve (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not device_id or not key:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id and key are required",
        }

    service_data = {"device_id": device_id, "key": key}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="shelly", service="get_kvs_value",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def set_kvs_value_impl(
    device_id=None, key=None, value=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set key-value store value on Shelly device.

    Args:
        device_id: Shelly device ID (required)
        key: Key name to set (required)
        value: Value to set (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not device_id or not key or value is None:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "device_id, key, and value are required",
        }

    service_data = {"device_id": device_id, "key": key, "value": value}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="shelly", service="set_kvs_value",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
