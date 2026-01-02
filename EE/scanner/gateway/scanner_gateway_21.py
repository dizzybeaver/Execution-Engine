"""Scanner Gateway - EE 2.1 Compliant

Domain gateway for scanner operations with factory-driven construction
and DI-mandatory pattern.

EE 2.1 Architecture:
- Extends DomainGateway base class
- Uniform constructor (5 DI parameters)
- Factory-driven interface creation
- No business logic (routing only)

Based on:
- EE/universal_gateway/domain_gateway.py (base class)
- EE/operations/cache/cache_gateway.py (reference implementation)
"""

from __future__ import annotations

from typing import Any, Callable


# =============================================================================
# Interface Factory Functions (Phase 2: Scan complete, others stubs)
# =============================================================================

# ADDED: Import ScanInterfaceFactory from new EE 2.1 interface (Phase 2 complete)
from EE.scanner.interface.scan.scanner_scan_interface_21 import (
    ScanInterfaceFactory as _ScanInterfaceFactoryImpl
)

# ADDED: Import ValidateInterfaceFactory from new EE 2.1 interface (STUB)
from EE.scanner.interface.validate.scanner_validate_interface_21 import (
    ValidateInterfaceFactory as _ValidateInterfaceFactoryImpl
)

# ADDED: Import TestInterfaceFactory from new EE 2.1 interface (STUB)
from EE.scanner.interface.test.scanner_test_interface_21 import (
    TestInterfaceFactory as _TestInterfaceFactoryImpl
)

def ScanInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create ScanInterface instances.

    ✅ PHASE 2 COMPLETE - Now implemented with ScanFactory

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name (e.g., "scanner")
        interface_name: Interface name (e.g., "scan")

    Returns:
        ScanInterface instance (routers to ScanFactory)
    """
    # MODIFIED: Phase 2 complete - delegate to actual factory
    return _ScanInterfaceFactoryImpl(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


def CompileInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create CompileInterface instances.

    PHASE 3: Will be implemented with CompileFactory
    """
    raise NotImplementedError(
        "CompileInterfaceFactory: Phase 3 implementation pending."
    )


def ValidateInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create ValidateInterface instances.

    STUB: EE 2.1 compliant router (no factory yet)

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name (e.g., "scanner")
        interface_name: Interface name (e.g., "validate")

    Returns:
        ValidateInterface stub instance (raises NotImplementedError for operations)
    """
    # Delegate to actual factory
    return _ValidateInterfaceFactoryImpl(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


def TestInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create TestInterface instances.

    STUB: EE 2.1 compliant router (no factory yet)

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name (e.g., "scanner")
        interface_name: Interface name (e.g., "test")

    Returns:
        TestInterface stub instance (raises NotImplementedError for operations)
    """
    # Delegate to actual factory
    return _TestInterfaceFactoryImpl(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


def ReportInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create ReportInterface instances.

    PHASE 3: Will be implemented with ReportFactory
    """
    raise NotImplementedError(
        "ReportInterfaceFactory: Phase 3 implementation pending."
    )


def CacheInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create CacheInterface instances.

    PHASE 3: Will be implemented with CacheFactory
    """
    raise NotImplementedError(
        "CacheInterfaceFactory: Phase 3 implementation pending."
    )


def CleanupInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create CleanupInterface instances.

    PHASE 3: Will be implemented with CleanupFactory
    """
    raise NotImplementedError(
        "CleanupInterfaceFactory: Phase 3 implementation pending."
    )


def UtilityInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> Any:
    """Factory function to create UtilityInterface instances.

    PHASE 3: Will be implemented with UtilityFactory
    """
    raise NotImplementedError(
        "UtilityInterfaceFactory: Phase 3 implementation pending."
    )


# =============================================================================
# Import DomainGateway Base Class
# =============================================================================

# ADDED: Lazy import to avoid circular dependency
from EE.universal_gateway.domain_gateway import DomainGateway


# =============================================================================
# Scanner Gateway - EE 2.1 Compliant
# =============================================================================

class ScannerGateway(DomainGateway):
    """Scanner domain gateway (EE 2.1 compliant).

    Responsibilities:
    - Register all 8 scanner interface factories
    - Route operations to appropriate interfaces
    - NO business logic (routing only)

    EE 2.1 Compliance:
    - Extends DomainGateway base class
    - Uniform constructor with 5 DI parameters
    - Factory-driven interface creation
    - Interface isolation enforced

    Usage:
        factory = ScannerGatewayFactory(get_logger, get_metrics, get_config, call_operation)
        gateway = factory.create_gateway()
        result = gateway.execute_domain_operation(
            interface="scan",
            operation="scan",
            path="D:\\\\Code\\\\EE\\\\src"
        )
    """

    # ADDED: EE 2.1 compliant constructor
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ) -> None:
        """Initialize scanner gateway with DI (EE 2.1).

        Args:
            domain_name: Domain name ("scanner")
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        # ADDED: Call parent constructor (DomainGateway requirement)
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation,
        )

        # ADDED: Register all 8 scanner interfaces
        self._register_interfaces()

        # MODIFIED: Use parent's logger (created by DomainGateway)
        self.logger.debug("ScannerGateway initialized with EE 2.1 DI pattern")

    # ADDED: Register interface factories
    def _register_interfaces(self) -> None:
        """Register all scanner interface factories.

        EE 2.1 Pattern:
        - Interface factory functions receive DI
        - Registered with base class's register_interface method
        - Stubs for Phase 1, implementations in Phase 2-3
        """
        # Register all 8 interfaces
        self.register_interface("scan", ScanInterfaceFactory)
        self.register_interface("compile", CompileInterfaceFactory)
        self.register_interface("validate", ValidateInterfaceFactory)
        self.register_interface("test", TestInterfaceFactory)
        self.register_interface("report", ReportInterfaceFactory)
        self.register_interface("cache", CacheInterfaceFactory)
        self.register_interface("cleanup", CleanupInterfaceFactory)
        self.register_interface("utility", UtilityInterfaceFactory)

        self.logger.info("Registered 8 scanner interfaces (Phase 1: stub implementations)")

# =============================================================================
# REMOVED: Unnecessary execute_domain_operation() override (FIXED CRITICAL BUG)
# =============================================================================
# The DomainGateway base class already provides execute_domain_operation().
# The previous override called non-existent _execute_via_interface() method,
# which would cause AttributeError at runtime.
#
# Base class method (domain_gateway.py:195-277) handles:
# - Interface validation
# - Interface creation via factory with DI
# - Operation execution
#
# ScannerGateway now relies on base class implementation.
# =============================================================================



# =============================================================================
# End of File
# =============================================================================
#
# **Version:** 1.2.0
# **Date:** 2026-01-01
# **Purpose:** EE 2.1 compliant scanner gateway (CRITICAL BUGS FIXED)
# **Lines:** 270
