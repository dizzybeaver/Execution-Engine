# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-09 - Fix import path for missing_parameter

"""ha_lifx_core.py - LIFX LED Lighting Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def effect_pulse_impl(
    entity_id=None, mode=None, brightness=None, brightness_pct=None,
    color_name=None, rgb_color=None, period=None, cycles=None,
    power_on=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set pulse effect on LIFX light.

    Args:
        entity_id: LIFX light entity ID (required)
        mode: Effect mode - blink, breathe, ping, strobe, solid (optional)
        brightness: Brightness 1-255 (optional)
        brightness_pct: Brightness percentage 1-100 (optional)
        color_name: Color name (optional)
        rgb_color: RGB color list (optional)
        period: Period in seconds 0.05-60 (optional, default: 1.0)
        cycles: Number of cycles 1-10000 (optional, default: 1)
        power_on: Power on state (optional, default: true)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    if mode is not None:
        service_data["mode"] = mode
    if brightness is not None:
        service_data["brightness"] = brightness
    if brightness_pct is not None:
        service_data["brightness_pct"] = brightness_pct
    if color_name is not None:
        service_data["color_name"] = color_name
    if rgb_color is not None:
        service_data["rgb_color"] = rgb_color
    if period is not None:
        service_data["period"] = period
    if cycles is not None:
        service_data["cycles"] = cycles
    if power_on is not None:
        service_data["power_on"] = power_on

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="lifx", service="effect_pulse",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}


def effect_stop_impl(
    entity_id=None, ha_config=None, correlation_id=None, **kwargs
):
    """Stop current effect on LIFX light.

    Args:
        entity_id: LIFX light entity ID (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="lifx", service="effect_stop",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "DATA_ERROR", "error_message": f"Data error: {e}"}
    except Exception as e:
        return {"success": False, "error_code": "EXCEPTION", "error_message": f"Unexpected error: {e}"}
