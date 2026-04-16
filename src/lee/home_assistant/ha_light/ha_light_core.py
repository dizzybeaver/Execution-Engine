# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_light_core.py - Core Implementation for Light Interface

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
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils.error_response_factory import missing_parameter

# ===== LIST LIGHTS =====

def list_lights_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all light entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - lights: list of light entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    result = list_devices_impl("light", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "lights": result.get("light", []),
            "count": result.get("count", 0)
        }

    return result


# ===== TURN ON LIGHT =====

def turn_on_light_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn light on.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters (brightness, color_temp, rgb_color)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return turn_on_device_impl("light", entity_id, ha_config, correlation_id, **kwargs)


# ===== TURN OFF LIGHT =====

def turn_off_light_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn light off.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return turn_off_device_impl("light", entity_id, ha_config, correlation_id, **kwargs)


# ===== TOGGLE LIGHT =====

def toggle_light_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Toggle light state.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="light",
        service="toggle",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Light toggled successfully"

    return result


# ===== SET BRIGHTNESS =====

def set_brightness_light_impl(
    entity_id: Optional[str] = None,
    brightness: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set light brightness.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        brightness: Brightness level (0-255)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if brightness is None:
        return missing_parameter("brightness")

    service_data = {
        "entity_id": entity_id,
        "brightness": brightness
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="light",
        service="turn_on",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Light brightness set successfully"

    return result


# ===== SET COLOR TEMP =====

def set_color_temp_light_impl(
    entity_id: Optional[str] = None,
    color_temp: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set light color temperature.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        color_temp: Color temperature in mireds
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if color_temp is None:
        return missing_parameter("color_temp")

    service_data = {
        "entity_id": entity_id,
        "color_temp": color_temp
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="light",
        service="turn_on",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Light color temperature set successfully"

    return result


# ===== SET RGB COLOR =====

def set_rgb_color_light_impl(
    entity_id: Optional[str] = None,
    rgb_color: Optional[list[int]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set light RGB color.

    Args:
        entity_id: Light entity ID (e.g., "light.living_room")
        rgb_color: RGB color list [r, g, b] (0-255 each)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if rgb_color is None:
        return missing_parameter("rgb_color")

    service_data = {
        "entity_id": entity_id,
        "rgb_color": rgb_color
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="light",
        service="turn_on",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Light RGB color set successfully"

    return result
