# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_persistent_core.py - Persistent Notification Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Persistent Notification integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def list_notifications_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all persistent notifications.

    Retrieves all persistent notifications that are currently active
    in the Home Assistant UI. These notifications remain until
    explicitly dismissed by the user.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and notifications list
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="persistent_notification/get",
            command_params={},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "notifications": result.get("result", {}).get("notifications", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get notifications")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting notifications: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error getting notifications: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error getting notifications: {e!s}"
        }


def create_notification_impl(
    title: Optional[str] = None,
    message: Optional[str] = None,
    notification_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Create a persistent notification.

    Creates a new persistent notification in the Home Assistant UI
    with the specified title and message.

    Args:
        title: Notification title
        message: Notification message
        notification_id: Optional notification ID
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not title:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "title is required"
        }

    if not message:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "message is required"
        }

    try:
        service_data: dict[str, Any] = {"title": title, "message": message}
        if notification_id:
            service_data["notification_id"] = notification_id

        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="persistent_notification",
            service="create",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "title": title,
                "message": "Notification created successfully"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to create notification")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error creating notification: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error creating notification: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error creating notification: {e!s}"
        }


def dismiss_notification_impl(
    notification_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Dismiss a persistent notification.

    Removes a persistent notification from the Home Assistant UI.
    The notification is identified by its notification_id.

    Args:
        notification_id: ID of the notification to dismiss
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not notification_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "notification_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="persistent_notification",
            service="dismiss",
            service_data={"notification_id": notification_id},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "notification_id": notification_id,
                "message": "Notification dismissed successfully"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to dismiss notification")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error dismissing notification: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error dismissing notification: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error dismissing notification: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "list_notifications_impl",
    "create_notification_impl",
    "dismiss_notification_impl",
]
