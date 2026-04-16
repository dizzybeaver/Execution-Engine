# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_weather_core.py - Core Implementation for Weather Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)


def list_weather_entities_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all weather entities."""
    result = list_devices_impl("weather", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "weather_entities": result.get("weather", []),
            "count": result.get("count", 0)
        }

    return result


def get_forecast_impl(
    entity_id: Optional[str] = None,
    forecast_type: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get weather forecast."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not forecast_type:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "forecast_type is required"
        }

    service_data = {
        "entity_id": entity_id,
        "type": forecast_type
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="weather",
        service="get_forecast",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Weather forecast retrieved successfully"

    return result


def get_forecasts_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get multiple weather forecasts."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="weather",
        service="get_forecasts",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Weather forecasts retrieved successfully"

    return result


def get_weather_impl(
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get current weather data.

    Retrieves current weather conditions including temperature,
    humidity, pressure, wind, etc.

    Args:
        entity_id: Weather entity ID (e.g., "weather.home")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and weather data
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_state",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            state = result.get("result", {})
            attributes = state.get("attributes", {})

            return {
                "success": True,
                "entity_id": entity_id,
                "temperature": attributes.get("temperature"),
                "humidity": attributes.get("humidity"),
                "pressure": attributes.get("pressure"),
                "wind_speed": attributes.get("wind_speed"),
                "wind_bearing": attributes.get("wind_bearing"),
                "visibility": attributes.get("visibility"),
                "condition": state.get("state"),
                "forecast": attributes.get("forecast"),
                "attribution": attributes.get("attribution"),
                "friendly_name": attributes.get("friendly_name")
            }

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting weather: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting weather: {e!s}"
        }


def get_state_impl(
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get weather entity state with all attributes.

    Retrieves full weather entity state including all attributes.

    Args:
        entity_id: Weather entity ID (e.g., "weather.home")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and full weather state
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_state",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            state = result.get("result", {})
            return {
                "success": True,
                "entity_id": entity_id,
                "state": state.get("state"),
                "attributes": state.get("attributes", {}),
                "last_changed": state.get("last_changed"),
                "last_updated": state.get("last_updated"),
                "context": state.get("context")
            }

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting weather state: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting weather state: {e!s}"
        }


__all__ = [
    "list_weather_entities_impl",
    "get_forecast_impl",
    "get_forecasts_impl",
    "get_weather_impl",
    "get_state_impl",
]
