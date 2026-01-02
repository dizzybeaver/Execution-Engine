# LESS-PY-02: Comprehensive Docstring Pattern

**Category:** Python Documentation
**Context:** Code maintainability and self-documentation
**Difficulty:** Beginner

---

## Overview

Use comprehensive triple-quoted module and class docstrings that include purpose, usage examples, and key characteristics. Create self-documenting code that serves as its own documentation.

## Pattern Structure

### Module Docstring Template

```python
"""
[Module Name] - [Brief one-line description]

[Detailed paragraph explaining what the module does and its role
in the system. Can be multiple paragraphs.]

Architecture:
    [Shows the module's place in the overall architecture]
    Module A → This Module → Module B

Key Principles:
1. [First key principle]
2. [Second key principle]
3. [Third principle]

Usage:
    [Code example showing basic usage]
    # Create instance
    instance = ClassName(param1, param2)

    # Call method
    result = instance.method()

Type Hints:
    - [Type hint notes]
    - [Generic return types if applicable]

Thread Safety:
    [Notes on thread safety if applicable]
    The module is thread-safe for read operations.

Cross-References:
    - [Related modules or patterns]
"""
```

### Class Docstring Template

```python
class ClassName:
    """[Brief one-line description].

    [Detailed description of the class purpose and behavior.

    Key Features:
        - Feature 1
        - Feature 2
        - Feature 3

    Architecture Pattern:
        [Shows class pattern or role]
        execute_operation(domain, interface, **kwargs)

    Thread Safety:
        [Thread safety notes]
        The class is thread-safe for read operations.

    Usage:
        [Usage example]
        # Create instance
        instance = ClassName(
            param1=value1,
            param2=value2
        )

        # Use method
        result = instance.method()

    Args:
        [Constructor parameters]
        param1: Description
        param2: Description

    Raises:
        ValueError: If invalid parameters

    Example:
        [More detailed example]
        instance = ClassName()
        result = instance.method(arg1, arg2)
    """
```

### Method Docstring Template

```python
def method_name(self, param1: str, param2: int) -> bool:
    """[One-line summary].

    [Detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is invalid
        TypeError: If wrong types provided

    Example:
        >>> obj.method_name("test", 42)
        True
    """
```

## Complete Examples

### Example 1: Module with Comprehensive Docstring

```python
"""
Universal Gateway (UG) - Central entry point for all EE operations.

This module provides the UniversalGateway class, which is the SINGLE entry
point for all operations in the EE system. The UG manages domain gateways
and provides dependency injection for cross-cutting concerns.

Architecture:
    Application Code
        ↓ execute_operation(domain, interface, operation, **kwargs)
    UniversalGateway (this module)
        ↓ get domain gateway
    DomainGateway
        ↓ execute domain operation
    Interface
        ↓ execute operation
    Implementation

Key Principles:
1. Single entry point - execute_operation() only
2. NO backward compatibility - no execute(route, payload)
3. Dependency injection for cross-cutting concerns
4. Type-safe with proper error handling
5. Clean separation of concerns

Usage:
    # Create UG instance
    ug = UniversalGateway(
        logger_factory=my_logger_factory,
        metrics_factory=my_metrics_factory
    )

    # Register domain gateways
    ug.register_domain_gateway("config", config_gateway)
    ug.register_domain_gateway("security", security_gateway)

    # Execute operations
    result = ug.execute_operation(
        domain="config",
        interface="config",
        operation="get",
        key="database.host"
    )

Type Hints:
    - Complete type coverage for all public methods
    - Generic return types for flexibility
    - Proper exception hierarchy

Thread Safety:
    The gateway is thread-safe for read operations (execute_operation,
    get_logger, get_metrics). Domain registration should be done during
    initialization and not modified during concurrent execution.

Cross-Domain Calls:
    Domains can call operations in other domains through the call_operation
    parameter passed during gateway initialization.
"""

from __future__ import annotations
from typing import Any, Dict, Callable, Optional, Protocol
import logging
```

### Example 2: Class with Comprehensive Docstring

```python
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

    Architecture Pattern:
        execute_operation(domain, interface, operation, **kwargs)
        - NO backward compatibility methods
        - Clean separation of concerns
        - Dependency injection throughout

    Thread Safety:
        The gateway is thread-safe for read operations (execute_operation,
        get_logger, get_metrics). Domain registration should be done during
        initialization and not modified during concurrent execution.

    Usage:
        # Create UG instance
        ug = UniversalGateway(
            logger_factory=lambda name: logging.getLogger(name),
            metrics_factory=lambda name: MyMetricsCollector(name)
        )

        # Register domain gateways
        config_gateway = ConfigGateway(
            get_logger=ug.get_logger,
            get_metrics=ug.get_metrics,
            call_operation=ug.execute_operation
        )
        ug.register_domain_gateway("config", config_gateway)

        # Execute operations
        result = ug.execute_operation(
            domain="config",
            interface="config",
            operation="get",
            key="database.host"
        )

    Cross-Domain Operations:
        Domains can call operations in other domains through the injected
        call_operation function. This enables clean separation while allowing
        necessary inter-domain communication.
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

        Example:
            ug = UniversalGateway(
                logger_factory=lambda name: logging.getLogger(f"EE.{name}"),
                metrics_factory=lambda name: PrometheusMetrics(name)
            )
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

### Example 3: Protocol with Comprehensive Docstring

```python
class LoggerFactory(Protocol):
    """Protocol for logger factory functions.

    The logger factory creates logger instances for components.

    Protocol Definition:
        Any callable with this signature satisfies the protocol:
        def __call__(self, name: str) -> logging.Logger

    Usage:
        # Lambda function
        factory = lambda name: logging.getLogger(f"App.{name}")

        # Regular function
        def create_logger(name: str) -> logging.Logger:
            return logging.getLogger(name)

        # Callable class
        class LoggerFactory:
            def __call__(self, name: str) -> logging.Logger:
                return logging.getLogger(name)

    Example:
        ug = UniversalGateway(
            logger_factory=lambda name: logging.getLogger(f"EE.{name}"),
            metrics_factory=metrics_factory
        )
    """
    def __call__(self, name: str) -> logging.Logger: ...
```

### Example 4: Method with Comprehensive Docstring

```python
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

        # Authenticate user
        auth_result = ug.execute_operation(
            domain="security",
            interface="auth",
            operation="authenticate",
            username="john",
            password="secret"
        )

        # Log message
        ug.execute_operation(
            domain="logging",
            interface="log",
            operation="info",
            message="Server started"
        )

    Cross-Domain Calls:
        Domains can call other domains through the call_operation parameter
        passed during gateway initialization:

        class MyDomainGateway:
            def __init__(self, call_operation):
                self._call_operation = call_operation

            def my_method(self):
                # Call another domain
                result = self._call_operation(
                    domain="config",
                    interface="config",
                    operation="get",
                    key="some.key"
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

## Docstring Sections Guide

### Essential Sections

1. **Summary (One-line)**
   - First line of docstring
   - Complete sentence ending with period
   - Concise description of purpose

2. **Detailed Description**
   - One or more paragraphs after summary
   - Explain what, why, and how
   - Blank line between summary and description

### Optional Sections (Use When Applicable)

3. **Architecture / Pattern**
   - Shows where this fits in system
   - Diagrams or flow descriptions
   - Design patterns used

4. **Key Principles / Features**
   - Bullet list of key characteristics
   - Design principles followed
   - Notable features

5. **Usage / Example**
   - Code examples showing typical use
   - Multiple examples for complex APIs
   - Show both basic and advanced usage

6. **Args / Parameters**
   - List method/function parameters
   - Include type and description
   - Optional parameters noted

7. **Returns**
   - Describe return value
   - Include type information
   - Note special cases (None, etc.)

8. **Raises**
   - List exceptions raised
   - Describe when each exception occurs
   - Include error conditions

9. **Thread Safety**
   - Note if class/method is thread-safe
   - Describe synchronization if any
   - Caveats for concurrent use

10. **Type Hints**
    - Notes on typing approach
    - Generic types explained
    - Forward references if used

## Best Practices

### 1. Be Specific and Complete

```python
# BAD - Too vague
def process(data):
    """Process data."""
    pass

# GOOD - Specific and complete
def process(data: dict[str, Any]) -> list[str]:
    """Process input data and extract string values.

    Args:
        data: Dictionary containing mixed-type values

    Returns:
        List of string values extracted from data

    Raises:
        ValueError: If data is not a dictionary
    """
```

### 2. Include Real Examples

```python
# GOOD - Copy-pasteable example
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value by key.

    Usage:
        # Get value with default
        host = get_config("database.host", "localhost")

        # Get value without default
        port = get_config("database.port")

    Args:
        key: Configuration key in dot notation
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
```

### 3. Document Thread Safety

```python
# GOOD - Clear thread safety documentation
class Cache:
    """Thread-safe in-memory cache.

    Thread Safety:
        All public methods are thread-safe and can be called
        concurrently from multiple threads.

        Uses internal RLock for synchronization.
        Read operations (get, has) don't block each other.
        Write operations (set, delete) are mutually exclusive.
    """
```

### 4. Show Architecture Context

```python
# GOOD - Shows place in architecture
"""
Domain Gateway - Base class for all domain gateways in UG architecture.

Architecture:
    UniversalGateway → DomainGateway → Interface → Operation

Each domain gateway manages interfaces within its domain and routes
operations to the appropriate interface implementations.
"""
```

### 5. Use Proper Formatting

```python
# GOOD - Consistent formatting
def complex_method(
    param1: str,
    param2: int,
    flag: bool = False
) -> dict[str, Any]:
    """Brief summary.

    Detailed description spanning
    multiple lines if needed.

    Args:
        param1: Description of param1
        param2: Description of param2
        flag: Description of flag (default: False)

    Returns:
        Dictionary containing:
            - 'status': str indicating result
            - 'value': processed value
            - 'errors': list of error messages

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer

    Example:
        >>> result = complex_method("test", 42, True)
        >>> print(result['status'])
        'success'
    """
```

## Cross-References

- **DEC-PY-01**: Protocol docstrings should explain structural subtyping
- **DEC-PY-02**: Use `from __future__ import annotations` for forward references in examples
- **Generic Principles**: Self-Documenting Code, Literate Programming

## Examples from EE Codebase

**Location:** `d:\Code\Project\EE\universal_gateway\gateway.py`

```python
"""
Universal Gateway (UG) - Central entry point for all EE operations.

This module provides the UniversalGateway class, which is the SINGLE entry
point for all operations in the EE system. The UG manages domain gateways
and provides dependency injection for cross-cutting concerns.

Architecture:
    Application Code
        ↓ execute_operation(domain, interface, operation, **kwargs)
    UniversalGateway (this module)
        ↓ get domain gateway
    DomainGateway
        ↓ execute domain operation
    Interface
        ↓ execute operation
    Implementation
...
"""
```

**Location:** `d:\Code\Project\EE\operations\object_pool\object_pool_factory.py`

```python
"""
Object Pool Factory - Operations Domain

Generic object pooling for resource management implementation.

Merges functionality from:
- EE/src/operations/object_pool/
- EE/src/object_pool/

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""
```

## Tools and Automation

### Generate Documentation

```python
# Use tools like:
# - Sphinx: http://www.sphinx-doc.org/
# - pdoc: https://pdoc.dev/
# - MkDocs: https://www.mkdocs.org/

# Install
pip install sphinx pdoc3

# Generate
sphinx-apidoc -o docs/ EE/
pdoc --html EE/ -o docs/
```

### Docstring Linters

```python
# pydocstyle: Check docstring style
pip install pydocstyle
pydocstyle EE/

# pylint: Check docstring coverage
pylint --disable=all --enable=missing-docstring EE/
```

## References

- PEP 257: Docstring Conventions
- PEP 287: reStructuredText Docstring Format
- Google Python Style Guide: Docstrings
- NumPy Docstring Guide
- https://docs.python.org/3/tutorial/controlflow.html#documentation-strings
