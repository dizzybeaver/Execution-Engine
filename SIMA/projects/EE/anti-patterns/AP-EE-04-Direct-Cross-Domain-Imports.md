# AP-EE-04: Direct Cross-Domain Imports

**Category:** Anti-Pattern
**Type:** Import Pattern
**Severity:** CRITICAL
**Scope:** EE Domain Interfaces
**REF-ID:** AP-EE-04
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Direct cross-domain imports violate interface isolation** and break UG architecture. EE 2.1 enforces strict interface isolation - interfaces may ONLY import from their own interface directory.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Cross-Domain Imports

```python
# EE/networking/http_client/interface.py
from ..security.auth import AuthManager  # ❌ WRONG
from EE.observability.logging import get_logger  # ❌ WRONG
from EE.foundation.config import get_config  # ❌ WRONG
```

**Problems:**
1. Violates interface isolation principle
2. Creates tight coupling between domains
3. Bypasses UG execution control
4. Prevents horizontal scaling
5. Makes testing difficult

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: call_operation for Cross-Domain Calls

```python
# EE/networking/http_client/interface.py
class HttpClientInterface:
    def __init__(
        self,
        logger: logging.Logger,
        metrics: Any,
        config: Any,
        call_operation: Callable,  # ← Injected for cross-domain calls
    ):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation

    def _get_auth_token(self):
        # Call security domain via UG
        return self._call_operation(
            domain="security",
            interface="authentication",
            operation="get_token",
        )
```

**Benefits:**
- Maintains interface isolation
- All cross-domain calls go through UG
- Properly testable (can inject mock call_operation)
- Enables horizontal scaling
- Consistent error handling

---

## Import Rules

### ✅ ALLOWED: Imports Within Same Interface

```python
# EE/networking/http_client/interface.py
from .http_factory import HttpClientFactory  # ✅ OK - same interface
from .models import Request, Response  # ✅ OK - same interface
from .helpers import build_url, parse_response  # ✅ OK - same interface
```

### ❌ FORBIDDEN: Any Cross-Domain Imports

```python
# All of these are FORBIDDEN:
from ..security import ...  # ❌
from .observability import ...  # ❌
from EE.foundation import ...  # ❌
from EE.security.authentication import ...  # ❌
import EE.observability.logging  # ❌
```

---

## Enforcement

### Must Use:
1. `call_operation` for ALL cross-domain behavior
2. Local imports only within interface directory
3. DI for all cross-cutting concerns

### Must NOT Use:
1. ANY imports from other domains
2. ANY imports of parent domain modules
3. Direct imports of UG or domain gateways

---

## Related Patterns

- **AP-EE-05:** Interface Logic
- **AP-EE-06:** Factory Cross-Domain Imports
- **ARCH-EE-05:** Interface Isolation

---

**END OF AP-EE-04**
