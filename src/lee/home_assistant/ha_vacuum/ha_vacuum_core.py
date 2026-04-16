"""ha_vacuum_core.py - Core Implementation for Vacuum Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    turn_on_device_impl,
    vacuum_control_impl,
)


def list_vacuums_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all vacuum entities."""
    return list_devices_impl("vacuum", ha_config, correlation_id)


def start_vacuum_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Start vacuum cleaning."""
    return turn_on_device_impl(
        "vacuum",
        entity_id,
        ha_config,
        correlation_id,
        service="start",
        **kwargs
    )


def pause_vacuum_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Pause vacuum cleaning."""
    return vacuum_control_impl(
        "pause",
        entity_id,
        ha_config,
        correlation_id
    )


def stop_vacuum_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Stop vacuum cleaning."""
    return vacuum_control_impl(
        "stop",
        entity_id,
        ha_config,
        correlation_id
    )


def return_to_base_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Return vacuum to base."""
    return vacuum_control_impl(
        "return_to_base",
        entity_id,
        ha_config,
        correlation_id
    )


def clean_spot_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Clean spot."""
    return vacuum_control_impl(
        "clean_spot",
        entity_id,
        ha_config,
        correlation_id
    )


def locate_vacuum_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Locate vacuum (play sound)."""
    return vacuum_control_impl(
        "locate",
        entity_id,
        ha_config,
        correlation_id
    )
