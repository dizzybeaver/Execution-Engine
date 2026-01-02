"""Scanner Gateway Factory - EE 2.1 Compliant

Factory for creating and pooling ScannerGateway instances with DI.

EE 2.1 Architecture:
- Factory-driven construction
- DI-mandatory (all dependencies injected)
- Object pooling (5-10 instances)
- Thread-safe pool management

Based on:
- EE/operations/cache/cache_factory.py (factory pattern reference)
- EE/universal_gateway/domain_gateway_factory.py (pool management)
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

# ADDED: Import ScannerGateway (will be created in gateway.py)
# Using lazy import to avoid circular dependency
# from EE.scanner.gateway.scanner_gateway_21 import ScannerGateway


# =============================================================================
# Scanner Gateway Factory - EE 2.1 Compliant
# =============================================================================

class ScannerGatewayFactory:
    """Factory for ScannerGateway instances (EE 2.1 compliant).

    Responsibilities:
    - Create ScannerGateway instances with DI
    - Maintain pool of reusable instances (5-10)
    - Thread-safe pool management
    - Provide pool statistics and management

    EE 2.1 Compliance:
    - Receives DI functions (get_logger, get_metrics, get_config, call_operation)
    - No global state (pool encapsulated in instance)
    - Object pooling for performance
    """

    # ADDED: Factory constructor with DI
    def __init__(
        self,
        get_logger: Callable[[str], any],
        get_metrics: Callable[[str], any],
        get_config: Callable[[str, any], any],
        call_operation: Callable[..., any],
        pool_min_size: int = 5,
        pool_max_size: int = 10,
    ):
        """Initialize scanner gateway factory.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
            pool_min_size: Minimum pool size (default: 5)
            pool_max_size: Maximum pool size (default: 10)
        """
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

        self._pool_min_size = pool_min_size
        self._pool_max_size = pool_max_size
        self._pool: list = []
        self._pool_lock = threading.RLock()

        # ADDED: Logger for factory
        self.logger = get_logger("scanner.gateway.factory")

    # ADDED: Create or retrieve gateway from pool
    def create_gateway(self) -> 'ScannerGateway':
        """Create ScannerGateway instance or retrieve from pool.

        Returns:
            ScannerGateway instance (pooled or new)

        EE 2.1 Pattern:
        - Check pool first
        - Create new instance if pool empty
        - Thread-safe pool access
        """
        with self._pool_lock:
            if self._pool:
                # Reuse pooled instance
                gateway = self._pool.pop()
                self.logger.debug("Retrieved gateway from pool")
                return gateway

        # Create new instance outside lock
        # ADDED: Lazy import to avoid circular dependency
        from EE.scanner.gateway.scanner_gateway_21 import ScannerGateway

        gateway = ScannerGateway(
            domain_name="scanner",
            get_logger=self._get_logger,
            get_metrics=self._get_metrics,
            get_config=self._get_config,
            call_operation=self._call_operation,
        )

        self.logger.debug("Created new ScannerGateway instance")
        return gateway

    # ADDED: Return gateway to pool
    def return_gateway(self, gateway: 'ScannerGateway') -> None:
        """Return ScannerGateway instance to pool.

        Args:
            gateway: Gateway instance to return

        EE 2.1 Pattern:
        - Return to pool if under max size
        - Otherwise let it be garbage collected
        - Thread-safe pool access
        """
        with self._pool_lock:
            if len(self._pool) < self._pool_max_size:
                self._pool.append(gateway)
                self.logger.debug(f"Returned gateway to pool (pool size: {len(self._pool)})")
            else:
                self.logger.debug("Pool at max capacity, discarding gateway")

    # ADDED: Get pool statistics
    def get_pool_stats(self) -> dict:
        """Get current pool statistics.

        Returns:
            Dictionary with pool stats:
            - current_size: Current number of instances in pool
            - min_size: Configured minimum pool size
            - max_size: Configured maximum pool size
            - utilization: Percentage of pool used (0-100)
        """
        with self._pool_lock:
            current_size = len(self._pool)
            utilization = (current_size / self._pool_max_size * 100) if self._pool_max_size > 0 else 0

            return {
                "current_size": current_size,
                "min_size": self._pool_min_size,
                "max_size": self._pool_max_size,
                "utilization": round(utilization, 2),
            }

    # ADDED: Clear pool (useful for testing or reset)
    def clear_pool(self) -> int:
        """Clear all instances from pool.

        Returns:
            Number of instances cleared

        EE 2.1 Pattern:
        - Thread-safe pool clearing
        - Returns count for verification
        """
        with self._pool_lock:
            count = len(self._pool)
            self._pool.clear()
            self.logger.info(f"Cleared {count} instances from pool")
            return count


# =============================================================================
# End of File
# =============================================================================
#
# **Version:** 1.0.0
# **Date:** 2026-01-01
# **Purpose:** EE 2.1 compliant gateway factory with pooling
# **Lines:** 130
