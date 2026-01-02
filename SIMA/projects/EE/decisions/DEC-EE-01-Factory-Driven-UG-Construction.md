# DEC-EE-01: Factory-Driven UG Construction

**Category:** Architecture Decision
**Status:** Active (EE 2.1)
**EE Version:** 2.1
**Date:** 2025-12-31
**REF-ID:** DEC-EE-01
**Supersedes:** All legacy UG construction patterns

---

## Decision

**UniversalGateway MUST be constructed via UniversalGatewayFactory, not global singleton.**

---

## Context

EE 2.0 used a global UG singleton pattern that:
- Prevented horizontal scaling
- Made testing difficult
- Violated dependency injection principles
- Could not create isolated UG instances

---

## Decision Details

### Chosen Approach: UniversalGatewayFactory

```python
class UniversalGatewayFactory:
    def __init__(self):
        self._logger_factory = LoggerFactory()
        self._metrics_factory = MetricsFactory()
        self._config_service = ConfigService()
        self._domain_registry = self._build_registry()
        self._domain_gateway_factory = DomainGatewayFactory(...)

    def build_gateway(self) -> UniversalGateway:
        return UniversalGateway(
            logger_factory=self._logger_factory,
            metrics_factory=self._metrics_factory,
            config_service=self._config_service,
            domain_registry=self._domain_registry,
            domain_gateway_factory=self._domain_gateway_factory,
        )
```

### Benefits

1. **Horizontal Scalability**
   - Can create multiple UG instances
   - Each instance can have different configuration
   - Supports multi-tenant deployments

2. **Dependency Injection**
   - All dependencies explicit
   - Easy to test with mocks
   - Clear dependency graph

3. **Optional Pooling**
   - Can pool UG instances for performance
   - Pool size configurable
   - Safe reuse of instances

4. **Testability**
   - Can inject mock factories
   - Can create test-specific UG instances
   - No global state to reset

---

## Consequences

### Positive

- Scalable architecture
- Testable code
- Clear dependencies
- No global state
- Pool-capable

### Negative

- More verbose construction
- Requires factory class
- More code paths to understand

---

## Alternatives Considered

1. **Global Singleton (EE 2.0)**
   - Rejected: Not scalable, hard to test

2. **Service Locator Pattern**
   - Rejected: Still global, implicit dependencies

3. **Context Manager Pattern**
   - Rejected: Adds complexity, not async-safe

---

## Implementation

All code MUST:
1. Use UniversalGatewayFactory to construct UG
2. Inject factory into EE/__init__.py
3. Support optional UG pooling
4. Never use global UG singleton

---

## Related Decisions

- **DEC-EE-02:** DomainGatewayFactory Pattern
- **DEC-EE-03:** DI-Mandatory Architecture
- **DEC-EE-04:** Uniform Gateway Constructors

---

**END OF DEC-EE-01**
