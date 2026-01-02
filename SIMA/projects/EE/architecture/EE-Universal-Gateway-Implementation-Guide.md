# EE Universal Gateway Implementation Guide  
**Version:** 2026.01.01.1  
**Status:** Updated for Factory‑Driven, Pooled, DI‑Centric UG Architecture  
**Scope:** Execution Engine (EE/) — Implementation Specification  
**Author:** EE Project

---

# 1. Purpose of This Guide

This guide explains **how to implement** the Execution Engine (EE) using the updated Universal Gateway (UG) architecture defined in:

`EE-Universal-Gateway-Architecture.md`

Where the architecture document defines **what** the system is, this guide defines **how** to build it correctly inside the real EE tree.

This guide is written for:

- EE developers  
- AI agents performing code generation or repair  
- Tooling in `EE/tools/`  
- SIMA knowledge consumers  

---

# 2. Implementation Overview

The updated EE architecture uses:

- **UniversalGatewayFactory** → builds UG instances  
- **DomainGatewayFactory** → builds domain gateways  
- **InterfaceFactory** → builds interface instances  
- **Factory pools** → reuse expensive resources  
- **Dependency injection** → no global state  
- **Minimal singletons** → only for config/logging/metrics  
- **Uniform gateway construction** → all domains follow the same pattern  
- **Domain‑local wrappers** → allowed only inside the domain  

The public API remains:

```
execute_operation(domain, interface, operation, **kwargs)
```

But the internals are now **fully scalable and uniform**.

---

# 3. EE/__init__.py — Updated Execution Entry Point

The public entry point stays the same, but the internals change from a global singleton to a **UG factory + optional pool**.

## 3.1 New structure

```
from .universal_gateway.gateway_factory import UniversalGatewayFactory

_ug_factory = UniversalGatewayFactory()
_ug_pool = []

def _get_ug():
    if _ug_pool:
        return _ug_pool.pop()
    return _ug_factory.build_gateway()

def _return_ug(ug):
    _ug_pool.append(ug)

def execute_operation(domain, interface, operation, **kwargs):
    ug = _get_ug()
    try:
        return ug.execute_operation(domain, interface, operation, **kwargs)
    finally:
        _return_ug(ug)
```

### Key improvements:

- No global UG singleton  
- UG instances are DI‑constructed  
- Optional pooling for performance  
- Fully scalable across threads/processes  

---

# 4. UniversalGatewayFactory — Construction of UG Instances

File: `EE/universal_gateway/gateway_factory.py`

## 4.1 Responsibilities

- Build fully wired UG instances  
- Construct and inject:
  - LoggerFactory  
  - MetricsFactory  
  - ConfigService  
  - DomainRegistry  
  - DomainGatewayFactory  
- Provide optional UG pooling  

## 4.2 Example structure

```
class UniversalGatewayFactory:
    def __init__(self):
        self._logger_factory = LoggerFactory()
        self._metrics_factory = MetricsFactory()
        self._config_service = ConfigService()
        self._domain_registry = self._build_registry()
        self._domain_gateway_factory = DomainGatewayFactory(
            logger_factory=self._logger_factory,
            metrics_factory=self._metrics_factory,
            config_service=self._config_service,
        )

    def _build_registry(self):
        registry = DomainRegistry()
        registry.register("networking", self._domain_gateway_factory.build_networking_gateway)
        registry.register("foundation", self._domain_gateway_factory.build_foundation_gateway)
        # ... register all 15 domains
        return registry

    def build_gateway(self):
        return UniversalGateway(
            logger_factory=self._logger_factory,
            metrics_factory=self._metrics_factory,
            config_service=self._config_service,
            domain_registry=self._domain_registry,
            domain_gateway_factory=self._domain_gateway_factory,
        )
```

---

# 5. UniversalGateway — Updated Implementation

File: `EE/universal_gateway/gateway.py`

## 5.1 Constructor

```
class UniversalGateway:
    def __init__(self, logger_factory, metrics_factory, config_service,
                 domain_registry, domain_gateway_factory):
        self._logger_factory = logger_factory
        self._metrics_factory = metrics_factory
        self._config_service = config_service
        self._domain_registry = domain_registry
        self._domain_gateway_factory = domain_gateway_factory
```

## 5.2 Execution

```
def execute_operation(self, domain, interface, operation, **kwargs):
    gateway = self._domain_registry.resolve(domain)
    return gateway.execute_domain_operation(interface, operation, **kwargs)
```

## 5.3 Cross‑domain calls

```
def call_operation(self, domain, interface, operation, **kwargs):
    return self.execute_operation(domain, interface, operation, **kwargs)
```

---

# 6. DomainRegistry — Updated Implementation

File: `EE/universal_gateway/gateway_registry.py`

## 6.1 Responsibilities

- Store domain → gateway builder mappings  
- Provide thread‑safe resolution  
- No global singleton  
- Constructed by UG factory  

## 6.2 Example

```
class DomainRegistry:
    def __init__(self):
        self._domains = {}

    def register(self, domain_name, builder):
        self._domains[domain_name] = builder

    def resolve(self, domain_name):
        if domain_name not in self._domains:
            raise DomainNotFoundError(domain_name)
        return self._domains[domain_name]()
```

---

# 7. DomainGatewayFactory — Uniform Gateway Construction

File: `EE/universal_gateway/domain_gateway_factory.py`

## 7.1 Responsibilities

- Build domain gateways uniformly  
- Maintain per‑domain gateway pools  
- Inject DI into gateways  

## 7.2 Example

```
class DomainGatewayFactory:
    def __init__(self, logger_factory, metrics_factory, config_service):
        self._logger_factory = logger_factory
        self._metrics_factory = metrics_factory
        self._config_service = config_service
        self._pools = defaultdict(list)

    def _get_from_pool(self, domain):
        if self._pools[domain]:
            return self._pools[domain].pop()
        return None

    def _return_to_pool(self, domain, gateway):
        self._pools[domain].append(gateway)

    def build_networking_gateway(self):
        gw = self._get_from_pool("networking")
        if gw:
            return gw

        from EE.networking import NetworkingGateway
        return NetworkingGateway(
            domain_name="networking",
            get_logger=self._logger_factory,
            get_metrics=self._metrics_factory,
            get_config=self._config_service.get_for_domain,
            call_operation=None,  # UG injects this later
        )
```

---

# 8. DomainGateways — Updated Pattern

Each domain gateway must follow the uniform constructor:

```
class NetworkingGateway(DomainGateway):
    def __init__(self, domain_name, get_logger, get_metrics, get_config, call_operation):
        self._domain_name = domain_name
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation
        self._interfaces = {}
```

## 8.1 Responsibilities

- Validate interface names  
- Maintain interface pool  
- Delegate to interface instances  
- Never import outside domain  
- Never call other domains directly  

---

# 9. Interfaces — Updated Pattern

Interfaces live inside domain subdirectories.

Example:

`EE/networking/http_client/interface.py`

## 9.1 Responsibilities

- Map operation → factory method  
- Maintain factory pool  
- Use DI exclusively  
- Never import outside interface directory  

## 9.2 Example

```
class HttpClientInterface:
    def __init__(self, logger, metrics, config, call_operation):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation
        self._factory_pool = []

    def execute_operation(self, operation, **kwargs):
        factory = self._get_factory()
        try:
            if operation == "get":
                return factory.get(**kwargs)
            if operation == "post":
                return factory.post(**kwargs)
            raise InvalidOperationError(operation)
        finally:
            self._return_factory(factory)
```

---

# 10. Factories — Execution Units

Factories implement real logic.

## 10.1 Responsibilities

- Execute operations  
- Use DI  
- Maintain client pools  
- Never import outside interface  
- Use `call_operation` for cross‑domain behavior  

---

# 11. Domain‑Local Wrappers — Allowed Pattern

Example:

```
from .http_interface import execute_http_operation
```

Allowed if:

- Wrapper stays inside domain  
- Wrapper is thin and stateless  
- Wrapper does not bypass UG for cross‑domain calls  

---

# 12. Object Pooling — Implementation Details

Pooling layers:

- UG pool  
- Domain gateway pool  
- Interface pool  
- Factory pool  
- Client pool (HTTP sessions, DB connections, etc.)

### Rules:

- Pooled objects must be safe  
- No shared mutable state unless explicitly safe  
- Pools must be deterministic  

---

# 13. Adding a New Domain — Updated Procedure

1. Create `EE/<domain>/`  
2. Create `gateway.py` with uniform constructor  
3. Create interface subdirectories  
4. Create interface + factory files  
5. Register domain in `UniversalGatewayFactory._build_registry()`  
6. Add tests  
7. Document in SIMA  

---

# 14. Adding a New Interface — Updated Procedure

1. Create `EE/<domain>/<interface>/`  
2. Add:
   - `interface.py`
   - `factory.py`
   - `models.py` (optional)
   - `helpers.py` (optional)
3. Update domain gateway to build interface  
4. Add tests  
5. Document in SIMA  

---

# 15. Compliance and Enforcement

Compliance is enforced by:

- `EE/tools/scanner/`  
- Multi‑agent system:
  - Architecture Compliance Enforcer  
  - Python UG‑Compliant Coder  
  - Coordinator Agent  

These tools ensure:

- Interface isolation  
- Factory‑only execution  
- UG‑centric routing  
- No cross‑domain imports  
- No wrappers except domain‑local  
- Correct pooling patterns  

---

# 16. Summary

This implementation guide defines:

- How to construct UG instances  
- How to build domain gateways uniformly  
- How to build interfaces and factories  
- How to use DI and pooling  
- How to avoid singletons  
- How to scale EE horizontally  
- How to maintain UG‑ISP compliance  

This is the **official implementation specification** for EE 2.1+.

---

**End of Document 2**
