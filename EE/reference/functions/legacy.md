# Legacy Domains - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Status:** Legacy (Need EE 2.1 Upgrade)
**Purpose:** Reference for legacy domains before migration

---

## Overview

This document provides reference information for legacy EE domains that have not yet been upgraded to EE 2.1 UG-ISP architecture. These domains are scheduled for migration.

**Legacy Domains:** 6 (cli, doc, sdk, web, dashboard, ha)
**Status:** Pending EE 2.1 Upgrade

---

## 1. CLI Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** CLIGatewayDomain class
**File:** `EE/cli/cli_gateway.py`

### Required Changes for EE 2.1

1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: command, parser, completion
3. Implement uniform constructor
4. Use DomainGatewayFactory

### Current Operations

**Command execution:**
```python
# OLD (Current)
from EE.cli.cli_gateway import CLIGatewayDomain
cli = CLIGatewayDomain()
result = cli.execute_command("status")

# NEW (After EE 2.1 upgrade)
result = execute_operation(
    domain="cli",
    interface="command",
    operation="execute",
    command="status"
)
```

---

## 2. Doc Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DocGatewayDomain class
**File:** `EE/doc/doc_gateway_domain.py`

### Required Changes for EE 2.1

1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: generator, renderer, exporter
3. Implement uniform constructor
4. Use DomainGatewayFactory

### Current Operations

**Documentation generation:**
```python
# OLD (Current)
from EE.doc.doc_gateway_domain import DocGatewayDomain
doc = DocGatewayDomain()
result = doc.generate_docs("networking")

# NEW (After EE 2.1 upgrade)
result = execute_operation(
    domain="doc",
    interface="generator",
    operation="generate",
    target="networking",
    format="markdown"
)
```

---

## 3. SDK Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** SDKGatewayDomain class
**File:** `EE/sdk/sdk_gateway_domain.py`

### Required Changes for EE 2.1

1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: local, remote, bindings
3. Implement uniform constructor
4. Use DomainGatewayFactory

### Current Operations

**SDK operations:**
```python
# OLD (Current)
from EE.sdk.sdk_gateway_domain import SDKGatewayDomain
sdk = SDKGatewayDomain()
result = sdk.call_sdk("homeassistant", "get_states")

# NEW (After EE 2.1 upgrade)
result = execute_operation(
    domain="sdk",
    interface="remote",
    operation="call",
    sdk="homeassistant",
    method="get_states"
)
```

---

## 4. Web Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** WebGatewayDomain class
**File:** `EE/web/web_gateway_domain.py`

### Required Changes for EE 2.1

1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: server, handler, middleware
3. Implement uniform constructor
4. Use DomainGatewayFactory

### Current Operations

**Web server operations:**
```python
# OLD (Current)
from EE.web.web_gateway_domain import WebGatewayDomain
web = WebGatewayDomain()
web.start_server(port=8080)

# NEW (After EE 2.1 upgrade)
execute_operation(
    domain="web",
    interface="server",
    operation="start",
    port=8080,
    host="0.0.0.0"
)
```

---

## 5. Dashboard Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DashboardGatewayDomain class
**File:** `EE/dashboard/dashboard_gateway.py`

### Required Changes for EE 2.1

1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: ui, api, widgets
3. Implement uniform constructor
4. Use DomainGatewayFactory

### Current Operations

**Dashboard operations:**
```python
# OLD (Current)
from EE.dashboard.dashboard_gateway import DashboardGatewayDomain
dash = DashboardGatewayDomain()
dash.render_dashboard("main")

# NEW (After EE 2.1 upgrade)
result = execute_operation(
    domain="dashboard",
    interface="ui",
    operation="render",
    dashboard="main",
    format="html"
)
```

---

## 6. HA Domain

**Status:** Factory Pattern (Needs EE 2.1 Standardization)
**Current Pattern:** ha_gateway_factory.py
**Files:** `EE/ha/ha_gateway_factory.py`, `EE/ha/ha_command_gateway_factory.py`, `EE/ha/ha_routing_gateway_factory.py`

### Required Changes for EE 2.1

1. Convert to DomainGatewayFactory pattern
2. Create interfaces: entities, services, events
3. Implement uniform constructor
4. Use DI-injected DomainGatewayFactory

### Current Operations

**Home Assistant operations:**
```python
# OLD (Current)
from EE.ha.ha_gateway_factory import ha_gateway_factory
ha = ha_gateway_factory()
states = ha.get_states()

# NEW (After EE 2.1 upgrade)
states = execute_operation(
    domain="ha",
    interface="entities",
    operation="list"
)
```

---

## Migration Priority

1. **HA Domain** (High Value) - Active usage, critical functionality
2. **CLI Domain** (High Value) - Command-line interface
3. **SDK Domain** (Medium Value) - SDK bindings
4. **Web Domain** (Medium Value) - Web server
5. **Doc Domain** (Low Value) - Documentation generation
6. **Dashboard Domain** (Low Value) - Dashboard UI

---

## EE 2.1 Upgrade Checklist

For each legacy domain:

- [ ] Convert gateway to DomainGateway subclass
- [ ] Implement uniform constructor (DI-injected)
- [ ] Create interface factories
- [ ] Move logic to factories
- [ ] Remove cross-domain imports
- [ ] Add interface isolation
- [ ] Implement object pooling
- [ ] Add comprehensive tests
- [ ] Update documentation
- [ ] Create migration guide

---

## Temporary Access Pattern

While domains are being migrated, use temporary wrapper:

```python
# Temporary wrapper for legacy domains
def legacy_execute(domain, operation, **kwargs):
    # Map legacy domains to current implementations
    legacy_gateways = {
        "cli": CLIGatewayDomain(),
        "doc": DocGatewayDomain(),
        "sdk": SDKGatewayDomain(),
        "web": WebGatewayDomain(),
        "dashboard": DashboardGatewayDomain(),
        "ha": ha_gateway_factory()
    }

    gateway = legacy_gateways.get(domain)
    if not gateway:
        raise DomainNotFoundError(f"Legacy domain {domain} not found")

    return gateway.execute(operation, kwargs)
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain catalog (section 4)
- [EE-Universal-Gateway-Implementation-Guide.md](../../SIMA/projects/EE/architecture/EE-Universal-Gateway-Implementation-Guide.md) - Implementation guide

**Migration Guides:**
- [LESS-EE-09](../../SIMA/projects/EE/lessons/LESS-EE-09-DISPATCH-Pattern-Migration.md) - DISPATCH pattern migration
- [LESS-EE-10](../../SIMA/projects/EE/lessons/LESS-EE-10-Migration-Validation-Checklist.md) - Migration checklist

**Implementation:**
- Individual domain directories in `EE/`

---

**END OF LEGACY DOMAINS REFERENCE**

**Version:** 1.0.0
**Lines:** 249
