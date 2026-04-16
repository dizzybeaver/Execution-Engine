"""ha_wake_on_lan_core.py - Core Implementation for WAKE_ON_LAN Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def send_magic_packet_impl(
    mac: Optional[str] = None,
    broadcast_address: Optional[str] = None,
    broadcast_port: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Send Wake-on-LAN magic packet via wake_on_lan.send_magic_packet service.

    Args:
        mac: MAC address (required, format: "aa:bb:cc:dd:ee:ff")
        broadcast_address: Broadcast address (optional, default: 192.168.255.255)
        broadcast_port: Broadcast port (optional, default: 9, range: 1-65535)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not mac:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "mac is required"
        }

    service_data = {"mac": mac}

    if broadcast_address:
        service_data["broadcast_address"] = broadcast_address
    if broadcast_port is not None:
        service_data["broadcast_port"] = broadcast_port

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="wake_on_lan",
        service="send_magic_packet",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Magic packet sent successfully"

    return result
