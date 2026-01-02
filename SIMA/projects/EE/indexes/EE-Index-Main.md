# EE Index - Main

**Version:** 2.1.1
**Date:** 2026-01-01
**Purpose:** Main knowledge index for EE 2.1 project
**Type:** Project Index

---

## OVERVIEW

**Project:** EE (Execution Engine) 2.1
**Architecture:** Universal Gateway (UG) Pattern - Factory-Driven, DI-Centric, Pooled
**Purpose:** Scalable, uniform gateway-based execution with strict interface isolation
**Status:** EE 2.1 Architecture Specification

---

## NAVIGATION

**Project Root:** `/sima/projects/EE/`

**Quick Links:**
- [Configuration](config/knowledge-config.yaml) - Project config
- [Project Overview](config/project_config.md) - Complete project info
- [README](README.md) - Project README

**Mode Extensions:**
- [Project Mode](modes/PROJECT-MODE-EE.md) - Development guidelines
- [Debug Mode](modes/DEBUG-MODE-EE.md) - Troubleshooting guide

---

## EE 2.1 ARCHITECTURE (Authoritative)

### Core Architecture Documents

**Location:** `/sima/projects/EE/architecture/`

| Document | Purpose | REF-ID |
|----------|---------|--------|
| [EE-Universal-Gateway-Architecture.md](architecture/EE-Universal-Gateway-Architecture.md) | Complete UG architecture specification | - |
| [EE-Universal-Gateway-Implementation-Guide.md](architecture/EE-Universal-Gateway-Implementation-Guide.md) | How to implement EE 2.1 | - |
| [EE-Domain-Interface-Catalog.md](architecture/EE-Domain-Interface-Catalog.md) | Complete domain/interface inventory | - |
| [EE-Multi-Agent-Workflow.md](architecture/EE-Multi-Agent-Workflow.md) | Multi-agent governance system | - |
| [EE-UG-Rules-For-AI-Agents.md](architecture/EE-UG-Rules-For-AI-Agents.md) | AI agent rulebook | - |
| [EE-Template-Repository-Layout.md](architecture/EE-Template-Repository-Layout.md) | Repository structure | - |

### EE 2.1 Core Principles

1. **Factory-Driven Construction** - UniversalGatewayFactory builds UG instances
2. **Dependency Injection** - All cross-cutting concerns injected, no direct imports
3. **Object Pooling** - Pools at UG, domain gateway, interface, and factory levels
4. **Uniform Gateway Construction** - All domains use same constructor signature
5. **Interface Isolation** - No cross-domain imports, strict enforcement
6. **Factory Execution** - Factories are execution units, interfaces only route

---

## ANTI-PATTERNS (EE 2.1)

**Location:** `/sima/projects/EE/anti-patterns/`
**Status:** Active - 8 entries
**Purpose:** Patterns to avoid in EE 2.1

### Current Entries

| REF-ID | Title | Severity | Description |
|--------|-------|----------|-------------|
| [AP-EE-01](anti-patterns/AP-EE-01-Global-UG-Singleton.md) | Global UG Singleton | CRITICAL | Forbidden - use factory pattern |
| [AP-EE-02](anti-patterns/AP-EE-02-Global-Registry-Singleton.md) | Global Registry Singleton | CRITICAL | Forbidden - use DI-injected registry |
| [AP-EE-03](anti-patterns/AP-EE-03-Mixed-Gateway-Constructors.md) | Mixed Gateway Constructors | HIGH | Forbidden - use uniform constructor |
| [AP-EE-04](anti-patterns/AP-EE-04-Direct-Cross-Domain-Imports.md) | Direct Cross-Domain Imports | CRITICAL | Forbidden - use call_operation |
| [AP-EE-05](anti-patterns/AP-EE-05-Interface-Logic.md) | Interface Logic | HIGH | Forbidden - factories execute, interfaces route |
| [AP-EE-06](anti-patterns/AP-EE-06-Factory-Cross-Domain-Imports.md) | Factory Cross-Domain Imports | CRITICAL | Forbidden - use call_operation |
| [AP-EE-07](anti-patterns/AP-EE-07-Wrapper-Layers.md) | Wrapper Layers | HIGH | Only domain-local wrappers allowed |
| [AP-EE-08](anti-patterns/AP-EE-08-Unsafe-Pooling.md) | Unsafe Pooling | HIGH | Forbidden - pools must be safe and deterministic |

---

## DECISIONS (EE 2.1)

**Location:** `/sima/projects/EE/decisions/`
**Status:** Active - 3 entries
**Purpose:** Architecture and design decisions for EE 2.1

### Current Entries

| REF-ID | Title | Description |
|--------|-------|-------------|
| [DEC-EE-01](decisions/DEC-EE-01-Factory-Driven-UG-Construction.md) | Factory-Driven UG Construction | UG built via factory, not singleton |
| [DEC-EE-02](decisions/DEC-EE-02-DI-Mandatory.md) | DI-Mandatory Architecture | All cross-cutting concerns injected |
| [DEC-EE-03](decisions/DEC-EE-03-ISP-Domain-Merge.md) | ISP Domain Merger | ISP domain absorbed into networking.connectivity |

---

## LEGACY EE 2.0 KNOWLEDGE (Deprecated)

**Status:** Superseded by EE 2.1
**Action:** DO NOT USE - For reference only during migration

### Deprecated Documents

| REF-ID | Title | Superseded By |
|--------|-------|---------------|
| ARCH-EE-01 | Single Entry Point Pattern | EE-Universal-Gateway-Architecture.md |
| GATE-EE-01 | Universal Gateway Class | EE-Universal-Gateway-Implementation-Guide.md |
| EE-Architecture-Overview.md | Legacy architecture overview | EE-Domain-Interface-Catalog.md |
| DEC-EE-01 (legacy) | Dispatch Pattern Requirement | DEC-EE-02 (DI-Mandatory) |
| LESS-EE-01 | Module-level singleton UG | Factory pattern (EE 2.1) |
| LESS-EE-02 | Protocol vs ABC for callables | Factory pattern (EE 2.1) |

**Deprecated Pattern:** `execute(route, payload)`
**EE 2.1 Pattern:** `execute_operation(domain, interface, operation, **kwargs)`

---

## PYTHON ANTI-PATTERNS

**Location:** `/sima/languages/python/anti-patterns/`

| REF-ID | Title | Scope |
|--------|-------|-------|
| [AP-28](../../languages/python/anti-patterns/AP-28-Relative-Imports-Lambda.md) | Relative Imports in Lambda | AWS Lambda, Plugins |

---

## REGISTERED DOMAINS (EE 2.1)

**Total:** 14 domains
**UG-ISP Compliant:** 8 domains
**Legacy (Need Upgrade):** 6 domains

### UG-ISP Compliant Domains (Ready for EE 2.1)

1. **foundation** - Config, DI, utilities
2. **observability** - Logging, metrics, debug
3. **security** - Auth, encryption, validation
4. **operations** - Cache, file I/O, pooling
5. **networking** - HTTP, protocols, clients, connectivity (includes former ISP operations)
6. **scanner** - Security scanning, compliance
7. **test** - Testing framework
8. **infrastructure** - Plugin management

### Legacy Domains (Need EE 2.1 Upgrade)

9. **cli** - Command-line interface
10. **doc** - Documentation generation
11. **sdk** - SDK bindings
12. **web** - Web server
13. **dashboard** - Dashboard UI
14. **ha** - Home Assistant integration

**Note:** ISP domain removed 2026-01-01 (see DEC-EE-03)

**See:** [EE-Domain-Interface-Catalog.md](architecture/EE-Domain-Interface-Catalog.md) for complete details

---

## EXECUTION PATTERN (EE 2.1)

### Entry Point

```python
from EE import execute_operation

result = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)
```

### Execution Flow

```
External Code
    ↓ execute_operation(domain, interface, operation, **kwargs)
UniversalGateway (from factory + pool)
    ↓ resolve domain via DomainRegistry
DomainGateway (from DomainGatewayFactory + pool)
    ↓ resolve interface from pool
Interface (from pool)
    ↓ delegate to factory from pool
Factory / Implementation (execution unit)
    ↓ use call_operation for cross-domain
Result
```

---

## MULTI-AGENT SYSTEM

**Location:** `/Doc/` (Agent manifests)

### Agent Types

1. **Coordinator Agent** - Orchestrates enforcement and repair
2. **Architecture Compliance Enforcer** - Analyzes code, detects violations
3. **Python UG-Compliant Coder** - Repairs code to enforce EE 2.1

**Workflow:** Enforce → Aggregate → Repair → Re-enforce → Iterate to 100% compliance

---

## REFERENCE KEY

### REF-ID Formats

**EE-Specific Entries:**
- `AP-EE-##` - EE anti-patterns (EE 2.1)
- `DEC-EE-##` - EE decisions (EE 2.1)
- `ARCH-EE-##` - EE architecture docs (EE 2.1)

**Python-Specific:**
- `AP-##` - Python anti-patterns
- `AP-28` - Relative Imports in Lambda

### Current EE 2.1 Entries
- **Anti-Patterns:** AP-EE-01 through AP-EE-08
- **Decisions:** DEC-EE-01, DEC-EE-02, DEC-EE-03
- **Architecture:** 6 comprehensive EE 2.1 documents

---

## MODE ACTIVATION

**For Development:**
```
"Start Project Mode for EE"
```
Loads: `/sima/projects/EE/modes/PROJECT-MODE-EE.md`

**For Debugging:**
```
"Start Debug Mode for EE"
```
Loads: `/sima/projects/EE/modes/DEBUG-MODE-EE.md`

---

## COMMON TASKS

### EE 2.1 Compliance Check

1. Review anti-patterns in `/sima/projects/EE/anti-patterns/`
2. Check architecture documents in `/sima/projects/EE/architecture/`
3. Verify against EE-UG-Rules-For-AI-Agents.md
4. Run multi-agent workflow for full compliance

### Find Knowledge

1. Check appropriate category directory
2. Use REF-ID if known
3. Search by keyword in category
4. Check related entries

---

## PROJECT STATUS

**Current Phase:** EE 2.1 Architecture Definition Complete

**Completed:**
- ✅ EE 2.1 architecture specification
- ✅ Anti-patterns documented (8 entries)
- ✅ Decisions documented (2 entries)
- ✅ Domain-Interface catalog created
- ✅ Multi-agent workflow defined
- ✅ AP-28 documented (Lambda imports)

**In Progress:**
- 🔄 EE codebase upgrade to EE 2.1
- 🔄 Domain-by-domain migration
- 🔄 AP-28 enforcement in plugins

**Pending:**
- ⏳ Complete EE 2.1 migration
- ⏳ Full compliance verification

---

## STATISTICS

**Total EE 2.1 Entries:** 17

**By Category:**
- Architecture: 6 comprehensive documents
- Anti-Patterns: 8 entries
- Decisions: 3 entries
- Python Anti-Patterns: 1 entry (AP-28)

**REF-IDs Used:**
- AP-EE-01 through AP-EE-08
- DEC-EE-01, DEC-EE-02, DEC-EE-03
- AP-28

---

## MAINTENANCE

**Last Updated:** 2026-01-01
**Update Frequency:** After adding new entries
**Maintenance Checklist:**
- [x] All EE 2.1 architecture entries listed
- [x] All anti-patterns listed
- [x] All decisions listed (including DEC-EE-03 for ISP merger)
- [x] Legacy knowledge marked deprecated
- [x] Links valid
- [x] REF-IDs unique
- [x] Domain count updated to 14 (ISP removed)

---

## RELATED DOCUMENTATION

**SIMA Base:**
- `/sima/Master-Index-of-Indexes.md`
- `/sima/SIMA-Quick-Reference-Card.md`

**Generic Knowledge:**
- `/sima/generic/` - Universal patterns
- `/sima/languages/python/` - Python-specific patterns

---

**END OF INDEX**

**Version:** 2.1.1
**Last Updated:** 2026-01-01
**Architecture Version:** EE 2.1
