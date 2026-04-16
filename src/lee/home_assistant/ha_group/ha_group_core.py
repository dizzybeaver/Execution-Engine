# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_group_core.py - Core Implementation for Group Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def list_groups_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all group entities."""
    result = ha_execute_operation(
        HAGatewayInterface.GROUP,
        "list_groups",
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    return result


def reload_groups_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload all groups."""
    result = ha_execute_operation(
        HAGatewayInterface.GROUP,
        "reload",
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    return result


def set_group_impl(
    object_id: Optional[str] = None,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    entities: Optional[list[str]] = None,
    add_entities: Optional[list[str]] = None,
    remove_entities: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Create or update a group."""
    result = ha_execute_operation(
        HAGatewayInterface.GROUP,
        "set",
        object_id=object_id,
        name=name,
        icon=icon,
        entities=entities,
        add_entities=add_entities,
        remove_entities=remove_entities,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    return result
