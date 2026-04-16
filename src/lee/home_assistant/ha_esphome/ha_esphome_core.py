# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_esphome_core.py - ESPHome Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for ESPHome integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def get_encryption_key_impl(
    entry_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get the encryption key for an ESPHome config entry.

    ESPHome devices use Noise PSK (Pre-Shared Key) for encrypted communication.
    This operation retrieves the encryption key for a specific ESPHome config entry.

    Args:
        entry_id: ESPHome config entry ID
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional keyword arguments (unused but accepted for compatibility)

    Returns:
        Dict with success status and encryption key data
    """
    if not entry_id or not isinstance(entry_id, str):
        return {
            "success": False,
            "error_code": "INVALID_ENTRY_ID",
            "error_message": "Entry ID must be a non-empty string"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="esphome/get_encryption_key",
            command_params={"entry_id": entry_id},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "entry_id": entry_id,
                "encryption_key": result.get("result", {}).get("encryption_key")
            }

        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get encryption key")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting encryption key: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting encryption key: {e!s}"
        }
    except RuntimeError as e:
        return {
            "success": False,
            "error_code": "RUNTIME_ERROR",
            "error_message": f"Runtime error getting encryption key: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "get_encryption_key_impl",
]
