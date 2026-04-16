"""ha_tts_core.py - Core Implementation for TTS Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def say_impl(
    entity_id: Optional[str] = None,
    message: Optional[str] = None,
    cache: Optional[bool] = None,
    language: Optional[str] = None,
    options: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Text-to-speech via tts.say service."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not message:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "message is required"
        }

    service_data = {"entity_id": entity_id, "message": message}

    if cache is not None:
        service_data["cache"] = cache
    if language:
        service_data["language"] = language
    if options:
        service_data["options"] = options

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tts",
        service="say",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Text-to-speech completed successfully"

    return result


def speak_impl(
    entity_id: Optional[str] = None,
    media_player_entity_id: Optional[str] = None,
    message: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Speak via tts.speak service."""
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if not media_player_entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "media_player_entity_id is required"
        }

    service_data = {
        "entity_id": entity_id,
        "media_player_entity_id": media_player_entity_id
    }

    if message:
        service_data["message"] = message

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tts",
        service="speak",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Speech completed successfully"

    return result


def list_tts_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all TTS (text-to-speech) entities."""
    result = list_devices_impl("tts", ha_config, correlation_id, **_kwargs)
    if result.get("success"):
        return {
            "success": True,
            "tts_services": result.get("tts", []),
            "count": result.get("count", 0)
        }
    return result


def tts_say_impl(
    entity_id: Optional[str] = None,
    message: Optional[str] = None,
    language: Optional[str] = None,
    cache: Optional[bool] = None,
    options: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Text-to-speech via tts.say service (alias for say_impl)."""
    return say_impl(
        entity_id=entity_id,
        message=message,
        cache=cache,
        language=language,
        options=options,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


def tts_clear_cache_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Clear TTS cache for an entity.

    Args:
        entity_id: TTS entity ID
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
        domain="tts",
        service="clear_cache",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "TTS cache cleared successfully"

    return result


def tts_get_voices_impl(
    entity_id: Optional[str] = None,
    language: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get available voices for a TTS entity.

    Args:
        entity_id: TTS entity ID
        language: Optional language filter
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for logging

    Returns:
        Dict with success status and available voices
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
        domain="tts",
        service="get_voices",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "TTS voices retrieved successfully"

    return result
