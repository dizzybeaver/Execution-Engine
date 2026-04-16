"""ha_stt_core.py - Core Implementation for STT Interface

Version: 2026-03-18_1
Copyright 2026 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import base64
from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def list_stt_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all STT (speech-to-text) entities."""
    result = list_devices_impl("stt", ha_config, correlation_id, **_kwargs)
    if result.get("success"):
        return {
            "success": True,
            "stt_services": result.get("stt", []),
            "count": result.get("count", 0)
        }
    return result


def stt_process_impl(
    entity_id: Optional[str] = None,
    audio_data: Optional[str] = None,
    language: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Process audio data through speech-to-text.

    Args:
        entity_id: STT entity ID to use
        audio_data: Base64-encoded audio data
        language: Language code (default: en)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for logging

    Returns:
        Dict with success status and transcribed text
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not audio_data:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "audio_data is required"
        }

    service_data = {"entity_id": entity_id}

    if audio_data:
        # Security: Validate size before base64 decoding to prevent DoS
        # Base64 encoding increases size by ~33%, so 10MB limit = ~7.5MB decoded audio
        MAX_AUDIO_DATA_SIZE = 10 * 1024 * 1024  # 10MB
        if len(audio_data) > MAX_AUDIO_DATA_SIZE:
            return {
                "success": False,
                "error_code": "AUDIO_TOO_LARGE",
                "error_message": f"Audio data exceeds maximum size of {MAX_AUDIO_DATA_SIZE} bytes"
            }

        try:
            decoded = base64.b64decode(audio_data)
            service_data["audio_data"] = decoded
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "error_code": "INVALID_AUDIO",
                "error_message": f"Invalid base64 audio data: {e}"
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                "success": False,
                "error_code": "EXCEPTION",
                "error_message": f"Exception decoding audio data: {e}"
            }

    if language:
        service_data["language"] = language

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="stt",
        service="process",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Speech-to-text processing completed successfully"

    return result


def stt_stream_start_impl(
    entity_id: Optional[str] = None,
    language: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Start streaming STT session.

    Args:
        entity_id: STT entity ID to use
        language: Language code (default: en)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for logging

    Returns:
        Dict with success status and stream session info
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    service_data = {"entity_id": entity_id}

    if language:
        service_data["language"] = language

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="stt",
        service="stream_start",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "STT streaming session started"

    return result


def stt_stream_stop_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Stop streaming STT session.

    Args:
        entity_id: STT entity ID
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for logging

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
        domain="stt",
        service="stream_stop",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "STT streaming session stopped"

    return result
