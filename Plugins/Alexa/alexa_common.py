"""Alexa Common Module for EE.

This module provides common error handling and utilities for the Alexa
Domain Gateway in EE.

Architecture Layer: Domain Gateway - Alexa Domain - Core Infrastructure

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_common.py

Integration:
    - Extends GatewayError from gateway_common
    - Provides Alexa-specific error types
    - Used across all Alexa gateway components
"""

from __future__ import annotations

from EE.src.gateway.gateway_common import GatewayError


class AlexaGatewayError(GatewayError):
    """Base error for Alexa gateway failures in EE.

    This error class represents all failures that occur within the Alexa
    Domain Gateway, including directive parsing errors, routing failures,
    capability execution errors, and response building errors.

    Attributes:
        message: Human-readable error description
        error_code: Error code (default: "ALEXA_GATEWAY_ERROR")
        context: Optional error context (directive info, endpoint details, etc.)
        source: Source component (default: "AlexaGateway")

    Example:
        >>> raise AlexaGatewayError(
        ...     message="Invalid directive format",
        ...     context={"directive": "TurnOn", "endpoint": "light-1"}
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "ALEXA_GATEWAY_ERROR",
        context: dict | None = None,
        source: str = "AlexaGateway",
    ) -> None:
        """Initialize an AlexaGatewayError.

        Args:
            message: Human-readable error description
            error_code: Error code for categorization (default: "ALEXA_GATEWAY_ERROR")
            context: Optional dictionary with error context
            source: Source component name (default: "AlexaGateway")

        Example:
            >>> raise AlexaGatewayError(
            ...     message="Failed to parse directive",
            ...     error_code="DIRECTIVE_PARSE_ERROR",
            ...     context={"raw_request": {...}}
            ... )
        """
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            source=source,
        )


__all__ = ['AlexaGatewayError']
