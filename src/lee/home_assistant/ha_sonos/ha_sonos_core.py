"""ha_sonas_core.py - Sonos Speaker System Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def snapshot_impl(entity_id=None, with_group=None, ha_config=None, correlation_id=None, **kwargs):
    """Snapshot Sonos system state.

    Args:
        entity_id: Sonos media player entity ID
        with_group: Include group state in snapshot (default: true)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if with_group is not None:
        service_data["with_group"] = with_group

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="snapshot",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def restore_impl(entity_id=None, with_group=None, ha_config=None, correlation_id=None, **kwargs):
    """Restore Sonos system state from snapshot.

    Args:
        entity_id: Sonos media player entity ID
        with_group: Include group state in restore (default: true)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if with_group is not None:
        service_data["with_group"] = with_group

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="restore",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def set_sleep_timer_impl(entity_id=None, sleep_time=None, ha_config=None, correlation_id=None, **kwargs):
    """Set Sonos sleep timer.

    Args:
        entity_id: Sonos media player entity ID
        sleep_time: Sleep duration in seconds (0-7200)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if sleep_time is not None:
        service_data["sleep_time"] = sleep_time

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="set_sleep_timer",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def clear_sleep_timer_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Clear Sonos sleep timer.

    Args:
        entity_id: Sonos media player entity ID
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="clear_sleep_timer",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def play_queue_impl(entity_id=None, queue_position=None, ha_config=None, correlation_id=None, **kwargs):
    """Play item from Sonos queue.

    Args:
        entity_id: Sonos media player entity ID
        queue_position: Queue position to play (0-10000)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if queue_position is not None:
        service_data["queue_position"] = queue_position

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="play_queue",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def remove_from_queue_impl(entity_id=None, queue_position=None, ha_config=None, correlation_id=None, **kwargs):
    """Remove item from Sonos queue.

    Args:
        entity_id: Sonos media player entity ID
        queue_position: Queue position to remove (0-10000)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if queue_position is not None:
        service_data["queue_position"] = queue_position

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="remove_from_queue",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def get_queue_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Get Sonos queue contents.

    Args:
        entity_id: Sonos media player entity ID
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="get_queue",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def update_alarm_impl(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    entity_id=None,
    alarm_id=None,
    time=None,
    volume=None,
    enabled=None,
    include_linked_zones=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Update Sonos alarm.

    Args:
        entity_id: Sonos media player entity ID
        alarm_id: Alarm ID to update (1-1440, required)
        time: Alarm time (format: "HH:MM", e.g., "07:00")
        volume: Alarm volume (0.0-1.0)
        enabled: Enable/disable alarm
        include_linked_zones: Include linked zones in alarm
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not alarm_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and alarm_id are required",
        }

    service_data = {"entity_id": entity_id, "alarm_id": alarm_id}
    if time is not None:
        service_data["time"] = time
    if volume is not None:
        service_data["volume"] = volume
    if enabled is not None:
        service_data["enabled"] = enabled
    if include_linked_zones is not None:
        service_data["include_linked_zones"] = include_linked_zones

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="sonos",
        service="update_alarm",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
