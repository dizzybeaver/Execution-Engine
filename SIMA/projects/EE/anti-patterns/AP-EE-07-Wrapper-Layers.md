# AP-EE-07: Wrapper Layers (Except Domain-Local)

**Category:** Anti-Pattern
**Type:** Architecture Pattern
**Severity:** HIGH
**Scope:** EE Architecture
**REF-ID:** AP-EE-07
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - RESTRICTED)

---

## Overview

**Wrapper layers that bypass UG or accumulate logic violate the execution pattern**. EE 2.1 ONLY allows thin, stateless, domain-local wrappers. All other wrappers are forbidden.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Cross-Domain Wrappers

```python
# EE/wrappers/http_wrapper.py  # ❌ WRONG - Cross-domain wrapper
def execute_http_operation(domain, interface, operation, **kwargs):
    """Bypasses UG's execution control"""
    ug = get_ug()  # ❌ Direct UG access
    return ug.execute_operation(domain, interface, operation, **kwargs)
```

**Problems:**
1. Creates alternative execution path
2. Bypasses UG's pooling and DI
3. Accumulates wrapper logic over time
4. Violates single entry point principle
5. Difficult to maintain and debug

---

## The Allowed Exception (Domain-Local Wrappers)

### ✅ ALLOWED: Thin Domain-Local Wrappers

```python
# EE/networking/http_client/local_wrapper.py
from .http_interface import execute_http_operation

# ✅ ALLOWED - Thin wrapper, same domain only
def get(url: str, **kwargs):
    """Convenience wrapper for HTTP GET"""
    return execute_http_operation("get", url=url, **kwargs)

def post(url: str, data=None, **kwargs):
    """Convenience wrapper for HTTP POST"""
    return execute_http_operation("post", url=url, data=data, **kwargs)
```

**Conditions for Allowance:**
1. Wrapper stays inside same domain
2. Wrapper is thin (1-3 lines)
3. Wrapper is stateless
4. Wrapper does not bypass UG for cross-domain calls
5. Wrapper is not used outside the domain

---

## Wrapper Rules (EE 2.1)

### ✅ ALLOWED Wrappers:

1. **Domain-local convenience wrappers**
   ```python
   # EE/networking/http_client/wrapper.py
   from .http_interface import execute_http_operation

   def get(url, **kwargs):
       return execute_http_operation("get", url=url, **kwargs)
   ```

2. **Interface-local helper wrappers**
   ```python
   # EE/networking/http_client/helpers.py
   def build_url(base: str, path: str) -> str:
       return f"{base.rstrip('/')}/{path.lstrip('/')}"
   ```

### ❌ FORBIDDEN Wrappers:

1. **Cross-domain wrappers**
   ```python
   # ❌ Wrapper that calls other domains
   def wrapper_that_calls_security():
       from EE.security import auth  # Cross-domain import
   ```

2. **UG bypass wrappers**
   ```python
   # ❌ Wrapper that bypasses UG
   def direct_gateway_call():
       gateway = get_registry().get("networking")
   ```

3. **Logic-accumulating wrappers**
   ```python
   # ❌ Wrapper with business logic
   def complex_wrapper(data):
       # Validation
       # Transformation
       # Caching
       # Logging
       # ... then call UG
   ```

---

## Enforcement

### Before Creating a Wrapper, Ask:
1. Is this wrapper staying in the same domain? (If no → DON'T)
2. Is this wrapper thin (< 5 lines)? (If no → DON'T)
3. Is this wrapper stateless? (If no → DON'T)
4. Does this wrapper go through UG for cross-domain calls? (If no → DON'T)

### If All Answers Are YES:
- Wrapper is ALLOWED
- Keep it thin
- Document its purpose
- Review regularly for logic creep

---

## Examples

### ✅ ALLOWED: Domain-Local Convenience Wrapper

```python
# EE/networking/http_client/convenience.py
from .http_interface import execute_http_operation

def quick_get(url: str, timeout=30):
    """Convenience wrapper for simple GET requests"""
    return execute_http_operation(
        operation="get",
        url=url,
        timeout=timeout
    )
```

### ❌ FORBIDDEN: Cross-Domain Wrapper

```python
# EE/wrappers/unified_wrapper.py
def unified_operation(domain, operation, **kwargs):
    """❌ WRONG - Cross-domain wrapper"""
    # Calls multiple domains
    # Bypasses UG execution flow
    # Accumulates logic
```

---

## Related Patterns

- **AP-EE-04:** Cross-Domain Imports
- **AP-EE-05:** Interface Logic
- **ARCH-EE-08:** Domain-Local Wrapper Pattern

---

**END OF AP-EE-07**
