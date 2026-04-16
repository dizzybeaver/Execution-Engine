# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_mobile_app_core.py - Mobile App Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Mobile App integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def register_push_channel_impl(
    webhook_id: str,
    support_confirm: bool = False,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Register a push notification channel for a mobile app.

    Creates a direct WebSocket channel for push notifications to a mobile app.
    This allows real-time push notifications without polling.

    Args:
        webhook_id: Mobile app webhook ID (required)
        support_confirm: Whether to support delivery confirmation (default: False)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and channel registration data
    """
    if not webhook_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "webhook_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="mobile_app/push_notification_channel",
            command_params={
                "webhook_id": webhook_id,
                "support_confirm": support_confirm
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "webhook_id": webhook_id,
                "support_confirm": support_confirm,
                "channel_registered": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to register push channel")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error registering push channel: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error registering push channel: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception registering push channel"
        }


def confirm_push_notification_impl(
    webhook_id: str,
    confirm_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Confirm delivery of a push notification.

    Confirms that a push notification was successfully received by the mobile app.
    This is used for delivery tracking and retry logic.

    Args:
        webhook_id: Mobile app webhook ID (required)
        confirm_id: Confirmation ID from the push notification (required)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and confirmation data
    """
    if not webhook_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "webhook_id is required"
        }

    if not confirm_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "confirm_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="mobile_app/push_notification_confirm",
            command_params={
                "webhook_id": webhook_id,
                "confirm_id": confirm_id
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "webhook_id": webhook_id,
                "confirm_id": confirm_id,
                "confirmed": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to confirm push notification")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error confirming push notification: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error confirming push notification: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception confirming push notification"
        }


# ===== EXPORTS =====

__all__ = [
    "register_push_channel_impl",
    "confirm_push_notification_impl",
]
