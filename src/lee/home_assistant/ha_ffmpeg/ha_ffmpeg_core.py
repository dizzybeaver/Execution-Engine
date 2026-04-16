# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_ffmpeg_core.py - FFmpeg Video Processing Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def restart_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Restart FFmpeg binary sensor.

    Args:
        entity_id: FFmpeg binary sensor entity ID
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
        domain="ffmpeg",
        service="restart",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def start_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Start FFmpeg binary sensor.

    Args:
        entity_id: FFmpeg binary sensor entity ID
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
        domain="ffmpeg",
        service="start",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def stop_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Stop FFmpeg binary sensor.

    Args:
        entity_id: FFmpeg binary sensor entity ID
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
        domain="ffmpeg",
        service="stop",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
