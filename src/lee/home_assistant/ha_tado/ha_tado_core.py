"""ha_tado_core.py - Tado° Smart Thermostat Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


# pylint: disable=too-many-arguments,too-many-positional-arguments
def set_climate_timer_impl(entity_id=None, temperature=None, time_period=None, requested_overlay=None, ha_config=None, correlation_id=None, **kwargs):
    """Set Tado climate timer.

    Args:
        entity_id: Tado climate entity ID
        temperature: Target temperature (0-100°C)
        time_period: Timer duration (format: "HH:MM:SS", e.g., "01:30:00")
        requested_overlay: Overlay type (NEXT_TIME_BLOCK, MANUAL, TADO_DEFAULT)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not temperature:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and temperature are required",
        }

    service_data = {"entity_id": entity_id, "temperature": temperature}
    if time_period:
        service_data["time_period"] = time_period
    if requested_overlay:
        service_data["requested_overlay"] = requested_overlay

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tado",
        service="set_climate_timer",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def set_water_heater_timer_impl(entity_id=None, time_period=None, temperature=None, ha_config=None, correlation_id=None, **kwargs):
    """Set Tado water heater timer.

    Args:
        entity_id: Tado water heater entity ID
        time_period: Timer duration (format: "HH:MM:SS", default: "01:00:00")
        temperature: Target temperature (0-100°C)
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
    if time_period:
        service_data["time_period"] = time_period
    if temperature:
        service_data["temperature"] = temperature

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tado",
        service="set_water_heater_timer",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def set_climate_temperature_offset_impl(entity_id=None, offset=None, ha_config=None, correlation_id=None, **kwargs):
    """Set Tado climate temperature offset.

    Args:
        entity_id: Tado climate entity ID
        offset: Temperature offset (-10 to +10°C, default: 0)
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
    if offset is not None:
        service_data["offset"] = offset

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tado",
        service="set_climate_temperature_offset",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def add_meter_reading_impl(config_entry=None, reading=None, ha_config=None, correlation_id=None, **kwargs):
    """Add meter reading to Tado.

    Args:
        config_entry: Tado config entry ID
        reading: Meter reading value
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not config_entry or not reading:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "config_entry and reading are required",
        }

    service_data = {"config_entry": config_entry, "reading": reading}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tado",
        service="add_meter_reading",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
