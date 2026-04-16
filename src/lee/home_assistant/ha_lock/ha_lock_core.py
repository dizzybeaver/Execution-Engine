# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_lock_core.py - Core Implementation for Lock Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    turn_off_device_impl,
    turn_on_device_impl,
)
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)
from lee.home_assistant.utils.error_response_factory import (
    missing_parameter,
)


def list_locks_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all lock entities."""
    result = list_devices_impl("lock", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "locks": result.get("lock", []),
            "count": result.get("count", 0)
        }

    return result


def lock_impl(
    entity_id: Optional[str] = None,
    code: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Lock lock."""
    if code is not None:
        kwargs["code"] = code
    return turn_on_device_impl(
        "lock",
        entity_id,
        ha_config,
        correlation_id,
        service="lock",
        **kwargs
    )


def unlock_impl(
    entity_id: Optional[str] = None,
    code: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Unlock lock."""
    if code is not None:
        kwargs["code"] = code
    return turn_off_device_impl(
        "lock",
        entity_id,
        ha_config,
        correlation_id,
        service="unlock",
        **kwargs
    )


def open_lock_impl(
    entity_id: Optional[str] = None,
    code: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Open lock (unlock and open)."""
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    if code is not None:
        service_data["code"] = code

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="lock",
        service="open",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Lock opened successfully"

    return result
