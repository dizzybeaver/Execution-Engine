# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_notify_core.py - Notify Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for sending notifications

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def send_message_impl(
    target: str,
    message: str,
    title: Optional[str] = None,
    data: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Send a notification message.

    Notifications are sent through Home Assistant's notify integration.
    Each notify platform has a target name (e.g., "mobile_app_my_iphone").
    The service domain is constructed as "notify.{target}".

    Common notify platforms:
    - Mobile apps: notify.mobile_app_<device_name>
    - Email: notify.smtp
    - Persistent: notify.persistent_notification
    - Telegram: notify.telegram
    - And many more...

    Args:
        target: Notify platform target name (e.g., "mobile_app_my_iphone", "smtp")
        message: Notification message body (required)
        title: Optional notification title
        data: Optional additional data for the notification (platform-specific)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and operation result
    """
    if not message:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "message is required"
        }

    if not target:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "target is required"
        }

    try:
        service_data = {"message": message}

        if title:
            service_data["title"] = title

        if data:
            service_data["data"] = data

        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain=f"notify.{target}",
            service="send_message",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "target": target,
                "sent": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to send notification")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error sending notification: {e!s}"
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error sending notification: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error sending notification: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "send_message_impl",
]
