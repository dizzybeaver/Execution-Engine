"""ha_homekit_core.py - Apple HomeKit Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def reset_accessory_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Reset HomeKit accessory.

    Args:
        entity_id: HomeKit entity ID (supports multiple entities)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="homekit",
        service="reset_accessory",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def unpair_impl(device_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Unpair HomeKit device.

    Args:
        device_id: HomeKit device ID (supports multiple devices)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not device_id:
        return missing_parameter("device_id")

    service_data = {"device_id": device_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="homekit",
        service="unpair",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
