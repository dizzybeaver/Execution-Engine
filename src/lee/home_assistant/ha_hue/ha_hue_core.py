# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-09 - Added debug mode support and fixed type annotations

import os
from typing import Any, Optional

from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def _is_debug_mode() -> bool:
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


"""ha_hue_core.py - Philips Hue Core Implementation.

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


def hue_activate_scene_impl(
    group_name: Optional[str] = None,
    scene_name: Optional[str] = None,
    dynamic: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Activate Hue scene (legacy method).

    Args:
        group_name: Hue group name (e.g., "Living Room")
        scene_name: Hue scene name (e.g., "Energize")
        dynamic: Use dynamic scene mode
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary

    """
    if _is_debug_mode():
        print(f"DEBUG: hue_activate_scene_impl called - group={group_name}, scene={scene_name}")

    if not group_name or not scene_name:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "group_name and scene_name are required",
        }

    service_data = {"group_name": group_name, "scene_name": scene_name}
    if dynamic is not None:
        service_data["dynamic"] = dynamic

    return ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="hue",
        service="hue_activate_scene",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
def activate_scene_impl(
    entity_id: Optional[str] = None,
    transition: Optional[int] = None,
    dynamic: Optional[bool] = None,
    speed: Optional[int] = None,
    brightness: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Activate Hue scene (V2 entity method).

    Args:
        entity_id: Hue scene entity ID
        transition: Transition duration in seconds (0-3600)
        dynamic: Use dynamic scene mode
        speed: Animation speed (1-100)
        brightness: Scene brightness (1-255)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary

    """
    if _is_debug_mode():
        print(f"DEBUG: activate_scene_impl called - entity_id={entity_id}")

    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if transition is not None:
        service_data["transition"] = transition
    if dynamic is not None:
        service_data["dynamic"] = dynamic
    if speed is not None:
        service_data["speed"] = speed
    if brightness is not None:
        service_data["brightness"] = brightness

    return ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="hue",
        service="activate_scene",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
