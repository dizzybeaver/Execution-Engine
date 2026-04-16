# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-09 - Created binary sensor core implementation


"""ha_binary_sensor_core.py - Binary Sensor Core Implementation

Version: 2026-04-09_1
Description: Core implementations for Binary Sensor integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl, reload_domain_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def list_binary_sensors_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all binary sensor entities.

    Binary sensors are on/off sensors that report binary states (true/false).
    Examples: motion sensors, door/window sensors, presence sensors.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and list of binary sensors
    """
    return list_devices_impl("binary_sensor", ha_config, correlation_id)


def get_state_impl(
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get binary sensor state.

    Args:
        entity_id: Binary sensor entity ID (e.g., "binary_sensor.motion_living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and binary sensor state
    """
    if not entity_id:
        return missing_parameter("entity_id")

    return ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "get_state",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


def reload_binary_sensors_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload all binary sensor entities.

    Forces Home Assistant to reload all binary sensor entities
    from their configured integrations.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return reload_domain_impl('binary_sensor', ha_config, correlation_id)


__all__ = [
    "get_state_impl",
    "list_binary_sensors_impl",
    "reload_binary_sensors_impl",
]
