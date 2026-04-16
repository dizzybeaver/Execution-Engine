"""ha_neato_core.py - Neato Robot Vacuum Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def custom_cleaning_impl(  # pylint: disable=too-many-arguments
    entity_id=None,
    mode=None,
    navigation=None,
    category=None,
    zone=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Start Neato custom cleaning.

    Args:
        entity_id: Neato vacuum entity ID
        mode: Cleaning mode (1=house, 2=spot)
        navigation: Navigation mode (1=normal, 2=extra, 3=deep)
        category: Cleaning category (2=grid, 4=zone)
        zone: Zone name for zone cleaning (e.g., "Kitchen")
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}
    if mode is not None:
        service_data["mode"] = mode
    if navigation is not None:
        service_data["navigation"] = navigation
    if category is not None:
        service_data["category"] = category
    if zone:
        service_data["zone"] = zone

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="neato",
        service="custom_cleaning",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
