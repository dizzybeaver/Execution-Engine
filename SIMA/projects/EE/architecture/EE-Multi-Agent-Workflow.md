# EE Multi‑Agent Workflow Architecture  
**Version:** 2026.01.01.1  
**Status:** Updated for Factory‑Driven, Pooled, DI‑Centric UG Architecture  
**Scope:** SIMA → EE Governance & Enforcement Layer  
**Author:** EE Project

---

# 1. Purpose of This Document

This document defines the **multi‑agent governance and enforcement workflow** for the Execution Engine (EE).  
It describes how AI agents:

- Analyze EE code  
- Repair EE code  
- Enforce UG‑ISP architectural rules  
- Maintain consistency across 15 domains and ~285 operations  
- Ensure scalability, uniformity, and correctness  

This workflow is part of the **SIMA governance layer**, not the EE runtime.  
It ensures that EE remains:

- UG‑centric  
- Factory‑driven  
- DI‑based  
- Pooled  
- Uniform  
- Scalable  
- Wrapper‑safe  
- Cross‑domain‑clean  

This document is the **source of truth** for all AI agents interacting with EE.

---

# 2. Multi‑Agent System Overview

The EE multi‑agent system consists of three agent types:

1. **Coordinator Agent**  
   - Orchestrates the entire workflow  
   - Allocates Enforcers and Coders dynamically  
   - Manages iterations until 100% compliance  

2. **Architecture Compliance Enforcer Agents**  
   - Analyze EE code  
   - Detect violations of UG‑ISP rules  
   - Produce structured compliance reports  
   - Never modify code  

3. **Python UG‑Compliant Coding Agents**  
   - Repair code  
   - Generate new UG‑compliant modules  
   - Rewrite modules to remove violations  
   - Never analyze code beyond what is needed for repair  

The workflow is **iterative** and converges to full compliance.

---

# 3. Why Multi‑Agent Enforcement Exists

EE is a large, multi‑domain system:

- 15 domains  
- 285+ operations  
- 100+ directories  
- 500+ files  
- Multiple gateway construction patterns  
- Multiple interface patterns  
- Multiple factory patterns  
- Legacy code still being phased out  

Without automated enforcement:

- Wrappers creep back in  
- Cross‑domain imports appear  
- Factories get bypassed  
- Interfaces accumulate logic  
- Gateways become inconsistent  
- Singletons proliferate  
- DI boundaries erode  

The multi‑agent system prevents this.

---

# 4. High‑Level Workflow

```
User / Developer / Tool
    ↓
Coordinator Agent
    ↓ dispatch
Enforcer Agents (parallel)
    ↓ reports
Coordinator Agent
    ↓ tasks
Coder Agents (parallel)
    ↓ repaired code
Coordinator Agent
    ↓ re-dispatch
Enforcer Agents (parallel)
    ↓ reports
Coordinator Agent
    ↓
Converged? → YES → Final Output
           → NO → Loop
```

This loop continues until **all Enforcers report PASS**.

---

# 5. Workflow Phases (Detailed)

## 5.1 Phase 1 — Intake

Coordinator receives:

- Codebase snapshot  
- Optional metadata:
  - Domain registry  
  - Interface registry  
  - Operation catalog  
- Optional constraints:
  - Max iterations  
  - Time budget  
  - Domain focus  

Coordinator normalizes:

- File list  
- Domain/interface mapping  
- Operation mapping  
- Dependency graph  

---

## 5.2 Phase 2 — Enforcement

Coordinator spawns **N Enforcer Agents** (dynamic allocation).

Each Enforcer:

- Parses AST  
- Builds import graph  
- Builds call graph  
- Applies UG‑ISP rules:
  - No cross‑domain imports  
  - No interface‑to‑interface imports  
  - No bypassing UG  
  - No wrappers except domain‑local  
  - No logic in interfaces  
  - Factories must be execution units  
  - DI must be used  
  - Pools must be safe  
  - Gateway constructors must be uniform  
  - Registry must be DI‑injected  
  - No global singletons except allowed services  

Enforcer outputs:

```
COMPLIANCE REPORT
Status: PASS | FAIL
Violations:
  - rule: UG-IMP-001
    severity: HIGH
    description: Interface imported another domain
    location: EE/networking/http_client/interface.py:12
    suggested_fix: Replace direct import with call_operation
Confidence: 0.97
```

---

## 5.3 Phase 3 — Aggregation

Coordinator merges all reports:

- Deduplicates violations  
- Groups by:
  - File  
  - Domain  
  - Interface  
  - Severity  
- Computes:
  - Total violations  
  - Severity distribution  
  - Complexity score  
  - Confidence score  
  - Improvement rate (iteration‑to‑iteration)  

Coordinator decides:

- Whether to proceed to repair  
- How many Coders to deploy  
- How many Enforcers to deploy next iteration  
- Which files to assign to which Coder  

---

## 5.4 Phase 4 — Repair

Coordinator sends repair tasks to **M Coding Agents**.

Each Coder receives:

- Files to repair  
- Violations for those files  
- Relevant UG‑ISP rules  
- DI patterns  
- Gateway construction patterns  
- Pooling patterns  
- Interface isolation rules  

Coder performs:

- Import rewriting  
- Execution path correction  
- DI insertion  
- Factory extraction  
- Wrapper removal  
- Pooling fixes  
- Gateway constructor normalization  
- Registry injection fixes  
- Removal of global singletons  
- Replacement of cross‑domain imports with `call_operation`  

Coder outputs:

```
REPAIR SUMMARY
changed_files:
  - path: EE/networking/http_client/interface.py
    new_content: <updated code>
resolved_violations:
  - UG-IMP-001
  - UG-EXEC-004
unresolved_violations:
  - UG-POOL-002 (requires domain-level refactor)
rationale: "Moved logic to factory, replaced cross-domain import with call_operation"
confidence: 0.94
```

Coordinator integrates repaired code.

---

## 5.5 Phase 5 — Re‑Enforcement

Coordinator re‑runs Enforcers on:

- Entire codebase, or  
- Only changed files (configurable)  

Enforcers produce updated reports.

---

## 5.6 Phase 6 — Convergence

If:

- All Enforcers report PASS  
- No violations remain  
- All domains are consistent  
- All gateways follow uniform constructor pattern  
- All interfaces are isolated  
- All factories are execution‑only  
- All cross‑domain calls use `call_operation`  
- All pools are safe  
- No forbidden singletons exist  

Then workflow ends.

Coordinator outputs:

- Final codebase  
- Final compliance report  
- Iteration history  
- Metrics  

---

# 6. Dynamic Agent Allocation

Coordinator dynamically adjusts:

- Number of Enforcers  
- Number of Coders  
- Partitioning strategy  
- Iteration depth  

### Example heuristic:

| Violations | Enforcers | Coders |
|-----------|-----------|--------|
| > 50 | 5 | 3 |
| 10–50 | 3 | 2 |
| 1–10 | 2 | 1 |
| 0 | 1 | 0 |

Coordinator may also adjust based on:

- Severity distribution  
- Domain complexity  
- Confidence scores  
- Improvement rate  

---

# 7. Enforcement Rules (UG‑ISP)

Enforcers apply the following rule categories:

### 7.1 Import Rules
- No cross‑domain imports  
- No interface‑to‑interface imports  
- No importing UG or domain gateways inside interfaces  
- No importing factories across interfaces  

### 7.2 Execution Rules
- All operations must flow through UG  
- Interfaces must not execute logic  
- Factories must be execution units  
- No wrappers except domain‑local  

### 7.3 DI Rules
- Logger, metrics, config must be injected  
- No direct imports of logging/metrics/config modules  

### 7.4 Pooling Rules
- Pools must be safe  
- No shared mutable state unless explicitly safe  

### 7.5 Gateway Rules
- Gateways must use uniform constructor  
- Gateways must be built via DomainGatewayFactory  
- Registry must be DI‑injected  

### 7.6 Singleton Rules
- No global UG singleton  
- No global domain gateway singletons  
- Only config/logging/metrics may be long‑lived  

---

# 8. Interaction With SIMA

SIMA stores:

- Architecture docs  
- Anti‑patterns  
- Decisions  
- Lessons  
- Workflows  
- Knowledge indexes  

Agents reference SIMA for:

- Rule definitions  
- Patterns  
- Best practices  
- Domain/interface catalogs  
- Gateway construction patterns  
- DI patterns  
- Pooling patterns  

SIMA is the **knowledge layer**.  
EE is the **runtime layer**.  
The multi‑agent system is the **governance layer**.

---

# 9. Interaction With EE

Agents operate on:

- `EE/` source code  
- `EE/tools/scanner/`  
- `EE/universal_gateway/`  
- `EE/<domain>/<interface>/`  
- `EE/doc/`  

Agents must not modify:

- SIMA  
- Plugins  
- Reports  
- External integrations  

---

# 10. Invariants (Non‑Negotiable)

1. All operations must go through UG.  
2. UG must be constructed via factory + DI.  
3. No global UG singleton.  
4. No global registry singleton.  
5. Domain gateways must be built via DomainGatewayFactory.  
6. Interfaces must be isolated.  
7. Factories must be execution units.  
8. Cross‑domain calls must use `call_operation`.  
9. No direct imports across domains.  
10. Domain‑local wrappers allowed only under strict rules.  
11. Object pooling must be safe and deterministic.  
12. Observability and config must be injected.  
13. No backward compatibility with legacy gateway.  
14. Multi‑agent workflow must converge to 100% compliance.  

---

# 11. Summary

This document defines:

- The multi‑agent workflow  
- The responsibilities of each agent  
- The enforcement rules  
- The iteration cycle  
- The dynamic allocation strategy  
- The integration with SIMA and EE  
- The invariants that must always hold  

This is the **authoritative SIMA‑side specification** for EE’s multi‑agent governance system.

---

**End of Document 3**