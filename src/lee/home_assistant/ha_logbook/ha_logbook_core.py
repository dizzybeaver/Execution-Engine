# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_logbook_core.py - Logbook Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for human-readable event logs

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils.error_response_factory import missing_parameter


# ===== CORE IMPLEMENTATIONS =====


def get_events_impl(
    start_time: str,
    end_time: Optional[str] = None,
    entity_ids: Optional[list[str]] = None,
    device_ids: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get human-readable event logs for a time period.

    The logbook provides chronological event information showing what happened
    in your home (automation triggers, service calls, state changes with context)
    in a human-readable format.

    Args:
        start_time: Start time in ISO format (required)
        end_time: End time in ISO format (optional, defaults to now)
        entity_ids: List of entity IDs to filter events (optional)
        device_ids: List of device IDs to filter events (optional)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and list of event objects
    """
    if not start_time:
        return missing_parameter("start_time")

    try:
        request_params = {
            "start_time": start_time
        }

        if end_time:
            request_params["end_time"] = end_time

        if entity_ids:
            request_params["entity_ids"] = entity_ids

        if device_ids:
            request_params["device_ids"] = device_ids

        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="logbook/get_events",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "events": result.get("result", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get logbook events")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting logbook events: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error getting logbook events: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Unexpected error getting logbook events"
        }


# ===== EXPORTS =====

__all__ = [
    "get_events_impl",
]
