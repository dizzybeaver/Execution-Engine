# DEC-EE-03: ISP Domain Merger into Networking Domain

**Category:** Architecture Decision
**Status:** Active (EE 2.1)
**EE Version:** 2.1
**Date:** 2026-01-01
**REF-ID:** DEC-EE-03
**Supersedes:** ISP domain as separate domain

---

## Decision

**The ISP domain has been absorbed into the networking domain as the `connectivity` interface. The standalone ISP domain is removed from EE 2.1 architecture.**

---

## Context

### Previous State

EE 2.1 architecture listed 15 domains, including a standalone `isp` domain with factory pattern status:

```
15. isp - ISP operations
   Status: Factory Pattern (Needs EE 2.1 Standardization)
   Current Pattern: isp_gateway_factory.py
```

### Problem Identified

The standalone ISP domain created multiple issues:

1. **Scanner Confusion**
   - AI scanners and linters confused "ISP" (Internet Service Provider operations) with "UG-ISP" (Universal Gateway - Interface-Separated Pattern)
   - False positives in compliance checking
   - Ambiguous terminology in documentation

2. **Structural Misalignment**
   - ISP operations are fundamentally networking operations
   - No clear separation between networking and ISP concerns
   - ISP operations fit naturally within networking domain's responsibility

3. **Architectural Redundancy**
   - ISP domain would need networking interfaces anyway
   - Unnecessary cross-domain calls for connectivity operations
   - Violates principle of domain cohesion

### Domain Structure Violation

EE 2.1 architecture principles state:
- Domains should be cohesive and self-contained
- Domains should minimize cross-domain dependencies
- Related functionality should be grouped together

The ISP domain violated these by separating connectivity operations from the networking domain where they naturally belong.

---

## Decision

### Chosen Approach: Absorb ISP as Networking Interface

The ISP domain is **removed** as a standalone domain. All ISP operations are now provided through:

```
networking.connectivity interface
```

### New Domain Count

**Before:** 15 domains
**After:** 14 domains

### Removed Entry

```
15. isp - ISP operations [REMOVED]
```

### Updated Networking Domain

The networking domain now includes:

| Interface | Operations | Description |
|-----------|-----------|-------------|
| connectivity | check_connection, test_latency, diagnose_connection, get_network_info, resolve_dns | ISP/network connectivity operations |
| http_client | get, post, put, delete, patch, request | HTTP operations |
| websocket_client | connect, send, receive, close | WebSocket client |
| redis | get, set, delete, hget, hset, publish | Redis client |
| mqtt | connect, publish, subscribe, unsubscribe | MQTT client |
| ldap | search, bind, unbind, add, modify | LDAP client |
| snmp | get, set, walk, trap | SNMP client |
| ntp | get_time, sync_time, check_sync | NTP client |
| memcached | get, set, delete, add, replace | Memcached client |
| rpc | call, notify, batch, register | RPC client |

### Operation Pattern

```python
# OLD PATTERN (DEPRECATED):
result = execute_operation(
    domain="isp",
    interface="operations",
    operation="check_connection",
    target="example.com"
)

# NEW PATTERN:
result = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="check_connection",
    target="example.com"
)
```

---

## Alternatives Considered

### Option 1: Keep ISP as Separate Domain

**Description:** Maintain ISP as standalone domain, upgrade to EE 2.1 UG-ISP pattern

**Pros:**
- Clear separation of concerns (networking vs ISP-specific)
- Domain autonomy for ISP operations

**Cons:**
- Terminology confusion (ISP vs UG-ISP)
- Scanner false positives
- Unnecessary cross-domain calls
- Domain fragmentation for related functionality

**Rejected:** Terminology confusion and architectural redundancy made this unacceptable

### Option 2: Rename ISP Domain

**Description:** Rename ISP domain to "connectivity" domain to avoid confusion

**Pros:**
- Eliminates ISP/UG-ISP confusion
- Maintains domain separation

**Cons:**
- Still fragments networking operations
- Connectivity IS networking
- Cross-domain complexity remains
- Redundant domain structure

**Rejected:** Doesn't solve architectural problem of fragmenting related functionality

### Option 3: Absorb ISP into Networking (CHOSEN)

**Description:** Merge ISP operations as networking.connectivity interface

**Pros:**
- Eliminates terminology confusion
- Cohesive domain structure
- No cross-domain calls for connectivity
- Follows natural domain boundaries
- Simpler architecture

**Cons:**
- Networking domain becomes larger
- Less domain autonomy for ISP operations

**Accepted:** Benefits outweigh drawbacks. Networking domain is properly scoped to include all connectivity operations.

---

## Rationale

### Primary Factors

1. **Eliminate Terminology Confusion**
   - "ISP" and "UG-ISP" are too similar
   - Caused scanner false positives
   - Confused developers and AI agents

2. **Architectural Cohesion**
   - ISP operations ARE networking operations
   - Natural fit within networking domain
   - Follows principle of domain cohesion

3. **Simplify Compliance**
   - Cleaner UG-ISP compliance checking
   - No ambiguous domain names
   - Clearer domain boundaries

### Constraints Accepted

- Networking domain now has 10 interfaces (was 9)
- Networking gateway handles more responsibility
- ISP operations no longer have separate domain autonomy

These constraints are acceptable because:
- Networking domain is properly scoped for connectivity
- Interface isolation still enforced
- Operations are naturally related

---

## Consequences

### Positive

1. **Eliminated Confusion**
   - No ISP/UG-ISP terminology conflict
   - Clearer scanner compliance
   - Better documentation clarity

2. **Improved Architecture**
   - More cohesive domain structure
   - Reduced cross-domain calls
   - Follows natural domain boundaries

3. **Simplified Compliance**
   - UG-ISP scanners work without confusion
   - Domain count reduced to 14
   - Cleaner domain catalog

4. **Better Developer Experience**
   - All connectivity in one place
   - Simpler routing (all networking -> networking domain)
   - Clearer operation patterns

### Negative

1. **Larger Networking Domain**
   - Now has 10 interfaces
   - May seem less modular
   - More complex gateway

2. **Less ISP Autonomy**
   - No separate ISP domain
   - ISP operations mixed with general networking

### Risks

1. **Networking Domain Complexity**
   - **Risk:** Networking domain becomes too large
   - **Mitigation:** Interface isolation keeps boundaries clear; 10 interfaces is manageable

2. **Legacy Code Migration**
   - **Risk:** Existing code calling `domain="isp"` breaks
   - **Mitigation:** Provide migration guide; support old routes with deprecation warnings

---

## Implementation

### Changes Required

1. **Update Domain Catalog**
   - Remove ISP domain entry from EE-Domain-Interface-Catalog.md
   - Add networking.connectivity interface
   - Update domain count: 15 → 14

2. **Update Indexes**
   - Remove ISP from EE-Index-Main.md domain list
   - Update total domain count
   - Update statistics

3. **Update Documentation**
   - Remove ISP from EE-Template-Repository-Layout.md
   - Update operation examples
   - Document networking.connectivity interface

4. **Create Decision Entry**
   - Document this decision (DEC-EE-03)
   - Explain rationale and consequences
   - Provide migration guide

### Migration Path

**For code using ISP domain:**

```python
# BEFORE (deprecated):
execute_operation(
    domain="isp",
    interface="operations",
    operation="check_connection",
    target="example.com"
)

# AFTER:
execute_operation(
    domain="networking",
    interface="connectivity",
    operation="check_connection",
    target="example.com"
)
```

**File locations:**
- Remove: `EE/src/isp/` (if exists)
- Add: `EE/src/networking/interfaces/connectivity/`

---

## Validation

### Success Metrics

1. **Zero ISP/UG-ISP Confusion**
   - Scanners no longer false-positive on ISP
   - Documentation is clear
   - Developers understand domain structure

2. **Compliance Verification**
   - All UG-ISP checks pass without ISP-related false positives
   - Domain catalog shows 14 domains
   - Networking domain includes connectivity interface

3. **Code Migration**
   - All `domain="isp"` calls migrated to `domain="networking", interface="connectivity"`
   - No orphaned ISP references in codebase
   - Tests updated

### Indicators for Reconsideration

- Networking domain becomes unwieldy (>15 interfaces)
- ISP operations need separate autonomy
- Scanner confusion returns

---

## Outcome

**Status:** Decision implemented 2026-01-01

**Actual Results:**
- Domain catalog updated to 14 domains
- networking.connectivity interface documented
- All SIMA knowledge updated
- Zero ISP/UG-ISP confusion in subsequent scans

**Lessons:**
- Domain names should avoid architectural terminology conflicts
- Related functionality belongs in same domain
- Early elimination of confusing naming prevents technical debt

---

## Related Decisions

**Builds on:**
- **DEC-EE-01:** Factory-Driven UG Construction - Establishes domain gateway pattern
- **DEC-EE-02:** DI-Mandatory Architecture - Establishes DI requirements for all domains

**Supersedes:**
- ISP domain as standalone domain (EE 2.1 architecture draft)

**Related to:**
- **EE-Domain-Interface-Catalog.md:** Complete domain/interface inventory
- **EE-UG-Rules-For-AI-Agents.md:** AI agent rulebook for domain structure

---

**Keywords:** domain merge, ISP, networking, connectivity, UG-ISP, terminology, architecture, EE 2.1

**Related:** EE-Domain-Interface-Catalog.md, EE-Index-Main.md, EE-Template-Repository-Layout.md

**Status:** Active

**Version History:**
- v1.0.0 (2026-01-01): Initial decision documenting ISP domain merger

---

**END OF DEC-EE-03**
