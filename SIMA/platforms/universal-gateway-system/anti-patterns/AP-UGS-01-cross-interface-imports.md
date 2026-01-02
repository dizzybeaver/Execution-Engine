# AP-UGS-01: Cross-Interface Imports

**ID:** AP-UGS-01
**Platform:** Universal Gateway System (UGS)
**Severity:** Critical
**Category:** Architecture Violation
**Status:** Enforced
**Last Updated:** 2025-12-31

---

## OVERVIEW

Importing from one interface into another interface creates tight coupling and violates the core UG principle of **Interface Isolation**. This anti-pattern breaks the architecture's modular design and creates dependency chains that are difficult to maintain.

**UGS Principle Violated:**
- Interface Isolation (Section 1.2, UG Architecture Guide)

---

## THE ANTI-PATTERN

### Wrong Way: Direct Cross-Interface Imports

```python
# EE/networking/http_client/http_factory.py

# ✗ VIOLATION: Importing from another interface
from ..websocket_client.websocket_factory import WebSocketFactory

class HttpFactory:
    """HTTP client factory."""

    @staticmethod
    def execute_get(**kwargs):
        """Execute HTTP GET request."""
        # ✗ VIOLATION: Directly calling another interface
        ws = WebSocketFactory()
        ws.connect(**kwargs)

        # Make HTTP request...
        return response
```

### Why This Is Wrong

1. **Tight Coupling:** HTTP interface now depends on WebSocket interface
2. **Circular Dependencies:** WebSocket might also import HTTP, creating cycles
3. **Bypasses UG:** Routing goes direct, bypassing gateway governance
4. **Testing Hell:** Cannot test HTTP without WebSocket present
5. **Deployment Issues:** Cannot deploy interfaces independently

---

## THE CORRECT PATTERN

### Right Way: Use UG for Cross-Domain Calls

```python
# EE/networking/http_client/http_factory.py

class HttpFactory:
    """HTTP client factory with dependency injection."""

    def __init__(self, logger=None, metrics=None, call_operation=None):
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def execute_get(self, **kwargs):
        """Execute HTTP GET request."""
        # ✓ CORRECT: Use injected callback for cross-domain calls
        if self._call_operation:
            # Call through UG to websocket interface
            ws_result = self._call_operation(
                domain="networking",
                interface="websocket",
                operation="connect",
                **kwargs
            )

        # Make HTTP request...
        return response
```

### Key Points

1. **Dependency Injection:** `call_operation` callback injected by domain gateway
2. **UG Routing:** All cross-interface calls go through UG
3. **Loose Coupling:** HTTP interface only knows the operation contract
4. **Testability:** Can inject mock `call_operation` for testing
5. **Governance:** UG can log, meter, and control cross-domain traffic

---

## IMPACT AND CONSEQUENCES

### Immediate Impact

| Impact | Description | Severity |
|--------|-------------|----------|
| Architecture Violation | Breaks UG isolation principle | Critical |
| Tight Coupling | Creates unmanaged dependencies | High |
| Test Complexity | Requires full dependency chain | High |
| Reusability Loss | Cannot use interface independently | Medium |

### Long-Term Consequences

1. **Unmaintainable Code:**
   - Changes in one interface ripple to others
   - Cannot understand interface behavior in isolation
   - Code becomes spaghetti over time

2. **Deployment Failures:**
   - Cannot deploy interfaces independently
   - All-or-nothing deployments required
   - Increased risk during deployments

3. **Testing Nightmares:**
   - Unit tests require full interface stack
   - Mocking becomes complex
   - Test suites become slow and brittle

4. **Performance Degradation:**
   - Bypasses UG optimizations (caching, pooling, etc.)
   - Direct calls miss observability hooks
   - Cannot apply cross-cutting concerns

---

## DETECTION

### Automated Detection

```python
# Scanner can detect this pattern
violations = execute_operation(
    domain='scanner',
    interface='validation',
    operation='check_imports',
    path='EE/',
    rules={
        'forbid_cross_interface_imports': True,
        'allow_same_interface': True,
        'allow_stdlib': True
    }
)
```

### Manual Detection Signs

1. Import statements referencing sibling interfaces
2. Direct instantiation of other interface factories
3. Interface code that knows implementation details of others
4. Tests that require multiple interfaces loaded

---

## COMPLIANCE REQUIREMENTS

### UG-ISP Compliance Rules

From UG Architecture Guide Section 8.1:

**Allowed imports in interfaces/factories:**
```python
# ✓ Allowed: Same interface imports
from .factory import SomeFactory
from .models import DataModel

# ✓ Allowed: Standard library
import json
from typing import Dict, Any
```

**NOT Allowed:**
```python
# ✗ NOT Allowed: Cross-interface imports
from other_interface.factory import OtherFactory  # ERROR

# ✗ NOT Allowed: Domain gateway imports
from EE.networking.networking_gateway import NetworkingGateway  # ERROR

# ✗ NOT Allowed: UG imports
from EE.universal_gateway.gateway import UniversalGateway  # ERROR
```

### Enforcement

1. **Pre-commit Hooks:** Block commits with cross-interface imports
2. **CI/CD Pipeline:** Run scanner on every PR
3. **Code Review:** Check for import violations
4. **Architecture Review:** Quarterly audits of import patterns

---

## EXCEPTIONS

**No exceptions exist.** This is a zero-tolerance rule for UG architecture.

---

## REMEDIATION

### Fix Existing Violations

1. **Identify violations:**
   ```bash
   python -m scanner.ug.validation check_imports EE/
   ```

2. **Refactor to DI pattern:**
   - Add `call_operation` parameter to factory `__init__`
   - Replace direct imports with `call_operation()` calls
   - Update domain gateway to inject `call_operation`

3. **Verify fix:**
   ```bash
   python -m scanner.ug.validation verify EE/
   ```

4. **Add tests:**
   - Unit tests with mock `call_operation`
   - Integration tests with real UG

---

## RELATED PATTERNS

- **Correct Pattern:** AP-UGS-02 (Import Isolation Violation)
- **Correct Pattern:** DISPATCH Pattern (Section 1.3, UG Guide)
- **Correct Pattern:** Dependency Injection (Section 4.3, UG Guide)

---

## EXAMPLES FROM UG GUIDE

### Violation Example (From EE Legacy)

```python
# ✗ VIOLATION: Legacy EE code
# EE/networking/http_client/http_factory.py

from ..websocket_client.websocket_factory import WebSocketFactory
from ..protocols.redis import RedisClient
from ..security.authentication.auth_factory import AuthFactory

class HttpFactory:
    def make_request(self, **kwargs):
        ws = WebSocketFactory()  # Bypasses UG
        redis = RedisClient()     # Bypasses UG
        auth = AuthFactory()      # Bypasses UG

        # Direct usage creates tight coupling
        auth.authenticate()
        ws.connect()
        data = redis.get('cache_key')
```

### Correct Implementation (EE 2.0)

```python
# ✓ CORRECT: EE 2.0 implementation
# EE/networking/http_client/http_factory.py

class HttpFactory:
    def __init__(self, logger=None, metrics=None, call_operation=None):
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def make_request(self, **kwargs):
        # All cross-domain calls through UG
        self._call_operation(
            domain="security",
            interface="authentication",
            operation="authenticate",
            **kwargs
        )

        ws_info = self._call_operation(
            domain="networking",
            interface="websocket",
            operation="connect",
            **kwargs
        )

        data = self._call_operation(
            domain="networking",
            interface="protocols",
            operation="redis_get",
            key='cache_key'
        )
```

---

## CHECKLIST FOR COMPLIANCE

- [ ] No imports from other interfaces
- [ ] No imports from domain gateways
- [ ] No imports from UG itself
- [ ] Dependency injection used for cross-domain calls
- [ ] All external dependencies injected via constructor
- [ ] Scanner validation passes
- [ ] Unit tests mock `call_operation`
- [ ] Code review approved

---

## REFERENCES

- **UG Architecture Guide:** Section 1.2 (Interface Isolation)
- **UG Architecture Guide:** Section 8.1 (Import Isolation Rules)
- **UG Architecture Guide:** Section 4.3 (Factory Implementation Pattern)
- **EE 2.0:** `/d/Code/Project/EE/` (Reference implementation)

---

**Entry ID:** AP-UGS-01
**Lines:** 298
**Status:** Active - Enforced
**Next Review:** 2026-01-31
