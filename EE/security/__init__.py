"""
Security Domain - UG-ISP Compliant

The Security Domain provides security capabilities:
- Authentication and authorization
- Data encryption and hashing
- Input validation and sanitization

This domain is UG-ISP compliant:
- Domain Gateway extends DomainGateway base class
- Interfaces use DISPATCH dictionary pattern
- Factories contain actual implementation
- NO imports outside the domain (except stdlib)
- All cross-domain calls via call_operation callback

Usage:
    from EE.security import SecurityGateway
    gateway = SecurityGateway()
    result = gateway.execute_domain_operation("authentication", "verify_password",
                                              password="secret", hash="...")
"""

from EE.security.security_gateway import SecurityGateway

__all__ = [
    "SecurityGateway",
]
