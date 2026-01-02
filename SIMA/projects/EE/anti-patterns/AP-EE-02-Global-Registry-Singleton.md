# AP-EE-02: Global Registry Singleton

**Category:** Anti-Pattern
**Type:** Architecture Pattern
**Severity:** CRITICAL
**Scope:** EE Architecture
**REF-ID:** AP-EE-02
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Global registry singleton prevents proper dependency injection** and breaks testability. EE 2.1 uses DI-injected DomainRegistry constructed by UniversalGatewayFactory.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Global Registry Singleton

```python
# EE 2.0 Legacy Pattern
class EEDomainRegistry:
    _instance = None

    @classmethod
    def get_instance(cls) -> 'EEDomainRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Problems:**
1. Global state prevents testing
2. Cannot create isolated registries
3. Violates dependency injection
4. Cannot mock registry in tests
5. Difficult to manage lifecycle

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: DI-Injected DomainRegistry

```python
# EE 2.1 Pattern
class DomainRegistry:
    def __init__(self):
        self._domains = {}

    def register(self, domain_name: str, builder):
        self._domains[domain_name] = builder

    def resolve(self, domain_name: str):
        if domain_name not in self._domains:
            raise DomainNotFoundError(domain_name)
        return self._domains[domain_name]()

# Factory constructs and injects
class UniversalGatewayFactory:
    def __init__(self):
        self._domain_registry = self._build_registry()

    def build_gateway(self):
        return UniversalGateway(
            domain_registry=self._domain_registry,
            ...
        )
```

**Benefits:**
- Proper dependency injection
- Testable (can inject mock registry)
- Can create isolated registries
- Clear lifecycle management
- Factory-based construction

---

## Enforcement

### Must Use:
1. DomainRegistry constructed by factory
2. Registry injected into UG
3. Registry passed to DomainGatewayFactory

### Must NOT Use:
1. `EEDomainRegistry.get_instance()`
2. Static registry singleton
3. Global registry variable
4. Module-level registry initialization

---

## Related Patterns

- **AP-EE-01:** Global UG Singleton
- **AP-EE-03:** Mixed Gateway Constructors
- **ARCH-EE-03:** DomainRegistry Pattern

---

**END OF AP-EE-02**
