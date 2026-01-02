# Alexa Domain Gateway for EE

Complete Alexa Smart Home v3 integration gateway for EE (Enterprise Edge) platform.

## Overview

The Alexa Domain Gateway provides comprehensive support for Amazon Alexa Smart Home integration, enabling EE to control smart devices through Alexa voice commands and routines. The gateway implements the full Alexa Smart Home v3 API specification.

## Architecture

```
EE Universal Gateway
    └── EEDomainRegistry
            └── Alexa Domain Gateway
                    ├── AlexaDirective (Request Parser)
                    ├── AlexaRouter (Directive Router)
                    ├── AlexaCapabilityHandler (Capability Execution)
                    └── AlexaResponseFactory (Response Builder)
```

## Components

### 1. **AlexaGateway** (`alexa_gateway_factory.py`)
Main gateway that orchestrates directive processing:
- Receives Alexa requests
- Parses into AlexaDirective
- Routes to capability handlers
- Builds Alexa-compliant responses
- Handles errors gracefully

### 2. **AlexaDirective** (`alexa_directive.py`)
Immutable dataclass representing Alexa directives:
```python
@dataclass(frozen=True)
class AlexaDirective:
    namespace: str        # e.g., "Alexa.PowerController"
    name: str            # e.g., "TurnOn"
    correlation_token: str
    endpoint_id: str
    payload: dict
```

### 3. **AlexaRouter** (`alexa_router_factory.py`)
Routes directives to capability handlers:
- Indexes handlers by "namespace.name" key
- Routes AlexaDirective to appropriate handler
- Provides handler lookup and listing

### 4. **AlexaCapabilityHandler** (`alexa_capability_factory.py`)
Encapsulates capability execution logic:
- Optional schema validation
- Handler function execution
- Error handling and reporting

### 5. **AlexaResponseFactory** (`alexa_response_factory.py`)
Builds Alexa-compliant responses:
- Success responses with context
- Error responses with proper error types
- Follows Alexa v3 response format

### 6. **AlexaGatewayError** (`alexa_common.py`)
Enhanced error handling:
- Extends GatewayError
- Provides error codes and context
- Supports error chaining

## Installation

The Alexa gateway is included in EE at:
```
D:\Code\Project\EE\src\gateway\alexa\
```

## Usage

### Basic Example

```python
from EE.src.gateway.alexa import (
    create_alexa_gateway,
    create_alexa_capability_handler,
)

# Define a capability handler
def turn_on_handler(payload):
    # Execute device turn-on logic
    return {"state": "ON"}

# Create handler
turn_on = create_alexa_capability_handler(
    namespace="Alexa.PowerController",
    name="TurnOn",
    schema=None,  # Optional validation schema
    handler=turn_on_handler,
)

# Create gateway
gateway = create_alexa_gateway(
    handlers={
        "turn_on": turn_on,
    }
)

# Process Alexa request
alexa_request = {
    "directive": {
        "header": {
            "namespace": "Alexa.PowerController",
            "name": "TurnOn",
            "messageId": "msg-001",
            "correlationToken": "token-001",
            "payloadVersion": "3",
        },
        "endpoint": {
            "endpointId": "light-001",
        },
        "payload": {},
    }
}

response = gateway.execute(alexa_request)
# Returns Alexa-compliant response
```

### Multiple Capabilities

```python
# Define multiple handlers
turn_on = create_alexa_capability_handler(
    namespace="Alexa.PowerController",
    name="TurnOn",
    schema=None,
    handler=lambda p: {"state": "ON"},
)

turn_off = create_alexa_capability_handler(
    namespace="Alexa.PowerController",
    name="TurnOff",
    schema=None,
    handler=lambda p: {"state": "OFF"},
)

set_brightness = create_alexa_capability_handler(
    namespace="Alexa.BrightnessController",
    name="SetBrightness",
    schema=None,
    handler=lambda p: {"brightness": p["brightness"]},
)

# Create gateway with all handlers
gateway = create_alexa_gateway(
    handlers={
        "turn_on": turn_on,
        "turn_off": turn_off,
        "set_brightness": set_brightness,
    }
)
```

### With Schema Validation

```python
from EE.src.validation import create_object_schema

# Define schema
power_schema = create_object_schema({
    "entity_id": {"type": "string", "required": True},
})

# Create handler with validation
turn_on = create_alexa_capability_handler(
    namespace="Alexa.PowerController",
    name="TurnOn",
    schema=power_schema,
    handler=turn_on_handler,
)
```

## Supported Alexa Capabilities

### Standard Capabilities

1. **Alexa.PowerController**
   - TurnOn
   - TurnOff

2. **Alexa.BrightnessController**
   - SetBrightness
   - AdjustBrightness

3. **Alexa.ColorController**
   - SetColor

4. **Alexa.ColorTemperatureController**
   -SetColorTemperature
   - IncreaseColorTemperature
   - DecreaseColorTemperature

5. **Alexa.ThermostatController**
   - SetTargetTemperature
   - AdjustTargetTemperature
   - SetThermostatMode

6. **Alexa.LockController**
   - Lock
   - Unlock

7. **Alexa.PercentageController**
   - SetPercentage
   - AdjustPercentage

8. **Alexa.ToggleController**
   - Toggle

And many more as defined in the Alexa Smart Home v3 API.

## Response Format

### Success Response

```json
{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "Response",
            "messageId": "msg-1",
            "correlationToken": "token-001",
            "payloadVersion": "3"
        },
        "endpoint": {
            "endpointId": "endpoint-001"
        },
        "payload": {
            "state": "ON"
        }
    },
    "context": {
        "properties": [
            {
                "namespace": "Alexa.PowerController",
                "name": "powerState",
                "value": "ON",
                "timeOfSample": "2025-12-29T20:00:00Z",
                "uncertaintyInMilliseconds": 0
            }
        ]
    }
}
```

### Error Response

```json
{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "ErrorResponse",
            "messageId": "msg-1",
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
```

## Error Handling

The gateway provides comprehensive error handling:

```python
try:
    response = gateway.execute(alexa_request)
except AlexaGatewayError as e:
    print(f"Error Code: {e.error_code}")
    print(f"Message: {e.message}")
    print(f"Context: {e.context}")
```

Common error types:
- `DIRECTIVE_PARSE_ERROR`: Invalid directive format
- `HANDLER_NOT_FOUND`: No handler for directive
- `CAPABILITY_EXECUTION_ERROR`: Handler execution failed
- `RESPONSE_BUILD_ERROR`: Response building failed

## Integration with EEDomainRegistry

```python
from EE.src.gateway.gateway_registry import EEDomainRegistry

# Create gateway
gateway = create_alexa_gateway(handlers={...})

# Register with domain registry
registry = EEDomainRegistry.get_instance()
registry.register("alexa", gateway)

# Execute through registry
alexa_gateway = registry.get("alexa")
response = alexa_gateway.execute(request)
```

## Testing

Run the integration test:

```bash
cd D:\Code\Project\EE
python -m src.gateway.alexa.test_alexa_integration
```

## API Reference

### create_alexa_gateway()

Factory function to create an Alexa gateway.

**Parameters:**
- `handlers` (Dict[str, AlexaCapabilityHandler]): Dictionary of handlers

**Returns:**
- `AlexaGateway`: Configured gateway instance

### create_alexa_capability_handler()

Factory function to create a capability handler.

**Parameters:**
- `namespace` (str): Capability namespace
- `name` (str): Directive name
- `schema` (Any): Optional validation schema
- `handler` (Callable): Handler function

**Returns:**
- `AlexaCapabilityHandler`: Configured handler instance

### AlexaGateway.execute()

Process an Alexa directive request.

**Parameters:**
- `request` (dict): Raw Alexa request dictionary

**Returns:**
- `dict`: Alexa-compliant response

## File Structure

```
D:\Code\Project\EE\src\gateway\alexa\
├── __init__.py                    # Package exports
├── alexa_common.py                # Error handling
├── alexa_directive.py             # Directive parsing
├── alexa_response_factory.py      # Response building
├── alexa_capability_factory.py    # Capability handlers
├── alexa_router_factory.py        # Directive routing
├── alexa_gateway_factory.py       # Main gateway
├── test_alexa_integration.py      # Integration tests
└── README.md                      # This file
```

## Design Principles

1. **Immutability**: AlexaDirective and AlexaGateway are frozen dataclasses
2. **Type Safety**: Full type hints throughout
3. **Error Handling**: Comprehensive error handling with context
4. **Separation of Concerns**: Each component has single responsibility
5. **Factory Pattern**: All components created via factory functions
6. **Thread Safety**: Frozen dataclasses enable safe concurrent use

## Based On

Reference implementation:
```
D:\Code\Project\Gateway\Alexa\
```

## License

EE Enterprise License - See project root for details.

## Contributing

When adding new capabilities:
1. Create handler function
2. Wrap with `create_alexa_capability_handler()`
3. Add to gateway handlers dictionary
4. Add integration tests
5. Update documentation

## Support

For issues or questions:
- Check test file: `test_alexa_integration.py`
- Review reference implementation in Gateway project
- Contact EE platform team
