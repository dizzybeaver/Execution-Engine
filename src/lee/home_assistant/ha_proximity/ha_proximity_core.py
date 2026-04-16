# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to use ha_device_base functions and remove obsolete code


"""ha_proximity_core.py - Proximity Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Proximity integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def list_proximity_zones_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all proximity zone entities.

    Proximity zones monitor distance between tracked devices
    and a specific zone, triggering automations based on
    distance thresholds.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and proximity zones list
    """
    result = list_devices_impl("proximity", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "proximity_zones": result.get("proximity", []),
            "count": result.get("count", 0)
        }

    return result


def get_proximity_state_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get specific proximity zone state.

    Args:
        entity_id: Proximity entity ID (e.g., "proximity.home")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and proximity zone details
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
            "get_states",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "state": all_states[0]
                }
            return {
                "success": False,
                "error_code": "PROXIMITY_NOT_FOUND",
                "error_message": f"Proximity zone {entity_id} not found"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get proximity zone")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting proximity zone: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error getting proximity zone: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error getting proximity zone: {e!s}"
        }


def set_proximity_zone_impl(
    entity_id: Optional[str] = None,
    zone_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set target zone for proximity monitoring.

    Args:
        entity_id: Proximity entity ID
        zone_id: Target zone ID to set
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not zone_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "zone_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="proximity",
            service="set_zone",
            service_data={"entity_id": entity_id, "zone_id": zone_id},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "entity_id": entity_id,
                "zone_id": zone_id,
                "message": "Proximity zone set successfully"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to set proximity zone")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error setting proximity zone: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error setting proximity zone: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error setting proximity zone: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "list_proximity_zones_impl",
    "get_proximity_state_impl",
    "set_proximity_zone_impl",
]
