# EE Template Repository Layout (Updated for UG 2.1+)
**Version:** 2026.01.01.2
**Status:** Authoritative Template Layout
**Scope:** Execution Engine (EE/) + SIMA/ + Agents/
**Author:** EE Project
**Last Updated:** 2026-01-01

---

# 1. Purpose of This Template

This template defines the **canonical repository layout** for the Execution Engine (EE) and its supporting systems:

- Universal Gateway (UG) runtime  
- Domain gateways  
- Interfaces  
- Factories  
- Object pools  
- Dependency injection roots  
- Multi‑agent governance system  
- SIMA knowledge system  
- Tools, scanners, and developer utilities  

This layout is optimized for:

- **Scalability**  
- **Uniformity**  
- **Factory‑driven construction**  
- **Dependency injection**  
- **Object pooling**  
- **Minimal singletons**  
- **UG‑ISP compliance**  
- **AI‑assisted governance**  

---

# 2. Top‑Level Repository Structure

```
Project/
├── EE/                                    # Execution Engine (runtime)
├── SIMA/                                  # Knowledge system (documentation + rules)
├── agents/                                # Multi-agent governance system
├── Plugins/                               # External integrations (Alexa, HA, etc.)
├── reports/                               # Generated reports
├── scripts/                               # Bootstrap, validation, orchestration scripts
├── tools/                                 # Developer tools (linters, scanners, generators)
├── docs/                                  # Architecture + implementation docs
└── README.md                              # Project overview
```

---

# 3. EE/ — Execution Engine (Runtime)

```
EE/
├── __init__.py                            # Public entry point: execute_operation()
│
├── universal_gateway/                     # UG core
│   ├── gateway.py                         # UniversalGateway (DI + pooled)
│   ├── gateway_factory.py                 # UniversalGatewayFactory (DI root)
│   ├── domain_gateway_factory.py          # DomainGatewayFactory (uniform builder)
│   ├── gateway_registry.py                # DomainRegistry (DI-injected)
│   └── __init__.py
│
├── foundation/                            # Domain: config, DI, utilities
│   ├── config/
│   ├── di/
│   ├── utility/
│   ├── initialization/
│   └── gateway.py
│
├── observability/                         # Domain: logging, metrics, debug, diagnosis
│   ├── logging/
│   ├── metrics/
│   ├── debug/
│   ├── diagnosis/
│   └── gateway.py
│
├── security/                              # Domain: auth, encryption, validation
│   ├── authentication/
│   ├── encryption/
│   ├── validation/
│   └── gateway.py
│
├── networking/                            # Domain: HTTP, WS, protocols
│   ├── http_client/
│   ├── websocket_client/
│   ├── protocols/
│   │   ├── redis/
│   │   ├── mqtt/
│   │   ├── ldap/
│   │   ├── snmp/
│   │   ├── ntp/
│   │   ├── memcached/
│   │   └── rpc/
│   └── gateway.py
│
├── operations/                            # Domain: caching, file I/O, pooling, templates
│   ├── cache/
│   ├── fileio/
│   ├── serialization/
│   ├── template/
│   ├── object_pool/
│   ├── circuit_breaker/
│   └── gateway.py
│
├── scanner/                               # Domain: security scanning + UG compliance scanning
│   ├── core/
│   ├── interface/
│   ├── gateway/
│   └── gateway.py
│
├── test/                                  # Domain: testing framework
│   ├── pytest/
│   ├── report/
│   ├── scanner/
│   └── gateway.py
│
├── infrastructure/                        # Domain: DB, cache, storage
│   ├── plugins/
│   └── gateway.py
│
├── cli/                                   # Domain: CLI + shell
│   └── gateway.py
│
├── doc/                                   # Domain: documentation generation
│   └── gateway.py
│
├── sdk/                                   # Domain: SDK bindings
│   └── gateway.py
│
├── web/                                   # Domain: web server + handlers
│   ├── static/
│   ├── templates/
│   └── gateway.py
│
├── dashboard/                             # Domain: dashboard UI
│   └── gateway.py
│
├── ha/                                    # Domain: Home Assistant integration
│   └── gateway.py
│
├── config/                                # EE configuration files
│   ├── ee_config.yaml
│   ├── ee_server_config.yaml
│   └── server_settings.yaml
│
├── tools/                                 # Developer tools
│   ├── dev/                               # Factory generator, linter, registry tools
│   └── scanner/                           # UG compliance scanner
│
└── tests/                                 # Test suites
```

---

# 4. SIMA/ — Knowledge System

```
SIMA/
├── projects/
│   └── EE/
│       ├── architecture/
│       │   ├── EE-Universal-Gateway-Architecture.md
│       │   ├── EE-Universal-Gateway-Implementation-Guide.md
│       │   ├── EE-Multi-Agent-Workflow.md
│       │   ├── EE-UG-Rules-For-AI-Agents.md
│       │   └── EE-Domain-Interface-Catalog.md (NEW)
│       ├── anti-patterns/
│       ├── decisions/
│       ├── lessons/
│       ├── config/
│       ├── modes/
│       ├── indexes/
│       └── README.md
```

---

# 5. agents/ — Multi‑Agent Governance System

```
agents/
├── coordinator/
│   ├── coordinator_agent.md
│   ├── coordinator_logic.py
│   └── coordinator_state.py
│
├── enforcers/
│   ├── architecture_compliance_enforcer.md
│   ├── enforcer_logic.py
│   └── rule_definitions.py
│
└── coders/
    ├── python_ug_compliant_coder.md
    ├── coder_logic.py
    └── repair_strategies.py
```

---

# 6. docs/ — Architecture & Implementation Docs

```
docs/
├── EE-Template-Repository-Layout.md
├── EE-Universal-Gateway-Architecture.md
├── EE-Universal-Gateway-Implementation-Guide.md
├── Multi-Agent-Workflow.md
└── UG-Rules-For-AI-Agents.md
```

---

# 7. scripts/ — Bootstrap & Validation

```
scripts/
├── bootstrap_ee_project.py                # Creates EE skeleton
├── validate_ee_repo.py                    # Validates UG-ISP compliance
├── run_coordinator.py                     # Runs multi-agent workflow
├── run_enforcer.py                        # Runs enforcer manually
└── run_coder.py                           # Runs coder manually
```

---

# 8. tools/ — Developer Tools

```
tools/
├── linter/                                # UG-ISP linter
├── generator/                             # Factory + interface generators
└── scanner/                               # UG compliance scanner
```

---

# 9. NEW: EE-Domain-Interface-Catalog.md

This is a new file that should be added to SIMA:

`SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md`

It will contain:

- All 15 domains  
- All interfaces per domain  
- All operations per interface  
- DI requirements  
- Pooling requirements  
- Cross‑domain rules  
- Wrapper rules  