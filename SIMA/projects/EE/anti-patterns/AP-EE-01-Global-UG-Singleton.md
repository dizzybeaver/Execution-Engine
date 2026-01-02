# AP-EE-01: Global UG Singleton

**Category:** Anti-Pattern
**Type:** Architecture Pattern
**Severity:** CRITICAL
**Scope:** EE Architecture
**REF-ID:** AP-EE-01
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Global UG singleton violates horizontal scalability** and prevents proper dependency injection. EE 2.1 uses factory-based UG construction with optional pooling instead.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Global UG Singleton

```python
# EE/__init__.py - EE 2.0 Legacy Pattern
_ug: Optional[UniversalGateway] = None

def get_ug() -> UniversalGateway:
    global _ug
    if _ug is None:
        _ug = UniversalGateway(...)
    return _ug
```

**Problems:**
1. Not horizontally scalable
2. Cannot create isolated UG instances
3. Difficult to test (global state)
4. Cannot pool UG instances
5. Violates dependency injection principles

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: UniversalGatewayFactory + Optional Pool

```python
# EE/__init__.py - EE 2.1 Pattern
from .universal_gateway.gateway_factory import UniversalGatewayFactory

_ug_factory = UniversalGatewayFactory()
_ug_pool = []

def _get_ug():
    if _ug_pool:
        return _ug_pool.pop()
    return _ug_factory.build_gateway()

def _return_ug(ug):
    _ug_pool.append(ug)

def execute_operation(domain, interface, operation, **kwargs):
    ug = _get_ug()
    try:
        return ug.execute_operation(domain, interface, operation, **kwargs)
    finally:
        _return_ug(ug)
```

**Benefits:**
- Horizontally scalable (multiple UG instances)
- Can pool UG instances for performance
- Properly testable (can inject factory)
- Follows dependency injection principles
- Factory-based construction

---

## Enforcement

### Must Use:
1. UniversalGatewayFactory for UG construction
2. Optional UG pool for reuse
3. DI-injected registry and factories

### Must NOT Use:
1. Global `_ug` singleton variable
2. `get_ug()` singleton accessor pattern
3. Static UG instance
4. Module-level UG initialization

---

## Related Patterns

- **AP-EE-02:** Global Registry Singleton
- **AP-EE-03:** Mixed Gateway Constructors
- **AP-EE-04:** Direct Cross-Domain Imports
- **ARCH-EE-02:** UniversalGatewayFactory Pattern

---

**END OF AP-EE-01**
