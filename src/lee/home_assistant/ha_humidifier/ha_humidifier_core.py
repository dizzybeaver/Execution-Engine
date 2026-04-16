# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use ha_device_base functions


"""ha_humidifier_core.py - Core Implementation for Humidifier Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    toggle_device_impl,
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


def list_humidifiers_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all humidifier entities."""
    result = list_devices_impl("humidifier", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "humidifiers": result.get("humidifier", []),
            "count": result.get("count", 0)
        }

    return result


def turn_on_humidifier_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Turn humidifier on."""
    result = turn_on_device_impl(
        "humidifier",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Humidifier turned on successfully"

    return result


def turn_off_humidifier_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Turn humidifier off."""
    result = turn_off_device_impl(
        "humidifier",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Humidifier turned off successfully"

    return result


def set_humidity_impl(
    entity_id: Optional[str] = None,
    humidity: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set humidifier target humidity."""
    if not entity_id:
        return missing_parameter("entity_id")

    if humidity is None:
        return missing_parameter("humidity")

    service_data = {
        "entity_id": entity_id,
        "humidity": humidity
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="humidifier",
        service="set_humidity",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Humidity set successfully"

    return result


def set_mode_impl(
    entity_id: Optional[str] = None,
    mode: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set humidifier mode."""
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
        domain="humidifier",
        service="set_mode",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Mode set successfully"

    return result


def toggle_humidifier_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Toggle humidifier."""
    result = toggle_device_impl(
        "humidifier",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Humidifier toggled successfully"

    return result
