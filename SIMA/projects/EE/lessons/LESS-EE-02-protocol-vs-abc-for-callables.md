# LESS-EE-02: Protocol vs ABC for Callables

**Category:** Lesson Learned
**Status:** Production
**EE Version:** 2.0.0
**Last Updated:** 2025-12-31

---

## Overview

**Lesson:** Use `Protocol` for callable signatures and `ABC` for class interfaces.

**Problem:** How to define type-safe interfaces for dependency injection?

**Solution:**
- Use `Protocol` for factory functions and callable signatures
- Use `ABC` for domain gateway base classes
- Benefits: Duck typing with type safety, better IDE support, cleaner code

---

## The Pattern

### Protocol for Callables

```python
# EE/universal_gateway/gateway.py (lines 55-68)

class LoggerFactory(Protocol):
    """Protocol for logger factory functions."""
    def __call__(self, name: str) -> logging.Logger: ...

class MetricsFactory(Protocol):
    """Protocol for metrics factory functions."""
    def __call__(self, name: str) -> Any: ...

class OperationCaller(Protocol):
    """Protocol for operation call functions."""
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...
```

### ABC for Classes

```python
# EE/universal_gateway/domain_gateway.py (lines 137-351)

from abc import ABC, abstractmethod

class DomainGateway(ABC):
    """Base class for all domain gateways in UG architecture."""

    @abstractmethod
    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute an operation in this domain."""
        pass

    @abstractmethod
    def list_all(self) -> Dict[str, Any]:
        """List all interfaces in this domain."""
        pass
```

---

## When to Use Protocol vs ABC

### ✅ Use Protocol When:

1. **Defining callable signatures:**
   ```python
   class LoggerFactory(Protocol):
       def __call__(self, name: str) -> logging.Logger: ...
   ```

2. **Enforcing duck typing:**
   ```python
   # Any callable with matching signature works
   def my_logger_factory(name: str) -> logging.Logger:
       return logging.getLogger(name)

   factory: LoggerFactory = my_logger_factory  # ✅ Type-safe
   ```

3. **Working with functions:**
   ```python
   # Functions implement Protocol automatically
   def get_logger(name: str) -> logging.Logger:
       return logging.getLogger(name)

   factory: LoggerFactory = get_logger  # ✅ Type-safe
   ```

4. **Third-party compatibility:**
   ```python
   # External library function
   import external_lib
   factory: LoggerFactory = external_lib.create_logger  # ✅
   ```

### ✅ Use ABC When:

1. **Defining class interfaces:**
   ```python
   class DomainGateway(ABC):
       @abstractmethod
       def execute_domain_operation(self, interface: str, operation: str, **kwargs) -> Any:
           pass
   ```

2. **Providing base implementation:**
   ```python
   class DomainGateway(ABC):
       def __init__(self, domain_name: str, ...):
           self._domain_name = domain_name
           # Common initialization

       @abstractmethod
       def execute_domain_operation(self, ...):
           pass
   ```

3. **Enforcing inheritance:**
   ```python
   class MyGateway(DomainGateway):
       def execute_domain_operation(self, ...):
           pass  # Concrete implementation
   ```

---

## Benefits of Protocol for Callables

### 1. Duck Typing with Type Safety

```python
# Protocol - any callable with matching signature works
class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

# ✅ Functions, classes, lambdas all work
def my_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

lambda_logger = lambda name: logging.getLogger(name)

factory: LoggerFactory = my_logger  # ✅ Type-safe
factory: LoggerFactory = lambda_logger  # ✅ Type-safe
```

### 2. Third-Party Compatibility

```python
# Protocol works with external libraries
import structlog

# structlog.get_logger matches signature
factory: LoggerFactory = structlog.get_logger  # ✅ Works!
```

### 3. Cleaner Code

```python
# Protocol - simple function
def default_logger_factory(name: str) -> logging.Logger:
    return logging.getLogger(f"EE.{name}")

# Direct usage
ug = UniversalGateway(
    logger_factory=default_logger_factory,  # Clean!
    metrics_factory=default_metrics_factory,
)
```

---

## Real-World Examples from EE

### Example 1: Protocol for Factory Functions

```python
# EE/universal_gateway/gateway.py (lines 55-68)
class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

# EE/__init__.py (lines 82-92)
def _default_logger_factory(name: str) -> logging.Logger:
    """Default logger factory using Python's logging module."""
    return logging.getLogger(f"EE.{name}")

# Usage (accepts any callable with matching signature)
_ug = UniversalGateway(
    logger_factory=_default_logger_factory,  # ✅ Function works
    metrics_factory=_default_metrics_factory,
)
```

### Example 2: ABC for Domain Gateways

```python
# EE/universal_gateway/domain_gateway.py (lines 137-231)
from abc import ABC, abstractmethod

class DomainGateway(ABC):
    """Base class for all domain gateways."""

    def __init__(
        self,
        domain_name: str,
        get_logger: LoggerFactory,  # Protocol type
        get_metrics: MetricsFactory,  # Protocol type
        call_operation: OperationCaller,  # Protocol type
    ) -> None:
        self._domain_name = domain_name
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation

    @abstractmethod
    def execute_domain_operation(self, interface: str, operation: str, **kwargs) -> Any:
        """Execute an operation in this domain."""
        pass
```

---

## Type Safety Comparison

**Protocol (Structural Typing):**
```python
class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

# Any callable with matching signature works
factory: LoggerFactory = lambda name: logging.getLogger(name)  # ✅
```

**ABC (Nominal Typing):**
```python
class LoggerFactory(ABC):
    @abstractmethod
    def __call__(self, name: str) -> logging.Logger:
        pass

# Only explicit subclasses work
factory: LoggerFactory = my_logger  # ❌ Type error!
factory: LoggerFactory = MyLoggerFactory()  # ✅ Works
```

---

## Best Practices

### ✅ Best Practice 1: Protocol for Callables

```python
# DO: Use Protocol for factory functions
from typing import Protocol

class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

class MetricsFactory(Protocol):
    def __call__(self, name: str) -> Any: ...

# Use in type hints
def create_ug(
    logger_factory: LoggerFactory,
    metrics_factory: MetricsFactory,
) -> UniversalGateway:
    return UniversalGateway(
        logger_factory=logger_factory,
        metrics_factory=metrics_factory,
    )
```

### ✅ Best Practice 2: ABC for Classes

```python
# DO: Use ABC for base classes
from abc import ABC, abstractmethod

class DomainGateway(ABC):
    """Base class for domain gateways."""

    @abstractmethod
    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute operation in this domain."""
        pass

    @abstractmethod
    def list_all(self) -> Dict[str, Any]:
        """List all interfaces."""
        pass
```

### ✅ Best Practice 3: Combine Protocol and ABC

```python
# DO: Use Protocol for callable parameters in ABC classes
class DomainGateway(ABC):
    def __init__(
        self,
        domain_name: str,
        get_logger: LoggerFactory,  # Protocol
        get_metrics: MetricsFactory,  # Protocol
        call_operation: OperationCaller,  # Protocol
    ):
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation

    @abstractmethod
    def execute_domain_operation(self, ...):
        pass
```

### ✅ Best Practice 4: Runtime Callable Check

```python
# DO: Validate callables at runtime
class UniversalGateway:
    def __init__(
        self,
        logger_factory: LoggerFactory,
        metrics_factory: MetricsFactory,
    ):
        if not callable(logger_factory):
            raise TypeError("logger_factory must be callable")
        if not callable(metrics_factory):
            raise TypeError("metrics_factory must be callable")
```

---

## Common Mistakes

### ❌ Mistake 1: Using ABC for Callables

```python
# DON'T: Use ABC for factory functions
from abc import ABC, abstractmethod

class LoggerFactory(ABC):
    @abstractmethod
    def __call__(self, name: str) -> logging.Logger:
        pass

# Problem: Functions don't work
def my_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

factory: LoggerFactory = my_logger  # ❌ Type error!
```

**Fix: Use Protocol**

```python
# DO: Use Protocol for callables
from typing import Protocol

class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger: ...

factory: LoggerFactory = my_logger  # ✅ Works!
```

### ❌ Mistake 2: Using Protocol for Class Hierarchies

```python
# DON'T: Use Protocol when you need base implementation
from typing import Protocol

class DomainGateway(Protocol):
    def execute_domain_operation(self, interface: str, operation: str, **kwargs) -> Any: ...

# Problem: Can't provide common implementation
class FoundationGateway(DomainGateway):
    pass  # No common methods available!
```

**Fix: Use ABC**

```python
# DO: Use ABC for class hierarchies
from abc import ABC, abstractmethod

class DomainGateway(ABC):
    def __init__(self, domain_name: str):
        self._domain_name = domain_name

    @abstractmethod
    def execute_domain_operation(self, ...):
        pass

# Inherits __init__ and common methods
class FoundationGateway(DomainGateway):
    def execute_domain_operation(self, ...):
        pass
```

---

## Decision Tree

```
Need to define interface type?
│
├─ Is it a callable (function)?
│  └─ YES → Use Protocol (duck typing, functions work)
│
└─ Is it a class?
   └─ Need base implementation?
      ├─ YES → Use ABC (shared methods, enforced inheritance)
      └─ NO → Use Protocol (structural typing, third-party compatible)
```

---

## Related Patterns

- **GATE-EE-01:** UniversalGateway class (ABC usage)
- **LESS-EE-01:** Module-level singleton (Protocol in factories)
- **DEC-EE-01:** DISPATCH pattern (Protocol for factories)

---

## References

- **UG Implementation:** `d:\Code\Project\EE\universal_gateway\gateway.py`
- **DomainGateway ABC:** `d:\Code\Project\EE\universal_gateway\domain_gateway.py`
- **Python Protocols:** PEP 544 - Structural subtyping (static duck typing)
- **Python ABC:** https://docs.python.org/3/library/abc.html
