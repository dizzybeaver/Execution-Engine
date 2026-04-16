# LEE Project Code File
# Modified: 2026-04-11 - Extended core device implementations

"""ha_devices_core_extended.py - Extended core device operations

This module provides extended device management functions that are
imported by the state management wrappers.
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def get_state_impl(
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get device state with attributes.

    Retrieves full state including attributes like friendly_name,
    unit_of_measurement, device_class, etc.

    Args:
        entity_id: Device entity ID (e.g., "light.bubs_bedroom_inside_light_switch_1")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and full device state
    """
    if not entity_id:
        from lee.home_assistant.ha_common import missing_parameter
        return missing_parameter("entity_id")

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_state",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            state = result.get("result", {})
            return {
                "success": True,
                "entity_id": entity_id,
                "state": state.get("state"),
                "attributes": state.get("attributes", {}),
                "last_changed": state.get("last_changed"),
                "last_updated": state.get("last_updated"),
                "context": state.get("context")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "error_code": result.get("error_code", "GET_STATE_FAILED")
            }

    except Exception as e:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"get_state_impl failed: {str(e)}",
            corr_id=correlation_id
        )
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_STATE_EXCEPTION"
        }


__all__ = [
    "get_state_impl",
]
