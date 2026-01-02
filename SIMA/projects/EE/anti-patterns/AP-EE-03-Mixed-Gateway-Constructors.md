# AP-EE-03: Mixed Gateway Constructors

**Category:** Anti-Pattern
**Type:** Architecture Pattern
**Severity:** HIGH
**Scope:** EE Domain Gateways
**REF-ID:** AP-EE-03
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Mixed gateway constructor signatures prevent uniform construction** and break the DomainGatewayFactory pattern. EE 2.1 requires ALL domain gateways to use the same constructor signature.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Mixed Constructor Signatures

```python
# Different gateways with different constructors
class ConfigGateway:
    def __init__(self, config_path):  # ❌ Wrong
        ...

class SecurityGateway:
    def __init__(self, auth_provider, encryption_key):  # ❌ Wrong
        ...

class NetworkingGateway:
    def __init__(self, logger, metrics, pool_size):  # ❌ Wrong
        ...
```

**Problems:**
1. Cannot use uniform DomainGatewayFactory
2. Inconsistent DI patterns
3. Difficult to maintain
4. Violates uniform architecture principle
5. Prevents gateway pooling

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: Uniform Constructor Signature

```python
# EE 2.1 - ALL gateways MUST use this signature
class DomainGateway(ABC):
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        self._domain_name = domain_name
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

# Every domain gateway follows this pattern
class NetworkingGateway(DomainGateway):
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        super().__init__(domain_name, get_logger, get_metrics, get_config, call_operation)
        self._interfaces = {}
```

**Benefits:**
- Uniform DomainGatewayFactory can build any gateway
- Consistent DI across all domains
- Proper gateway pooling
- Easier to maintain and extend
- Clear architectural pattern

---

## Enforcement

### Must Use:
1. Standard 5-parameter constructor
2. Domain name as first parameter
3. Callable factories for logger, metrics, config
4. call_operation for cross-domain calls

### Must NOT Use:
1. Custom constructor parameters
2. Domain-specific constructor signatures
3. Direct injection of loggers/metrics (use callables)
4. Omitted call_operation parameter

---

## Related Patterns

- **AP-EE-01:** Global UG Singleton
- **AP-EE-02:** Global Registry Singleton
- **ARCH-EE-04:** Uniform Gateway Construction

---

**END OF AP-EE-03**
