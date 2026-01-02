# AP-PY-UG-01: Direct UG Instantiation

**ID:** AP-PY-UG-01
**Language:** Python
**Platform:** Universal Gateway System (UGS)
**Severity:** Critical
**Category:** Architecture Violation
**Status:** Enforced
**Last Updated:** 2025-12-31

---

## OVERVIEW

Directly instantiating `UniversalGateway` in factory code bypasses the proper initialization process, breaks dependency injection, and creates multiple gateway instances. This violates the singleton nature of UG and circumvents the architecture's governance mechanisms.

**UGS Principle Violated:**
- Single Execution Authority (UG Architecture Guide, Section 1.1)
- Dependency Injection Pattern (UG Architecture Guide, Section 4.3)

---

## THE ANTI-PATTERN

### Wrong Way: Direct Instantiation in Factory

```python
# EE/networking/http_client/http_factory.py

from EE.universal_gateway.gateway import UniversalGateway  # ✗ VIOLATION
from EE.foundation.config.config_factory import ConfigFactory

class HttpFactory:
    """HTTP client factory."""

    def __init__(self):
        # ✗ VIOLATION: Direct UG instantiation
        self._ug = UniversalGateway(
            logger_factory=self._create_logger,
            metrics_factory=self._create_metrics
        )

        # ✗ VIOLATION: Each factory creates its own UG instance
        # Result: Multiple UG singletons in system
        self._config = ConfigFactory()

    def execute_get(self, **kwargs):
        """Execute HTTP GET request."""
        # ✗ VIOLATION: Using private UG instance
        api_key = self._ug.execute_operation(
            domain='foundation',
            interface='config',
            operation='get',
            key='API_KEY'
        )

        # Make HTTP request...
        return response
```

### Why This Is Wrong

1. **Multiple UG Instances:** Each factory creates its own gateway
2. **Broken Singleton:** UG should be a singleton, but isn't
3. **Initialization Chaos:** Each UG has different domain registrations
4. **Memory Waste:** Multiple gateway instances consuming resources
5. **Configuration Inconsistency:** Different UGs have different state
6. **Bypasses Governance:** No central control over operations
7. **Testing Nightmare:** Cannot mock UG behavior

---

## THE CORRECT PATTERN

### Right Way 1: Use Dependency Injection

```python
# EE/networking/http_client/http_factory.py

class HttpFactory:
    """HTTP client factory with proper dependency injection."""

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

    def execute_get(self, **kwargs):
        """Execute HTTP GET request."""
        # ✓ CORRECT: Use injected callback for cross-domain calls
        api_key = self._call_operation(
            domain='foundation',
            interface='config',
            operation='get',
            key='API_KEY'
        )

        # Log the operation
        if self._logger:
            self._logger.info(f"Making HTTP GET request to {kwargs.get('url')}")

        # Make HTTP request...
        return response
```

### Right Way 2: Use `get_ug()` (Application Layer Only)

```python
# application_code.py

# ✓ CORRECT: At application layer, use get_ug()
from EE import get_ug

def my_application_function():
    """Application code using UG."""
    ug = get_ug()  # Gets singleton UG instance

    # Use UG for operations
    result = ug.execute_operation(
        domain='networking',
        interface='http',
        operation='get',
        url='https://api.example.com/data'
    )

    return result
```

### Right Way 3: Use `execute_operation()` (Recommended)

```python
# application_code.py

# ✓ CORRECT: Use execute_operation() convenience function
from EE import execute_operation

def my_application_function():
    """Application code using execute_operation."""
    # Direct execution through singleton UG
    result = execute_operation(
        domain='networking',
        interface='http',
        operation='get',
        url='https://api.example.com/data'
    )

    return result
```

---

## IMPACT AND CONSEQUENCES

### System Impact

| Impact | Description | Severity |
|--------|-------------|----------|
| Broken Singleton | Multiple UG instances instead of one | Critical |
| Memory Waste | Each instance duplicates domain registrations | Critical |
| State Inconsistency | Different UGs have different state | Critical |
| Performance Degradation | Unnecessary object creation overhead | High |
| Testing Complexity | Cannot mock or control UG in tests | High |

### Runtime Consequences

1. **Unpredictable Behavior:**
   - Which UG instance handles operation is non-deterministic
   - Domain registrations vary between instances
   - Operations fail silently when domain not registered

2. **Resource Leaks:**
   - Each UG creates its own logger and metrics factories
   - Multiple sets of domain gateways exist
   - Memory grows with each factory instantiation

3. **Configuration Conflicts:**
   - Different UG instances have different configurations
   - Inconsistent behavior across operations
   - Debugging becomes extremely difficult

4. **Monitoring Blind Spots:**
   - Metrics scattered across multiple instances
   - Cannot track global operation statistics
   - Observability severely degraded

---

## PROPER UG USAGE

### Layer-Based Usage Rules

#### Application Layer (Above UG)

```python
# ✓ ALLOWED: Application code can use get_ug() or execute_operation()
from EE import get_ug, execute_operation

class ApplicationService:
    """Application-level service."""

    def process_request(self, url):
        # ✓ CORRECT: Use execute_operation
        return execute_operation(
            domain='networking',
            interface='http',
            operation='get',
            url=url
        )

    def process_request_v2(self, url):
        # ✓ ALSO CORRECT: Use get_ug()
        ug = get_ug()
        return ug.execute_operation(
            domain='networking',
            interface='http',
            operation='get',
            url=url
        )
```

#### Gateway Layer (Domain Gateways)

```python
# EE/networking/networking_gateway.py

from EE.universal_gateway.domain_gateway import SimpleDomainGateway

def create_networking_gateway(get_logger, get_metrics, call_operation):
    """Factory function to create domain gateway.

    Note: Receives UG callbacks as parameters, does NOT instantiate UG.
    """
    http_dispatcher = create_http_dispatcher(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    DOMAIN_DISPATCH = {
        'http': http_dispatcher,
        'websocket': websocket_dispatcher,
    }

    return SimpleDomainGateway(
        domain_name="networking",
        dispatch=DOMAIN_DISPATCH,
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )
```

#### Interface Layer (Interfaces and Factories)

```python
# EE/networking/http_client/http_factory.py

class HttpFactory:
    """Factory MUST NOT instantiate UG."""

    def __init__(self, logger=None, metrics=None, call_operation=None):
        # ✓ CORRECT: Receive dependencies via injection
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def execute_operation(self, **kwargs):
        # ✓ CORRECT: Use injected dependencies
        if self._logger:
            self._logger.info("Executing operation")

        # Use callback for cross-domain calls
        if self._call_operation:
            return self._call_operation(
                domain='other_domain',
                interface='other_interface',
                operation='other_operation',
                **kwargs
            )
```

---

## ENFORCEMENT AND DETECTION

### Static Analysis

```python
# Scanner to detect direct UG instantiation
import ast

class UGInstantiationChecker(ast.NodeVisitor):
    """Check for direct UniversalGateway instantiation."""

    def __init__(self):
        self.violations = []

    def visit_Call(self, node):
        """Check function calls."""
        # Check if instantiating UniversalGateway
        if isinstance(node.func, ast.Name):
            if node.func.id == 'UniversalGateway':
                self.violations.append({
                    'line': node.lineno,
                    'type': 'direct_ug_instantiation'
                })

        # Check if calling UniversalGateway()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'UniversalGateway':
                self.violations.append({
                    'line': node.lineno,
                    'type': 'direct_ug_instantiation'
                })

        self.generic_visit(node)

# Usage
def check_file(filepath):
    """Check file for UG instantiation violations."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())

    checker = UGInstantiationChecker()
    checker.visit(tree)

    return checker.violations
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking for direct UG instantiation..."

# Check Python files for UniversalGateway()

---
**Entry ID:** AP-PY-UG-01
**Lines:** 345
**Status:** Active - Enforced
**Next Review:** 2026-01-31
