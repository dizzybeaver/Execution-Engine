"""Alexa Gateway Factory Module for EE.

This module implements the main Alexa Smart Home gateway for EE.
Provides the primary interface for processing Alexa directives and
returning Alexa-compliant responses.

Architecture Layer: Domain Gateway - Alexa Domain - Main Gateway

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\alexa_gateway_factory.py

Integration:
    - Uses AlexaGatewayError from alexa_common
    - Uses AlexaDirective from alexa_directive
    - Uses AlexaRouter from alexa_router_factory
    - Uses AlexaResponseFactory from alexa_response_factory
    - Implements DomainGateway interface for EEDomainRegistry
    - Can be registered as "alexa" domain in gateway system

Flow:
    1. Receive Alexa request (dict)
    2. Parse into AlexaDirective
    3. Route to capability handler via AlexaRouter
    4. Execute capability handler
    5. Build success response
    6. Return Alexa-compliant response

Error Handling:
    - Catches AlexaGatewayError (expected errors)
    - Catches Exception (unexpected errors)
    - Both return formatted error responses to Alexa

Example:
    >>> gateway = create_alexa_gateway(
    ...     handlers={
    ...         "power_controller": power_handler,
    ...         "brightness_controller": brightness_handler,
    ...     }
    ... )
    >>> response = gateway.execute(alexa_request_dict)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError
from EE.src.gateway.alexa.alexa_directive import AlexaDirective
from EE.src.gateway.alexa.alexa_router_factory import AlexaRouter
from EE.src.gateway.alexa.alexa_response_factory import AlexaResponseFactory, create_alexa_response_factory


@dataclass(frozen=True)
class AlexaGateway:
    """Main Alexa Smart Home gateway for EE.

    A frozen (immutable) gateway that processes Alexa directives and
    generates Alexa-compliant responses. Thread-safe for concurrent use.

    Attributes:
        router: AlexaRouter for directive routing
        responses: AlexaResponseFactory for response building

    Example:
        >>> gateway = AlexaGateway(
        ...     router=router,
        ...     responses=response_factory
        ... )
        >>> response = gateway.execute(alexa_request)
    """

    router: AlexaRouter
    responses: AlexaResponseFactory

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute an Alexa directive request.

        Processes the complete flow: parse request -> route directive ->
        execute handler -> build response.

        Args:
            request: Raw Alexa request dictionary

        Returns:
            Alexa-compliant response dictionary (success or error)

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
            >>> response = gateway.execute(request)
        """
        directive = None

        try:
            # Step 1: Parse request into directive
            directive = AlexaDirective.from_request(request)

            # Step 2: Route to appropriate handler
            handler = self.router.route(directive)

            # Step 3: Execute handler
            result = handler.execute(directive)

            # Step 4: Build success response
            return self.responses.success(directive, payload=result)

        except AlexaGatewayError as e:
            # Known error - return formatted error response
            if directive is None:
                # Create a minimal directive for error response
                directive = AlexaDirective(
                    namespace="Alexa",
                    name="Error",
                    correlation_token=request.get("directive", {}).get("header", {}).get("correlationToken", ""),
                    endpoint_id=request.get("directive", {}).get("endpoint", {}).get("endpointId", ""),
                    payload={},
                )

            return self.responses.error(
                directive,
                type=e.error_code.replace("ALEXA_", "").replace("_", " ").title().replace(" ", ""),
                message=e.message,
            )

        except Exception as e:
            # Unexpected error - return internal error response
            if directive is None:
                # Create a minimal directive for error response
                directive = AlexaDirective(
                    namespace="Alexa",
                    name="Error",
                    correlation_token=request.get("directive", {}).get("header", {}).get("correlationToken", ""),
                    endpoint_id=request.get("directive", {}).get("endpoint", {}).get("endpointId", ""),
                    payload={},
                )

            return self.responses.error(
                directive,
                type="INTERNAL_ERROR",
                message=f"Unhandled exception: {e}",
            )


def create_alexa_gateway(
    *,
    handlers: Dict[str, Any],
) -> AlexaGateway:
    """Factory function to create an Alexa gateway.

    Args:
        handlers: Dictionary of handler names to AlexaCapabilityHandler instances

    Returns:
        AlexaGateway instance with configured router and response factory

    Example:
        >>> from EE.src.gateway.alexa import (
        ...     create_alexa_capability_handler,
        ...     create_alexa_gateway
        ... )
        >>>
        >>> # Define capability handlers
        >>> turn_on_handler = create_alexa_capability_handler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOn",
        ...     schema=None,
        ...     handler=lambda p: {"state": "ON"}
        ... )
        >>>
        >>> turn_off_handler = create_alexa_capability_handler(
        ...     namespace="Alexa.PowerController",
        ...     name="TurnOff",
        ...     schema=None,
        ...     handler=lambda p: {"state": "OFF"}
        ... )
        >>>
        >>> # Create gateway
        >>> gateway = create_alexa_gateway(
        ...     handlers={
        ...         "turn_on": turn_on_handler,
        ...         "turn_off": turn_off_handler,
        ...     }
        ... )
        >>>
        >>> # Execute request
        >>> response = gateway.execute(alexa_request)

    Integration with EEDomainRegistry:
        >>> from EE.src.gateway.gateway_registry import (
        ...     EEDomainRegistry,
        ...     DomainGateway
        ... )
        >>>
        >>> # Create Alexa gateway
        >>> alexa_gateway = create_alexa_gateway(handlers={...})
        >>>
        >>> # Register with domain registry
        >>> registry = EEDomainRegistry.get_instance()
        >>> registry.register("alexa", alexa_gateway)
    """
    router = AlexaRouter(handlers={f"{h.namespace}.{h.name}": h for h in handlers.values()})
    responses = create_alexa_response_factory()

    return AlexaGateway(router=router, responses=responses)


__all__ = [
    'AlexaGateway',
    'create_alexa_gateway',
]
