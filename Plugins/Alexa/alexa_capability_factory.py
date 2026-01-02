"""Alexa Capability Factory Module for EE.

This module implements the capability handler factory for Alexa Smart Home
integration. Creates handlers for individual Alexa capabilities like
PowerController, BrightnessController, etc.

Architecture Layer: Domain Gateway - Alexa Domain - Capability Management

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_capability_factory.py

Integration:
    - Uses AlexaGatewayError from alexa_common
    - Encapsulates schema validation
    - Provides capability execution interface
    - Used by AlexaRouter for directive handling

Alexa Capabilities:
    - Alexa.PowerController: TurnOn, TurnOff
    - Alexa.BrightnessController: SetBrightness, AdjustBrightness
    - Alexa.ColorController: SetColor
    - Alexa.ThermostatController: SetTargetTemperature, etc.
    - Alexa.LockController: Lock, Unlock
    - And many more...

Example Capability Handler:
    >>> def turn_on_handler(payload):
    ...     # Execute turn on logic
    ...     return {"state": "ON"}
    >>>
    >>> handler = create_alexa_capability_handler(
    ...     namespace="Alexa.PowerController",
    ...     name="TurnOn",
    ...     schema=power_schema,
    ...     handler=turn_on_handler
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError


@dataclass
class AlexaCapabilityHandler:
    """Handler for a specific Alexa capability.

    Encapsulates the schema validation and handler logic for a single
    Alexa capability directive (e.g., "Alexa.PowerController.TurnOn").

    Attributes:
        namespace: Capability namespace (e.g., "Alexa.PowerController")
        name: Directive name (e.g., "TurnOn")
        schema: Optional schema for payload validation
        handler: Handler function that executes the capability

    Example:
        >>> handler = AlexaCapabilityHandler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOn",
        ...     schema=None,
        ...     handler=lambda p: {"state": "ON"}
        ... )
        >>> result = handler.execute(alexa_directive)
    """

    namespace: str
    name: str
    schema: Any
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def execute(self, directive: Any) -> dict[str, Any]:
        """Execute the capability handler with validation.

        Validates the directive payload using the schema (if provided)
        and then executes the handler function.

        Args:
            directive: AlexaDirective containing the payload

        Returns:
            Handler execution result

        Raises:
            AlexaGatewayError: If validation or execution fails

        Example:
            >>> handler = AlexaCapabilityHandler(
            ...     namespace="Alexa.BrightnessController",
            ...     name="SetBrightness",
            ...     schema=brightness_schema,
            ...     handler=set_brightness_handler
            ... )
            >>> result = handler.execute(directive)
        """
        try:
            # Validate payload if schema provided
            if self.schema:
                if hasattr(self.schema, 'validate'):
                    validated = self.schema.validate(directive.payload)
                elif callable(self.schema):
                    validated = self.schema(directive.payload)
                else:
                    raise AlexaGatewayError(
                        message=f"Invalid schema for capability '{self.namespace}.{self.name}'",
                        error_code="INVALID_SCHEMA",
                        context={
                            "namespace": self.namespace,
                            "name": self.name,
                            "schema_type": type(self.schema).__name__,
                        },
                    )
            else:
                validated = directive.payload

            # Execute handler
            return self.handler(validated)

        except AlexaGatewayError:
            # Re-raise Alexa errors as-is
            raise

        except Exception as e:
            # Wrap other exceptions
            raise AlexaGatewayError(
                message=f"Capability '{self.namespace}.{self.name}' failed: {e}",
                error_code="CAPABILITY_EXECUTION_ERROR",
                context={
                    "namespace": self.namespace,
                    "name": self.name,
                    "exception_type": type(e).__name__,
                },
            ) from e


def create_alexa_capability_handler(
    *,
    namespace: str,
    name: str,
    schema: Any,
    handler: Callable[[dict[str, Any]], dict[str, Any]],
) -> AlexaCapabilityHandler:
    """Factory function to create an Alexa capability handler.

    Args:
        namespace: Capability namespace (e.g., "Alexa.PowerController")
        name: Directive name (e.g., "TurnOn")
        schema: Schema for payload validation (None for no validation)
        handler: Handler function that processes validated payloads

    Returns:
        AlexaCapabilityHandler instance

    Example:
        >>> def turn_on_handler(payload):
        ...     # Execute device turn on
        ...     return {"state": "ON"}
        >>>
        >>> handler = create_alexa_capability_handler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOn",
        ...     schema=None,
        ...     handler=turn_on_handler
        ... )
    """
    return AlexaCapabilityHandler(
        namespace=namespace,
        name=name,
        schema=schema,
        handler=handler,
    )


__all__ = [
    'AlexaCapabilityHandler',
    'create_alexa_capability_handler',
]
