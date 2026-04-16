"""ha_input_boolean_core.py - Input Boolean Core Implementation

Version: 2025-12-22_1
Description: Core implementations for Input Boolean integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    reload_domain_impl,
    toggle_device_impl,
    turn_off_device_impl,
    turn_on_device_impl,
)


# ===== CORE IMPLEMENTATIONS =====


def list_input_booleans_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_boolean entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and input_boolean entities list
    """
    return list_devices_impl("input_boolean", ha_config, correlation_id)


def turn_on_input_boolean_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn on input_boolean entity.

    Args:
        entity_id: Input Boolean entity ID
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return turn_on_device_impl(
        "input_boolean",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def turn_off_input_boolean_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn off input_boolean entity.

    Args:
        entity_id: Input Boolean entity ID
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return turn_off_device_impl(
        "input_boolean",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def toggle_input_boolean_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Toggle input_boolean entity.

    Args:
        entity_id: Input Boolean entity ID
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return toggle_device_impl(
        "input_boolean",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )


def reload_input_booleans_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_boolean entities.

    Args:
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return reload_domain_impl("input_boolean", ha_config, correlation_id)


# ===== EXPORTS =====

__all__ = [
    "list_input_booleans_impl",
    "turn_on_input_boolean_impl",
    "turn_off_input_boolean_impl",
    "toggle_input_boolean_impl",
    "reload_input_booleans_impl",
]
