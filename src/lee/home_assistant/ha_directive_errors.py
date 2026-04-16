# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract error classes from ha_directive_handlers.py


"""ha_directive_errors.py - Alexa Directive Error Hierarchy
Version: 2026-04-11_1
Purpose: Error exception classes for Alexa directive handling

This module provides:
- AlexaError base class
- Specialized error types for different Alexa namespaces
- Error payload construction for API v3 compliance

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any


class AlexaError(Exception):
    """Base class for Alexa directive errors."""

    namespace: str | None = None
    error_type: str | None = None
    error_message: str
    payload: dict[str, Any] | None = None

    def __init__(
        self,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Initialize Alexa error.

        Args:
            message: Error message
            payload: Optional error payload
        """
        super().__init__(message)
        self.error_message = message
        self.payload = payload


class AlexaInvalidValueError(AlexaError):
    """Invalid value error."""

    namespace = "Alexa"
    error_type = "INVALID_VALUE"


class AlexaTempRangeError(AlexaError):
    """Temperature out of range error."""

    namespace = "Alexa.ThermostatController"
    error_type = "TEMPERATURE_VALUE_OUT_OF_RANGE"

    def __init__(
        self,
        message: str,
        min_temp: float = None,
        max_temp: float = None
    ):
        super().__init__(message)
        if min_temp is not None and max_temp is not None:
            self.payload = {
                "validRange": {
                    "minimumValue": {"value": min_temp, "scale": "CELSIUS"},
                    "maximumValue": {"value": max_temp, "scale": "CELSIUS"},
                },
            }


class AlexaInvalidDirectiveError(AlexaError):
    """Invalid directive error."""

    namespace = "Alexa"
    error_type = "INVALID_DIRECTIVE"


class AlexaUnsupportedError(AlexaError):
    """Unsupported operation error."""

    namespace = "Alexa"
    error_type = "UNSUPPORTED_OPERATION"


class AlexaUnsupportedThermostatModeError(AlexaError):
    """Unsupported thermostat mode error."""

    namespace = "Alexa.ThermostatController"
    error_type = "UNSUPPORTED_THERMOSTAT_MODE"


class AlexaEndpointUnreachableError(AlexaError):
    """Endpoint unreachable error."""

    namespace = "Alexa"
    error_type = "ENDPOINT_UNREACHABLE"


class AlexaSecurityPanelAuthorizationRequiredError(AlexaError):
    """Security panel authorization required error."""

    namespace = "Alexa.SecurityPanelController"
    error_type = "AUTHORIZATION_REQUIRED"


class AlexaSecurityPanelUnauthorizedError(AlexaError):
    """Security panel unauthorized error."""

    namespace = "Alexa.SecurityPanelController"
    error_type = "UNAUTHORIZED"


__all__ = [
    "AlexaError",
    "AlexaInvalidValueError",
    "AlexaTempRangeError",
    "AlexaInvalidDirectiveError",
    "AlexaUnsupportedError",
    "AlexaUnsupportedThermostatModeError",
    "AlexaEndpointUnreachableError",
    "AlexaSecurityPanelAuthorizationRequiredError",
    "AlexaSecurityPanelUnauthorizedError",
]
