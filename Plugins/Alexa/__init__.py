"""Alexa Domain Gateway for EE.

This package implements the Alexa Smart Home integration gateway for EE.
Provides comprehensive support for Alexa directives, capabilities, and responses.

Architecture:
    EE Universal Gateway -> Alexa Domain Gateway -> Alexa Capabilities

Components:
    - AlexaGateway: Main gateway for Alexa directive handling
    - AlexaDirective: Represents incoming Alexa directives
    - AlexaResponseFactory: Builds Alexa-compliant responses
    - AlexaCapabilityHandler: Handles individual Alexa capabilities
    - AlexaRouter: Routes directives to capability handlers

Based on:
    D:\\Code\\Project\\Gateway\\Alexa\\

Usage:
    from EE.src.gateway.alexa import create_alexa_gateway

    # Create gateway with capability handlers
    gateway = create_alexa_gateway(
        handlers={
            "power_controller": power_handler,
            "brightness_controller": brightness_handler,
        }
    )

    # Execute Alexa directive
    response = gateway.execute(alexa_request)

Integration:
    - Registers with EEDomainRegistry as "alexa" domain
    - Uses GatewayError from gateway_common
    - Implements DomainGateway interface
    - Supports standard Alexa Smart Home v3 API
"""

from EE.src.gateway.alexa.alexa_common import AlexaGatewayError
from EE.src.gateway.alexa.alexa_directive import AlexaDirective
from EE.src.gateway.alexa.alexa_response_factory import AlexaResponseFactory, create_alexa_response_factory
from EE.src.gateway.alexa.alexa_capability_factory import (
    AlexaCapabilityHandler,
    create_alexa_capability_handler,
)
from EE.src.gateway.alexa.alexa_router_factory import AlexaRouter, create_alexa_router
from EE.src.gateway.alexa.alexa_gateway_factory import AlexaGateway, create_alexa_gateway

__all__ = [
    'AlexaGatewayError',
    'AlexaDirective',
    'AlexaResponseFactory',
    'create_alexa_response_factory',
    'AlexaCapabilityHandler',
    'create_alexa_capability_handler',
    'AlexaRouter',
    'create_alexa_router',
    'AlexaGateway',
    'create_alexa_gateway',
]
