# EE Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Purpose:** Complete function reference for all EE domains and operations
**Type:** Function Reference Documentation

---

## Overview

This directory contains comprehensive function reference documentation for all EE (Execution Engine) domains. Each domain is documented with its interfaces, operations, parameters, return values, and usage examples.

---

## Quick Reference

**Total Domains:** 14
- **UG-ISP Compliant:** 8 domains
- **Legacy:** 6 domains

**Total Operations:** ~170 operations across ~41 interfaces

---

## Domain Reference Files

| Domain | File | Status | Operations |
|--------|------|--------|------------|
| [Foundation](foundation.md) | [foundation.md](foundation.md) | UG-ISP | ~20 |
| [Observability](observability.md) | [observability.md](observability.md) | UG-ISP | ~15 |
| [Security](security.md) | [security.md](security.md) | UG-ISP | ~10 |
| [Operations](operations.md) | [operations.md](operations.md) | UG-ISP | ~25 |
| [Networking](networking.md) | [networking.md](networking.md) | UG-ISP | ~35 |
| [Scanner](scanner.md) | [scanner.md](scanner.md) | UG-ISP | ~20 |
| [Test](test.md) | [test.md](test.md) | UG-ISP | ~10 |
| [Infrastructure](infrastructure.md) | [infrastructure.md](infrastructure.md) | UG-ISP | ~5 |
| [Legacy Domains](legacy.md) | [legacy.md](legacy.md) | Legacy | ~30 |

---

## Usage Pattern

All EE operations follow the Universal Gateway pattern:

```python
from EE import execute_operation

result = execute_operation(
    domain="<domain>",
    interface="<interface>",
    operation="<operation>",
    **kwargs
)
```

---

## Example Usage

```python
# Foundation - Get configuration
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
    message="System started",
    context={"component": "api"}
)

# Security - Encrypt data
encrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value="secret data",
    algorithm="aes-256-gcm"
)

# Networking - HTTP GET
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="get",
    url="https://api.example.com/data",
    headers={"Authorization": "Bearer token"}
)

# Operations - Cache get
cached = execute_operation(
    domain="operations",
    interface="cache",
    operation="get",
    key="user:123"
)
```

---

## Error Handling

```python
from EE.universal_gateway import (
    DomainNotFoundError,
    InterfaceNotFoundError,
    OperationNotFoundError,
    InvalidOperationError,
)

try:
    result = execute_operation(
        domain="foundation",
        interface="config",
        operation="get",
        key="timeout"
    )
except DomainNotFoundError as e:
    print(f"Domain not registered: {e}")
except InterfaceNotFoundError as e:
    print(f"Interface not found in domain: {e}")
except OperationNotFoundError as e:
    print(f"Operation not found: {e}")
except InvalidOperationError as e:
    print(f"Execution failed: {e}")
```

---

## Cross-Domain Operations

Domains can call operations in other domains through `call_operation`:

```python
# Example: Security domain calling Foundation for config
class SecurityGateway(DomainGateway):
    def __init__(self, get_logger, get_metrics, call_operation):
        super().__init__(
            domain_name="security",
            get_logger=get_logger,
            get_metrics=get_metrics,
            call_operation=call_operation
        )

    def get_encryption_key(self):
        # Cross-domain call to Foundation
        return self._call_operation(
            domain="foundation",
            interface="config",
            operation="get",
            key="security.encryption.key"
        )
```

---

## Convention Notes

### Parameter Naming
- `key` - Configuration keys, cache keys
- `value` - Values to set/encrypt
- `url` - HTTP/HTTPS URLs
- `target` - Network targets (hostnames, IPs)
- `message` - Log messages
- `data` - Generic data payloads
- `**kwargs` - Domain-specific parameters

### Return Values
- Operations return domain-specific types
- Common returns: strings, dicts, lists, booleans, None
- Complex operations return structured data (objects, named tuples)

### Error Handling
- All operations may raise `InvalidOperationError`
- Domain-specific errors may be raised
- Check individual operation documentation for details

---

## Architecture Compliance

This documentation reflects **EE 2.1 UG-ISP Architecture**:

✅ Factory-driven construction
✅ Dependency injection
✅ Object pooling
✅ Interface isolation
✅ Uniform gateway constructor

**For architecture details:** See [EE-Universal-Gateway-Architecture.md](../../SIMA/projects/EE/architecture/EE-Universal-Gateway-Architecture.md)

---

## Related Documentation

**Project Documentation:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Complete domain inventory
- [EE-Universal-Gateway-Implementation-Guide.md](../../SIMA/projects/EE/architecture/EE-Universal-Gateway-Implementation-Guide.md) - Implementation guide

**Quick References:**
- [Universal Gateway README](../../universal_gateway/README.md) - UG usage and architecture
- [PROJECT-MODE-EE.md](../../SIMA/projects/EE/modes/PROJECT-MODE-EE.md) - Development guidelines

---

## Maintenance

**Last Updated:** 2026-01-02
**Update Frequency:** After adding new domains, interfaces, or operations
**Maintenance:** Keep in sync with EE-Domain-Interface-Catalog.md

---

**END OF README**

**Version:** 1.0.0
**Lines:** 207 (within limits)
