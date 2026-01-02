"""Alexa Router Factory Module for EE.

This module implements the directive router for Alexa Smart Home integration.
Routes incoming Alexa directives to the appropriate capability handlers.

Architecture Layer: Domain Gateway - Alexa Domain - Directive Routing

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_router_factory.py

Integration:
    - Uses AlexaGatewayError from alexa_common
    - Uses AlexaDirective from alexa_directive
    - Uses AlexaCapabilityHandler from alexa_capability_factory
    - Provides routing logic for AlexaGateway

Routing Logic:
    - Constructs route key as "namespace.name" (e.g., "Alexa.PowerController.TurnOn")
    - Matches against registered capability handlers
    - Returns handler for execution
    - Raises error if no handler found

Example:
    >>> router = AlexaRouter(handlers={
    ...     "Alexa.PowerController.TurnOn": turn_on_handler,
    ...     "Alexa.PowerController.TurnOff": turn_off_handler,
    ... })
    >>> handler = router.route(directive)
    >>> result = handler.execute(directive)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError
from EE.src.gateway.alexa.alexa_directive import AlexaDirective
from EE.src.gateway.alexa.alexa_capability_factory import AlexaCapabilityHandler


@dataclass
class AlexaRouter:
    """Router for Alexa directives to capability handlers.

    Maintains a registry of capability handlers indexed by their full
    directive key (namespace.name) and routes incoming directives to
    the appropriate handler.

    Attributes:
        handlers: Dictionary mapping "namespace.name" to capability handlers

    Example:
        >>> router = AlexaRouter(handlers={
        ...     "Alexa.PowerController.TurnOn": power_on_handler,
        ...     "Alexa.PowerController.TurnOff": power_off_handler,
        ...     "Alexa.BrightnessController.SetBrightness": brightness_handler,
        ... })
        >>> handler = router.route(directive)
    """

    handlers: Dict[str, AlexaCapabilityHandler]

    def route(self, directive: AlexaDirective) -> AlexaCapabilityHandler:
        """Route a directive to the appropriate capability handler.

        Constructs the route key from the directive's namespace and name,
        looks up the corresponding handler, and returns it for execution.

        Args:
            directive: AlexaDirective to route

        Returns:
            AlexaCapabilityHandler for processing the directive

        Raises:
            AlexaGatewayError: If no handler is registered for the directive

        Example:
            >>> directive = AlexaDirective(
            ...     namespace="Alexa.PowerController",
            ...     name="TurnOn",
            ...     correlation_token="token-123",
            ...     endpoint_id="light-1",
            ...     payload={}
            ... )
            >>> handler = router.route(directive)
            >>> result = handler.execute(directive)
        """
        key = directive.get_full_key()

        if key not in self.handlers:
            available = list(self.handlers.keys())
            raise AlexaGatewayError(
                message=f"No handler registered for Alexa directive: {key}",
                error_code="HANDLER_NOT_FOUND",
                context={
                    "requested_directive": key,
                    "namespace": directive.namespace,
                    "name": directive.name,
                    "available_handlers": available,
                },
            )

        return self.handlers[key]

    def has_handler(self, directive: AlexaDirective) -> bool:
        """Check if a handler exists for the given directive.

        Args:
            directive: AlexaDirective to check

        Returns:
            True if handler exists, False otherwise

        Example:
            >>> if router.has_handler(directive):
            ...     handler = router.route(directive)
            ...     result = handler.execute(directive)
        """
        key = directive.get_full_key()
        return key in self.handlers

    def list_handlers(self) -> list[str]:
        """List all registered handler keys.

        Returns:
            List of "namespace.name" strings for all registered handlers

        Example:
            >>> router.list_handlers()
            ['Alexa.PowerController.TurnOn', 'Alexa.PowerController.TurnOff']
        """
        return list(self.handlers.keys())


def create_alexa_router(**handlers: AlexaCapabilityHandler) -> AlexaRouter:
    """Factory function to create an Alexa router with handlers.

    Args:
        **handlers: Keyword arguments mapping names to AlexaCapabilityHandler instances

    Returns:
        AlexaRouter instance with handlers indexed by namespace.name

    Example:
        >>> turn_on = create_alexa_capability_handler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOn",
        ...     schema=None,
        ...     handler=lambda p: {"state": "ON"}
        ... )
        >>>
        >>> turn_off = create_alexa_capability_handler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOff",
        ...     schema=None,
        ...     handler=lambda p: {"state": "OFF"}
        ... )
        >>>
        >>> router = create_alexa_router(
        ...     power_on=turn_on,
        ...     power_off=turn_off,
        ... )
    """
    return AlexaRouter(
        handlers={f"{h.namespace}.{h.name}": h for h in handlers.values()}
    )


__all__ = [
    'AlexaRouter',
    'create_alexa_router',
]
