"""ha_mqtt_core.py - Core Implementation for MQTT Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import reload_domain_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def publish_impl(
    topic: Optional[str] = None,
    payload: Optional[str] = None,
    evaluate_payload: Optional[bool] = None,
    qos: Optional[int] = None,
    retain: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Publish message to MQTT topic via mqtt.publish service.

    Args:
        topic: MQTT topic to publish to (required)
        payload: Message payload
        evaluate_payload: Whether to evaluate payload as template
        qos: Quality of Service level (0, 1, or 2)
        retain: Whether to retain message
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not topic:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "topic is required"
        }

    service_data = {"topic": topic}

    if payload:
        service_data["payload"] = payload
    if evaluate_payload is not None:
        service_data["evaluate_payload"] = evaluate_payload
    if qos is not None:
        service_data["qos"] = qos
    if retain is not None:
        service_data["retain"] = retain

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="mqtt",
        service="publish",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "MQTT message published successfully"

    return result


def dump_impl(
    topic: Optional[str] = None,
    duration: Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Dump MQTT messages for debugging via mqtt.dump service.

    Args:
        topic: Topic pattern to dump (e.g., "OpenZWave/#")
        duration: Duration in seconds (1-300, default: 5)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    if topic:
        service_data["topic"] = topic
    if duration:
        service_data["duration"] = duration

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="mqtt",
        service="dump",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "MQTT dump started successfully"

    return result


def reload_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Reload MQTT configuration via mqtt.reload service.

    Args:
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return reload_domain_impl("mqtt", ha_config, correlation_id)
