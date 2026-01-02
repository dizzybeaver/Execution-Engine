# Universal Gateway (UG) Core

The Universal Gateway (UG) is the central entry point for all operations in the EE (Execution Engine) system. This is the **new architecture** that replaces the legacy route-based gateway system.

## Architecture

```
Application Code
    ↓ execute_operation(domain, interface, operation, **kwargs)
UniversalGateway (UG)
    ↓ dispatch to domain gateway
DomainGateway (per domain)
    ↓ execute domain operation
Interface Factory
    ↓ build interface with dependency injection
Interface Instance
    ↓ execute operation
Implementation
```

## Key Principles

1. **Single Entry Point**: All operations go through `execute_operation()`
2. **No Backward Compatibility**: Does NOT support legacy `execute(route, payload)` pattern
3. **Clean Architecture**: Proper separation of concerns with dependency injection
4. **Type Safety**: Full type hints throughout
5. **Clear Error Handling**: Descriptive error messages for all failure modes

## Usage

### Basic Usage

```python
from EE import execute_operation

# Execute an operation
result = execute_operation(
    domain="config",
    interface="config",
    operation="get",
    key="database.host"
)
```

### Domain Gateway Registration

```python
from EE import get_ug
from EE.universal_gateway import DomainGateway

# Create a domain gateway
class ConfigGateway(DomainGateway):
    def __init__(self, get_logger, get_metrics, call_operation):
        super().__init__(
            domain_name="config",
            get_logger=get_logger,
            get_metrics=get_metrics,
            call_operation=call_operation
        )
        # Register interfaces
        self.register_interface("config", ConfigInterfaceFactory)

# Register with UG
ug = get_ug()
config_gateway = ConfigGateway(
    get_logger=ug.get_logger,
    get_metrics=ug.get_metrics,
    call_operation=ug.execute_operation
)
ug.register_domain_gateway("config", config_gateway)
```

### Cross-Domain Operations

Domains can call operations in other domains through the injected `call_operation` function:

```python
class MyDomainGateway(DomainGateway):
    def my_method(self):
        # Call another domain
        result = self._call_operation(
            domain="config",
            interface="config",
            operation="get",
            key="some.key"
        )
        return result
```

## Files

### `gateway.py` - UniversalGateway Class

Main entry point for all operations.

**Key Methods:**
- `execute_operation(domain, interface, operation, **kwargs)` - Execute operation
- `register_domain_gateway(domain_name, gateway)` - Register domain
- `get_logger(name)` - Get logger for component
- `get_metrics(name)` - Get metrics for component
- `list_all()` - List all operations

**Exceptions:**
- `DomainNotFoundError` - Domain not registered
- `InvalidOperationError` - Operation execution failed

### `gateway_registry.py` - EEDomainRegistry Class

Singleton registry for managing domain gateways.

**Key Methods:**
- `get_instance()` - Get singleton instance
- `register(domain_name, gateway)` - Register domain
- `get(domain_name)` - Get domain gateway
- `has_domain(domain_name)` - Check if domain exists
- `list_domains()` - List all domain names

**Exceptions:**
- `DomainNotRegisteredError` - Domain not found
- `DomainAlreadyRegisteredError` - Duplicate domain

### `domain_gateway.py` - DomainGateway Base Class

Base class for all domain gateways.

**Key Methods:**
- `register_interface(interface_name, factory)` - Register interface
- `execute_domain_operation(interface, operation, **kwargs)` - Execute operation
- `list_all()` - List domain operations
- `has_interface(interface_name)` - Check if interface exists

**Exceptions:**
- `InterfaceNotFoundError` - Interface not found
- `OperationNotFoundError` - Operation not found

## Migration from Legacy Gateway

### OLD Pattern (Deprecated)

```python
from EE import execute

result = execute("config.get", {"key": "database.host"})
```

### NEW Pattern (UG)

```python
from EE import execute_operation

result = execute_operation(
    domain="config",
    interface="config",
    operation="get",
    key="database.host"
)
```

## AWS Lambda Usage

```python
from EE import execute_operation

def lambda_handler(event, context):
    result = execute_operation(
        domain="config",
        interface="secrets",
        operation="get",
        key="API_KEY"
    )
    return result
```

## Type Hints

All classes and methods have complete type hints:

```python
from typing import Any, Callable

def execute_operation(
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    ...
```

## Error Handling

```python
from EE.universal_gateway import (
    DomainNotFoundError,
    InvalidOperationError,
    InterfaceNotFoundError,
    OperationNotFoundError,
)

try:
    result = execute_operation(...)
except DomainNotFoundError as e:
    # Domain not registered
    print(f"Unknown domain: {e}")
except InterfaceNotFoundError as e:
    # Interface not found in domain
    print(f"Unknown interface: {e}")
except OperationNotFoundError as e:
    # Operation not found
    print(f"Unknown operation: {e}")
except InvalidOperationError as e:
    # Operation execution failed
    print(f"Execution error: {e}")
```

## Testing

```python
# Test imports
from EE.universal_gateway import (
    UniversalGateway,
    EEDomainRegistry,
    DomainGateway,
)

# Test EE module
from EE import execute_operation, get_ug, get_registry

# Verify instances
ug = get_ug()
registry = get_registry()
```

## Next Steps

1. Create domain gateways inheriting from `DomainGateway`
2. Implement interface factories for each domain
3. Register domain gateways with UG in `EE/__init__.py`
4. Migrate existing code to use `execute_operation()`
5. Remove legacy gateway code (`EE/src/gateway/`)

## Version

- Version: 2.0.0 (UG Architecture)
- EE Version: 2.0.0
