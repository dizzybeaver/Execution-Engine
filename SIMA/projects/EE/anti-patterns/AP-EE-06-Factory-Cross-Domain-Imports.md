# AP-EE-06: Factory Cross-Domain Imports

**Category:** Anti-Pattern
**Type:** Import Pattern
**Severity:** CRITICAL
**Scope:** EE Domain Factories
**REF-ID:** AP-EE-06
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Cross-domain imports in factories violate interface isolation** just as much as interface imports. EE 2.1 enforces that factories MUST use `call_operation` for cross-domain behavior.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Cross-Domain Imports in Factories

```python
# EE/foundation/config/factory.py
from EE.security.encryption import encrypt  # ❌ WRONG
from EE.observability.logging import log_info  # ❌ WRONG
from EE.operations.cache import cache_get  # ❌ WRONG

class ConfigFactory:
    def get_encrypted_value(self, key: str):
        value = self._config[key]
        return encrypt(value)  # ❌ Direct cross-domain call
```

**Problems:**
1. Violates interface isolation
2. Creates tight coupling
3. Bypasses UG execution control
4. Cannot mock dependencies for testing
5. Prevents horizontal scaling

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: call_operation in Factories

```python
# EE/foundation/config/factory.py
class ConfigFactory:
    def __init__(
        self,
        logger: logging.Logger,
        metrics: Any,
        config: Any,
        call_operation: Callable,  # ← Injected
    ):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation

    def get_encrypted_value(self, key: str):
        """✅ CORRECT - Uses call_operation"""
        encrypted = self._config[key]

        # Call security domain via UG
        decrypted = self._call_operation(
            domain="security",
            interface="encryption",
            operation="decrypt",
            value=encrypted
        )

        return decrypted
```

**Benefits:**
- Maintains isolation
- All cross-domain calls go through UG
- Testable (can inject mock call_operation)
- Enables horizontal scaling
- Consistent error handling

---

## Factory Import Rules

### ✅ ALLOWED: Factory Imports

```python
# EE/foundation/config/factory.py
import os  # ✅ OK - Standard library
import json  # ✅ OK - Standard library
from .models import ConfigEntry  # ✅ OK - Same interface
from .helpers import parse_config  # ✅ OK - Same interface
```

### ❌ FORBIDDEN: Factory Imports

```python
# All of these are FORBIDDEN:
from ..security import ...  # ❌
from EE.security.encryption import ...  # ❌
from .observability.logging import ...  # ❌
import EE.networking.http_client  # ❌
```

---

## Enforcement

### Must Use:
1. `call_operation` for ALL cross-domain behavior
2. Local imports only within interface directory
3. Standard library imports are OK

### Must NOT Use:
1. ANY imports from other EE domains
2. ANY imports of other domain factories
3. Direct instantiation of other domain interfaces

---

## Common Patterns

### ✅ CORRECT: Cross-Domain Calls

```python
# Get config from security domain
security_config = self._call_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="security.api_key"
)

# Encrypt value via security domain
encrypted = self._call_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value=data
)

# Log via observability domain
self._call_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="Operation completed"
)
```

---

## Related Patterns

- **AP-EE-04:** Interface Cross-Domain Imports
- **AP-EE-05:** Interface Logic
- **ARCH-EE-07:** Factory Isolation

---

**END OF AP-EE-06**
