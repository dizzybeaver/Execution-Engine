# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Consolidated Alexa response utilities

"""Alexa Response Utilities (Consolidated)

Provides standardized Alexa Smart Home response generation functions.
Consolidates response creation logic to eliminate duplication across controllers.

Reference: Alexa Smart Home API v3
https://developer.amazon.com/docs/smart-home/alexa-interface-message-catalog.html
"""

import uuid
from typing import Any, Optional


def create_success_response(
    endpoint: dict[str, Any],
    correlation_token: str,
    payload: dict[str, Any]
) -> dict[str, Any]:
    """Create a standard Alexa success response.

    Args:
        endpoint: Endpoint object with scope and token
            Example: {
                "scope": {"type": "BearerToken", "token": "access_token"},
                "endpointId": "device_id"
            }
        correlation_token: Alexa correlation token from request
        payload: Response payload containing properties or other data
            Example: {"properties": [{"name": "powerState", "value": "ON"}]}

    Returns:
        Standard Alexa success response structure

    Example:
        >>> endpoint = {"scope": {"type": "BearerToken", "token": "token"}, "endpointId": "light-1"}
        >>> payload = {"properties": [{"name": "powerState", "value": "ON"}]}
        >>> create_success_response(endpoint, "token123", payload)
        {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "messageId": "msg_...",
                    "correlationToken": "token123",
                    "payloadVersion": "3"
                },
                "endpoint": {
                    "scope": {"type": "BearerToken", "token": "token"},
                    "endpointId": "light-1"
                },
                "payload": {
                    "properties": [{"name": "powerState", "value": "ON"}]
                }
            }
        }
    """
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "Response",
                "messageId": str(uuid.uuid4()),
                "correlationToken": correlation_token,
                "payloadVersion": "3"
            },
            "endpoint": endpoint,
            "payload": payload
        }
    }


def create_error_response(
    endpoint: Optional[dict[str, Any]],
    correlation_token: str,
    error_type: str,
    error_message: str
) -> dict[str, Any]:
    """Create a standard Alexa error response.

    Args:
        endpoint: Endpoint object with scope and token (may be None for non-endpoint errors)
            Example: {
                "scope": {"type": "BearerToken", "token": "access_token"},
                "endpointId": "device_id"
            }
        correlation_token: Alexa correlation token from request
        error_type: Alexa error type (e.g., "INVALID_VALUE", "ENDPOINT_UNREACHABLE")
            Valid types: https://developer.amazon.com/docs/smart-home/error-catalog.html
        error_message: Human-readable error message

    Returns:
        Standard Alexa error response structure

    Example:
        >>> endpoint = {"scope": {"type": "BearerToken", "token": "token"}, "endpointId": "light-1"}
        >>> create_error_response(endpoint, "token123", "ENDPOINT_UNREACHABLE", "Device is offline")
        {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": "msg_...",
                    "correlationToken": "token123",
                    "payloadVersion": "3"
                },
                "endpoint": {
                    "scope": {"type": "BearerToken", "token": "token"},
                    "endpointId": "light-1"
                },
                "payload": {
                    "type": "ENDPOINT_UNREACHABLE",
                    "message": "Device is offline"
                }
            }
        }

    Example (non-endpoint error):
        >>> create_error_response(None, "token123", "INVALID_AUTHORIZATION_CREDENTIAL", "Invalid token")
        {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": "msg_...",
                    "correlationToken": "token123",
                    "payloadVersion": "3"
                },
                "payload": {
                    "type": "INVALID_AUTHORIZATION_CREDENTIAL",
                    "message": "Invalid token"
                }
            }
        }
    """
    response = {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": str(uuid.uuid4()),
                "correlationToken": correlation_token,
                "payloadVersion": "3"
            },
            "payload": {
                "type": error_type,
                "message": error_message
            }
        }
    }

    # Only include endpoint if provided (not all errors have endpoints)
    if endpoint:
        response["event"]["endpoint"] = endpoint

    return response


def create_success_response_batch(
    responses: list[dict[str, Any]]
) -> dict[str, Any]:
    """Create a batched success response for multiple endpoints.

    This is useful when handling multiple device control operations in a single directive.
    Alexa expects individual responses, but this utility ensures consistent structure.

    Args:
        responses: List of individual success response dictionaries

    Returns:
        List of response dictionaries (Alexa expects array for multiple endpoints)

    Example:
        >>> responses = [
        ...     create_success_response(endpoint1, "token123", payload1),
        ...     create_success_response(endpoint2, "token123", payload2)
        ... ]
        >>> create_success_response_batch(responses)
        [response1, response2]
    """
    return responses


def create_mixed_response_batch(
    success_responses: list[dict[str, Any]],
    error_responses: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Create a batched response containing both successes and errors.

    This handles scenarios where some operations succeed and others fail.
    Alexa processes each response independently.

    Args:
        success_responses: List of success response dictionaries
        error_responses: List of error response dictionaries

    Returns:
        Combined list of response dictionaries

    Example:
        >>> successes = [create_success_response(ep1, "token", payload1)]
        >>> errors = [create_error_response(ep2, "token", "UNREACHABLE", "Offline")]
        >>> create_mixed_response_batch(successes, errors)
        [success_response, error_response]
    """
    return success_responses + error_responses


def consolidate_properties(
    properties_list: list[list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    """Consolidate multiple property lists into a single list.

    Useful when batching responses from multiple devices that need to be combined
    into a single response payload.

    Args:
        properties_list: List of properties lists from multiple devices

    Returns:
        Consolidated list of all properties

    Example:
        >>> props1 = [{"name": "powerState", "value": "ON"}]
        >>> props2 = [{"name": "powerState", "value": "OFF"}, {"name": "brightness", "value": 50}]
        >>> consolidate_properties([props1, props2])
        [{"name": "powerState", "value": "ON"}, {"name": "powerState", "value": "OFF"}, {"name": "brightness", "value": 50}]
    """
    consolidated = []
    for properties in properties_list:
        if properties:
            consolidated.extend(properties)
    return consolidated


def validate_response_structure(
    response: dict[str, Any]
) -> bool:
    """Validate that a response has the required Alexa structure.

    Args:
        response: Response dictionary to validate

    Returns:
        True if response has required structure, False otherwise

    Example:
        >>> response = create_success_response(endpoint, token, payload)
        >>> validate_response_structure(response)
        True
    """
    if not isinstance(response, dict):
        return False

    if "event" not in response:
        return False

    event = response["event"]
    if not isinstance(event, dict):
        return False

    if "header" not in event:
        return False

    header = event["header"]
    required_fields = ["namespace", "name", "messageId", "payloadVersion"]
    for field in required_fields:
        if field not in header:
            return False

    return True
