"""ha_roku_core.py - Roku Streaming Device Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def search_impl(entity_id=None, keyword=None, ha_config=None, correlation_id=None, **kwargs):
    """Search on Roku streaming device.

    Args:
        entity_id: Roku media player entity ID
        keyword: Search keyword (e.g., "Space Jam")
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not keyword:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and keyword are required",
        }

    service_data = {"entity_id": entity_id, "keyword": keyword}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="roku",
        service="search",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
