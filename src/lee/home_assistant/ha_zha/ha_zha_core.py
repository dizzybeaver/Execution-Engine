"""ha_zha_core.py - Core Implementation for ZHA Interface (Zigbee Home Automation)

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def permit_impl(
    duration: Optional[int] = None,
    ieee: Optional[str] = None,
    source_ieee: Optional[str] = None,
    install_code: Optional[str] = None,
    qr_code: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Permit Zigbee device joining via zha.permit service.

    Args:
        duration: Permit duration in seconds (0-254, default: 60)
        ieee: Target device IEEE address
        source_ieee: Source device IEEE address
        install_code: Install code for secure joining
        qr_code: QR code for device discovery
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    if duration is not None:
        service_data["duration"] = duration
    if ieee:
        service_data["ieee"] = ieee
    if source_ieee:
        service_data["source_ieee"] = source_ieee
    if install_code:
        service_data["install_code"] = install_code
    if qr_code:
        service_data["qr_code"] = qr_code

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="permit",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "ZHA permit mode activated successfully"

    return result


def remove_impl(
    ieee: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Remove Zigbee device via zha.remove service.

    Args:
        ieee: Device IEEE address (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    service_data = {"ieee": ieee}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="remove",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Zigbee device removed successfully"

    return result


def reconfigure_device_impl(
    ieee: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Reconfigure Zigbee device via zha.reconfigure_device service.

    Args:
        ieee: Device IEEE address (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    service_data = {"ieee": ieee}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="reconfigure_device",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Zigbee device reconfigured successfully"

    return result


def set_zigbee_cluster_attribute_impl(
    ieee: Optional[str] = None,
    endpoint_id: Optional[int] = None,
    cluster_id: Optional[int] = None,
    cluster_type: Optional[str] = None,
    attribute: Optional[int] = None,
    value: Optional[str] = None,
    manufacturer: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Set Zigbee cluster attribute via zha.set_zigbee_cluster_attribute service.

    Args:
        ieee: Device IEEE address (required)
        endpoint_id: Endpoint ID (required, 1-65535)
        cluster_id: Cluster ID (required, 1-65535)
        cluster_type: Cluster type ("in" or "out", default: "in")
        attribute: Attribute ID (required, 1-65535)
        value: Attribute value (required)
        manufacturer: Manufacturer code
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    if not endpoint_id:
        return missing_parameter("endpoint_id")

    if not cluster_id:
        return missing_parameter("cluster_id")

    if not attribute:
        return missing_parameter("attribute")

    if not value:
        return missing_parameter("value")

    service_data = {
        "ieee": ieee,
        "endpoint_id": endpoint_id,
        "cluster_id": cluster_id,
        "attribute": attribute,
        "value": value
    }

    if cluster_type:
        service_data["cluster_type"] = cluster_type
    if manufacturer:
        service_data["manufacturer"] = manufacturer

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="set_zigbee_cluster_attribute",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Zigbee cluster attribute set successfully"

    return result


def issue_zigbee_cluster_command_impl(
    ieee: Optional[str] = None,
    endpoint_id: Optional[int] = None,
    cluster_id: Optional[int] = None,
    cluster_type: Optional[str] = None,
    command: Optional[int] = None,
    command_type: Optional[str] = None,
    args: Optional[list] = None,
    params: Optional[dict] = None,
    manufacturer: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Issue Zigbee cluster command via zha.issue_zigbee_cluster_command service.

    Args:
        ieee: Device IEEE address (required)
        endpoint_id: Endpoint ID (required, 1-65535)
        cluster_id: Cluster ID (required, 1-65535)
        cluster_type: Cluster type ("in" or "out", default: "in")
        command: Command ID (required, 1-65535)
        command_type: Command type ("client" or "server", required)
        args: Command arguments
        params: Command parameters
        manufacturer: Manufacturer code
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    if not endpoint_id:
        return missing_parameter("endpoint_id")

    if not cluster_id:
        return missing_parameter("cluster_id")

    if not command:
        return missing_parameter("command")

    if not command_type:
        return missing_parameter("command_type")

    service_data = {
        "ieee": ieee,
        "endpoint_id": endpoint_id,
        "cluster_id": cluster_id,
        "command": command,
        "command_type": command_type
    }

    if cluster_type:
        service_data["cluster_type"] = cluster_type
    if args:
        service_data["args"] = args
    if params:
        service_data["params"] = params
    if manufacturer:
        service_data["manufacturer"] = manufacturer

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="issue_zigbee_cluster_command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Zigbee cluster command issued successfully"

    return result


def issue_zigbee_group_command_impl(
    group: Optional[str] = None,
    cluster_id: Optional[int] = None,
    cluster_type: Optional[str] = None,
    command: Optional[int] = None,
    args: Optional[list] = None,
    manufacturer: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Issue Zigbee group command via zha.issue_zigbee_group_command service.

    Args:
        group: Group ID (required)
        cluster_id: Cluster ID (required, 1-65535)
        cluster_type: Cluster type ("in" or "out", default: "in")
        command: Command ID (required, 1-65535)
        args: Command arguments
        manufacturer: Manufacturer code
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not group:
        return missing_parameter("group")

    if not cluster_id:
        return missing_parameter("cluster_id")

    if not command:
        return missing_parameter("command")

    service_data = {
        "group": group,
        "cluster_id": cluster_id,
        "command": command
    }

    if cluster_type:
        service_data["cluster_type"] = cluster_type
    if args:
        service_data["args"] = args
    if manufacturer:
        service_data["manufacturer"] = manufacturer

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="issue_zigbee_group_command",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Zigbee group command issued successfully"

    return result


def warning_device_squawk_impl(
    ieee: Optional[str] = None,
    mode: Optional[int] = None,
    strobe: Optional[int] = None,
    level: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Squawk warning device via zha.warning_device_squawk service.

    Args:
        ieee: Device IEEE address (required)
        mode: Warning mode (0-1, default: 0)
        strobe: Strobe setting (0-1, default: 1)
        level: Warning level (0-3, default: 2)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    service_data = {"ieee": ieee}

    if mode is not None:
        service_data["mode"] = mode
    if strobe is not None:
        service_data["strobe"] = strobe
    if level is not None:
        service_data["level"] = level

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="warning_device_squawk",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Warning device squawked successfully"

    return result


def warning_device_warn_impl(
    ieee: Optional[str] = None,
    mode: Optional[int] = None,
    strobe: Optional[int] = None,
    level: Optional[int] = None,
    duration: Optional[int] = None,
    duty_cycle: Optional[int] = None,
    intensity: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Warn warning device via zha.warning_device_warn service.

    Args:
        ieee: Device IEEE address (required)
        mode: Warning mode (0-6, default: 3)
        strobe: Strobe setting (0-1, default: 1)
        level: Warning level (0-3, default: 2)
        duration: Duration in seconds (0-65535, default: 5)
        duty_cycle: Duty cycle percentage (0-100 step 10, default: 0)
        intensity: Warning intensity (0-3, default: 2)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not ieee:
        return missing_parameter("ieee")

    service_data = {"ieee": ieee}

    if mode is not None:
        service_data["mode"] = mode
    if strobe is not None:
        service_data["strobe"] = strobe
    if level is not None:
        service_data["level"] = level
    if duration is not None:
        service_data["duration"] = duration
    if duty_cycle is not None:
        service_data["duty_cycle"] = duty_cycle
    if intensity is not None:
        service_data["intensity"] = intensity

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="warning_device_warn",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Warning device warned successfully"

    return result


def clear_lock_user_code_impl(
    entity_id: Optional[str] = None,
    code_slot: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Clear lock user code via zha.clear_lock_user_code service.

    Args:
        entity_id: Lock entity ID (required, zha integration)
        code_slot: Code slot (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if not code_slot:
        return missing_parameter("code_slot")

    service_data = {"entity_id": entity_id, "code_slot": code_slot}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="clear_lock_user_code",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Lock user code cleared successfully"

    return result


def enable_lock_user_code_impl(
    entity_id: Optional[str] = None,
    code_slot: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Enable lock user code via zha.enable_lock_user_code service.

    Args:
        entity_id: Lock entity ID (required, zha integration)
        code_slot: Code slot (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if not code_slot:
        return missing_parameter("code_slot")

    service_data = {"entity_id": entity_id, "code_slot": code_slot}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="enable_lock_user_code",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Lock user code enabled successfully"

    return result


def disable_lock_user_code_impl(
    entity_id: Optional[str] = None,
    code_slot: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Disable lock user code via zha.disable_lock_user_code service.

    Args:
        entity_id: Lock entity ID (required, zha integration)
        code_slot: Code slot (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if not code_slot:
        return missing_parameter("code_slot")

    service_data = {"entity_id": entity_id, "code_slot": code_slot}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="disable_lock_user_code",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Lock user code disabled successfully"

    return result


def set_lock_user_code_impl(
    entity_id: Optional[str] = None,
    code_slot: Optional[str] = None,
    user_code: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Set lock user code via zha.set_lock_user_code service.

    Args:
        entity_id: Lock entity ID (required, zha integration)
        code_slot: Code slot (required)
        user_code: User code (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if not code_slot:
        return missing_parameter("code_slot")

    if not user_code:
        return missing_parameter("user_code")

    service_data = {
        "entity_id": entity_id,
        "code_slot": code_slot,
        "user_code": user_code
    }

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="zha",
        service="set_lock_user_code",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Lock user code set successfully"

    return result
