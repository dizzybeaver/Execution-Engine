"""Scanner Interfaces - EE 2.1 UG-ISP Compliant Interface Layer.

EE 2.1 Architecture Rules:
- NO cross-interface imports (each interface is isolated)
- Each interface exports only its own functionality
- Gateway handles routing between interfaces
- Use EE 2.1 ScannerGateway for cross-interface operations

Correct Usage (EE 2.1):
    from EE.scanner.gateway import ScannerGateway, ScannerGatewayFactory

    factory = ScannerGatewayFactory(get_logger, get_metrics, get_config, call_operation)
    gateway = factory.create_gateway()
    result = gateway.execute_domain_operation("scan", "scan", path="D:/Code/EE/src")

Legacy Usage (EE 2.0 - DEPRECATED):
    from EE.scanner.interface import execute_scan_operation  # DO NOT USE
"""

from __future__ import annotations

__all__ = []  # Intentionally empty - interfaces are isolated in EE 2.1

