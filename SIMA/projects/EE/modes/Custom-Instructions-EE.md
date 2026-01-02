# Custom-Instructions-EE.md

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Project:** EE (Execution Engine)  
**Purpose:** Custom instructions for EE-specific workflows  
**Type:** Custom Instructions

---

## EE CUSTOM INSTRUCTIONS

**Type:** Project  
**Domain:** Execution Engine with Universal Gateway  
**Architecture:** Universal Gateway (UG) Pattern  
**Language:** Python  
**Platform:** Generic (Platform-agnostic)

---

## CRITICAL CONSTRAINTS

### Architecture Constraints (MANDATORY)

1. **Interface Isolation**
   - Interfaces CANNOT import outside their package
   - No cross-domain dependencies
   - All communication via gateway

2. **Single Execution Authority**
   - UG is the ONLY entry point for cross-component operations
   - No direct domain access from external code
   - All operations go through `execute_operation(route, payload)`

3. **Factory Pattern**
   - Factories are execution units
   - No intermediate wrappers
   - Direct instantiation prohibited

4. **Route-Based Execution**
   - All operations use route strings: `"domain.operation"`
   - Route format: `"domain.operation"`
   - Route validation required

---

## ACTIVATION PHRASES

**Mode Activation:**
- Project Mode: `"Start Project Mode for EE"`
- Debug Mode: `"Start Debug Mode for EE"`

**Context Loading:**
- Base modes: `/sima/context/`
- Domain modes: `/sima/projects/EE/modes/`
- Shared knowledge: `/sima/context/shared/`

---

## PROJECT-SPECIFIC RULES

### File Structure Rules

**EE Package Structure:**
```
EE/
├── __init__.py              # ONLY exports execute_operation
├── src/
│   ├── gateway/             # Universal Gateway
│   │   ├── gateway.py       # Main UG implementation
│   │   └── __init__.py
│   └── domains/             # Domain implementations
│       ├── {domain}/
│       │   ├── __init__.py
│       │   ├── {domain}_gateway.py
│       │   ├── interfaces/
│       │   ├── factories/
│       │   └── tests/
```

**EE/__init__.py Requirements:**
- MUST only export `execute_operation`
- No other exports
- No other public API

---

### Code Standards

**Gateway Implementation:**
```python
# REQUIRED: execute_operation signature
def execute_operation(route: str, payload: dict) -> Any:
    """
    Execute operation via Universal Gateway.
    
    Args:
        route: Operation route (format: "domain.operation")
        payload: Operation parameters
    
    Returns:
        Operation result
    
    Raises:
        RouteNotFoundError: If route not registered
        ExecutionError: If operation fails
    """
```

**Domain Gateway Requirements:**
- MUST inherit from `DomainGateway` base class
- MUST implement `execute(operation, payload)` method
- MUST use interface for operations
- MUST use factory for execution units

**Interface Requirements:**
- MUST be self-contained (no cross-domain imports)
- MUST use factory for execution units
- MUST include type hints
- MUST include docstrings

**Factory Requirements:**
- MUST be static methods
- MUST return execution units
- MUST handle creation logic

---

### Operation Patterns

**Pattern 1: Simple Operation**
```python
# Gateway
def execute(self, operation: str, payload: dict) -> Any:
    if operation == "get":
        return self._interface.get(payload["key"])
    # ...

# Interface
def get(self, key: str) -> Any:
    reader = self._factory.create_reader()
    return reader.read(key)
```

**Pattern 2: Operation with Default Values**
```python
# Gateway
def execute(self, operation: str, payload: dict) -> Any:
    if operation == "send":
        return self._interface.send(
            recipient=payload["recipient"],
            message=payload["message"],
            channel=payload.get("channel", "default")  # Default value
        )
```

**Pattern 3: Operation with Validation**
```python
# Gateway
def execute(self, operation: str, payload: dict) -> Any:
    if operation == "set":
        # Validate required fields
        required = ["key", "value"]
        missing = [f for f in required if f not in payload]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return self._interface.set(
            key=payload["key"],
            value=payload["value"]
        )
```

---

## RED FLAGS (EE-Specific)

### Architecture Violations

❌ **Direct Domain Access**
```python
# BAD
from EE.src.domains.config.config_gateway import ConfigGateway
gateway = ConfigGateway()
result = gateway.get_value("key")  # ❌ Bypasses UG

# GOOD
from EE import execute_operation
result = execute_operation("config.get_value", {"key": "key"})
```

❌ **Cross-Domain Imports**
```python
# BAD
# In config_interface.py
from ..security.auth import AuthManager  # ❌ Cross-domain

# GOOD
# Use gateway for cross-domain operations
from EE import execute_operation
auth_result = execute_operation("security.check_auth", {"token": token})
```

❌ **Multiple Exports from EE/__init__.py**
```python
# BAD
# EE/__init__.py
from .src.gateway.gateway import execute_operation, Gateway  # ❌ Multiple exports
__all__ = ['execute_operation', 'Gateway']

# GOOD
# EE/__init__.py
from .src.gateway.gateway import execute_operation
__all__ = ['execute_operation']  # Only one export
```

❌ **Direct Factory Usage in Gateway**
```python
# BAD
# In gateway
from EE.src.domains.config.factories.config_factory import ConfigFactory
result = ConfigFactory.create_reader().read(key)  # ❌ Bypasses interface

# GOOD
# Use interface
result = self._interface.get(key)
```

---

## WORKFLOW SPECIFICS

### Adding New Domain

**Steps:**
1. Create directory: `EE/src/domains/{domain}/`
2. Create `{domain}_gateway.py` implementing `DomainGateway`
3. Create `interfaces/` directory with `{domain}_interface.py`
4. Create `factories/` directory with `{domain}_factory.py`
5. Register gateway in UG initialization
6. Add unit tests
7. Document decision in SIMA (DEC-##)
8. Update EE-Index-Main.md

### Adding New Operation

**Steps:**
1. Add operation handler in domain gateway `execute()` method
2. Add interface method if needed
3. Add factory method if new execution unit needed
4. Add unit tests
5. Update documentation
6. Document in SIMA if significant (DEC-##)

### Debugging Issues

**Steps:**
1. Activate Debug Mode: `"Start Debug Mode for EE"`
2. Check DEBUG-MODE-EE.md for known issues
3. Trace execution: UG → Gateway → Interface → Factory
4. Identify failing layer
5. Implement fix with `# FIXED:` marker
6. Add regression test
7. Document bug in SIMA (BUG-##)
8. Consider anti-pattern if applicable (AP-##)

---

## QUALITY STANDARDS

### Code Quality

**Required:**
- Type hints for all public functions
- Docstrings for all public APIs
- Specific exception handling (no bare except)
- Structured logging with context
- Unit tests for all operations

**Forbidden:**
- Bare except clauses
- Cross-domain imports
- Direct domain access from external code
- Direct factory instantiation (use factory methods)
- Multiple exports from EE/__init__.py

---

### File Standards

**Required:**
- Files ≤350 lines (HARD LIMIT)
- UTF-8 encoding
- LF line endings (no CRLF)
- File headers (version, date, purpose)
- Change markers (# ADDED:, # MODIFIED:, # FIXED:)

**Artifact Standards:**
- Complete files only (no fragments)
- Include all existing code
- Mark changes clearly
- No code in chat for files >20 lines

---

## VERIFICATION CHECKLISTS

### Pre-Commit Checklist
```
[ ] File ≤350 lines?
[ ] UTF-8 encoding, LF endings?
[ ] Type hints present?
[ ] Docstrings present?
[ ] Specific exceptions (no bare except)?
[ ] Structured logging?
[ ] Unit tests added?
[ ] Following UG pattern?
[ ] Interface isolation maintained?
[ ] Factory pattern used?
[ ] No cross-domain imports?
[ ] Changes marked with comments?
```

### Pre-Deployment Checklist
```
[ ] All tests passing?
[ ] Documentation updated?
[ ] Known issues documented?
[ ] Performance acceptable?
[ ] Security review complete?
[ ] Rollback plan ready?
```

---

## REFERENCES

**SIMA Documentation:**
- `/sima/context/projects/context-PROJECT-MODE-Context.md`
- `/sima/context/shared/Artifact-Standards.md`
- `/sima/context/shared/File-Standards.md`
- `/sima/context/shared/Common-Patterns.md`
- `/sima/context/shared/RED-FLAGS.md`

**EE Documentation:**
- `/sima/projects/EE/config/project_config.md`
- `/sima/projects/EE/modes/PROJECT-MODE-EE.md`
- `/sima/projects/EE/modes/DEBUG-MODE-EE.md`
- `/sima/projects/EE/EE-Architecture-Overview.md`
- `/sima/projects/EE/EE-Index-Main.md`

**Templates:**
- `/sima/templates/gateway_pattern_template.md`
- `/sima/templates/interface_catalog_template.md`

---

## CONTACT

**For questions about EE:**
- Check EE-Index-Main.md for knowledge index
- Activate Project Mode: `"Start Project Mode for EE"`
- Activate Debug Mode: `"Start Debug Mode for EE"`

---

**END OF CUSTOM INSTRUCTIONS**

**Version:** 1.0.0  
**Last Updated:** 2025-12-31
