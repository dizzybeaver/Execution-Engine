# DEBUG-MODE-EE.md

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Project:** EE (Execution Engine)  
**Purpose:** Debug Mode extension for EE troubleshooting  
**Type:** Mode Extension

---

## PROJECT: EE (Execution Engine)

**Architecture:** Universal Gateway (UG) Pattern  
**Language:** Python  
**Platform:** Generic (Platform-agnostic)

---

## DEBUGGING APPROACH

### Four Debug Principles

1. **Systematic Investigation** - Follow the execution flow layer by layer
2. **Known Issues First** - Check documented issues before deep investigation
3. **Trace All Layers** - UG → Domain Gateway → Interface → Factory
4. **Measure Don't Guess** - Use logs, traces, and measurements

---

## EXECUTION FLOW TRACE

### Normal Flow
```
External Code
    ↓
UG.execute_operation(route, payload)
    ↓
Route parsing: domain.operation
    ↓
DomainGateway.execute(operation, payload)
    ↓
Interface.method()
    ↓
Factory.execution_unit()
    ↓
Result
```

### Debug Trace Strategy

**Step 1: Verify Route Format**
```python
# Check route format
if '.' not in route:
    raise InvalidRouteError(f"Invalid route format: {route}")

domain, operation = route.split('.', 1)
log_debug("route_parsed", domain=domain, operation=operation)
```

**Step 2: Verify Gateway Registration**
```python
# Check if domain gateway is registered
if domain not in _gateways:
    log_error("gateway_not_registered", domain=domain)
    log_debug("available_gateways", gateways=list(_gateways.keys()))
    raise GatewayNotFoundError(domain)
```

**Step 3: Trace Domain Execution**
```python
# Add logging in domain gateway
log_debug("executing_domain_operation", 
          domain=domain, 
          operation=operation,
          payload=payload)

try:
    result = gateway.execute(operation, payload)
    log_debug("operation_completed", result=result)
except Exception as e:
    log_error("operation_failed", 
              error=str(e),
              error_type=type(e).__name__)
    raise
```

**Step 4: Trace Interface Call**
```python
# Add logging in interface
log_debug("interface_call", 
          method=method.__name__,
          args=args,
          kwargs=kwargs)
```

**Step 5: Trace Factory Execution**
```python
# Add logging in factory
log_debug("factory_execution",
          factory=self.__class__.__name__,
          unit=execution_unit.__class__.__name__)
```

---

## KNOWN ISSUES

### Issue 1: Route Not Found

**Symptom:**
```python
RouteNotFoundError: Unknown route: "config.get_valu"
```

**Diagnosis:**
- Typo in route string
- Domain not registered
- Operation not implemented

**Debug Steps:**
```python
# 1. Check route format
assert '.' in route, "Route must contain 'domain.operation'"

# 2. Check domain registration
assert domain in _gateways, f"Domain {domain} not registered"

# 3. Check operation implementation
gateway = _gateways[domain]
available_ops = [op for op in dir(gateway) if not op.startswith('_')]
log_debug("available_operations", operations=available_ops)
```

**Fix:**
```python
# Verify route spelling
result = execute_operation("config.get_value", {"key": "timeout"})  # FIXED: typo
```

---

### Issue 2: Gateway Not Registered

**Symptom:**
```python
GatewayNotFoundError: Domain 'cache' not registered
```

**Diagnosis:**
- Domain gateway not created
- Gateway not registered in UG
- Import error

**Debug Steps:**
```python
# 1. Check if gateway class exists
try:
    from EE.src.domains.cache.cache_gateway import CacheGateway
except ImportError as e:
    log_error("gateway_import_failed", error=str(e))
    raise

# 2. Check if gateway is registered
log_debug("registered_gateways", gateways=list(_gateways.keys()))

# 3. Check registration code
# EE/src/gateway/gateway.py
from EE.src.domains.cache.cache_gateway import CacheGateway
_register_gateway('cache', CacheGateway())  # ADDED: Missing registration
```

**Fix:**
```python
# Register gateway in UG initialization
from EE.src.domains.cache.cache_gateway import CacheGateway

# In gateway.py initialization
_gateways['cache'] = CacheGateway()
```

---

### Issue 3: Interface Isolation Violation

**Symptom:**
```python
ImportError: attempted relative import beyond top-level package
```

**Diagnosis:**
- Interface importing from another domain
- Cross-domain dependency
- Package structure issue

**Debug Steps:**
```python
# 1. Check interface imports
# EE/src/domains/config/config_interface.py
# BAD: from ..security.auth import AuthManager  # ❌ Cross-domain

# 2. Use gateway instead
# GOOD:
from EE import execute_operation
auth_result = execute_operation("security.check_auth", {"token": token})
```

**Fix:**
```python
# Remove cross-domain imports
# Use gateway for cross-domain communication
result = execute_operation("security.check_auth", {"token": token})
```

---

### Issue 4: Factory Not Implemented

**Symptom:**
```python
AttributeError: module has no attribute 'ConfigFactory'
```

**Diagnosis:**
- Factory class not created
- Factory not imported
- Factory method missing

**Debug Steps:**
```python
# 1. Check if factory exists
from EE.src.domains.config.factories.config_factory import ConfigFactory

# 2. Check factory methods
factory_methods = [method for method in dir(ConfigFactory) if not method.startswith('_')]
log_debug("factory_methods", methods=factory_methods)

# 3. Create factory if missing
class ConfigFactory:
    """Factory for config execution units."""
    
    @staticmethod
    def create_reader() -> ConfigReader:
        return ConfigReader()
```

**Fix:**
```python
# Create factory class
# EE/src/domains/config/factories/config_factory.py
class ConfigFactory:
    @staticmethod
    def create_reader() -> ConfigReader:
        return ConfigReader()
```

---

## ERROR PATTERNS

### Pattern 1: Import Errors

**Symptoms:**
- `ImportError`
- `ModuleNotFoundError`

**Common Causes:**
1. Missing `__init__.py` in package directories
2. Incorrect import paths
3. Circular imports
4. Missing dependencies

**Debug Strategy:**
```python
# 1. Verify package structure
import os
assert os.path.exists("EE/__init__.py"), "Missing EE/__init__.py"
assert os.path.exists("EE/src/__init__.py"), "Missing EE/src/__init__.py"

# 2. Check import path
import sys
sys.path.insert(0, '/path/to/Project')

# 3. Test import
try:
    from EE.src.gateway.gateway import execute_operation
except ImportError as e:
    log_error("import_failed", error=str(e))
    raise
```

---

### Pattern 2: Type Errors

**Symptoms:**
- `TypeError: 'NoneType' object is not callable`
- `TypeError: execute_operation() takes 2 positional arguments but 3 were given`

**Common Causes:**
1. Missing self parameter
2. Incorrect type hints
3. Payload structure mismatch

**Debug Strategy:**
```python
# 1. Check function signature
import inspect
sig = inspect.signature(execute_operation)
log_debug("function_signature", signature=str(sig))

# 2. Verify payload structure
if not isinstance(payload, dict):
    raise TypeError(f"Payload must be dict, got {type(payload)}")

# 3. Add type validation
def execute_operation(route: str, payload: dict) -> Any:
    if not isinstance(route, str):
        raise TypeError(f"Route must be str, got {type(route)}")
    if not isinstance(payload, dict):
        raise TypeError(f"Payload must be dict, got {type(payload)}")
    # ...
```

---

### Pattern 3: Key Errors

**Symptoms:**
- `KeyError: 'key'`

**Common Causes:**
1. Missing required keys in payload
2. Incorrect key names
3. Case sensitivity issues

**Debug Strategy:**
```python
# 1. Validate payload keys
required_keys = ['key', 'value']
missing_keys = [k for k in required_keys if k not in payload]
if missing_keys:
    raise KeyError(f"Missing required keys: {missing_keys}")

# 2. Log payload structure
log_debug("payload_structure", keys=list(payload.keys()))

# 3. Provide clear error messages
if 'key' not in payload:
    raise ValueError("Payload must contain 'key' field")
```

---

## DEBUG TOOLS

### Tool 1: Execution Tracer

```python
import logging
from contextlib import contextmanager

@contextmanager
def trace_execution(operation_name: str):
    """Context manager for tracing execution."""
    logging.info(f"START: {operation_name}")
    try:
        yield
        logging.info(f"SUCCESS: {operation_name}")
    except Exception as e:
        logging.error(f"FAILED: {operation_name}", exc_info=True)
        raise

# Usage
with trace_execution("config.get_value"):
    result = execute_operation("config.get_value", {"key": "timeout"})
```

---

### Tool 2: Route Validator

```python
def validate_route(route: str) -> tuple[str, str]:
    """
    Validate and parse route.
    
    Args:
        route: Route string (e.g., "config.get_value")
    
    Returns:
        Tuple of (domain, operation)
    
    Raises:
        InvalidRouteError: If route format is invalid
    """
    if not isinstance(route, str):
        raise InvalidRouteError(f"Route must be str, got {type(route)}")
    
    if '.' not in route:
        raise InvalidRouteError(f"Route must contain 'domain.operation': {route}")
    
    parts = route.split('.')
    if len(parts) != 2:
        raise InvalidRouteError(f"Invalid route format: {route}")
    
    domain, operation = parts
    return domain, operation
```

---

### Tool 3: Payload Inspector

```python
def inspect_payload(payload: dict, required_keys: list = None) -> None:
    """
    Inspect payload structure.
    
    Args:
        payload: Payload to inspect
        required_keys: List of required keys
    
    Raises:
        PayloadError: If payload is invalid
    """
    if not isinstance(payload, dict):
        raise PayloadError(f"Payload must be dict, got {type(payload)}")
    
    logging.info("Payload structure", keys=list(payload.keys()))
    
    if required_keys:
        missing = [k for k in required_keys if k not in payload]
        if missing:
            raise PayloadError(f"Missing required keys: {missing}")
```

---

## COMMON FIXES

### Fix 1: Add Missing Gateway Registration

```python
# BEFORE: Gateway not registered
# EE/src/gateway/gateway.py
_gateways = {
    'config': ConfigGateway(),
    'security': SecurityGateway(),
    # cache: Missing!
}

# AFTER: Add registration
# MODIFIED: Added cache gateway
_gateways = {
    'config': ConfigGateway(),
    'security': SecurityGateway(),
    'cache': CacheGateway(),  # FIXED: Added cache gateway
}
```

---

### Fix 2: Correct Import Path

```python
# BEFORE: Wrong import path
from EE.gateway.gateway import execute_operation  # ❌ Wrong path

# AFTER: Correct import path
from EE.src.gateway.gateway import execute_operation  # FIXED: Correct path
```

---

### Fix 3: Add Missing Factory

```python
# BEFORE: Factory missing
# EE/src/domains/config/config_interface.py
reader = ConfigReader()  # ❌ Direct instantiation

# AFTER: Use factory
from .factories.config_factory import ConfigFactory  # ADDED: Import factory
reader = ConfigFactory.create_reader()  # FIXED: Via factory
```

---

## VERIFICATION PROTOCOL

### Pre-Fix Checklist

```
[ ] Identified failure layer (UG/Gateway/Interface/Factory)?
[ ] Checked known issues list?
[ ] Traced execution flow?
[ ] Added debug logging?
[ ] Created failing test case?
[ ] Verified root cause?
```

### Post-Fix Checklist

```
[ ] Fix implemented with # FIXED: marker?
[ ] Failing test now passes?
[ ] Added regression test?
[ ] Debug logging removed (or commented)?
[ ] Documented fix in BUG-## entry?
[ ] Updated related documentation?
[ ] Verified no side effects?
```

---

## REFERENCES

**Base Debug Mode:**
- `/sima/context/debug/context-DEBUG-MODE-Context.md`
- `/sima/context/shared/Artifact-Standards.md`
- `/sima/context/shared/RED-FLAGS.md`

**Project Documentation:**
- `/sima/projects/EE/modes/PROJECT-MODE-EE.md`
- `/sima/projects/EE/EE-Architecture-Overview.md`

**Tools:**
- `/sima/support/tools/TOOL-04-Verification-Protocol.md`
- `/sima/support/checklists/Checklist-01-Code-Review.md`

---

**END OF DEBUG MODE EXTENSION**

**Version:** 1.0.0  
**Lines:** 350 (target achieved)  
**Purpose:** EE Debug Mode extension
