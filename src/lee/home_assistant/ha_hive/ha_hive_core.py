"""ha_hive_core.py - Hive Heating Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def boost_heating_on_impl(
    entity_id=None, time_period=None, temperature=None, ha_config=None, correlation_id=None, **kwargs
):
    """Boost heating on Hive thermostat.

    Args:
        entity_id: Hive thermostat entity ID (required)
        time_period: Time period for boost (required)
        temperature: Temperature override (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not time_period:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and time_period are required",
        }

    service_data = {"entity_id": entity_id, "time_period": time_period}

    if temperature is not None:
        service_data["temperature"] = temperature

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="hive", service="boost_heating_on",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def boost_heating_off_impl(
    entity_id=None, ha_config=None, correlation_id=None, **kwargs
):
    """Turn off heating boost on Hive thermostat.

    Args:
        entity_id: Hive thermostat entity ID (required)
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

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="hive", service="boost_heating_off",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def boost_hot_water_impl(
    entity_id=None, time_period=None, on_off=None, ha_config=None, correlation_id=None, **kwargs
):
    """Boost hot water on Hive system.

    Args:
        entity_id: Hive hot water entity ID (required)
        time_period: Time period for boost (required)
        on_off: On or off state (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not time_period or on_off is None:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id, time_period, and on_off are required",
        }

    service_data = {"entity_id": entity_id, "time_period": time_period, "on_off": on_off}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="hive", service="boost_hot_water",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
