"""ha_utility_meter_core.py - Core Implementation for UTILITY_METER Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def reset_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Reset utility meter via utility_meter.reset service.

    Args:
        entity_id: Utility meter entity ID (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
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
        domain="utility_meter",
        service="reset",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Utility meter reset successfully"

    return result


def calibrate_impl(
    entity_id: Optional[str] = None,
    value: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Calibrate utility meter via utility_meter.calibrate service.

    Args:
        entity_id: Sensor entity ID (required)
        value: Calibration value (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not value:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "value is required"
        }

    service_data = {"entity_id": entity_id, "value": value}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="utility_meter",
        service="calibrate",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Utility meter calibrated successfully"

    return result
