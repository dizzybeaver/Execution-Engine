"""Scan Interface Router - EE 2.1 Compliant

Thin router that delegates to ScanFactory for all business logic.

EE 2.1 Architecture:
- Interface is a thin router only (no business logic)
- Factory contains all implementation
- Pool management for factory instances
- DI propagation to factory

Based on:
- EE/operations/cache/cache_interface.py (router pattern reference)
"""

from __future__ import annotations

from typing import Any, Callable
import threading

# ADDED: Import factory
from EE.scanner.interface.scan.scan_factory import ScanFactory


# =============================================================================
# Scan Interface Router - EE 2.1 Compliant
# =============================================================================

class ScanInterface:
    """Scan interface router (EE 2.1 compliant).

    Responsibilities:
    - Route operations to ScanFactory
    - Manage factory pool (3-5 instances)
    - NO business logic (routing only)

    EE 2.1 Compliance:
    - Receives DI in constructor
    - Routes to factory methods
    - Factory pool for performance
    - Cross-domain calls via call_operation
    """

    # MODIFIED: EE 2.1 compliant constructor with DI
    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ) -> None:
        """Initialize scan interface with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        # Store DI functions
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

        # Factory pool (size 3-5)
        self._factory_pool: list[ScanFactory] = []
        self._pool_lock = threading.RLock()
        self._POOL_SIZE = 5

        # Create logger for interface
        self.logger = get_logger("scanner.scan.interface")

    # MODIFIED: Get factory from pool or create new
    def _get_factory(self) -> ScanFactory:
        """Get ScanFactory from pool or create new instance.

        Returns:
            ScanFactory instance
        """
        with self._pool_lock:
            if self._factory_pool:
                factory = self._factory_pool.pop()
                self.logger.debug("Retrieved factory from pool")
                return factory

        # Create new instance outside lock
        factory = ScanFactory(
            get_logger=self._get_logger,
            get_metrics=self._get_metrics,
            get_config=self._get_config,
            call_operation=self._call_operation,
        )
        self.logger.debug("Created new ScanFactory instance")
        return factory

    # MODIFIED: Return factory to pool
    def _return_factory(self, factory: ScanFactory) -> None:
        """Return ScanFactory instance to pool.

        Args:
            factory: Factory instance to return

        EE 2.1 Pattern:
        - Return to pool if under max size
        - Otherwise let it be garbage collected
        - Thread-safe pool access
        """
        with self._pool_lock:
            if len(self._factory_pool) < self._POOL_SIZE:
                self._factory_pool.append(factory)
                self.logger.debug(f"Returned factory to pool (pool size: {len(self._factory_pool)})")
            else:
                self.logger.debug("Pool at max capacity, discarding factory")

    # MODIFIED: Main router method
    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Route scan operation to factory.

        Args:
            operation: Operation name (scan)
            **kwargs: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown

        EE 2.1 Pattern:
        - Get factory from pool
        - Route to factory method
        - Return factory to pool
        """
        self.logger.debug(f"Routing scan.{operation}")

        # Get factory from pool
        factory = self._get_factory()

        try:
            # Dispatch to factory method
            if operation == "scan":
                return factory.scan(**kwargs)
            else:
                # Unknown operation
                raise ValueError(
                    f"Unknown scan operation: '{operation}'. "
                    f"Valid: scan"
                )
        finally:
            # Always return factory to pool
            self._return_factory(factory)

    # MODIFIED: Pool management (optional)
    def get_pool_stats(self) -> dict:
        """Get factory pool statistics.

        Returns:
            Dictionary with pool stats
        """
        with self._pool_lock:
            return {
                "current_size": len(self._factory_pool),
                "max_size": self._POOL_SIZE,
                "utilization": round(len(self._factory_pool) / self._POOL_SIZE * 100, 2)
                if self._POOL_SIZE > 0 else 0
            }

    def clear_pool(self) -> int:
        """Clear factory pool.

        Returns:
            Number of instances cleared
        """
        with self._pool_lock:
            count = len(self._factory_pool)
            self._factory_pool.clear()
            self.logger.info(f"Cleared {count} factories from pool")
            return count


# =============================================================================
# Interface Factory Function (for gateway registration)
# =============================================================================

# ADDED: Factory function to create ScanInterface instances
def ScanInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> ScanInterface:
    """Factory function to create ScanInterface instances.

    This function is registered with ScannerGateway and called
    to create interface instances with injected dependencies.

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name ("scanner")
        interface_name: Interface name ("scan")

    Returns:
        ScanInterface instance with DI injected
    """
    return ScanInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
    )


# =============================================================================
# EE 2.1 Architecture Notes
# =============================================================================

# REMOVED: Legacy EE 2.0 compatibility function (execute_scan_operation)
# EE 2.1 does not support backward compatibility with legacy gateway patterns.
# All code must use the new EE 2.1 pattern:
#
#   from EE import execute_operation
#   result = execute_operation(domain='scanner', interface='scan', ...)
#
# Reference: EE-Universal-Gateway-Architecture.md, Section 3.7


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    'ScanInterface',
    'ScanInterfaceFactory',
]


# =============================================================================
# End of File
# =============================================================================
#
# **Version:** 1.0.0
# **Date:** 2026-01-01
# **Purpose:** EE 2.1 compliant scan interface router
# **Lines:** 180
