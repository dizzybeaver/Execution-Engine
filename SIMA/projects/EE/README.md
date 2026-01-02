# EE - Execution Engine

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Status:** Active Development  
**Architecture:** Universal Gateway (UG) Pattern

---

## OVERVIEW

EE (Execution Engine) is a Python-based execution engine implementing the **Universal Gateway (UG) pattern** for centralized cross-component coordination. EE provides a single entry point for all operations through route-based execution, enforcing strict interface isolation and factory-based execution units.

**What it does:**
- Coordinates cross-component operations via centralized gateway
- Routes operations to domain-specific gateways
- Enforces interface isolation (no cross-domain imports)
- Provides factory-based execution units

**What problem it solves:**
- Eliminates tight coupling between components
- Centralizes error handling and logging
- Provides consistent execution interface
- Enables independent testing and deployment

---

## ARCHITECTURE

### Universal Gateway Pattern

**Core Principles:**
1. **Single Execution Authority** - UG is the only entry point
2. **Interface Isolation** - Interfaces cannot import outside their package
3. **Direct Execution** - Factories are execution units, no extra wrappers

**Execution Flow:**
```
External Code → UG.execute_operation() → Domain Gateway → Interface → Factory
```

### Quick Start

```python
# Install
# (Add installation instructions here)

# Usage
from EE import execute_operation

# Get configuration value
result = execute_operation(
    route="config.get_value",
    payload={"key": "timeout"}
)
print(result)  # Output: 30

# Check authentication
auth_result = execute_operation(
    route="security.check_auth",
    payload={"token": "abc123"}
)
print(auth_result)  # Output: True/False
```

---

## KEY FEATURES

- **Route-Based Execution** - Simple `"domain.operation"` format
- **Domain Gateways** - Isolated domain-specific routing
- **Interface Isolation** - No cross-domain dependencies
- **Factory Pattern** - Managed execution unit creation
- **Type Safety** - Full type hints throughout
- **Structured Logging** - Context-aware logging
- **Error Handling** - Consistent exception hierarchy

---

## DIRECTORY STRUCTURE

```
EE/
├── __init__.py              # Only exports execute_operation
├── src/
│   ├── gateway/             # Universal Gateway implementation
│   │   ├── gateway.py       # Main UG with execute(route, payload)
│   │   └── __init__.py
│   └── domains/             # Domain-specific implementations
│       ├── config/          # Configuration domain
│       │   ├── config_gateway.py
│       │   ├── interfaces/
│       │   ├── factories/
│       │   └── tests/
│       ├── security/        # Security domain
│       ├── logging/         # Logging domain
│       └── metrics/         # Metrics domain
└── tests/                   # Integration tests
```

---

## REGISTERED DOMAINS

### ConfigGateway
**Operations:** `get`, `set`, `list`, `delete`  
**Purpose:** Configuration management  
**Status:** ✅ Implemented

### SecurityGateway
**Operations:** `check_auth`, `validate_token`, `encrypt`  
**Purpose:** Security operations  
**Status:** ✅ Implemented

### LoggingGateway
**Operations:** `log`, `get_logs`, `clear_logs`  
**Purpose:** Logging and monitoring  
**Status:** ✅ Implemented

### MetricsGateway
**Operations:** `record_metric`, `get_metric`, `list_metrics`  
**Purpose:** Metrics collection  
**Status:** ✅ Implemented

---

## GETTING STARTED

### Prerequisites
- Python 3.11+
- (Add other dependencies here)

### Setup
```bash
# Clone repository
git clone <repository-url>
cd <project-dir>

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest EE/tests/

# Use EE
python -c "from EE import execute_operation; print(execute_operation('config.list', {}))"
```

### Basic Usage
```python
from EE import execute_operation

# Get config value
timeout = execute_operation("config.get_value", {"key": "timeout"})

# Set config value
execute_operation("config.set_value", {"key": "timeout", "value": 60})

# Check authentication
is_valid = execute_operation("security.check_auth", {"token": "abc123"})

# Log message
execute_operation("logging.log", {"level": "info", "message": "System started"})
```

---

## ADVANCED USAGE

### Adding New Domain

**1. Create domain structure:**
```bash
mkdir -p EE/src/domains/{domain}/{interfaces,factories,tests}
```

**2. Implement gateway:**
```python
# EE/src/domains/{domain}/{domain}_gateway.py
from abc import ABC
from typing import Any, Dict

class {Domain}Gateway(DomainGateway):
    def execute(self, operation: str, payload: dict) -> Any:
        if operation == "operation_name":
            return self._interface.method(payload)
        # ... handle other operations
```

**3. Register in UG:**
```python
# EE/src/gateway/gateway.py
from EE.src.domains.{domain}.{domain}_gateway import {Domain}Gateway

_gateways["{domain}"] = {Domain}Gateway()
```

**4. Activate Project Mode:**
```
"Start Project Mode for EE"
```

---

### Error Handling

```python
from EE import execute_operation, RouteNotFoundError, ExecutionError

try:
    result = execute_operation("config.get_value", {"key": "timeout"})
except RouteNotFoundError as e:
    print(f"Route not found: {e}")
except ExecutionError as e:
    print(f"Execution failed: {e}")
```

---

### Debugging

**Activate Debug Mode:**
```
"Start Debug Mode for EE"
```

**Trace execution:**
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Execute with tracing
result = execute_operation("config.get_value", {"key": "timeout"})
```

---

## DOCUMENTATION

### Project Knowledge

**SIMA Integration:**
- Location: `/sima/projects/EE/`
- Mode Activation:
  - Project Mode: `"Start Project Mode for EE"`
  - Debug Mode: `"Start Debug Mode for EE"`

**Knowledge Categories:**
- `/lessons/` - Lessons learned (REF-ID: LESS-EE-##)
- `/decisions/` - Design decisions (REF-ID: DEC-EE-##)
- `/anti-patterns/` - Anti-patterns (REF-ID: AP-EE-##)
- `/architecture/` - Architecture docs (REF-ID: ARCH-EE-##)

**Key Documentation:**
- [Architecture Overview](SIMA/projects/EE/EE-Architecture-Overview.md) - Complete architecture guide
- [Project Configuration](SIMA/projects/EE/config/project_config.md) - Project settings
- [Main Index](SIMA/projects/EE/indexes/EE-Index-Main.md) - Knowledge index

---

## CONSTRAINTS

### Architecture Constraints
- **Interface Isolation:** Interfaces MUST NOT import outside their package
- **Single Entry Point:** All operations MUST go through `execute_operation()`
- **Factory Pattern:** Execution units created via factories only
- **Route-Based:** All operations use `"domain.operation"` format

### File Standards
- **EE/__init__.py:** MUST only export `execute_operation`
- **Max file size:** 350 lines (SIMA standard)
- **UTF-8 encoding:** All source files
- **LF line endings:** No CRLF

---

## CONTRIBUTING

### Development Guidelines

1. **Activate Project Mode:** `"Start Project Mode for EE"`
2. **Follow Universal Gateway pattern**
3. **Maintain interface isolation**
4. **Use factory pattern for execution**
5. **Document decisions and lessons**

### Code Standards
- Type hints required for public functions
- Docstrings required for public APIs
- Specific exception handling (no bare except)
- Structured logging with context
- Unit tests for all operations

### Testing
```bash
# Run all tests
pytest EE/tests/

# Run specific domain tests
pytest EE/src/domains/config/tests/

# Run with coverage
pytest --cov=EE EE/tests/
```

---

## STATUS

**Implementation Phase:** Active Development

**Completed:**
- ✅ Gateway implementation
- ✅ `execute(route, payload)` pattern
- ✅ Multiple domain gateways registered
- ✅ SIMA project structure
- ✅ Mode extensions defined

**In Progress:**
- 🔄 Interface isolation refinement
- 🔄 Factory pattern implementation
- 🔄 Test suite development

**Pending:**
- ⏳ Complete domain documentation
- ⏳ Performance benchmarks
- ⏳ Knowledge base population

---

## LICENSE

(Add license information here)

---

## CONTACT

**For questions:**
- Check [EE-Index-Main.md](SIMA/projects/EE/indexes/EE-Index-Main.md)
- Activate Project Mode: `"Start Project Mode for EE"`
- Activate Debug Mode: `"Start Debug Mode for EE"`

**For SIMA-related questions:**
- [SIMA Quick Reference](SIMA/SIMA-Quick-Reference-Card.md)
- [SIMA User Guide](SIMA/docs/user/SIMAv4.2.2-User-Guide.md)

---

**END OF README**

**Version:** 1.0.0  
**Last Updated:** 2025-12-31
