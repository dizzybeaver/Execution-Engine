"""Alexa Response Factory Module for EE.

This module implements the response builder for Alexa Smart Home integration.
Creates Alexa-compliant response messages following the Smart Home v3 API.

Architecture Layer: Domain Gateway - Alexa Domain - Response Building

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_response_factory.py

Integration:
    - Uses AlexaGatewayError from alexa_common
    - Builds Alexa v3 compliant responses
    - Handles success and error responses
    - Used by AlexaGateway for response generation

Alexa Response Structure (Success):
    {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "Response",
                "messageId": "msg-001",
                "correlationToken": "token-001",
                "payloadVersion": "3"
            },
            "endpoint": {
                "endpointId": "endpoint-001"
            },
            "payload": {}
        },
        "context": {
            "properties": []
        }
    }

Alexa Response Structure (Error):
    {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": "msg-001",
                "correlationToken": "token-001",
                "payloadVersion": "3"
            },
            "endpoint": {
                "endpointId": "endpoint-001"
            },
            "payload": {
                "type": "ENDPOINT_UNREACHABLE",
                "message": "Unable to reach endpoint"
            }
        }
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError


@dataclass
class AlexaResponseFactory:
    """Factory for creating Alexa Smart Home responses.

    Provides methods to build both success and error responses that comply
    with the Alexa Smart Home v3 API specification.

    Example:
        >>> factory = AlexaResponseFactory()
        >>> response = factory.success(
        ...     directive,
        ...     context={"properties": [...]},
        ...     payload={"state": "ON"}
        ... )
    """

    def success(
        self,
        directive: Any,
        *,
        context: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a success response for an Alexa directive.

        Creates a properly formatted Alexa response including the event
        header, endpoint information, payload, and optional context.

        Args:
            directive: The AlexaDirective being responded to
            context: Optional context with device properties
            payload: Optional response payload data

        Returns:
            Dictionary formatted as Alexa v3 success response

        Raises:
            AlexaGatewayError: If response building fails

        Example:
            >>> factory = AlexaResponseFactory()
            >>> response = factory.success(
            ...     directive=alexa_directive,
            ...     context={
            ...         "properties": [{
            ...             "namespace": "Alexa.PowerController",
            ...             "name": "powerState",
            ...             "value": "ON"
            ...         }]
            ...     },
            ...     payload={}
            ... )
        """
        try:
            return {
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "Response",
                        "messageId": "msg-1",
                        "correlationToken": directive.correlation_token,
                        "payloadVersion": "3",
                    },
                    "endpoint": {
                        "endpointId": directive.endpoint_id,
                    },
                    "payload": payload or {},
                },
                "context": context or {},
            }

        except Exception as e:
            raise AlexaGatewayError(
                message=f"Failed to build Alexa success response: {e}",
                error_code="RESPONSE_BUILD_ERROR",
                context={
                    "directive_namespace": getattr(directive, 'namespace', 'unknown'),
                    "directive_name": getattr(directive, 'name', 'unknown'),
                },
            ) from e

    def error(
        self,
        directive: Any,
        *,
        type: str,
        message: str,
    ) -> dict[str, Any]:
        """Build an error response for an Alexa directive.

        Creates a properly formatted Alexa error response following the
        Smart Home v3 error specification.

        Args:
            directive: The AlexaDirective being responded to
            type: Error type (e.g., "ENDPOINT_UNREACHABLE", "INVALID_VALUE")
            message: Human-readable error description

        Returns:
            Dictionary formatted as Alexa v3 error response

        Raises:
            AlexaGatewayError: If error response building fails

        Common Error Types:
            - ENDPOINT_UNREACHABLE: Device cannot be reached
            - INVALID_VALUE: Invalid parameter value
            - INTERNAL_ERROR: Unexpected internal failure
            - NOT_SUPPORTED_IN_CURRENT_MODE: Feature not available
            - RATE_LIMIT_EXCEEDED: Too many requests

        Example:
            >>> factory = AlexaResponseFactory()
            >>> response = factory.error(
            ...     directive=alexa_directive,
            ...     type="ENDPOINT_UNREACHABLE",
            ...     message="Unable to connect to device"
            ... )
        """
        try:
            return {
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "ErrorResponse",
                        "messageId": "msg-1",
                        "correlationToken": directive.correlation_token,
                        "payloadVersion": "3",
                    },
                    "endpoint": {
                        "endpointId": directive.endpoint_id,
                    },
                    "payload": {
                        "type": type,
                        "message": message,
                    },
                }
            }

        except Exception as e:
            raise AlexaGatewayError(
                message=f"Failed to build Alexa error response: {e}",
                error_code="ERROR_RESPONSE_BUILD_ERROR",
                context={
                    "error_type": type,
                    "original_message": message,
                },
            ) from e


def create_alexa_response_factory() -> AlexaResponseFactory:
    """Factory function to create an AlexaResponseFactory instance.

    Returns:
        New AlexaResponseFactory instance

    Example:
        >>> factory = create_alexa_response_factory()
        >>> response = factory.success(directive, payload={})
    """
    return AlexaResponseFactory()


__all__ = [
    'AlexaResponseFactory',
    'create_alexa_response_factory',
]
