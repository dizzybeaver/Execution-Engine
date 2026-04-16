# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_flux_led_core.py - Flux LED Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def set_custom_effect_impl(
    entity_id=None, colors=None, speed_pct=None, transition=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set custom effect on Flux LED.

    Args:
        entity_id: Flux LED entity ID (required)
        colors: Color list (required)
        speed_pct: Speed percentage 1-100 (optional)
        transition: Transition mode (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not colors:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and colors are required",
        }

    service_data = {"entity_id": entity_id, "colors": colors}

    if speed_pct is not None:
        service_data["speed_pct"] = speed_pct
    if transition is not None:
        service_data["transition"] = transition

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="flux_led", service="set_custom_effect",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def set_zones_impl(
    entity_id=None, colors=None, speed_pct=None, effect=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set zones on Flux LED.

    Args:
        entity_id: Flux LED entity ID (required)
        colors: Color list (required)
        speed_pct: Speed percentage (optional)
        effect: Effect type (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or not colors:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and colors are required",
        }

    service_data = {"entity_id": entity_id, "colors": colors}

    if speed_pct is not None:
        service_data["speed_pct"] = speed_pct
    if effect is not None:
        service_data["effect"] = effect

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="flux_led", service="set_zones",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def set_music_mode_impl(
    entity_id=None, sensitivity=None, brightness=None, light_screen=None, effect=None,
    foreground_color=None, background_color=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set music mode on Flux LED.

    Args:
        entity_id: Flux LED entity ID (required)
        sensitivity: Sensitivity 1-100 (optional)
        brightness: Brightness 1-100 (optional)
        light_screen: Light screen mode (optional)
        effect: Effect number 0-16 (optional)
        foreground_color: Foreground RGB color (optional)
        background_color: Background RGB color (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    if sensitivity is not None:
        service_data["sensitivity"] = sensitivity
    if brightness is not None:
        service_data["brightness"] = brightness
    if light_screen is not None:
        service_data["light_screen"] = light_screen
    if effect is not None:
        service_data["effect"] = effect
    if foreground_color is not None:
        service_data["foreground_color"] = foreground_color
    if background_color is not None:
        service_data["background_color"] = background_color

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="flux_led", service="set_music_mode",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
