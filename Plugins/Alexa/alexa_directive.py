"""Alexa Directive Module for EE.

This module implements the Alexa Directive data structure for parsing and
representing incoming Alexa Smart Home directives.

Architecture Layer: Domain Gateway - Alexa Domain - Directive Parsing

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_directive.py

Integration:
    - Uses AlexaGatewayError from alexa_common
    - Validates Alexa v3 directive format
    - Provides frozen dataclass for immutability
    - Used by AlexaGateway for request processing

Alexa Directive Structure:
    {
        "directive": {
            "header": {
                "namespace": "Alexa.PowerController",
                "name": "TurnOn",
                "messageId": "msg-001",
                "correlationToken": "token-001",
                "payloadVersion": "3"
            },
            "endpoint": {
                "endpointId": "endpoint-001",
                "cookie": {}
            },
            "payload": {}
        }
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError


@dataclass(frozen=True)
class AlexaDirective:
    """Represents an Alexa Smart Home directive.

    A frozen dataclass that encapsulates all information from an incoming
    Alexa directive. Immutable for thread safety and reliability.

    Attributes:
        namespace: Directive namespace (e.g., "Alexa.PowerController")
        name: Directive name (e.g., "TurnOn", "TurnOff")
        correlation_token: Token for correlating responses
        endpoint_id: Target endpoint identifier
        payload: Directive payload dictionary

    Example:
        >>> directive = AlexaDirective(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOn",
        ...     correlation_token="token-123",
        ...     endpoint_id="light-1",
        ...     payload={}
        ... )
        >>> print(directive.namespace)
        Alexa.PowerController
    """

    namespace: str
    name: str
    correlation_token: str
    endpoint_id: str
    payload: dict[str, Any]

    @staticmethod
    def from_request(req: dict[str, Any]) -> AlexaDirective:
        """Parse an Alexa directive from a raw request dictionary.

        Extracts and validates all required fields from the Alexa v3
        directive format.

        Args:
            req: Raw Alexa request dictionary

        Returns:
            AlexaDirective instance with parsed data

        Raises:
            AlexaGatewayError: If directive format is invalid or missing required fields

        Example:
            >>> request = {
            ...     "directive": {
            ...         "header": {
            ...             "namespace": "Alexa.PowerController",
            ...             "name": "TurnOn",
            ...             "correlationToken": "token-123",
            ...             "messageId": "msg-001",
            ...             "payloadVersion": "3"
            ...         },
            ...         "endpoint": {
            ...             "endpointId": "light-1"
            ...         },
            ...         "payload": {}
            ...     }
            ... }
            >>> directive = AlexaDirective.from_request(request)
            >>> print(directive.name)
            TurnOn
        """
        try:
            header = req["directive"]["header"]
            endpoint = req["directive"].get("endpoint", {})

            return AlexaDirective(
                namespace=header["namespace"],
                name=header["name"],
                correlation_token=header.get("correlationToken", ""),
                endpoint_id=endpoint.get("endpointId", ""),
                payload=req["directive"].get("payload", {}),
            )

        except KeyError as e:
            raise AlexaGatewayError(
                message=f"Missing required field in Alexa directive: {e}",
                error_code="DIRECTIVE_MISSING_FIELD",
                context={"missing_key": str(e), "request_keys": list(req.keys())},
            ) from e

        except Exception as e:
            raise AlexaGatewayError(
                message=f"Invalid Alexa directive format: {e}",
                error_code="DIRECTIVE_PARSE_ERROR",
                context={"exception_type": type(e).__name__},
            ) from e

    def get_full_key(self) -> str:
        """Get the full directive key for routing.

        Returns:
            Combined namespace and name as "namespace.name"

        Example:
            >>> directive = AlexaDirective(
            ...     namespace="Alexa.PowerController",
            ...     name="TurnOn",
            ...     correlation_token="",
            ...     endpoint_id="",
            ...     payload={}
            ... )
            >>> directive.get_full_key()
            'Alexa.PowerController.TurnOn'
        """
        return f"{self.namespace}.{self.name}"


__all__ = ['AlexaDirective']
