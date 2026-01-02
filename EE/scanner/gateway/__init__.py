"""
EE Scanner Gateway Package - EE 2.1 Compliant

Scanner domain gateway for EE Universal Gateway System.
Provides centralized routing for all scanner operations.

EE 2.1 Architecture (100% EE-UG Compliant):
    - ScannerGateway - EE 2.1 compliant domain gateway
    - ScannerGatewayFactory - Factory for creating gateway instances
    - NO backward compatibility with EE 2.0
    - NO legacy execute_operation() function
    - Factory-driven construction only
    - DI-mandatory pattern

Usage (EE 2.1):
    # Create gateway factory with DI
    from EE.scanner.gateway import ScannerGatewayFactory

    factory = ScannerGatewayFactory(
        get_logger=logger_factory,
        get_metrics=metrics_factory,
        get_config=config_factory,
        call_operation=cross_domain_caller
    )

    # Create gateway instance
    gateway = factory.create_gateway()

    # Execute operations
    result = gateway.execute_domain_operation(
        interface="scan",
        operation="scan",
        path="D:/Code/EE/src"
    )

Architecture:
    External Code
        ↓ (execute_domain_operation with interface name)
    Scanner Gateway (ScannerGateway - DomainGateway subclass)
        ↓ (factory.create_interface())
    Scanner Interface (Interface router)
        ↓ (operation dispatch)
    Scanner Factory (Factory with business logic)
        ↓ (implementation)
    Result
"""

from __future__ import annotations

# EE 2.1 Gateway Components
from EE.scanner.gateway.gateway_factory import ScannerGatewayFactory
from EE.scanner.gateway.scanner_gateway_21 import ScannerGateway

__all__ = [
    # EE 2.1 Gateway (Factory-driven, DI-mandatory)
    'ScannerGateway',
    'ScannerGatewayFactory',
]

# **Version:** 2.0.0
# **Date:** 2026-01-01
# **Purpose:** Scanner gateway package exports (EE 2.1 only, no legacy)
# **Lines:** 63

