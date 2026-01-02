# DEC-EE-02: DI-Mandatory Architecture

**Category:** Architecture Decision
**Status:** Active (EE 2.1)
**EE Version:** 2.1
**Date:** 2025-12-31
**REF-ID:** DEC-EE-02
**Supersedes:** All direct import patterns

---

## Decision

**Dependency Injection (DI) is MANDATORY for all cross-cutting concerns. No direct imports of logging, metrics, or config modules allowed.**

---

## Context

Previous EE versions allowed direct imports:
```python
import logging  # ❌ NOW FORBIDDEN
from some_config import get_config  # ❌ NOW FORBIDDEN
```

This created:
- Tight coupling to implementations
- Difficult to test
- Hard to swap implementations
- Implicit dependencies

---

## Decision Details

### Chosen Approach: Constructor Injection

```python
class ExampleFactory:
    def __init__(
        self,
        logger: logging.Logger,  # ← Injected
        metrics: Any,  # ← Injected
        config: Any,  # ← Injected
        call_operation: Callable,  # ← Injected
    ):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation
```

### Injection Flow

```
UniversalGatewayFactory
    ↓ constructs
UniversalGateway
    ↓ injects
DomainGateway
    ↓ injects
Interface
    ↓ injects
Factory
```

### Required Injections

All components MUST receive:
1. `get_logger: Callable` - Logger factory
2. `get_metrics: Callable` - Metrics factory
3. `get_config: Callable` - Config getter
4. `call_operation: Callable` - Cross-domain caller

---

## Benefits

1. **Testability**
   - Can inject mock logger
   - Can inject mock metrics
   - Can inject test config

2. **Flexibility**
   - Can swap implementations
   - Can configure per-environment
   - Can disable in tests

3. **Explicit Dependencies**
   - Clear what each component needs
   - No hidden imports
   - Easy to understand

---

## Enforcement

### ✅ ALLOWED:

```python
class MyFactory:
    def __init__(self, logger, metrics, config, call_operation):
        self._logger = logger  # ✅ Injected
        self._metrics = metrics  # ✅ Injected
        self._config = config  # ✅ Injected
```

### ❌ FORBIDDEN:

```python
import logging  # ❌ Direct import
from EE.observability.logging import get_logger  # ❌ Cross-domain import

class MyFactory:
    def __init__(self):
        self._logger = logging.getLogger(__name__)  # ❌ Direct creation
```

---

## Related Decisions

- **DEC-EE-01:** Factory-Driven UG Construction
- **DEC-EE-03:** Uniform Gateway Constructors
- **AP-EE-04:** Cross-Domain Imports

---

**END OF DEC-EE-02**
