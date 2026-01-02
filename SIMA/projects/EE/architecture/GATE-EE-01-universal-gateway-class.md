# GATE-EE-01: UniversalGateway Class

**Category:** Architecture
**Status:** Production
**EE Version:** 2.0.0
**Last Updated:** 2025-12-31

---

## Overview

The `UniversalGateway` (UG) class is the **central coordinator** for all EE operations. It manages domain gateway registration, provides dependency injection for cross-cutting concerns (logging, metrics), and enforces the UG architecture pattern.

---

## Pattern Definition

### Location
`d:\Code\Project\EE\universal_gateway\gateway.py`

### Core Class

```python
# EE/universal_gateway/gateway.py (lines 94-473)

class UniversalGateway:
    """Universal Gateway - SINGLE entry point for all EE operations.

    The UniversalGateway (UG) is the central hub for all operations in the
    EE system. It manages domain gateways, provides dependency injection for
    cross-cutting concerns (logging, metrics), and ensures clean architecture.

    Key Features:
    - Single entry point via execute_operation()
    - Domain gateway management
    - Dependency injection for loggers and metrics
    - Cross-domain operation support
    - Type-safe error handling

    Thread Safety:
        The gateway is thread-safe for read operations (execute_operation,
        get_logger, get_metrics). Domain registration should be done during
        initialization and not modified during concurrent execution.
    """

    def __init__(
        self,
        logger_factory: LoggerFactory,
        metrics_factory: MetricsFactory,
    ) -> None:
        """Initialize the Universal Gateway.

        Args:
            logger_factory: Factory function to create loggers
            metrics_factory: Factory function to create metrics collectors

        Raises:
            ValueError: If factory functions are None
        """
        if logger_factory is None:
            raise ValueError("logger_factory cannot be None")
        if metrics_factory is None:
            raise ValueError("metrics_factory cannot be None")

        self._logger_factory: LoggerFactory = logger_factory
        self._metrics_factory: MetricsFactory = metrics_factory
        self._domains: Dict[str, Any] = {}

        # Get UG-level logger
        self._logger = self._logger_factory("ug")
        self._logger.info("Universal Gateway initialized")
```

---

## Key Features

### 1. Domain Gateway Registration

The UG manages all domain gateways in a centralized registry:

```python
# EE/universal_gateway/gateway.py (lines 185-218)

def register_domain_gateway(
    self,
    domain_name: str,
    gateway: Any,
) -> None:
    """Register a domain gateway.

    Args:
        domain_name: Unique domain identifier (e.g., "config", "security")
        gateway: Domain gateway instance

    Raises:
        ValueError: If domain_name is empty or gateway is None
        ValueError: If domain already registered

    Example:
        config_gateway = ConfigGateway(...)
        ug.register_domain_gateway("config", config_gateway)
    """
    if not domain_name:
        raise ValueError("Domain name cannot be empty")

    if gateway is None:
        raise ValueError("Gateway cannot be None")

    if domain_name in self._domains:
        raise ValueError(
            f"Domain '{domain_name}' is already registered. "
            f"Cannot register duplicate domains."
        )

    self._domains[domain_name] = gateway
    self._logger.info(f"Registered domain gateway: {domain_name}")
```

**Registration from EE/__init__.py (lines 152-303):**

```python
# Create UG instance
_ug = UniversalGateway(
    logger_factory=_default_logger_factory,
    metrics_factory=_default_metrics_factory,
)

# Register Foundation Domain
from .foundation import FoundationGateway
foundation_gateway = FoundationGateway(
    logger=_ug.get_logger("foundation"),
    metrics=_ug.get_metrics("foundation"),
    call_operation=_ug.execute_operation
)
_ug.register_domain_gateway("foundation", foundation_gateway)

# Register Observability Domain
from .observability import ObservabilityGateway
observability_gateway = ObservabilityGateway(
    logger=_ug.get_logger("observability"),
    metrics=_ug.get_metrics("observability"),
    call_operation=_ug.execute_operation
)
_ug.register_domain_gateway("observability", observability_gateway)

# Register Security Domain
from .security import SecurityGateway
security_gateway = SecurityGateway(
    logger=_ug.get_logger("security"),
    metrics=_ug.get_metrics("security"),
    call_operation=_ug.execute_operation
)
_ug.register_domain_gateway("security", security_gateway)

# ... (12 more domains)
```

### 2. Dependency Injection

The UG provides factories for cross-cutting concerns:

```python
# EE/universal_gateway/gateway.py (lines 251-279)

def get_logger(self, name: str) -> logging.Logger:
    """Get a logger for a component.

    Args:
        name: Component name (e.g., "config", "security.auth")

    Returns:
        Logger instance

    Example:
        logger = ug.get_logger("config")
        logger.info("Configuration loaded")
    """
    return self._logger_factory(name)

def get_metrics(self, name: str) -> Any:
    """Get metrics collector for a component.

    Args:
        name: Component name

    Returns:
        Metrics collector instance

    Example:
        metrics = ug.get_metrics("config")
        metrics.increment("config.get")
    """
    return self._metrics_factory(name)
```

**Type Protocols for Factories:**

```python
# EE/universal_gateway/gateway.py (lines 55-68)

class LoggerFactory(Protocol):
    """Protocol for logger factory functions.

    The logger factory creates logger instances for components.
    """
    def __call__(self, name: str) -> logging.Logger: ...

class MetricsFactory(Protocol):
    """Protocol for metrics factory functions.

    The metrics factory creates metrics collectors for components.
    """
    def __call__(self, name: str) -> Any: ...
```

### 3. Operation Execution

The core `execute_operation()` method routes to domain gateways:

```python
# EE/universal_gateway/gateway.py (lines 285-396)

def execute_operation(
    self,
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    """Execute operation using UG pattern.

    This is the MAIN entry point for all EE operations.
    NO backward compatibility - this is the only pattern.

    Args:
        domain: Domain name (e.g., "config", "security", "logging")
        interface: Interface name (e.g., "config", "auth", "database")
        operation: Operation name (e.g., "get", "set", "query")
        **kwargs: Operation-specific parameters

    Returns:
        Operation result (type depends on operation)

    Raises:
        DomainNotFoundError: If domain not registered
        InvalidOperationError: If operation execution fails

    Example:
        # Get configuration value
        config_value = ug.execute_operation(
            domain="config",
            interface="config",
            operation="get",
            key="database.host"
        )
    """
    # Validate domain exists
    if domain not in self._domains:
        available = list(self._domains.keys())
        raise DomainNotFoundError(
            f"Unknown domain: '{domain}'. "
            f"Available domains: {available}"
        )

    # Get domain gateway
    gateway = self._domains[domain]

    # Execute operation
    try:
        self._logger.debug(
            f"Executing: {domain}.{interface}.{operation}()"
        )

        result = gateway.execute_domain_operation(
            interface=interface,
            operation=operation,
            **kwargs
        )

        self._logger.debug(
            f"Completed: {domain}.{interface}.{operation}()"
        )

        return result

    except Exception as e:
        # Wrap in UG exception
        raise InvalidOperationError(
            f"Failed to execute operation "
            f"'{domain}.{interface}.{operation}()': {e}"
        ) from e
```

### 4. Discovery and Statistics

```python
# EE/universal_gateway/gateway.py (lines 402-472)

def list_all(self) -> Dict[str, Any]:
    """List all available operations from all domains.

    Returns:
        Dictionary mapping domain names to their operations:
        {
            "config": {
                "domain": "config",
                "interfaces": ["config", "secrets"],
                "interface_count": 2
            },
            "security": {
                "domain": "security",
                "interfaces": ["auth", "encryption"],
                "interface_count": 2
            },
            ...
        }

    Example:
        all_ops = ug.list_all()
        for domain, info in all_ops.items():
            print(f"{domain}: {info['interface_count']} interfaces")
    """
    result = {}

    for domain_name, gateway in self._domains.items():
        try:
            result[domain_name] = gateway.list_all()
        except Exception as e:
            result[domain_name] = {
                "error": f"Failed to list operations: {e}"
            }

    return result

def get_stats(self) -> Dict[str, Any]:
    """Get gateway statistics.

    Returns:
        Dictionary with gateway statistics:
        {
            "total_domains": 5,
            "domains": ["config", "security", "logging", "metrics", "debug"],
            "domain_stats": {
                "config": {...},
                "security": {...},
                ...
            }
        }

    Example:
        stats = ug.get_stats()
        print(f"Total domains: {stats['total_domains']}")
    """
    domain_stats = {}

    for domain_name, gateway in self._domains.items():
        try:
            if hasattr(gateway, 'get_stats'):
                domain_stats[domain_name] = gateway.get_stats()
            else:
                domain_stats[domain_name] = gateway.list_all()
        except Exception as e:
            domain_stats[domain_name] = {"error": str(e)}

    return {
        "total_domains": len(self._domains),
        "domains": list(self._domains.keys()),
        "domain_stats": domain_stats,
    }
```

---

## Architecture Flow

### Request Flow

```
External Code
    ↓ execute_operation(domain, interface, operation, **kwargs)
UniversalGateway.execute_operation()
    ↓ Validate domain exists
    ↓ Get domain gateway from _domains dict
DomainGateway.execute_domain_operation()
    ↓ Validate interface exists
    ↓ Create interface instance with DI
Interface.execute_operation()
    ↓ Route via DISPATCH dict
Factory Method
    ↓ Execute implementation
Result
```

### Cross-Domain Communication

Domains communicate through the injected `call_operation` callback:

```python
# Domain gateway initialization
foundation_gateway = FoundationGateway(
    logger=_ug.get_logger("foundation"),
    metrics=_ug.get_metrics("foundation"),
    call_operation=_ug.execute_operation  # ← Inject UG's execute_operation
)

# Inside foundation domain
class ConfigFactory:
    def __init__(self, call_operation):
        self._call_operation = call_operation

    def get_encrypted_key(self, key):
        # Call security domain from foundation domain
        decrypted = self._call_operation(
            domain="security",
            interface="encryption",
            operation="decrypt",
            value=self._encrypted_config[key]
        )
        return decrypted
```

---

## Exception Hierarchy

```python
# EE/universal_gateway/gateway.py (lines 75-87)

class UniversalGatewayError(Exception):
    """Base exception for UniversalGateway errors."""
    pass

class DomainNotFoundError(UniversalGatewayError):
    """Raised when a domain is not found."""
    pass

class InvalidOperationError(UniversalGatewayError):
    """Raised when an operation cannot be executed."""
    pass
```

**Usage:**

```python
try:
    result = ug.execute_operation(
        domain="unknown",
        interface="test",
        operation="op"
    )
except DomainNotFoundError as e:
    print(f"Domain not found: {e}")
    print(f"Available domains: {ug.get_domain_gateways().keys()}")

except InvalidOperationError as e:
    print(f"Operation failed: {e}")
```

---

## Thread Safety

**Read Operations (Thread-Safe):**
- `execute_operation()` - Concurrent execution across domains
- `get_logger()` - Factory function calls
- `get_metrics()` - Factory function calls
- `has_domain()` - Dictionary reads
- `get_domain_gateways()` - Returns copy of domains dict

**Write Operations (Not Thread-Safe):**
- `register_domain_gateway()` - Must be done during initialization

**Best Practice:**

```python
# ✅ DO: Register all domains during initialization
def initialize_ee():
    ug = UniversalGateway(
        logger_factory=my_logger_factory,
        metrics_factory=my_metrics_factory
    )

    # Register all domains upfront
    ug.register_domain_gateway("foundation", foundation_gateway)
    ug.register_domain_gateway("security", security_gateway)
    ug.register_domain_gateway("networking", networking_gateway)

    return ug

# ❌ DON'T: Register domains during concurrent execution
# This can cause race conditions
```

---

## Usage Examples

### Example 1: Basic Usage

```python
from EE.universal_gateway import UniversalGateway
import logging

# Create UG instance
ug = UniversalGateway(
    logger_factory=lambda name: logging.getLogger(f"EE.{name}"),
    metrics_factory=lambda name: MyMetricsCollector(name)
)

# Register domain gateways
from EE.foundation import FoundationGateway
foundation_gateway = FoundationGateway(
    logger=ug.get_logger("foundation"),
    metrics=ug.get_metrics("foundation"),
    call_operation=ug.execute_operation
)
ug.register_domain_gateway("foundation", foundation_gateway)

# Execute operation
config_value = ug.execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)
```

### Example 2: Check Domain Availability

```python
# Check if domain exists before calling
if ug.has_domain("networking"):
    response = ug.execute_operation(
        domain="networking",
        interface="http",
        operation="get",
        url="https://api.example.com/data"
    )
else:
    print("Networking domain not available")
```

### Example 3: List All Operations

```python
# Get statistics
stats = ug.get_stats()
print(f"Total domains: {stats['total_domains']}")
print(f"Domains: {stats['domains']}")

# List all operations
all_ops = ug.list_all()
for domain_name, domain_info in all_ops.items():
    print(f"\n{domain_name}:")
    for interface in domain_info.get("interfaces", []):
        print(f"  - {interface}")
```

---

## Related Patterns

- **ARCH-EE-01:** Single entry point pattern (package-level)
- **LESS-EE-01:** Module-level singleton UG pattern
- **GATE-GEN-01:** DomainGateway base class

---

## References

- **Implementation:** `d:\Code\Project\EE\universal_gateway\gateway.py`
- **DomainGateway Base:** `d:\Code\Project\EE\universal_gateway\domain_gateway.py`
- **Package Init:** `d:\Code\Project\EE\__init__.py` (UG initialization)
- **UG Architecture Guide:** `d:\Code\Project\UG Architecture Guide.md`
