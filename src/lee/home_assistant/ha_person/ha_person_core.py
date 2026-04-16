# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to use ha_device_base functions
# and remove obsolete code


"""ha_person_core.py - Core Implementation for Person Interface

Version: 2026-04-10_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    get_entity_state_impl,
    list_devices_impl,
    reload_domain_impl
)
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def list_persons_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all person entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and persons list
    """
    result = list_devices_impl("person", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "persons": result.get("person", []),
            "count": result.get("count", 0)
        }

    return result


def get_person_state_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get specific person entity state.

    Args:
        entity_id: Person entity ID (e.g., "person.john")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and person details
    """
    return get_entity_state_impl(
        entity_type="person",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )


def update_person_location_impl(
    entity_id: Optional[str] = None,
    location: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Update person location.

    Args:
        entity_id: Person entity ID
        location: New location for the person
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

    if not location:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "location is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="person",
            service="update_device_state",
            service_data={
                "entity_id": entity_id,
                "location": location
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "entity_id": entity_id,
                "location": location,
                "message": "Person location updated successfully"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get(
                "error_message", "Failed to update person location"
            )
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error updating person location: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error updating person location: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception updating person location: {e!s}"
        }


def reload_persons_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload all person entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return reload_domain_impl("person", ha_config, correlation_id)


# ===== EXPORTS =====

__all__ = [
    "list_persons_impl",
    "get_person_state_impl",
    "update_person_location_impl",
    "reload_persons_impl",
]
