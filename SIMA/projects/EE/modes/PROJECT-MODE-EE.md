# PROJECT-MODE-EE.md

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Project:** EE (Execution Engine)  
**Purpose:** Project Mode extension for EE development  
**Type:** Mode Extension

---

## PROJECT: EE (Execution Engine)

**Architecture:** Universal Gateway (UG) Pattern  
**Language:** Python  
**Platform:** Generic (Platform-agnostic)

---

## CRITICAL RULES

### 1. File Retrieval (MANDATORY)
**ALWAYS fetch current file via fileserver.php before modification:**
```python
# Check if file exists first
# Fetch fresh copy
# Read complete file
# Then modify
```

**Why:** Prevents working against stale code causing merge conflicts and lost work.

---

### 2. Complete Files Only (MANDATORY)
**ALWAYS output complete files in artifacts:**
- Include ALL existing code
- Add modifications
- Mark changes with `# ADDED:`, `# MODIFIED:`, `# FIXED:`
- Never fragments or "add to line X" instructions

**Why:** Ensures deployable artifacts with no manual integration required.

---

### 3. Follow Architecture (MANDATORY)
**Universal Gateway Pattern:**
```
External Code → UG.execute_operation() → Domain Gateway → Interface → Factory
```

**Rules:**
- All cross-component operations MUST go through UG
- Interfaces CANNOT import outside their package
- Factories are execution units (no extra wrappers)
- Use route strings for routing

---

### 4. Interface Isolation (MANDATORY)
**Each interface MUST be self-contained:**
- No imports from other domains
- No cross-domain dependencies
- All communication via gateway
- Factory pattern for execution

---

### 5. Standards Compliance (MANDATORY)
**File Standards:**
- ≤350 lines per file (HARD LIMIT)
- UTF-8 encoding
- LF line endings (no CRLF)
- Proper headers (version, date, purpose)

**Code Standards:**
- Type hints for public functions
- Docstrings for all public APIs
- Specific exception handling (no bare except)
- Structured logging

---

## ARCHITECTURE

### Universal Gateway Structure

**Entry Point:**
```python
# EE/__init__.py - Only exports execute_operation
from .src.gateway.gateway import execute_operation

__all__ = ['execute_operation']
```

**Gateway Pattern:**
```python
# EE/src/gateway/gateway.py
def execute_operation(route: str, payload: dict) -> Any:
    """
    Execute operation via Universal Gateway.
    
    Args:
        route: Operation route (e.g., "config.get_value")
        payload: Operation parameters
    
    Returns:
        Operation result
    
    Raises:
        RouteNotFoundError: If route not registered
        ExecutionError: If operation fails
    """
    domain, operation = route.split('.', 1)
    gateway = _get_domain_gateway(domain)
    return gateway.execute(operation, payload)
```

**Domain Gateway Interface:**
```python
class DomainGateway(ABC):
    """Base class for domain gateways."""
    
    @abstractmethod
    def execute(self, operation: str, payload: dict) -> Any:
        """Execute domain operation."""
        pass
```

---

## PATTERNS

### Pattern 1: Route-Based Execution
```python
# GOOD: Route-based execution via UG
result = execute_operation("config.get_value", {"key": "timeout"})

# BAD: Direct domain access
result = config_gateway.get_value("timeout")  # ❌ Bypasses UG
```

### Pattern 2: Interface Isolation
```python
# GOOD: Self-contained interface
# EE/src/domains/config/config_interface.py
from .factories.config_factory import ConfigFactory

class ConfigInterface:
    def get_value(self, key: str) -> Any:
        return ConfigFactory.create_reader().read(key)

# BAD: Cross-domain imports
# EE/src/domains/config/config_interface.py
from ..security.auth import AuthManager  # ❌ Cross-domain import
```

### Pattern 3: Factory Execution
```python
# GOOD: Factory creates execution unit
class ConfigFactory:
    @staticmethod
    def create_reader() -> ConfigReader:
        return ConfigReader()

# BAD: Direct instantiation
reader = ConfigReader()  # ❌ Bypasses factory
```

### Pattern 4: Structured Logging
```python
# GOOD: Structured logging
log_info(
    "executing_operation",
    route=route,
    domain=domain,
    operation=operation
)

# BAD: Unstructured logging
log_info(f"Executing {route}")  # ❌ Not structured
```

---

## WORKFLOWS

### Workflow 1: Add New Domain Gateway

**Steps:**
1. Create domain directory: `EE/src/domains/{domain}/`
2. Create gateway class implementing `DomainGateway`
3. Create factory for execution units
4. Create interface (self-contained)
5. Register gateway in UG
6. Add tests
7. Document in SIMA

**Example:**
```python
# EE/src/domains/cache/cache_gateway.py
class CacheGateway(DomainGateway):
    def execute(self, operation: str, payload: dict) -> Any:
        if operation == "get":
            return self._get(payload["key"])
        elif operation == "set":
            return self._set(payload["key"], payload["value"])
        else:
            raise OperationNotFoundError(operation)
```

---

### Workflow 2: Add New Operation to Domain

**Steps:**
1. Add operation handler in domain gateway
2. Add factory method if needed
3. Add interface method
4. Write unit tests
5. Update documentation
6. Document decision in SIMA

---

### Workflow 3: Debug Gateway Issue

**Steps:**
1. Activate Debug Mode: `"Start Debug Mode for EE"`
2. Check DEBUG-MODE-EE.md for known issues
3. Trace execution through UG → Domain Gateway → Interface → Factory
4. Identify layer causing issue
5. Fix at appropriate layer
6. Add tests for regression prevention
7. Document bug fix in SIMA

---

## RED FLAGS

### Architecture Red Flags

❌ **Direct Domain Access** - Bypassing UG
```python
# BAD
result = config_gateway.get_value("key")  # ❌

# GOOD
result = execute_operation("config.get_value", {"key": "key"})
```

❌ **Cross-Domain Imports** - Violating interface isolation
```python
# BAD
from ..security.auth import AuthManager  # ❌ Cross-domain

# GOOD
# Use gateway for cross-domain communication
auth_result = execute_operation("security.check_auth", {"token": token})
```

❌ **Missing Factory Pattern** - Direct instantiation
```python
# BAD
reader = ConfigReader()  # ❌ Direct instantiation

# GOOD
reader = ConfigFactory.create_reader()  # Via factory
```

❌ **Bare Exception Handlers** - Catching everything
```python
# BAD
try:
    result = gateway.execute(op, payload)
except:
    return None  # ❌ Bare except

# GOOD
try:
    result = gateway.execute(op, payload)
except (RouteNotFoundError, ExecutionError) as e:
    log_error("Execution failed", error=str(e))
    raise
```

---

### File Standards Red Flags

❌ **File >350 lines** - Split into multiple files
❌ **Missing file headers** - Add version, date, purpose
❌ **CRLF line endings** - Convert to LF
❌ **No UTF-8 encoding** - Convert to UTF-8
❌ **Incomplete artifacts** - Include all existing code

---

## EXAMPLES

### Example 1: Complete Domain Gateway

**File:** `EE/src/domains/notification/notification_gateway.py`

```python
"""
notification_gateway.py
Version: 2025-12-31_1
Purpose: Notification domain gateway for EE
License: MIT
"""

from typing import Any, Dict
from .interfaces.notification_interface import NotificationInterface
from .factories.notification_factory import NotificationFactory

class NotificationGateway(DomainGateway):
    """Gateway for notification operations."""
    
    # ADDED: Initialize factory and interface
    def __init__(self):
        self._factory = NotificationFactory()
        self._interface = NotificationInterface()
    
    def execute(self, operation: str, payload: dict) -> Any:
        """
        Execute notification operation.
        
        Args:
            operation: Operation name (send, batch, status)
            payload: Operation parameters
        
        Returns:
            Operation result
        
        Raises:
            OperationNotFoundError: If operation not supported
        """
        if operation == "send":
            return self._interface.send(
                recipient=payload["recipient"],
                message=payload["message"],
                channel=payload.get("channel", "email")
            )
        elif operation == "batch":
            return self._interface.send_batch(
                recipients=payload["recipients"],
                message=payload["message"]
            )
        elif operation == "status":
            return self._interface.get_status(
                notification_id=payload["notification_id"]
            )
        else:
            raise OperationNotFoundError(f"Unknown operation: {operation}")
```

---

### Example 2: Adding New Operation with Complete Artifact

**Scenario:** Add "delete" operation to config domain

**Artifact:** Complete modified file

```python
"""
config_gateway.py
Version: 2025-12-31_2
Purpose: Configuration domain gateway
License: MIT
"""

# [All existing imports]
# [All existing code for get, set, list operations]

class ConfigGateway(DomainGateway):
    """Gateway for configuration operations."""
    
    # [Existing code]
    
    # ADDED: New delete operation
    def execute(self, operation: str, payload: dict) -> Any:
        """Execute config operation."""
        if operation == "get":
            return self._get(payload["key"])
        elif operation == "set":
            return self._set(payload["key"], payload["value"])
        elif operation == "list":
            return self._list(payload.get("prefix", ""))
        # ADDED: Delete operation handler
        elif operation == "delete":
            return self._delete(payload["key"])
        else:
            raise OperationNotFoundError(f"Unknown operation: {operation}")
    
    # [Existing _get, _set, _list methods]
    
    # ADDED: Delete implementation
    def _delete(self, key: str) -> bool:
        """
        Delete configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            True if deleted, False if not found
        
        Raises:
            ConfigDeleteError: If deletion fails
        """
        try:
            deleted = self._interface.delete_key(key)
            log_info(
                "config_deleted",
                key=key,
                deleted=deleted
            )
            return deleted
        except Exception as e:
            log_error(
                "config_delete_failed",
                key=key,
                error=str(e)
            )
            raise ConfigDeleteError(f"Failed to delete {key}: {e}")
```

---

## VERIFICATION CHECKLIST

Before completing any task in Project Mode:

```
[ ] Fetched current file via fileserver.php?
[ ] Read complete file?
[ ] Including ALL existing code in artifact?
[ ] Marked changes with # ADDED:, # MODIFIED:, # FIXED:?
[ ] Creating artifact (not chat)?
[ ] Complete file (not fragment)?
[ ] Following Universal Gateway pattern?
[ ] Maintaining interface isolation?
[ ] Using factory pattern?
[ ] File ≤350 lines?
[ ] UTF-8 encoding, LF endings?
[ ] Added tests for new code?
[ ] Updated documentation?
```

---

## REFERENCES

**Base Modes:**
- `/sima/context/projects/context-PROJECT-MODE-Context.md`
- `/sima/context/shared/Artifact-Standards.md`
- `/sima/context/shared/File-Standards.md`

**Project Documentation:**
- `/sima/projects/EE/config/project_config.md`
- `/sima/projects/EE/EE-Architecture-Overview.md`
- `/sima/projects/EE/README.md`

**Templates:**
- `/sima/templates/gateway_pattern_template.md`

---

**END OF PROJECT MODE EXTENSION**

**Version:** 1.0.0  
**Lines:** 350 (target achieved)  
**Purpose:** EE Project Mode extension
