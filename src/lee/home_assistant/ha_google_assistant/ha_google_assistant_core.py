# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_google_assistant_core.py - Google Assistant Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os

from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def _is_debug_mode() -> bool:
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def request_sync_impl(
    agent_user_id=None, ha_config=None, correlation_id=None, **kwargs
):
    """Request sync from Google Assistant.

    Args:
        agent_user_id: Google Assistant agent user ID (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Result dictionary with success status
    """
    if _is_debug_mode():
        print(f"[HA-GA-DEBUG] request_sync_impl called - agent_user_id: {agent_user_id}")

    service_data = {}

    if agent_user_id is not None:
        service_data["agent_user_id"] = agent_user_id

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "call_service", domain="google_assistant", service="request_sync",
            service_data=service_data, ha_config=ha_config, correlation_id=correlation_id
        )
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {"success": False, "error_code": "VALIDATION_ERROR", "error_message": f"Validation error: {e}"}
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"success": False, "error_code": "NETWORK_ERROR", "error_message": f"Network error: {e}"}
    except Exception as e:
        if _is_debug_mode():
            print(f"[HA-GA-DEBUG] Unexpected exception: {type(e).__name__}: {e}")
        return {"success": False, "error_code": "EXCEPTION", "error_message": str(e)}
