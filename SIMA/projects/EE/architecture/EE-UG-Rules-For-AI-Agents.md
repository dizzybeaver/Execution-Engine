# EE UG Rules for AI Agents  
**Version:** 2026.01.01.1  
**Status:** Authoritative SIMA Rulebook for AI Agents  
**Scope:** SIMA → EE Governance Layer  
**Author:** EE Project

---

# 1. Purpose of This Document

This document defines the **mandatory rules** that all AI agents must follow when:

- Analyzing EE code  
- Repairing EE code  
- Generating new EE modules  
- Refactoring EE domains, interfaces, or factories  
- Modifying UG, domain gateways, or registry logic  
- Working inside the EE repository  

These rules ensure that all AI‑generated or AI‑modified code remains:

- **UG‑centric**  
- **Factory‑driven**  
- **Dependency‑injected**  
- **Object‑pooled**  
- **Uniform across all domains**  
- **Scalable and horizontally distributable**  
- **Wrapper‑safe**  
- **Cross‑domain‑clean**  
- **UG‑ISP compliant**  

These rules are **non‑negotiable**.

---

# 2. Core Principles AI Agents Must Enforce

AI agents must enforce the following architectural principles:

1. **Universal Gateway is the only execution authority**  
2. **Factories + object pools at every layer**  
3. **Dependency injection (DI) everywhere**  
4. **Minimal singletons** (only config/logging/metrics allowed)  
5. **Uniform gateway construction**  
6. **Interfaces must be isolated**  
7. **Factories must be execution units**  
8. **Cross‑domain calls must use `call_operation`**  
9. **Domain‑local wrappers allowed only under strict rules**  
10. **No backward compatibility with legacy gateway**  
11. **Registry must be DI‑injected, not global**  
12. **UG must be built via factory, not global singleton**  
13. **All code must be horizontally scalable**  

---

# 3. Universal Gateway Rules

## 3.1 UG Construction Rules

AI agents must ensure:

- UG is constructed via **UniversalGatewayFactory**  
- UG receives:
  - `logger_factory`
  - `metrics_factory`
  - `config_service`
  - `domain_registry`
  - `domain_gateway_factory`
- UG is **not** a global singleton  
- UG may be pooled, but pooling must be explicit and safe  

Forbidden:

- Global `_ug` singleton  
- Static `get_instance()` patterns  
- Hard‑coded domain gateway imports inside UG  

## 3.2 UG Execution Rules

AI agents must ensure:

- All operations flow through:

```
execute_operation(domain, interface, operation, **kwargs)
```

- UG resolves domain gateways via registry  
- UG injects `call_operation` into domain gateways  
- UG does not execute domain logic directly  

Forbidden:

- Direct domain gateway calls  
- Direct interface calls  
- Direct factory calls  

---

# 4. Domain Gateway Rules

## 4.1 Construction Rules

AI agents must enforce:

- All domain gateways must use the **uniform constructor**:

```
DomainGateway(
    domain_name: str,
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable,
)
```

- All domain gateways must be built via **DomainGatewayFactory**  
- DomainGatewayFactory must maintain a **per‑domain pool**  
- Domain gateways must not be global singletons  

Forbidden:

- Mixed constructor signatures  
- Domain gateways built directly in `__init__.py`  
- Domain gateways storing global state  

## 4.2 Behavior Rules

Domain gateways must:

- Validate interface names  
- Maintain an interface pool  
- Delegate to interface instances  
- Never import outside their domain  
- Never call other domains directly  

Forbidden:

- Cross‑domain imports  
- Cross‑domain calls without `call_operation`  
- Logic inside domain gateways  

---

# 5. Interface Rules

## 5.1 Construction Rules

Interfaces must:

- Live inside domain subdirectories  
- Use DI exclusively  
- Maintain a **factory pool**  
- Expose a single public method:

```
execute_operation(operation, **kwargs)
```

Forbidden:

- Importing UG  
- Importing domain gateways  
- Importing other interfaces  
- Importing factories from other interfaces  

## 5.2 Behavior Rules

Interfaces must:

- Map operations to factory methods  
- Delegate execution to factories  
- Maintain minimal state  
- Use injected dependencies  

Forbidden:

- Implementing business logic  
- Performing cross‑domain calls directly  
- Creating global state  

---

# 6. Factory Rules

Factories are the **execution units**.

AI agents must enforce:

- Factories implement real logic  
- Factories use DI  
- Factories maintain client pools (HTTP sessions, DB connections, etc.)  
- Factories never import outside their interface  
- Factories use `call_operation` for cross‑domain behavior  

Forbidden:

- Logic inside interfaces  
- Logic inside domain gateways  
- Cross‑domain imports  
- Global state  

---

# 7. Registry Rules

AI agents must enforce:

- DomainRegistry is a normal object  
- Registry is constructed by UG factory  
- Registry is injected into UG  
- Registry stores domain → builder mappings  
- Registry must not be a global singleton  

Forbidden:

- `EEDomainRegistry.get_instance()` patterns  
- Static global registries  
- Hard‑coded domain gateway imports inside UG  

---

# 8. Dependency Injection Rules

AI agents must enforce:

- Logger, metrics, config must be injected  
- No direct imports of logging/metrics/config modules  
- DI must flow:

```
UG → DomainGateway → Interface → Factory
```

Forbidden:

- Direct imports of `logging` inside interfaces  
- Direct imports of config files inside factories  
- Hard‑coded metrics/logging calls  

---

# 9. Object Pooling Rules

AI agents must enforce:

- UG may be pooled  
- Domain gateways must be pooled  
- Interfaces must be pooled  
- Factories must be pooled  
- Client resources must be pooled  

Rules:

- Pooled objects must be safe  
- No shared mutable state unless explicitly safe  
- Pools must be deterministic  

Forbidden:

- Hidden global state  
- Unsafe reuse of objects  
- Non‑deterministic pooling  

---

# 10. Cross‑Domain Rules

AI agents must enforce:

- All cross‑domain behavior must use:

```
call_operation(domain, interface, operation, **kwargs)
```

Forbidden:

- Direct imports across domains  
- Direct instantiation of other domain interfaces  
- Domain‑to‑domain calls  

---

# 11. Wrapper Rules

AI agents must enforce:

- Only **domain‑local wrappers** are allowed  
- Wrappers must be thin and stateless  
- Wrappers must not bypass UG for cross‑domain calls  
- Wrappers must not leak outside the domain  

Allowed example:

```
from .http_interface import execute_http_operation
```

Forbidden:

- Cross‑domain wrappers  
- Wrapper layers that bypass UG  
- Wrapper layers that accumulate logic  

---

# 12. Legacy Rules

AI agents must enforce:

- No backward compatibility with legacy gateway  
- No `execute(route, payload)` patterns  
- No route‑based dispatch  
- No legacy gateway imports  

---

# 13. AI Agent Behavior Rules

## 13.1 Enforcer Agents Must:

- Analyze code  
- Detect violations  
- Produce structured compliance reports  
- Never modify code  
- Never generate code  
- Never declare compliance without analysis  

## 13.2 Coding Agents Must:

- Repair code  
- Generate new UG‑compliant modules  
- Rewrite modules to remove violations  
- Never analyze code beyond repair context  
- Never declare overall compliance  

## 13.3 Coordinator Agent Must:

- Orchestrate Enforcers and Coders  
- Manage iterations  
- Allocate agents dynamically  
- Declare completion only when all Enforcers PASS  

---

# 14. Compliance Report Format

AI agents must use:

```
COMPLIANCE REPORT
Status: PASS | FAIL
Violations:
  - rule: <rule_id>
    severity: LOW | MEDIUM | HIGH | CRITICAL
    description: <description>
    location: <file:line>
    suggested_fix: <fix>
Confidence: <0.0 - 1.0>
```

---

# 15. Repair Summary Format

Coding agents must output:

```
REPAIR SUMMARY
changed_files:
  - path: <path>
    new_content: <code>
resolved_violations:
  - <rule_id>
unresolved_violations:
  - <rule_id>
rationale: <explanation>
confidence: <0.0 - 1.0>
```

---

# 16. Invariants (Non‑Negotiable)

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
15. AI agents must follow this rulebook exactly.  

---

# 17. Summary

This document defines the **complete rulebook** for AI agents interacting with EE.  
It ensures that all AI‑generated or AI‑modified code remains:

- Scalable  
- Uniform  
- DI‑centric  
- Factory‑driven  
- Pooled  
- UG‑ISP compliant  
- Free of wrappers except domain‑local  
- Free of cross‑domain imports  
- Free of global singletons  

This is the **authoritative SIMA governance document** for EE.

---

**End of Document 4**