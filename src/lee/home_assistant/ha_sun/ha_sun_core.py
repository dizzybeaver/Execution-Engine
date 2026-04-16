# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_sun_core.py - Sun Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Sun integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def get_sun_state_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get sun position and state data.

    Returns comprehensive information about the sun's current
    position including elevation, azimuth, and rising/setting status.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and sun state data
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_states",
            entity_id="sun.sun",
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                return {
                    "success": True,
                    "sun_state": all_states[0]
                }
            return {
                "success": False,
                "error_code": "SUN_NOT_FOUND",
                "error_message": "Sun entity not found"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get sun state")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e!s}"
        }


def get_sunrise_time_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get sunrise time for today.

    Returns the next sunrise time based on the configured
    location in Home Assistant.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and sunrise time
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_states",
            entity_id="sun.sun",
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                sun_state = all_states[0]
                attributes = sun_state.get("attributes", {})
                sunrise = attributes.get("next_rising")

                if not sunrise:
                    return {
                        "success": False,
                        "error_code": "SUNRISE_NOT_AVAILABLE",
                        "error_message": "Sunrise time not available in sun entity attributes"
                    }

                return {
                    "success": True,
                    "sunrise_time": sunrise,
                    "attributes": attributes
                }
            return {
                "success": False,
                "error_code": "SUN_NOT_FOUND",
                "error_message": "Sun entity not found"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get sunrise time")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting sunrise time: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting sunrise time: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting sunrise time: {e!s}"
        }


def get_sunset_time_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get sunset time for today.

    Returns the next sunset time based on the configured
    location in Home Assistant.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and sunset time
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_states",
            entity_id="sun.sun",
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                sun_state = all_states[0]
                attributes = sun_state.get("attributes", {})
                sunset = attributes.get("next_setting")

                if not sunset:
                    return {
                        "success": False,
                        "error_code": "SUNSET_NOT_AVAILABLE",
                        "error_message": "Sunset time not available in sun entity attributes"
                    }

                return {
                    "success": True,
                    "sunset_time": sunset,
                    "attributes": attributes
                }
            return {
                "success": False,
                "error_code": "SUN_NOT_FOUND",
                "error_message": "Sun entity not found"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get sunset time")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting sunset time: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting sunset time: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting sunset time: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "get_sun_state_impl",
    "get_sunrise_time_impl",
    "get_sunset_time_impl",
]
