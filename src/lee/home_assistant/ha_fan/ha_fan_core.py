# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_fan_core.py - Core Implementation for Fan Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    turn_off_device_impl,
    turn_on_device_impl,
)
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def list_fans_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all fan entities."""
    result = list_devices_impl("fan", ha_config, correlation_id, **_kwargs)
    if result.get("success"):
        return {
            "success": True,
            "fans": result.get("fan", []),
            "count": result.get("count", 0)
        }
    return result


def turn_on_fan_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn fan on."""
    return turn_on_device_impl("fan", entity_id, ha_config, correlation_id, **kwargs)


def turn_off_fan_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn fan off."""
    return turn_off_device_impl("fan", entity_id, ha_config, correlation_id, **kwargs)


def toggle_fan_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Toggle fan."""
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="fan",
        service="toggle",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Fan toggled successfully"

    return result


def set_speed_impl(
    entity_id: Optional[str] = None,
    speed: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set fan speed."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not speed:
        return missing_parameter("speed")

    service_data = {
        "entity_id": entity_id,
        "speed": speed
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="fan",
        service="set_speed",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Fan speed set successfully"

    return result


def set_percentage_impl(
    entity_id: Optional[str] = None,
    percentage: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set fan percentage."""
    if not entity_id:
        return missing_parameter("entity_id")

    if percentage is None:
        return missing_parameter("percentage")

    service_data = {
        "entity_id": entity_id,
        "percentage": percentage
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="fan",
        service="set_percentage",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Fan percentage set successfully"

    return result


def increase_speed_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Increase fan speed."""
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="fan",
        service="increase_speed",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Fan speed increased successfully"

    return result
