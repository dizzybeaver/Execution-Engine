"""
Foundation Domain - UG-ISP Compliant

The Foundation Domain provides fundamental EE capabilities:
- Configuration management
- Singleton instances
- Utility functions
- Dependency injection
- System initialization

This domain is UG-ISP compliant:
- Domain Gateway extends DomainGateway base class
- Interfaces use DISPATCH dictionary pattern
- Factories contain actual implementation
- NO imports outside the domain (except stdlib)
- All cross-domain calls via call_operation callback

Usage:
    from EE.foundation import FoundationGateway
    gateway = FoundationGateway()
    result = gateway.execute_domain_operation("config", "get", key="cache")
"""

from EE.foundation.foundation_gateway import FoundationGateway

__all__ = [
    "FoundationGateway",
]
