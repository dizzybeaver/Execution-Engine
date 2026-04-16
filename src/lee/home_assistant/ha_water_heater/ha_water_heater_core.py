# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_water_heater_core.py - Core Implementation for Water Heater Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    turn_off_device_impl,
    turn_on_device_impl,
)
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)
from lee.home_assistant.utils.error_response_factory import (
    missing_parameter,
)


def list_water_heaters_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all water heater entities."""
    result = list_devices_impl("water_heater", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "water_heaters": result.get("water_heater", []),
            "count": result.get("count", 0)
        }

    return result


def turn_on_water_heater_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn water heater on."""
    return turn_on_device_impl(
        "water_heater",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def turn_off_water_heater_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn water heater off."""
    return turn_off_device_impl(
        "water_heater",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def set_temperature_impl(
    entity_id: Optional[str] = None,
    temperature: Optional[float] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set water heater target temperature."""
    if not entity_id:
        return missing_parameter("entity_id")

    if temperature is None:
        return missing_parameter("temperature")

    service_data = {
        "entity_id": entity_id,
        "temperature": temperature
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="water_heater",
        service="set_temperature",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Temperature set successfully"

    return result


def set_operation_mode_impl(
    entity_id: Optional[str] = None,
    operation_mode: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set water heater operation mode."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not operation_mode:
        return missing_parameter("operation_mode")

    service_data = {
        "entity_id": entity_id,
        "operation_mode": operation_mode
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="water_heater",
        service="set_operation_mode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Operation mode set successfully"

    return result


def set_away_mode_impl(
    entity_id: Optional[str] = None,
    mode: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set water heater away mode."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not mode:
        return missing_parameter("mode")

    service_data = {
        "entity_id": entity_id,
        "mode": mode
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="water_heater",
        service="set_away_mode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Away mode set successfully"

    return result
