"""ha_siren_core.py - Core Implementation for Siren Interface

Version: 2025-12-22_1
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


def list_sirens_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all siren entities."""
    return list_devices_impl("siren", ha_config, correlation_id)


def turn_on_siren_impl(
    entity_id: Optional[str] = None,
    tone: Optional[str] = None,
    volume_level: Optional[float] = None,
    duration: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn on siren."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    if tone:
        kwargs["tone"] = tone
    if volume_level is not None:
        kwargs["volume_level"] = volume_level
    if duration:
        kwargs["duration"] = duration
    return turn_on_device_impl("siren", entity_id, ha_config, correlation_id, **kwargs)


def turn_off_siren_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn off siren."""
    return turn_off_device_impl("siren", entity_id, ha_config, correlation_id, **kwargs)


def toggle_siren_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Toggle siren."""
    return toggle_device_impl("siren", entity_id, ha_config, correlation_id, **kwargs)
