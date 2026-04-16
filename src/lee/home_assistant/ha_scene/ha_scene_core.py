"""ha_scene_core.py - Scene Interface Core Implementation

Version: 2025-12-22_1
Description: Core implementations for scene activation

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    reload_domain_impl,
    turn_on_device_impl,
)
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


# ===== CORE IMPLEMENTATIONS =====


def list_scenes_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all scene entities."""
    return list_devices_impl("scene", ha_config, correlation_id)


def turn_on_scene_impl(
    entity_id: Optional[str] = None,
    transition: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn on scene."""
    if transition is not None:
        kwargs["transition"] = transition
    return turn_on_device_impl("scene", entity_id, ha_config, correlation_id, **kwargs)


def reload_scenes_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload all scenes."""
    return reload_domain_impl("scene", ha_config, correlation_id)


def apply_scene_impl(
    entities: Optional[dict[str, Any]] = None,
    transition: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Apply scene state to entities."""
    if not entities:
        return missing_parameter("entities")

    service_data = {"entities": entities}

    if transition is not None:
        service_data["transition"] = transition

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="scene",
        service="apply",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Scene applied successfully"

    return result


def create_scene_impl(
    scene_id: Optional[str] = None,
    entities: Optional[dict[str, Any]] = None,
    snapshot_entities: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Create new scene."""
    if not scene_id:
        return missing_parameter("scene_id")

    service_data = {"scene_id": scene_id}

    if entities:
        service_data["entities"] = entities
    if snapshot_entities:
        service_data["snapshot_entities"] = snapshot_entities

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="scene",
        service="create",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Scene created successfully"

    return result


# ===== LEGACY FUNCTION =====

def activate_scene_impl(
    entity_id: str,
    transition: Optional[float] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Legacy function - use turn_on_scene_impl instead."""
    return turn_on_scene_impl(
        entity_id=entity_id,
        transition=transition,
        ha_config=ha_config,
        correlation_id=correlation_id,
    )


# ===== EXPORTS =====

__all__ = [
    "list_scenes_impl",
    "turn_on_scene_impl",
    "reload_scenes_impl",
    "apply_scene_impl",
    "create_scene_impl",
    "activate_scene_impl",  # Legacy
]
