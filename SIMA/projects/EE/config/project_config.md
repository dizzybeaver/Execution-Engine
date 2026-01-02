# EE Project Configuration

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** EE Execution Engine project overview  
**Type:** Project Configuration

---

## PROJECT OVERVIEW

**Name:** EE (Execution Engine)  
**Type:** Universal Gateway Architecture  
**Language:** Python  
**Platform:** Generic (Platform-agnostic)

---

## ARCHITECTURE

### Universal Gateway (UG) Pattern

**Core Principles:**
1. **Single Execution Authority**: UG is the only entry point for all cross-component behavior
2. **Interface Isolation**: Interfaces cannot import outside their package
3. **Direct Execution**: Factories are the execution units, no extra wrappers

**Architecture Layers:**
1. **Universal Gateway (UG)**: Central coordinator and single entry point
2. **Domain Gateways**: Domain-specific routers (e.g., ConfigGateway, SecurityGateway, LoggingGateway, MetricsGateway)
3. **Interfaces**: Isolated modules for specific capabilities
4. **Factories**: Concrete execution units

**Execution Flow:**
```
External Code → UG.execute_operation() → Domain Gateway → Interface → Factory
```

---

## DIRECTORY STRUCTURE

```
EE/
├── __init__.py              # Only exports execute_operation through gateway
├── src/
│   ├── gateway/             # Universal Gateway implementation
│   │   ├── gateway.py       # Main UG with execute(route, payload) pattern
│   │   └── __init__.py
│   └── [domains]/           # Domain-specific implementations
│       ├── config/          # Configuration domain gateway
│       ├── security/        # Security domain gateway
│       ├── logging/         # Logging domain gateway
│       └── metrics/         # Metrics domain gateway
└── tests/                   # Test suite
```

---

## REGISTERED DOMAIN GATEWAYS

**Current Implementation:**
- ConfigGateway - Configuration management
- SecurityGateway - Security operations
- LoggingGateway - Logging and monitoring
- MetricsGateway - Metrics collection
- (Additional domains can be registered)

---

## GATEWAY INTERFACE

**Entry Point:**
```python
# EE/__init__.py
from .src.gateway.gateway import execute_operation

__all__ = ['execute_operation']
```

**Usage:**
```python
from EE import execute_operation

result = execute_operation(
    route="config.get_value",
    payload={"key": "timeout"}
)
```

---

## CONSTRAINTS

### Architecture Constraints
- **Interface Isolation**: Interfaces MUST NOT import outside their package
- **Single Entry Point**: All cross-component operations MUST go through UG
- **Factory Pattern**: Factories are execution units, no intermediate wrappers
- **Route-Based**: All operations use route strings for routing

### File Standards
- **EE/__init__.py**: MUST only export `execute_operation`
- **Max file size**: 350 lines (SIMA standard)
- **UTF-8 encoding**: All source files
- **LF line endings**: No CRLF

---

## IMPLEMENTATION STATUS

**Completed:**
- ✅ Gateway implementation at `EE/src/gateway/gateway.py`
- ✅ `execute(route, payload)` pattern implemented
- ✅ Multiple domain gateways registered
- ✅ EE `__init__.py` exports only `execute_operation`

**In Progress:**
- 🔄 Refactoring to match UG Architecture Guide
- 🔄 Domain-specific interface isolation
- 🔄 Factory pattern implementation

**Pending:**
- ⏳ Complete documentation
- ⏳ Test suite coverage
- ⏳ Performance benchmarks

---

## INTEGRATION WITH SIMA

**Project Knowledge Location:** `/sima/projects/EE/`

**Mode Activation:**
- Project Mode: `"Start Project Mode for EE"`
- Debug Mode: `"Start Debug Mode for EE"`

**Knowledge Categories:**
- `/lessons/` - Lessons learned during development
- `/decisions/` - Architecture and design decisions
- `/anti-patterns/` - Anti-patterns discovered and avoided
- `/architecture/` - Architecture documentation
- `/indexes/` - Navigation indexes

---

## DEVELOPMENT GUIDELINES

### When Adding New Features
1. Activate Project Mode: `"Start Project Mode for EE"`
2. Follow Universal Gateway pattern
3. Maintain interface isolation
4. Use factory pattern for execution
5. All operations go through UG
6. Document decisions and lessons

### When Fixing Bugs
1. Activate Debug Mode: `"Start Debug Mode for EE"`
2. Check known issues in DEBUG-MODE-EE.md
3. Follow systematic debugging process
4. Document root causes and fixes
5. Update anti-patterns if applicable

### When Documenting Knowledge
1. Activate Learning Mode: `"Start SIMA Learning Mode"`
2. Genericize insights (remove EE-specifics when applicable)
3. Use appropriate templates (LESS, DEC, AP, BUG)
4. Update indexes
5. Mark with REF-IDs

---

## RELATED DOCUMENTATION

**SIMA Documentation:**
- `/sima/docs/user/SIMAv4.2.2-User-Guide.md`
- `/sima/context/shared/Common-Patterns.md`
- `/sima/templates/gateway_pattern_template.md`

**Project Documentation:**
- `EE-Architecture-Overview.md` - Complete architecture guide
- `README.md` - Project overview
- `EE-Index-Main.md` - Knowledge index

---

**END OF CONFIGURATION**

**Version:** 1.0.0  
**Last Updated:** 2025-12-31
