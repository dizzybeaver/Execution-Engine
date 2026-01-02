# AP-EE-05: Interface Logic

**Category:** Anti-Pattern
**Type:** Architecture Pattern
**Severity:** HIGH
**Scope:** EE Domain Interfaces
**REF-ID:** AP-EE-05
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Business logic in interfaces breaks the factory execution pattern** and makes code difficult to test and maintain. EE 2.1 enforces that interfaces are thin routers and factories contain ALL logic.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Logic in Interfaces

```python
# EE/security/authentication/interface.py
class AuthenticationInterface:
    def verify_password(self, password: str, hash: str) -> bool:
        # ❌ WRONG - Logic in interface
        salt = hash[:32]
        stored_hash = hash[32:]
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return new_hash == stored_hash
```

**Problems:**
1. Interface contains business logic
2. Difficult to test (can't mock factory)
3. Cannot reuse logic outside interface
4. Violates single responsibility principle
5. Interface should only ROUTE to factory

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: Interface Routes, Factory Executes

```python
# EE/security/authentication/interface.py
class AuthenticationInterface:
    def __init__(
        self,
        logger: logging.Logger,
        metrics: Any,
        config: Any,
        call_operation: Callable,
    ):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation
        self._factory_pool = []  # Pool of factory instances

    def _get_factory(self):
        if self._factory_pool:
            return self._factory_pool.pop()
        from .authentication_factory import AuthenticationFactory
        return AuthenticationFactory(
            logger=self._logger,
            metrics=self._metrics,
            config=self._config,
            call_operation=self._call_operation,
        )

    def _return_factory(self, factory):
        self._factory_pool.append(factory)

    def verify_password(self, password: str, hash: str) -> bool:
        """✅ CORRECT - Interface only routes to factory"""
        factory = self._get_factory()
        try:
            return factory.verify_password(password, hash)
        finally:
            self._return_factory(factory)

# EE/security/authentication/factory.py
class AuthenticationFactory:
    def verify_password(self, password: str, hash: str) -> bool:
        """✅ ALL logic is in factory"""
        salt = hash[:32]
        stored_hash = hash[32:]
        new_hash = hashlib.pbkdf2_hmac(...)
        return new_hash == stored_hash
```

**Benefits:**
- Interfaces are thin routers (maintain pools, route calls)
- Factories contain ALL business logic
- Factories can be tested independently
- Factories can be reused outside interface
- Clear separation of concerns

---

## Interface Responsibilities (EE 2.1)

### ✅ Interface MAY:
1. Maintain factory pool
2. Route operations to factories
3. Acquire/return factories from pool
4. Map operation names to factory methods
5. Handle minimal routing logic

### ❌ Interface MUST NOT:
1. Implement business logic
2. Perform calculations
3. Make external calls directly
4. Handle data transformations
5. Contain algorithms

---

## Factory Responsibilities (EE 2.1)

### ✅ Factory MUST:
1. Implement ALL business logic
2. Perform calculations
3. Make external calls (via call_operation)
4. Handle data transformations
5. Contain algorithms
6. Maintain client pools (HTTP sessions, DB connections, etc.)

---

## Enforcement

### Interface Pattern:
```python
def execute_operation(self, operation: str, **kwargs):
    factory = self._get_factory()
    try:
        if operation == "get":
            return factory.get(**kwargs)
        if operation == "post":
            return factory.post(**kwargs)
        raise InvalidOperationError(operation)
    finally:
        self._return_factory(factory)
```

### Factory Pattern:
```python
def get(self, url: str, **kwargs):
    """ALL logic here"""
    # Build request
    # Make HTTP call
    # Handle response
    # Return result
```

---

## Related Patterns

- **AP-EE-04:** Cross-Domain Imports
- **AP-EE-06:** Factory Cross-Domain Imports
- **ARCH-EE-06:** Factory Execution Pattern

---

**END OF AP-EE-05**
