# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_switch_core.py - Core Implementation for Switch Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    toggle_device_impl,
    turn_off_device_impl,
    turn_on_device_impl,
)

# ===== LIST SWITCHES =====

def list_switches_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all switch entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - switches: list of switch entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    result = list_devices_impl("switch", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "switches": result.get("switch", []),
            "count": result.get("count", 0)
        }

    return result


# ===== TURN ON SWITCH =====

def turn_on_switch_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn switch on.

    Args:
        entity_id: Switch entity ID (e.g., "switch.living_room_fan")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return turn_on_device_impl(
        "switch",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


# ===== TURN OFF SWITCH =====

def turn_off_switch_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn switch off.

    Args:
        entity_id: Switch entity ID (e.g., "switch.living_room_fan")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return turn_off_device_impl(
        "switch",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


# ===== TOGGLE SWITCH =====

def toggle_switch_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Toggle switch state.

    Args:
        entity_id: Switch entity ID (e.g., "switch.living_room_fan")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return toggle_device_impl(
        "switch",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )
