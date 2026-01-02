# ARCH-EE-01: Single Entry Point Pattern

**Category:** Architecture
**Status:** Production
**EE Version:** 2.0.0
**Last Updated:** 2025-12-31

---

## Overview

The EE package follows a **Single Entry Point** pattern where the package's `__init__.py` exports only one public function: `execute_operation()`. This design enables Lambda compatibility, provides a clean API surface, and enforces the UG architecture pattern.

---

## Pattern Definition

### Location
`d:\Code\Project\EE\__init__.py`

### Implementation

The EE package exports exactly one function for external use:

```python
# EE/__init__.py (lines 347-436)

def execute_operation(
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    """SINGLE entry point for EE operations.

    UG Architecture Pattern:
        execute_operation(domain, interface, operation, **kwargs)

    This is the ONLY function that should be imported from EE for
    Lambda compatibility and clean architecture.

    Args:
        domain: Domain name (e.g., "foundation", "security", "observability")
        interface: Interface name (e.g., "config", "auth", "logging")
        operation: Operation name (e.g., "get", "verify_password", "info")
        **kwargs: Operation-specific parameters

    Returns:
        Operation result (type depends on operation)

    Raises:
        DomainNotFoundError: If domain not registered
        InvalidOperationError: If operation execution fails

    Examples:
        # Foundation operations
        config_value = execute_operation(
            domain="foundation",
            interface="config",
            operation="get",
            key="database.host"
        )

        # Observability operations
        execute_operation(
            domain="observability",
            interface="logging",
            operation="info",
            message="Server started"
        )

        # Security operations
        result = execute_operation(
            domain="security",
            interface="authentication",
            operation="verify_password",
            password="secret",
            hash="..."
        )

        # Networking operations
        response = execute_operation(
            domain="networking",
            interface="http",
            operation="get",
            url="https://api.example.com/data"
        )
    """
    ug = get_ug()
    return ug.execute_operation(domain, interface, operation, **kwargs)
```

### Public API Definition

The package `__all__` export list is intentionally minimal:

```python
# EE/__init__.py (lines 443-454)

__all__ = [
    # Primary entry point
    "execute_operation",

    # Advanced access
    "get_ug",
    "get_registry",

    # Types (for type hints)
    "UniversalGateway",
    "EEDomainRegistry",
]
```

---

## Rationale

### 1. Lambda Compatibility

AWS Lambda functions require fast cold starts. By exporting only `execute_operation()`, the package can defer UG initialization until first use:

```python
# Lazy initialization pattern (lines 117-321)

_ug: Optional[UniversalGateway] = None
_registry: Optional[EEDomainRegistry] = None

def get_ug() -> UniversalGateway:
    """Get the Universal Gateway instance.

    This function initializes the UG on first call and returns the singleton.
    """
    global _ug
    if _ug is None:
        _ug = _initialize_ug()
    return _ug
```

**Benefits:**
- Fast import time (no initialization during import)
- Lazy UG singleton creation on first call
- Minimal memory footprint until execution

### 2. Clean API Surface

External code has ONE way to interact with EE:

```python
# Import
from EE import execute_operation

# Use
result = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)
```

**No confusing alternatives:**
- ❌ `from EE import execute` (legacy pattern, removed in 2.0)
- ❌ `from EE import get_ug` (advanced use only)
- ❌ `from EE.foundation import FoundationGateway` (bypasses UG)
- ❌ Direct imports from subpackages (breaks isolation)

### 3. Architecture Enforcement

The single entry point enforces UG architecture:

```
External Code
    ↓ execute_operation(domain, interface, operation, **kwargs)
UniversalGateway (UG)
    ↓ get domain gateway
DomainGateway
    ↓ execute domain operation
Interface
    ↓ execute operation
Implementation
```

**Cannot bypass UG:**
- All operations must go through `execute_operation()`
- Domain/interface/operation triple is required
- No direct gateway access from external code
- Enforces dependency injection pattern

---

## Usage Examples

### Example 1: AWS Lambda Function

```python
# lambda_function.py
from EE import execute_operation

def lambda_handler(event, context):
    """Handle Lambda invocation using EE for config and logging."""

    # Log invocation
    execute_operation(
        domain="observability",
        interface="logging",
        operation="info",
        message="Lambda invoked",
        event=event
    )

    # Get configuration
    api_key = execute_operation(
        domain="foundation",
        interface="config",
        operation="get",
        key="API_KEY"
    )

    # Process event
    result = process_event(event, api_key)

    return result
```

### Example 2: Flask Application

```python
# app.py
from flask import Flask, request, jsonify
from EE import execute_operation

app = Flask(__name__)

@app.route("/api/config/<key>")
def get_config(key):
    """Get configuration value through EE."""
    try:
        value = execute_operation(
            domain="foundation",
            interface="config",
            operation="get",
            key=key
        )
        return jsonify({"key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Example 3: Background Worker

```python
# worker.py
from EE import execute_operation
import time

def worker_loop():
    """Background worker using EE for all operations."""
    while True:
        # Get work items from queue
        items = execute_operation(
            domain="operations",
            interface="queue",
            operation="dequeue",
            batch_size=10
        )

        for item in items:
            try:
                # Process item
                result = process_item(item)

                # Log success
                execute_operation(
                    domain="observability",
                    interface="logging",
                    operation="info",
                    message=f"Processed {item.id}",
                    result=result
                )
            except Exception as e:
                # Log error
                execute_operation(
                    domain="observability",
                    interface="logging",
                    operation="error",
                    message=f"Failed {item.id}",
                    error=str(e)
                )

        time.sleep(1)
```

---

## Migration from Legacy

### Old Pattern (Removed in 2.0)

```python
# EE 1.x - NO LONGER SUPPORTED
from EE import execute

result = execute("config.get", {"key": "database.host"})
```

**Problems:**
- String-based routing (error-prone)
- No type safety
- Difficult to discover available operations
- Mixes domain, interface, and operation in single string

### New Pattern (UG Architecture)

```python
# EE 2.0 - UG Pattern
from EE import execute_operation

result = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)
```

**Benefits:**
- Explicit domain/interface/operation
- Type-safe parameters
- Self-documenting
- Easy to discover operations via `list_all()`

---

## Advanced Usage

### Direct UG Access (Advanced)

For advanced scenarios, you can access the UG directly:

```python
from EE import get_ug

# Get UG instance
ug = get_ug()

# Get statistics
stats = ug.get_stats()
print(f"Total domains: {stats['total_domains']}")

# List all operations
all_ops = ug.list_all()
for domain, info in all_ops.items():
    print(f"{domain}: {info['interface_count']} interfaces")
```

### Domain Registry Access

```python
from EE import get_registry

# Get registry
registry = get_registry()

# Check if domain exists
if registry.has_domain("foundation"):
    gateway = registry.get("foundation")
    # Use gateway directly (advanced)
```

---

## Enforcement

### What's NOT Allowed

```python
# ❌ DON'T: Import directly from subpackages
from EE.foundation import FoundationGateway
from EE.universal_gateway import UniversalGateway

# ❌ DON'T: Bypass execute_operation
ug = UniversalGateway(...)
result = ug.execute_operation(...)  # Should use package-level function

# ❌ DON'T: Import legacy pattern
from EE import execute  # Removed in 2.0
```

### What's Allowed

```python
# ✅ DO: Use single entry point
from EE import execute_operation

result = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)

# ✅ DO: Advanced access when needed
from EE import get_ug, get_registry

ug = get_ug()
stats = ug.get_stats()
```

---

## Related Patterns

- **GATE-EE-01:** UniversalGateway class implementation
- **LESS-EE-01:** Module-level singleton UG pattern
- **DEC-EE-01:** DISPATCH pattern requirement in interfaces

---

## References

- **Implementation:** `d:\Code\Project\EE\__init__.py` (lines 347-436)
- **UG Architecture:** `d:\Code\Project\UG Architecture Guide.md`
- **UniversalGateway:** `d:\Code\Project\EE\universal_gateway\gateway.py`
- **DomainGateway:** `d:\Code\Project\EE\universal_gateway\domain_gateway.py`
