# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_hardware_core.py - Hardware Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Hardware integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def get_hardware_info_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get hardware information from Home Assistant.

    Retrieves detailed hardware information including CPU, memory,
    and other system components.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and hardware information
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="hardware/info",
            command_params={},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "hardware": result.get("result", {}).get("hardware", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get hardware info")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting hardware info: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting hardware info: {e!s}"
        }
    except RuntimeError as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting hardware info: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "get_hardware_info_impl",
]
