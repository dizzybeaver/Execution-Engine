"""Test script for Alexa Domain Gateway integration.

This script demonstrates:
1. Creating Alexa capability handlers
2. Building an Alexa gateway
3. Registering with EEDomainRegistry
4. Processing Alexa directives

Usage:
    python -m EE.src.gateway.alexa.test_alexa_integration
"""

from EE.src.gateway.gateway_registry import EEDomainRegistry, DomainGateway
from EE.src.gateway.alexa import (
    create_alexa_gateway,
    create_alexa_capability_handler,
    AlexaGatewayError,
)


# Sample capability handlers
def turn_on_handler(payload):
    """Handle PowerController.TurnOn directive."""
    print(f"Turning ON device with payload: {payload}")
    return {
        "state": "ON",
        "timestamp": "2025-12-29T20:00:00Z"
    }


def turn_off_handler(payload):
    """Handle PowerController.TurnOff directive."""
    print(f"Turning OFF device with payload: {payload}")
    return {
        "state": "OFF",
        "timestamp": "2025-12-29T20:00:00Z"
    }


def set_brightness_handler(payload):
    """Handle BrightnessController.SetBrightness directive."""
    brightness = payload.get("brightness", 0)
    print(f"Setting brightness to {brightness}")
    return {
        "brightness": brightness,
        "timestamp": "2025-12-29T20:00:00Z"
    }


def test_alexa_gateway():
    """Test Alexa gateway creation and execution."""
    print("=" * 60)
    print("Testing Alexa Domain Gateway for EE")
    print("=" * 60)

    # Create capability handlers
    turn_on = create_alexa_capability_handler(
        namespace="Alexa.PowerController",
        name="TurnOn",
        schema=None,
        handler=turn_on_handler,
    )

    turn_off = create_alexa_capability_handler(
        namespace="Alexa.PowerController",
        name="TurnOff",
        schema=None,
        handler=turn_off_handler,
    )

    set_brightness = create_alexa_capability_handler(
        namespace="Alexa.BrightnessController",
        name="SetBrightness",
        schema=None,
        handler=set_brightness_handler,
    )

    # Create Alexa gateway
    gateway = create_alexa_gateway(
        handlers={
            "turn_on": turn_on,
            "turn_off": turn_off,
            "set_brightness": set_brightness,
        }
    )

    print("\n1. Alexa Gateway Created")
    print(f"   Handlers: {list(gateway.router.handlers.keys())}")

    # Test directive execution
    test_request = {
        "directive": {
            "header": {
                "namespace": "Alexa.PowerController",
                "name": "TurnOn",
                "messageId": "test-msg-001",
                "correlationToken": "test-token-001",
                "payloadVersion": "3",
            },
            "endpoint": {
                "endpointId": "light-001",
            },
            "payload": {},
        }
    }

    print("\n2. Processing Test Directive")
    print(f"   Namespace: {test_request['directive']['header']['namespace']}")
    print(f"   Name: {test_request['directive']['header']['name']}")
    print(f"   Endpoint: {test_request['directive']['endpoint']['endpointId']}")

    response = gateway.execute(test_request)

    print("\n3. Response Received:")
    print(f"   Event Name: {response['event']['header']['name']}")
    print(f"   Endpoint: {response['event']['endpoint']['endpointId']}")
    print(f"   Payload: {response['event']['payload']}")

    # Test error handling
    print("\n4. Testing Error Handling")
    error_request = {
        "directive": {
            "header": {
                "namespace": "Alexa.UnknownController",
                "name": "UnknownAction",
                "messageId": "test-msg-002",
                "correlationToken": "test-token-002",
                "payloadVersion": "3",
            },
            "endpoint": {
                "endpointId": "device-001",
            },
            "payload": {},
        }
    }

    error_response = gateway.execute(error_request)
    print(f"   Error Type: {error_response['event']['payload']['type']}")
    print(f"   Error Message: {error_response['event']['payload']['message']}")

    print("\n" + "=" * 60)
    print("Alexa Domain Gateway Test Completed Successfully!")
    print("=" * 60)


def test_registry_integration():
    """Test integration with EEDomainRegistry."""
    print("\n" + "=" * 60)
    print("Testing EEDomainRegistry Integration")
    print("=" * 60)

    # Create gateway
    gateway = create_alexa_gateway(
        handlers={
            "turn_on": create_alexa_capability_handler(
                namespace="Alexa.PowerController",
                name="TurnOn",
                schema=None,
                handler=lambda p: {"state": "ON"},
            ),
        }
    )

    # Get registry instance
    registry = EEDomainRegistry.get_instance()

    # Check if alexa domain exists
    if registry.has_domain("alexa"):
        print("\nAlexa domain already registered, skipping...")
    else:
        print("\n1. Registering Alexa gateway with EEDomainRegistry")
        # Note: For actual registration, AlexaGateway needs to implement DomainGateway
        # This is a demonstration of the intended integration pattern
        print("   Gateway type:", type(gateway).__name__)
        print("   Domain name: alexa")
        print("\n   NOTE: Full registration requires implementing DomainGateway interface")

    print("\n2. Registry Statistics:")
    stats = registry.get_stats()
    print(f"   Total domains: {stats['total_domains']}")
    print(f"   Domains: {stats['domains']}")

    print("\n" + "=" * 60)
    print("Registry Integration Test Completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_alexa_gateway()
    test_registry_integration()
