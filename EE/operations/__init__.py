"""
Operations Domain - UG-ISP Compliant

The Operations Domain provides operational EE capabilities:
- Caching operations with LRU eviction
- Fault tolerance and circuit breaker pattern
- File I/O operations
- Data serialization (JSON, pickle, etc.)
- Template operations and rendering
- Generic object pooling for resource management
- Thread pool management and concurrent execution

This domain is UG-ISP compliant:
- Domain Gateway extends DomainGateway base class
- Interfaces use DISPATCH dictionary pattern
- Factories contain actual implementation
- NO imports outside the domain (except stdlib)
- All cross-domain calls via call_operation callback

Usage:
    from EE.operations import OperationsGateway
    gateway = OperationsGateway()
    result = gateway.execute_domain_operation("cache", "get", key="user:123")
"""

# Lazy import to avoid issues when src module is not available
try:
    from EE.operations.operations_gateway import OperationsGateway
    _gateway_available = True
except ImportError:
    _gateway_available = False

__all__ = [
    "OperationsGateway",
]
