"""ha_update_core.py - Core Implementation for Update Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def list_updates_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all update entities."""
    result = list_devices_impl("update", ha_config, correlation_id, **_kwargs)
    if result.get("success"):
        return {
            "success": True,
            "updates": result.get("update", []),
            "count": result.get("count", 0)
        }
    return result


def install_update_impl(
    entity_id: Optional[str] = None,
    version: Optional[str] = None,
    backup: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Install update."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    service_data = {"entity_id": entity_id}

    if version:
        service_data["version"] = version
    if backup is not None:
        service_data["backup"] = backup

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="update",
        service="install",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Update installed successfully"

    return result


def skip_update_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Skip update."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="update",
        service="skip",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Update skipped successfully"

    return result
