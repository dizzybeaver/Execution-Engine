# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to use ha_device_base functions


"""ha_calendar_core.py - Calendar Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Calendar integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)
from lee.home_assistant.utils.error_response_factory import (
    missing_parameter,
)


# ===== CORE IMPLEMENTATIONS =====


def list_calendars_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all calendar entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and calendar entities list
    """
    result = list_devices_impl("calendar", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "calendars": result.get("calendar", []),
            "count": result.get("count", 0)
        }

    return result


def create_event_impl(
    entity_id: Optional[str] = None,
    event_data: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Create calendar event.

    Args:
        entity_id: Calendar entity ID
        event_data: Event data (summary, start, end, etc.)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if not event_data:
        return missing_parameter("event_data")

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="calendar",
            service="create_event",
            service_data={
                "entity_id": entity_id,
                **event_data
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "entity_id": entity_id,
                "message": "Calendar event created successfully"
            }

        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to create calendar event")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error creating calendar event: {exc!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error creating calendar event: {exc!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception creating calendar event"
        }


# ===== EXPORTS =====

__all__ = [
    "list_calendars_impl",
    "create_event_impl",
]
