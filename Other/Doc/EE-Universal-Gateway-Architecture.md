# EE Universal Gateway Architecture  
**Version:** 2026.01.01.1  
**Status:** Updated for Factory‑Driven, Pooled, DI‑Centric UG Architecture  
**Scope:** Execution Engine (EE/) — Runtime Architecture Specification  
**Author:** EE Project

---

# 1. Purpose of This Document

This document defines the **Execution Engine (EE)** architecture using the **Universal Gateway (UG)** pattern, updated to support:

- **Factory‑driven construction**  
- **Object pooling at every layer**  
- **Dependency injection (DI)** as the primary wiring mechanism  
- **Minimal singleton usage** (only where safe and necessary)  
- **Uniform gateway construction across all domains**  
- **Scalable, testable, horizontally distributable execution**  
- **Strict UG‑ISP compliance**  
- **No wrappers except domain‑local interface wrappers**  

This is the **canonical architecture reference** for EE 2.1+.

---

# 2. High‑Level Architecture (Updated Model)

The EE uses a **Universal Gateway (UG)** as the single execution authority.

The updated execution flow is:

```
Application Code
    ↓ execute_operation(domain, interface, operation, **kwargs)
UniversalGateway (UG instance from UG Factory)
    ↓ resolve domain via DomainRegistry
DomainGateway (from DomainGatewayFactory + pool)
    ↓ resolve interface
Interface (from InterfaceFactory + pool)
    ↓ delegate to factory
Factory / Implementation (execution unit)
```

### Key differences from the old architecture:

| Old EE Architecture | New EE Architecture |
|---------------------|---------------------|
| Global UG singleton | UG Factory + optional UG pool |
| Global registry singleton | Registry is DI‑injected, not global |
| Mixed gateway construction patterns | Uniform gateway construction via DomainGatewayFactory |
| Some DI, some direct injection | Full DI across all layers |
| Some wrappers bypassed UG | Only domain‑local wrappers allowed |
| Limited pooling | Pooling at UG, domain gateway, interface, and factory levels |

---

# 3. Core Architectural Principles

## 3.1 Universal Gateway is the Only Execution Authority
All operations must go through:

```
execute_operation(domain, interface, operation, **kwargs)
```

No direct domain‑to‑domain calls.  
No direct interface‑to‑interface calls.  
No bypassing UG.

## 3.2 Factories + Object Pools Everywhere
Every major component is constructed by a factory and may be pooled:

- UniversalGatewayFactory → UG pool  
- DomainGatewayFactory → domain gateway pools  
- InterfaceFactory → interface pools  
- Factories inside interfaces → client pools (HTTP sessions, DB connections, etc.)

## 3.3 Dependency Injection (DI) is Mandatory
All components receive:

- `get_logger(name)`  
- `get_metrics(name)`  
- `get_config(name)`  
- `call_operation`  

No component may import these directly.

## 3.4 Minimal Singletons
Only the following may be long‑lived:

- LoggerFactory  
- MetricsFactory  
- ConfigService  
- DomainRegistry (optional)  

UG, domain gateways, interfaces, and factories **must not** be singletons.

## 3.5 Uniform Gateway Construction
Every domain gateway must follow the same constructor signature:

```
DomainGateway(
    domain_name: str,
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable,
)
```

## 3.6 Domain‑Local Interface Wrappers Are Allowed
Example:

```
from .http_interface import execute_http_operation
```

Allowed **only if**:

- They stay inside the same domain  
- They do not bypass UG for cross‑domain calls  
- They remain thin and stateless  

## 3.7 No Backward Compatibility
Legacy route‑based gateway patterns are **not supported**.

---

# 4. Updated Component Model

## 4.1 UniversalGatewayFactory (New)
Responsible for:

- Constructing UG instances  
- Injecting:
  - DomainRegistry  
  - DomainGatewayFactory  
  - LoggerFactory  
  - MetricsFactory  
  - ConfigService  
- Managing an optional **UG pool**  

UG is no longer a global singleton.

## 4.2 UniversalGateway (Updated)
UG now receives all dependencies via DI:

```
UniversalGateway(
    logger_factory,
    metrics_factory,
    config_service,
    domain_registry,
    domain_gateway_factory,
)
```

UG responsibilities:

- Validate domain/interface  
- Resolve domain gateway  
- Provide DI to domain gateways  
- Provide `call_operation` for cross‑domain calls  
- Enforce UG‑ISP invariants  

## 4.3 DomainRegistry (Updated)
Registry is now:

- A normal object  
- Constructed by UG factory  
- Passed into UG and DomainGatewayFactory  
- Holds:
  - Domain names  
  - Gateway builder functions  
  - Optional interface/operation metadata  

No more `get_instance()`.

## 4.4 DomainGatewayFactory (New)
Responsible for:

- Uniform construction of domain gateways  
- Maintaining a **per‑domain gateway pool**  
- Injecting DI into gateways  

This replaces the old mixed construction patterns.

## 4.5 DomainGateways (Updated)
Domain gateways must:

- Use the uniform constructor signature  
- Maintain an **interface pool**  
- Resolve interfaces  
- Delegate to interface instances  
- Never call other domains directly  

## 4.6 Interfaces (Updated)
Interfaces must:

- Map operations to factory methods  
- Maintain a **factory pool**  
- Use DI exclusively  
- Never import outside their interface directory  

## 4.7 Factories (Execution Units)
Factories must:

- Implement real logic  
- Use DI  
- Never import outside their interface  
- Use `call_operation` for cross‑domain behavior  
- Maintain client pools (HTTP sessions, DB connections, etc.)

---

# 5. Updated Execution Flow

### Step 1 — Caller invokes:
```
execute_operation("networking", "http_client", "get", url="...")
```

### Step 2 — UG Factory provides a UG instance
From pool or freshly built.

### Step 3 — UG resolves domain gateway
Via DomainRegistry.

### Step 4 — DomainGateway resolves interface
From interface pool.

### Step 5 — Interface delegates to factory
From factory pool.

### Step 6 — Factory executes operation
Using DI and internal client pools.

### Step 7 — Result returns up the chain

---

# 6. Cross‑Domain Behavior

All cross‑domain calls must use:

```
self._call_operation(domain, interface, operation, **kwargs)
```

Forbidden:

- Direct imports across domains  
- Direct instantiation of other domain interfaces  
- Domain‑to‑domain calls  

---

# 7. Object Pooling Strategy

Pooling layers:

| Layer | Pool Type | Purpose |
|-------|-----------|---------|
| UG | Optional pool | High concurrency, low overhead |
| DomainGatewayFactory | Per‑domain pool | Reuse domain gateways |
| DomainGateway | Interface pool | Reuse interface instances |
| Interface | Factory pool | Reuse clients/resources |
| Factory | Client pools | HTTP sessions, DB connections, etc. |

Rules:

- Pooled objects must be safe  
- No shared mutable state unless explicitly safe  
- Pools must be deterministic  

---

# 8. Domain and Interface Structure

Domains correspond to top‑level directories under `EE/`:

- `foundation/`  
- `observability/`  
- `security/`  
- `operations/`  
- `networking/`  
- `scanner/`  
- `test/`  
- `infrastructure/`  
- `cli/`  
- `doc/`  
- `sdk/`  
- `web/`  
- `dashboard/`  
- `ha/`  
- `isp/`  

Each domain:

- Has a domain gateway  
- Has multiple interfaces  
- Has domain‑local wrappers (optional)  
- Must not import outside its domain  

---

# 9. Domain‑Local Interface Wrappers (Allowed)

Example:

```
from .http_interface import execute_http_operation
```

Allowed if:

- Wrapper stays inside the domain  
- Wrapper does not bypass UG for cross‑domain calls  
- Wrapper is thin and stateless  
- Wrapper is not used outside the domain  

This pattern is **officially supported**.

---

# 10. Invariants (Non‑Negotiable)

1. All operations must go through UG.  
2. UG must be constructed via factory + DI.  
3. No global UG singleton.  
4. No global registry singleton.  
5. Domain gateways must be built via DomainGatewayFactory.  
6. Interfaces must be isolated.  
7. Factories must be the only execution units.  
8. Cross‑domain calls must use `call_operation`.  
9. No direct imports across domains.  
10. Domain‑local wrappers allowed only under strict rules.  
11. Object pooling must be safe and deterministic.  
12. Observability and config must be injected.  
13. No backward compatibility with legacy route‑based gateway.  

---

# 11. SIMA Integration

SIMA stores:

- Architecture docs  
- Anti‑patterns  
- Decisions  
- Lessons  
- Workflows  
- Knowledge indexes  

EE runtime enforces the rules; SIMA documents them.

---

# 12. Summary

This updated architecture:

- Removes global singletons  
- Introduces factories and pools at every layer  
- Makes DI the backbone of the system  
- Ensures uniform gateway construction  
- Supports horizontal scalability  
- Preserves UG‑ISP compliance  
- Allows domain‑local wrappers safely  
- Eliminates legacy gateway patterns  

This is the foundation for EE 2.1+.

---

**End of Document 1**
