"""EE (Execution Engine) - Universal Execution Platform (EE 2.1).

Version: 2.1.0
Architecture: UG Domain Architecture with Factory-Driven Construction

Key Changes from EE 2.0:
    - UniversalGatewayFactory instead of global singleton (DEC-EE-01)
    - Mandatory dependency injection (DEC-EE-02)
    - Object pooling for performance (ARCH-EE-09)
    - Uniform gateway constructors (DEC-EE-03)
    - DomainGatewayFactory for all gateway construction

Usage:
    from EE import execute_operation
    result = execute_operation(domain="foundation", interface="config",
                             operation="get", key="database.host")
"""

from __future__ import annotations

__version__ = "2.1.0"
__author__ = "EE Project"

import logging
import threading
from typing import Any, Optional, List

def _get_ug() -> UniversalGateway:
    """Get UG instance from pool or create new one (EE 2.1)."""
    global _ug_pool
    if _ug_pool:
        return _ug_pool.pop()
    return _create_ug()

def _return_ug(ug: UniversalGateway) -> None:
    """Return a UG instance to the pool (EE 2.1)."""
    global _ug_pool, _ug_max_pool_size

    if len(_ug_pool) < _ug_max_pool_size:
        _ug_pool.append(ug)

# ============================================================================
# Public API
# ============================================================================

def execute_operation(
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    """SINGLE entry point for EE operations (EE 2.1)."""
    with _ug_lock:
        ug = _get_ug()

    try:
        result = ug.execute_operation(domain, interface, operation, **kwargs)
        return result
    finally:
        with _ug_lock:
            _return_ug(ug)

def get_ug() -> UniversalGateway:
    """Get the Universal Gateway instance (EE 2.1 compatible)."""
    with _ug_lock:
        return _get_ug()

def get_registry() -> EEDomainRegistry:
    """Get domain registry instance (creates fresh registry, no singleton)."""
    ug = get_ug()
    registry = EEDomainRegistry()

    for domain_name in ug.list_domains():
        gateway = ug.get_domain_gateway(domain_name)
        registry.register(domain_name, gateway)

    return registry

__all__ = [
    "execute_operation",
    "get_ug",
    "get_registry",
    "UniversalGateway",
    "EEDomainRegistry",
    "DomainGatewayFactory",
]
