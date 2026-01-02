# AP-UGS-02: Import Isolation Violation

**ID:** AP-UGS-02
**Platform:** Universal Gateway System (UGS)
**Severity:** Critical
**Category:** Architecture Violation
**Status:** Enforced
**Last Updated:** 2025-12-31

---

## OVERVIEW

Import isolation is the foundation of Universal Gateway architecture. Violating import rules by importing domain gateways, UG, or shared utilities directly from interfaces breaks the entire architecture's design principles and creates unmanaged dependencies.

**UGS Principle Violated:**
- Interface Isolation (Section 1.2, UG Architecture Guide)
- Single Execution Authority (Section 1.1, UG Architecture Guide)

---

## THE ANTI-PATTERN

### Violation Types

This anti-pattern encompasses **all forms of improper imports** in interfaces:

1. **Importing Domain Gateways**
   - Directly importing any `*_gateway.py` module
   - Creating gateway instances in interfaces
   - Bypassing UG routing layer

2. **Importing Universal Gateway**
   - Importing `UniversalGateway` class
   - Importing gateway registry
   - Direct UG instantiation

3. **Importing Shared Utilities**
   - Importing global logging modules
   - Importing shared configuration
   - Importing shared metrics/monitoring

4. **Importing Cross-Domain Code**
   - Importing from other domains
   - Importing from sibling interfaces
   - Any import that breaks package boundaries

### Conceptual Anti-Pattern

```
Interface Package
    │
    ├── ✗ Direct Gateway Import
    │   └── from EE.security.security_gateway import SecurityGateway
    │
    ├── ✗ Direct UG Import
    │   └── from EE.universal_gateway.gateway import UniversalGateway
    │
    ├── ✗ Shared Utility Import
    │   └── from EE.shared.logging import get_logger
    │
    └── ✗ Cross-Domain Import
        └── from EE.networking.http import HttpFactory
```

### Why These Are Wrong

1. **Breaks Architecture:** Violates core UG design principles
2. **Creates Coupling:** Tightly couples implementation to infrastructure
3. **Bypasses Governance:** Avoids UG's central control and monitoring
4. **Prevents Testing:** Makes unit testing extremely difficult
5. **Hidden Dependencies:** Dependencies not visible in interface contract

---

## THE CORRECT PATTERN

### Dependency Injection Model

All external dependencies must be **injected**, not imported:

```
Universal Gateway (UG)
    │
    ├── Creates domain gateways
    │   └── Injects: logger_factory, metrics_factory, call_operation
    │
    ├── Domain gateways create interfaces
    │   └── Injects: logger, metrics, call_operation
    │
    └── Interfaces create factories
        └── Injects: logger, metrics, call_operation
```

### Correct Approach

**Instead of importing external dependencies:**

1. **Declare dependencies in constructor**
2. **Receive them as parameters**
3. **Use injected callbacks for operations**
4. **Stay within interface boundaries**

### Example Pattern

```python
# ✓ CORRECT: Factory with dependency injection
class MyFactory:
    """Factory with injected dependencies."""

    def __init__(self, logger=None, metrics=None, call_operation=None):
        """Initialize with injected dependencies.

        Args:
            logger: Injected logger instance (from UG)
            metrics: Injected metrics instance (from UG)
            call_operation: Callback for cross-domain calls (from UG)
        """
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def my_operation(self, **kwargs):
        """Execute operation using only injected dependencies."""
        # Use injected logger
        if self._logger:
            self._logger.info("Executing operation")

        # Use injected metrics
        if self._metrics:
            self._metrics.counter('operation_calls', 1)

        # Use injected callback for cross-domain calls
        if self._call_operation:
            result = self._call_operation(
                domain="other_domain",
                interface="other_interface",
                operation="other_operation",
                **kwargs
            )
            return result
```

---

## IMPACT AND CONSEQUENCES

### Architecture Impact

| Impact | Description | Severity |
|--------|-------------|----------|
| Architecture Violation | Breaks UG isolation principle | Critical |
| Lost Governance | Bypasses central control | Critical |
| Hidden Dependencies | Dependencies not in contract | High |
| Test Complexity | Requires full infrastructure stack | High |
| Deployment Risk | Cannot deploy independently | Medium |

### Development Consequences

1. **Code Comprehension:**
   - Cannot understand interface behavior in isolation
   - Must trace multiple files to understand one operation
   - Hidden dependencies make code review difficult

2. **Testing Complexity:**
   - Unit tests require full UG infrastructure
   - Cannot mock external dependencies easily
   - Test suites become slow and fragile

3. **Maintenance Burden:**
   - Changes ripple across unmanaged dependencies
   - Refactoring becomes risky
   - Technical debt accumulates rapidly

4. **Deployment Issues:**
   - Cannot deploy interfaces independently
   - All interfaces must be deployed together
   - Increased blast radius of changes

---

## IMPORT ISOLATION RULES

### What IS Allowed

```python
# ✓ Allowed: Same interface imports
from .factory import MyFactory
from .models import DataModel
from .utils import helper_function

# ✓ Allowed: Standard library
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
```

### What is NOT Allowed

```python
# ✗ NOT Allowed: Domain gateway imports
from EE.networking.networking_gateway import NetworkingGateway
from EE.security.security_gateway import SecurityGateway
from EE.foundation.foundation_gateway import FoundationGateway

# ✗ NOT Allowed: UG imports
from EE.universal_gateway.gateway import UniversalGateway
from EE.universal_gateway.domain_gateway import DomainGateway
from EE import get_ug

# ✗ NOT Allowed: Shared utility imports
from EE.shared.logging import get_logger
from EE.shared.metrics import get_metrics
from EE.shared.config import get_config

# ✗ NOT Allowed: Cross-interface imports
from EE.networking.websocket import WebSocketFactory
from EE.security.authentication import AuthFactory
from EE.operations.cache import CacheFactory

# ✗ NOT Allowed: Cross-domain imports
from EE.networking.http_client import HttpClientFactory
from EE.security.encryption import EncryptionFactory
```

---

## ENFORCEMENT MECHANISMS

### 1. Automated Scanner

```python
# Validate import isolation
from EE import execute_operation

violations = execute_operation(
    domain='scanner',
    interface='validation',
    operation='check_import_isolation',
    path='EE/',
    rules={
        'forbid_gateway_imports': True,
        'forbid_ug_imports': True,
        'forbid_shared_imports': True,
        'forbid_cross_domain_imports': True,
        'allow_same_interface': True,
        'allow_stdlib': True
    }
)

if violations:
    print(f"Found {len(violations)} import violations:")
    for v in violations:
        print(f"  {v['file']}: {v['import_line']}")
```

### 2. Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking import isolation..."
python -m scanner.ug.validation check_imports EE/

if [ $? -ne 0 ]; then
    echo "❌ Import isolation violations detected"
    echo "Commit aborted. Fix violations before committing."
    exit 1
fi

echo "✓ Import isolation validated"
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/validate.yml
name: Validate UG Architecture

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Import Isolation
        run: |
          python -m scanner.ug.validation check_imports EE/ --fail-on-error
```

---

## DETECTION AND REMEDIATION

### Detection Checklist

Review each interface for:

- [ ] Any import ending in `_gateway.py`
- [ ] Any import from `universal_gateway/`
- [ ] Any import from `shared/` directories
- [ ] Any import from sibling interfaces
- [ ] Any import from other domains
- [ ] Direct instantiation of gateway/UG classes
- [ ] Static access to shared utilities

### Remediation Steps

1. **Identify all violations:**
   ```bash
   python -m scanner.ug.validation check_imports EE/ --report
   ```

2. **Create dependency injection contract:**
   ```python
   def __init__(self, logger=None, metrics=None, call_operation=None):
       self._logger = logger
       self._metrics = metrics
       self._call_operation = call_operation
   ```

3. **Replace imports with injected dependencies:**
   - Remove prohibited imports
   - Use `self._call_operation()` for cross-domain calls
   - Use `self._logger` for logging
   - Use `self._metrics` for metrics

4. **Update domain gateway to inject dependencies:**
   ```python
   def create_interface_dispatcher(get_logger, get_metrics, call_operation):
       def dispatcher(operation, **kwargs):
           factory = MyFactory(
               logger=get_logger('domain.interface'),
               metrics=get_metrics('domain.interface'),
               call_operation=call_operation
           )
           return DISPATCH[operation](factory, **kwargs)
       return dispatcher
   ```

5. **Verify fix:**

---
**Entry ID:** AP-UGS-02
**Lines:** 345
**Status:** Active - Enforced
**Next Review:** 2026-01-31
