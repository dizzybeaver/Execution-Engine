# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor get_zone_state_impl to use base function


"""ha_zone_core.py - Zone Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Zone integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from collections.abc import Sequence
from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    get_entity_state_impl,
    list_devices_impl
)
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def list_zones_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all zone entities.

    Zones are used to organize devices/entities by location or logical area.
    Common zones include 'home', 'away', and room names like 'living_room'.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and zone entities list
    """
    result = list_devices_impl("zone", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "zones": result.get("zone", []),
            "count": result.get("count", 0)
        }

    return result


def get_zone_state_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get specific zone entity state.

    Args:
        entity_id: Zone entity ID (e.g., "zone.home")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and zone details
    """
    return get_entity_state_impl(
        entity_type="zone",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )


def get_zone_entities_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get entities within a zone.

    Returns the list of entities that are currently associated
    with the specified zone.

    Args:
        entity_id: Zone entity ID (e.g., "zone.home")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and zone entities
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
                zone_state = all_states[0]
                attributes = zone_state.get("attributes", {})
                entities = attributes.get("entity_id", [])

                entity_list = (
                    entities if isinstance(entities, Sequence) else [entities]
                )
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "entities": entity_list,
                    "count": len(entity_list)
                }

            return {
                "success": False,
                "error_code": "ZONE_NOT_FOUND",
                "error_message": f"Zone {entity_id} not found"
            }

        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get zone entities")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting zone entities: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting zone entities: {e!s}"
        }


def update_zone_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Update zone entity (reload or update).

    Args:
        entity_id: Zone entity ID to update
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

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="zone",
            service="reload",
            service_data={"entity_id": entity_id},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "entity_id": entity_id,
                "message": "Zone updated successfully"
            }

        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to update zone")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error updating zone: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error updating zone: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "list_zones_impl",
    "get_zone_state_impl",
    "get_zone_entities_impl",
    "update_zone_impl",
]
