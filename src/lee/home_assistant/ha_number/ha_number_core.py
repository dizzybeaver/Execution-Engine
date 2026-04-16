"""ha_number_core.py - Number Core Operations

Version: 2025-12-22_1
Description: Core implementations for Number integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway_enums import HAGatewayInterface
from lee.home_assistant.ha_gateway_generic import ha_execute_operation

# ===== NUMBER CORE OPERATIONS =====


def get_device_class_units_impl(
    device_class: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get convertible units for a number device class.

    Args:
        device_class: The device class to query (e.g., "temperature", "humidity")
        ha_config: Optional Home Assistant configuration
        correlation_id: Optional correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Dict with:
        - success: True if successful
        - units: List of convertible unit strings
        - response: Full WebSocket response

    Raises:
        RuntimeError: If WebSocket command fails
    """
    result = ha_execute_operation(
        HAGatewayInterface.WEBSOCKET,
        "execute_command",
        command_type="number/device_class_convertible_units",
        command_params={"device_class": device_class},
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    return result


# ===== EXPORTS =====

__all__ = [
    "get_device_class_units_impl",
]
