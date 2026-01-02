"""
Universal Gateway (UG) - EE Core Architecture (EE 2.1)

UG Architecture Compliant - 100%
Single entry point: execute_operation(domain, interface, operation, **kwargs)

This module provides the clean architecture gateway system that replaces the
legacy route-based gateway with a proper domain/interface/operation pattern.

Architecture:
    UniversalGatewayFactory (creates UG instances)
        └── UniversalGateway (UG)
            └── DomainGatewayFactory (creates domain gateways)
                └── DomainGateway (per domain)
                    └── Interface Factory (per interface)
                        └── Interface Instance
                            └── Operations

Key Principles (EE 2.1):
1. Factory-driven construction (DEC-EE-01)
2. NO backward compatibility - only execute_operation()
3. Dependency injection for cross-cutting concerns (DEC-EE-02)
4. Clean separation of domains, interfaces, operations
5. Object pooling at all layers (ARCH-EE-09)
6. Type-safe with proper error handling
"""

from EE.universal_gateway.gateway import UniversalGateway, ConfigFactory
from EE.universal_gateway.gateway_registry import EEDomainRegistry
from EE.universal_gateway.domain_gateway import DomainGateway
from EE.universal_gateway.domain_gateway_factory import DomainGatewayFactory
from EE.universal_gateway.universal_gateway_factory import UniversalGatewayFactory

__all__ = [
    # Core classes
    'UniversalGateway',
    'EEDomainRegistry',
    'DomainGateway',

    # Factories (EE 2.1)
    'UniversalGatewayFactory',
    'DomainGatewayFactory',

    # Type protocols
    'ConfigFactory',
]
