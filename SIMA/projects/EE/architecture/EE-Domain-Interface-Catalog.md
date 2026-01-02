# EE Domain-Interface Catalog

**Version:** 2026.01.01.2
**Status:** EE 2.1 Architecture Specification
**Scope:** Complete catalog of all 14 EE domains and their interfaces
**Date:** 2026-01-01
**Author:** EE Project

---

# 1. Purpose of This Catalog

This catalog provides a **complete inventory** of all EE 2.1 domains, interfaces, and operations. It serves as:

- The **authoritative reference** for EE's operation surface
- A **routing guide** for the Universal Gateway
- A **discovery tool** for developers using EE
- A **compliance checklist** for EE 2.1 upgrades

---

# 2. Domain Summary

| # | Domain | Status | Interfaces | Operations | Notes |
|---|--------|--------|-----------|------------|-------|
| 1 | foundation | UG-ISP | 5 | ~20 | Config, DI, utilities |
| 2 | observability | UG-ISP | 4 | ~15 | Logging, metrics, debug |
| 3 | security | UG-ISP | 3 | ~10 | Auth, encryption, validation |
| 4 | operations | UG-ISP | 7 | ~25 | Cache, file I/O, pooling |
| 5 | networking | UG-ISP | 10 | ~35 | HTTP, protocols, clients, connectivity |
| 6 | scanner | UG-ISP | 8 | ~20 | Security scanning, compliance |
| 7 | test | UG-ISP | 3 | ~10 | Pytest, reporting |
| 8 | infrastructure | UG-ISP | 1 | ~5 | Plugin management |
| 9 | cli | Legacy | 0 | ~5 | Command-line interface |
| 10 | doc | Legacy | 0 | ~5 | Documentation generation |
| 11 | sdk | Legacy | 0 | ~5 | SDK bindings |
| 12 | web | Legacy | 0 | ~5 | Web server |
| 13 | dashboard | Legacy | 0 | ~5 | Dashboard UI |
| 14 | ha | Factory | 0 | ~5 | Home Assistant integration |

**Total:** 14 domains, ~41 interfaces, ~170 operations

**Note:** ISP domain removed in EE 2.1, merged into networking.connectivity (see DEC-EE-03)

---

# 3. Domain Details

## 3.1 Foundation Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** FoundationGateway
**Purpose:** Configuration, dependency injection, utilities

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| config | get, set, list, delete, reload | Configuration management |
| di | inject, resolve, singleton | Dependency injection |
| initialization | init, bootstrap, shutdown | System initialization |
| singleton | get, reset, exists | Singleton management |
| utility | parse, validate, sanitize | Utility functions |

### DI Requirements
- `get_logger` - Logger factory function
- `get_metrics` - Metrics factory function
- `get_config` - Config getter function
- `call_operation` - Cross-domain operation caller

### Pooling Requirements
- Config readers: Pool of 5-10 instances
- DI containers: Singleton pool

### Cross-Domain Rules
- May call: security.encryption for encrypted config values
- May call: observability.logging for init logging
- Must use: `call_operation` for all cross-domain calls

---

## 3.2 Observability Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** ObservabilityGateway
**Purpose:** Logging, metrics, debugging

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| logging | info, warning, error, debug, critical | Structured logging |
| metrics | increment, gauge, timing, histogram | Metrics collection |
| debug | breakpoint, inspect, trace | Debug utilities |
| diagnosis | health_check, status, diagnostics | System diagnosis |

### DI Requirements
- `get_logger` - Logger factory (self-referential)
- `get_metrics` - Metrics factory (self-referential)
- `get_config` - Config for observability settings
- `call_operation` - Cross-domain calls

### Pooling Requirements
- Loggers: Singleton pool per name
- Metrics collectors: Pool of 5-10 instances

### Cross-Domain Rules
- All domains may call: observability.logging
- All domains may call: observability.metrics
- May call: foundation.config for logger config

---

## 3.3 Security Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** SecurityGateway
**Purpose:** Authentication, encryption, validation

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| authentication | login, logout, verify, refresh | Auth operations |
| encryption | encrypt, decrypt, hash, verify_hash | Cryptography |
| validation | validate_input, sanitize, check_permission | Input validation |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for security settings
- `call_operation` - Cross-domain calls

### Pooling Requirements
- Encryption engines: Pool of 3-5 instances
- Auth sessions: Pool of 10-20 instances

### Cross-Domain Rules
- May be called by: All domains (for auth/encryption)
- May call: foundation.config for security config
- May call: observability.logging for audit logs

---

## 3.4 Operations Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** OperationsGateway
**Purpose:** Caching, file I/O, pooling, templates

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| cache | get, set, delete, clear, exists | Caching operations |
| fileio | read, write, delete, exists, list | File operations |
| object_pool | acquire, release, size, clear | Object pooling |
| circuit_breaker | check_state, record_success, record_failure | Circuit breaker |
| serialization | serialize, deserialize, to_json, from_json | Data serialization |
| template | render, compile, load_template | Template rendering |
| threading_ops | spawn, join, cancel, list_threads | Thread management |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for operations
- `call_operation` - Cross-domain calls

### Pooling Requirements
- File handles: Pool of 10-20 instances
- Cache connections: Pool of 5-10 instances
- Thread pools: Configurable pool sizes

### Cross-Domain Rules
- May be called by: All domains (for caching/file I/O)
- May call: foundation.config for cache config
- May call: observability.metrics for cache metrics

---

## 3.5 Networking Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** NetworkingGateway
**Purpose:** HTTP clients, protocol clients, networking, connectivity

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| connectivity | check_connection, test_latency, diagnose_connection, get_network_info, resolve_dns | Network connectivity operations |
| http_client | get, post, put, delete, patch, request | HTTP operations |
| websocket_client | connect, send, receive, close | WebSocket client |
| redis | get, set, delete, hget, hset, publish | Redis client |
| mqtt | connect, publish, subscribe, unsubscribe | MQTT client |
| ldap | search, bind, unbind, add, modify | LDAP client |
| snmp | get, set, walk, trap | SNMP client |
| ntp | get_time, sync_time, check_sync | NTP client |
| memcached | get, set, delete, add, replace | Memcached client |
| rpc | call, notify, batch, register | RPC client |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for networking
- `call_operation` - Cross-domain calls

### Pooling Requirements
- HTTP sessions: Pool of 10-20 instances
- WebSocket connections: Pool of 5-10 instances
- Protocol connections: Pool per protocol
- Connectivity checkers: Pool of 3-5 instances

### Cross-Domain Rules
- May be called by: All domains (for networking)
- May call: foundation.config for connection config
- May call: security.authentication for auth
- May call: observability.logging for connection logs

### Networking Operations Examples

```python
# Connectivity - Check connection
status = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="check_connection",
    target="example.com"
)

# Connectivity - Test latency
latency = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="test_latency",
    target="api.example.com",
    count=5
)

# Connectivity - Get network info
info = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="get_network_info"
)

# HTTP GET (existing)
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="get",
    url="https://api.example.com/data"
)
```

---

## 3.6 Scanner Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** ScannerGateway
**Purpose:** Security scanning, UG-ISP compliance checking

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| scan | run_scan, scan_target, generate_report | Security scanning |
| validate | validate_compliance, check_rules | Compliance validation |
| test | run_tests, generate_coverage | Test execution |
| report | generate, export, format | Report generation |
| cache | get, set, invalidate | Scan result caching |
| cleanup | clean_artifacts, purge_temp | Cleanup operations |
| compile | compile_rules, validate_rules | Rule compilation |
| utility | parse, format, transform | Scanner utilities |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for scanner
- `call_operation` - Cross-domain calls

### Pooling Requirements
- Scanner instances: Pool of 3-5 instances
- Report generators: Pool of 5-10 instances

### Cross-Domain Rules
- May call: All domains (for compliance checking)
- May call: observability.logging for scan logs
- May call: operations.cache for scan result caching

---

## 3.7 Test Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** TestGateway
**Purpose:** Testing framework, test execution

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| pytest | run, collect, coverage, list_tests | Pytest operations |
| report | generate, export, compare | Test reporting |
| scanner | scan_tests, find_coverage | Test scanning |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for testing
- `call_operation` - Cross-domain calls

### Pooling Requirements
- Test runners: Pool of 3-5 instances
- Report generators: Pool of 5-10 instances

### Cross-Domain Rules
- May call: All domains (for testing)
- May call: observability.logging for test logs
- May call: operations.fileio for test file access

---

## 3.8 Infrastructure Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Gateway:** InfrastructureGateway
**Purpose:** Plugin management, infrastructure operations

### Interfaces

| Interface | Operations | Description |
|-----------|-----------|-------------|
| plugins | load, unload, list, register, status | Plugin management |

### DI Requirements
- `get_logger` - Logger factory
- `get_metrics` - Metrics factory
- `get_config` - Config for infrastructure
- `call_operation` - Cross-domain calls

### Pooling Requirements
- Plugin loaders: Pool of 3-5 instances

### Cross-Domain Rules
- May call: All domains (plugin dependencies)
- May call: operations.fileio for plugin loading

---

# 4. Legacy Domains (Need EE 2.1 Upgrade)

## 4.1 CLI Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** CLIGatewayDomain class
**Required Changes:**
1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: command, parser, completion
3. Implement uniform constructor
4. Use DomainGatewayFactory

## 4.2 Doc Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DocGatewayDomain class
**Required Changes:**
1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: generator, renderer, exporter
3. Implement uniform constructor
4. Use DomainGatewayFactory

## 4.3 SDK Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** SDKGatewayDomain class
**Required Changes:**
1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: local, remote, bindings
3. Implement uniform constructor
4. Use DomainGatewayFactory

## 4.4 Web Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** WebGatewayDomain class
**Required Changes:**
1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: server, handler, middleware
3. Implement uniform constructor
4. Use DomainGatewayFactory

## 4.5 Dashboard Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DashboardGatewayDomain class
**Required Changes:**
1. Convert to UG-ISP DomainGateway pattern
2. Create interfaces: ui, api, widgets
3. Implement uniform constructor
4. Use DomainGatewayFactory

## 4.6 HA Domain

**Status:** Factory Pattern (Needs EE 2.1 Standardization)
**Current Pattern:** ha_gateway_factory.py
**Required Changes:**
1. Convert to DomainGatewayFactory pattern
2. Create interfaces: entities, services, events
3. Implement uniform constructor
4. Use DI-injected DomainGatewayFactory

---

# 5. Domain Changes History

## Removed Domains

### ISP Domain (Removed 2026-01-01)

**Reason:** Terminology confusion with UG-ISP pattern and architectural redundancy
**Decision:** DEC-EE-03
**Details:** ISP operations absorbed into networking domain as `connectivity` interface
**Migration:** All `domain="isp"` calls changed to `domain="networking", interface="connectivity"`

---

# 6. EE 2.1 Compliance Requirements

For every domain, the following MUST be true:

1. **Uniform Gateway Constructor:**
   ```python
   DomainGateway(
       domain_name: str,
       get_logger: Callable,
       get_metrics: Callable,
       get_config: Callable,
       call_operation: Callable,
   )
   ```

2. **DomainGatewayFactory Usage:**
   - All gateways built via DomainGatewayFactory
   - Per-domain gateway pools maintained

3. **Interface Isolation:**
   - No cross-domain imports
   - No interface-to-interface imports
   - All imports local to interface directory

4. **Factory Execution:**
   - Interfaces delegate to factories
   - Factories contain all logic
   - No logic in interfaces or gateways

5. **DI Compliance:**
   - Logger, metrics, config injected
   - No direct imports of logging/metrics/config
   - call_operation injected for cross-domain calls

6. **Pooling Compliance:**
   - Safe, deterministic pooling
   - No shared mutable state
   - Explicit pool sizes

---

# 7. Operation Reference

All operations follow the pattern:
```python
result = execute_operation(
    domain="<domain>",
    interface="<interface>",
    operation="<operation>",
    **kwargs
)
```

### Examples

```python
# Foundation - Get config value
config = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)

# Observability - Log message
execute_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="System started"
)

# Security - Encrypt data
encrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value="secret data"
)

# Networking - Connectivity check
status = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="check_connection",
    target="example.com"
)

# Networking - HTTP GET
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="get",
    url="https://api.example.com/data"
)
```

---

**END OF CATALOG**
