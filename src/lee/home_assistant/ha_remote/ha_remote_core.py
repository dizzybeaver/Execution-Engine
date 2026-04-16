# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use ha_device_base functions


"""ha_remote_core.py - Core Implementation for Remote Interface

Version: 2026-04-11_1
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
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)
from lee.home_assistant.utils.error_response_factory import (
    missing_parameter,
)


def list_remotes_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all remote entities."""
    result = list_devices_impl("remote", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "remotes": result.get("remote", []),
            "count": result.get("count", 0)
        }

    return result


def turn_on_remote_impl(
    entity_id: Optional[str] = None,
    activity: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Turn on remote."""
    result = turn_on_device_impl(
        "remote",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs
    )

    if result.get("success"):
        result["message"] = "Remote turned on successfully"

    return result


def toggle_remote_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Toggle remote."""
    result = toggle_device_impl(
        "remote",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Remote toggled successfully"

    return result


def turn_off_remote_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Turn off remote."""
    result = turn_off_device_impl(
        "remote",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Remote turned off successfully"

    return result


def send_command_impl(  # pylint: disable=R0913,R0917
    entity_id: Optional[str] = None,
    command: Optional[dict[str, Any]] = None,
    device: Optional[str] = None,
    num_repeats: Optional[int] = None,
    delay_secs: Optional[float] = None,
    hold_secs: Optional[float] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Send command to remote."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not command:
        return missing_parameter("command")

    service_data = {"entity_id": entity_id, "command": command}

    if device:
        service_data["device"] = device
    if num_repeats is not None:
        service_data["num_repeats"] = num_repeats
    if delay_secs is not None:
        service_data["delay_secs"] = delay_secs
    if hold_secs is not None:
        service_data["hold_secs"] = hold_secs

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="remote",
        service="send_command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Command sent successfully"

    return result


def learn_command_impl(  # pylint: disable=R0913,R0917
    entity_id: Optional[str] = None,
    device: Optional[str] = None,
    command: Optional[dict[str, Any]] = None,
    command_type: Optional[str] = None,
    alternative: Optional[bool] = None,
    timeout: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Learn command on remote."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not device:
        return missing_parameter("device")

    if not command:
        return missing_parameter("command")

    service_data = {"entity_id": entity_id, "device": device, "command": command}

    if command_type:
        service_data["command_type"] = command_type
    if alternative is not None:
        service_data["alternative"] = alternative
    if timeout is not None:
        service_data["timeout"] = timeout

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="remote",
        service="learn_command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Command learned successfully"

    return result


def delete_command_impl(
    entity_id: Optional[str] = None,
    device: Optional[str] = None,
    command: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Delete command from remote."""
    if not entity_id:
        return missing_parameter("entity_id")

    if not device:
        return missing_parameter("device")

    if not command:
        return missing_parameter("command")

    service_data = {"entity_id": entity_id, "device": device, "command": command}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="remote",
        service="delete_command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Command deleted successfully"

    return result
