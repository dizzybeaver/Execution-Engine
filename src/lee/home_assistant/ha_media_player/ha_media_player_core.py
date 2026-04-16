"""ha_media_player_core.py - Core Implementation for Media Player Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    media_control_impl,
    turn_off_device_impl,
    turn_on_device_impl,
    volume_control_impl,
)
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def list_media_players_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all media player entities."""
    return list_devices_impl("media_player", ha_config, correlation_id)


def turn_on_media_player_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn media player on."""
    return turn_on_device_impl(
        "media_player",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def turn_off_media_player_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn media player off."""
    return turn_off_device_impl(
        "media_player",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def play_media_impl(
    entity_id: Optional[str] = None,
    media_content_id: Optional[str] = None,
    media_content_type: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Play media item on media player."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not media_content_id:
        return missing_parameter("media_content_id")

    service_data = {
        "entity_id": entity_id,
        "media_content_id": media_content_id
    }

    if media_content_type is not None:
        service_data["media_content_type"] = media_content_type

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service="play_media",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Media played successfully"

    return result


def media_pause_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Pause media playback."""
    return media_control_impl(
        "media_pause",
        entity_id,
        ha_config,
        correlation_id
    )


def media_stop_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Stop media playback."""
    return media_control_impl(
        "media_stop",
        entity_id,
        ha_config,
        correlation_id
    )


def volume_set_impl(
    entity_id: Optional[str] = None,
    volume_level: Optional[float] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Set volume level (0.0 to 1.0)."""
    if not entity_id:
        return missing_parameter("entity_id")

    if volume_level is None:
        return missing_parameter("volume_level")

    service_data = {
        "entity_id": entity_id,
        "volume_level": volume_level
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service="volume_set",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Volume set successfully"

    return result


def volume_up_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Increase volume."""
    return volume_control_impl(
        "volume_up",
        entity_id,
        ha_config,
        correlation_id
    )


def volume_down_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Decrease volume."""
    return volume_control_impl(
        "volume_down",
        entity_id,
        ha_config,
        correlation_id
    )


def volume_mute_impl(
    entity_id: Optional[str] = None,
    is_volume_muted: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Mute/unmute volume."""
    if not entity_id:
        return missing_parameter("entity_id")

    if is_volume_muted is None:
        return missing_parameter("is_volume_muted")

    service_data = {
        "entity_id": entity_id,
        "is_volume_muted": is_volume_muted
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service="volume_mute",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        mute_status = "muted" if is_volume_muted else "unmuted"
        result["message"] = f"Volume {mute_status} successfully"

    return result


def media_play_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Resume media playback."""
    return media_control_impl(
        "media_play",
        entity_id,
        ha_config,
        correlation_id
    )


def media_next_track_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Skip to next track."""
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service="media_next_track",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Skipped to next track successfully"

    return result


def media_previous_track_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Skip to previous track."""
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service="media_previous_track",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Skipped to previous track successfully"

    return result


def get_state_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Get media player state."""
    if not entity_id:
        return missing_parameter("entity_id")

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "get_state",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    return result
