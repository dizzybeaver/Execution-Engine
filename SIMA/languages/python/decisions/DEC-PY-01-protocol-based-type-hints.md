# DEC-PY-01: Protocol-Based Type Hints

**Status:** Accepted
**Date:** 2025-12-31
**Context:** EE codebase type system design
**Applies to:** All Python modules requiring type-safe interfaces

---

## Decision

Use `typing.Protocol` for structural subtyping instead of abstract base classes or nominal inheritance.

## Rationale

### Benefits

1. **Duck Typing with Type Safety**: Protocols provide structural subtyping, allowing any object with matching methods to satisfy the type, while still enabling static type checking
2. **Flexible Dependency Injection**: Factories and callbacks can be typed without requiring concrete class inheritance
3. **Better IDE Support**: Type checkers (mypy, pyright) can verify protocol conformance without runtime overhead
4. **Clean Separation**: Interfaces defined by behavior rather than inheritance hierarchy

### Comparison

**Nominal Typing (ABC):**
```python
from abc import ABC, abstractmethod

class LoggerFactory(ABC):
    @abstractmethod
    def __call__(self, name: str) -> logging.Logger:
        pass

# Must inherit from LoggerFactory
class MyLogger(LoggerFactory):
    def __call__(self, name: str) -> logging.Logger:
        return logging.getLogger(name)
```

**Structural Typing (Protocol):**
```python
from typing import Protocol

class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

# Any callable with matching signature works
def my_logger_factory(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Or a class
class MyLogger:
    def __call__(self, name: str) -> logging.Logger:
        return logging.getLogger(name)
```

## Implementation

### Pattern Definition

```python
from __future__ import annotations
from typing import Protocol, Any, Callable
import logging

# Define protocol with complete type signatures
class LoggerFactory(Protocol):
    """Protocol for logger factory functions.

    Any object with a __call__ method matching this signature
    satisfies the protocol.
    """
    def __call__(self, name: str) -> logging.Logger: ...


class MetricsFactory(Protocol):
    """Protocol for metrics factory functions."""
    def __call__(self, name: str) -> Any: ...


class OperationCaller(Protocol):
    """Protocol for cross-domain operation calls."""
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...
```

### Usage in Classes

```python
class UniversalGateway:
    """Universal Gateway with protocol-based dependency injection."""

    def __init__(
        self,
        logger_factory: LoggerFactory,
        metrics_factory: MetricsFactory,
    ) -> None:
        """Initialize with protocol-typed dependencies.

        Any object satisfying the protocol works:
        - Functions with matching signature
        - Classes with __call__ method
        - Lambda expressions
        """
        if logger_factory is None:
            raise ValueError("logger_factory cannot be None")

        self._logger_factory: LoggerFactory = logger_factory
        self._metrics_factory: MetricsFactory = metrics_factory

    def get_logger(self, name: str) -> logging.Logger:
        """Get logger using injected factory."""
        return self._logger_factory(name)
```

### Instantiation Examples

```python
# Option 1: Lambda function
ug = UniversalGateway(
    logger_factory=lambda name: logging.getLogger(f"EE.{name}"),
    metrics_factory=lambda name: MyMetrics(name)
)

# Option 2: Function
def create_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"EE.{name}")

ug = UniversalGateway(
    logger_factory=create_logger,
    metrics_factory=create_metrics
)

# Option 3: Callable class
class LoggerFactory:
    def __call__(self, name: str) -> logging.Logger:
        return logging.getLogger(f"EE.{name}")

ug = UniversalGateway(
    logger_factory=LoggerFactory(),
    metrics_factory=MetricsFactory()
)
```

## Protocol Design Guidelines

### 1. Complete Type Signatures

```python
# GOOD - Complete signature
class DataProcessor(Protocol):
    def process(self, data: dict[str, Any]) -> list[str]: ...

# BAD - Missing return type
class DataProcessor(Protocol):
    def process(self, data: dict[str, Any]): ...
```

### 2. Use Ellipsis for Protocol Bodies

```python
# GOOD - Ellipsis indicates protocol
class Validator(Protocol):
    def validate(self, value: str) -> bool: ...

# ACCEPTABLE - Pass also works
class Validator(Protocol):
    def validate(self, value: str) -> bool:
        pass
```

### 3. Protocol Attributes

```python
class Configurable(Protocol):
    """Protocol for objects with configuration."""
    config: dict[str, Any]
    def reload(self) -> None: ...

class MyConfig:
    def __init__(self):
        self.config = {}
    def reload(self) -> None:
        pass

# MyConfig satisfies Configurable
```

### 4. Generic Protocols

```python
from typing import TypeVar, Protocol

T = TypeVar('T')

class Factory(Protocol[T]):
    """Generic factory protocol."""
    def create(self, **kwargs) -> T: ...

class ConnectionFactory:
    def create(self, host: str = "localhost") -> Connection:
        return Connection(host)
```

## Type Checking

### Verify Protocol Conformance

```python
# mypy will verify these at type-check time
def verify_factory(factory: LoggerFactory) -> None:
    """Verify factory satisfies protocol."""
    # Type checker ensures factory has correct signature
    pass

# These pass type checking:
verify_factory(lambda name: logging.getLogger(name))
verify_factory(logging.getLogger)

# These fail type checking:
verify_factory("not a callable")  # Error: not callable
verify_factory(lambda x: x)  # Error: wrong signature
```

## When to Use Protocols

### Use Protocols When:
- Defining dependency injection interfaces
- Creating callback types
- Specifying factory contracts
- Enforcing duck typing with type safety
- Designing plugin interfaces

### Use ABCs When:
- You need runtime isinstance() checks
- There's shared implementation code
- You want to prevent protocol satisfaction by unrelated types
- Building strict class hierarchies

## Cross-References

- **DEC-PY-02**: Combine with `from __future__ import annotations` for forward references
- **LESS-PY-01**: Module-level state patterns work with protocol-based injection
- **Generic Principles**: Interface Segregation Principle (ISP), Dependency Inversion Principle (DIP)

## Examples from EE Codebase

**Location:** `d:\Code\Project\EE\universal_gateway\gateway.py`

```python
class LoggerFactory(Protocol):
    """Protocol for logger factory functions."""
    def __call__(self, name: str) -> logging.Logger: ...

class MetricsFactory(Protocol):
    """Protocol for metrics factory functions."""
    def __call__(self, name: str) -> Any: ...

class UniversalGateway:
    def __init__(
        self,
        logger_factory: LoggerFactory,
        metrics_factory: MetricsFactory,
    ) -> None:
        # Any callable satisfying protocol works
        self._logger_factory = logger_factory
        self._metrics_factory = metrics_factory
```

**Location:** `d:\Code\Project\EE\universal_gateway\domain_gateway.py`

```python
class OperationCaller(Protocol):
    """Protocol for operation call functions."""
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...

class DomainGateway:
    def __init__(
        self,
        domain_name: str,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        call_operation: OperationCaller,
    ) -> None:
        # Protocol-based dependency injection
        self._call_operation = call_operation
```

## References

- PEP 544: Protocols: Structural subtyping (static duck typing)
- https://docs.python.org/3/library/typing.html#typing.Protocol
- https://mypy.readthedocs.io/en/stable/protocols.html
