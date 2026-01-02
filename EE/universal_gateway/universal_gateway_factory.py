"""
Universal Gateway Factory - Factory-driven UG construction (EE 2.1).

This module provides the UniversalGatewayFactory class that constructs
UniversalGateway instances according to EE 2.1 architecture principles.

EE 2.1 Architecture Decision (DEC-EE-01):
    "UniversalGateway MUST be constructed via UniversalGatewayFactory,
    not global singleton."

Benefits:
    - Horizontal scalability (can create multiple UG instances)
    - Dependency injection (all dependencies explicit)
    - Optional pooling (pool UG instances for performance)
    - Testability (can inject mock factories)

Usage:
    factory = UniversalGatewayFactory()
    ug = factory.build_gateway()

    # Or with pooling
    ug1 = factory.get_from_pool()
    factory.return_to_pool(ug1)
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
import logging


# ============================================================================
# Default Factory Implementations
# ============================================================================

def _default_logger_factory(name: str) -> logging.Logger:
    """Default logger factory using Python's logging module.

    Args:
        name: Logger name (component path)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"EE.{name}")


def _default_metrics_factory(name: str) -> Any:
    """Default metrics factory (placeholder).

    TODO: Implement proper metrics collection
    - Prometheus metrics
    - CloudWatch metrics
    - Custom metrics backend

    Args:
        name: Metrics name (component path)

    Returns:
        Metrics collector instance (currently None)
    """
    return None


def _default_config_service(key: str, default: Any = None) -> Any:
    """Default config service (placeholder).

    TODO: Implement proper config service
    - Environment variables
    - Configuration files
    - Parameter Store (SSM)
    - Secrets Manager

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value
    """
    # Placeholder for now
    return default


# ============================================================================
# Universal Gateway Factory
# ============================================================================

class UniversalGatewayFactory:
    """Factory for constructing UniversalGateway instances (EE 2.1).

    This factory implements DEC-EE-01 (Factory-Driven UG Construction).
    It provides clean, testable, and scalable UG construction.

    Key Features:
    - Factory-driven construction (no global singleton)
    - Dependency injection support
    - Optional UG pooling
    - Configurable factory functions
    - Thread-safe for concurrent access

    Usage:
        # Basic usage
        factory = UniversalGatewayFactory()
        ug = factory.build_gateway()

        # With custom factories
        factory = UniversalGatewayFactory(
            logger_factory=my_logger_factory,
            metrics_factory=my_metrics_factory,
            config_service=my_config_service
        )
        ug = factory.build_gateway()

        # With pooling
        ug1 = factory.get_from_pool()
        factory.return_to_pool(ug1)
    """

    def __init__(
        self,
        logger_factory: Optional[Callable[[str], logging.Logger]] = None,
        metrics_factory: Optional[Callable[[str], Any]] = None,
        config_service: Optional[Callable[[str], Any], Any] = None,
        pool_size: int = 3,
    ) -> None:
        """Initialize the Universal Gateway Factory.

        Args:
            logger_factory: Factory function to create loggers
            metrics_factory: Factory function to create metrics collectors
            config_service: Factory function to get configuration values
            pool_size: Maximum size of UG pool (default: 3)
        """
        self._logger_factory = logger_factory or _default_logger_factory
        self._metrics_factory = metrics_factory or _default_metrics_factory
        self._config_service = config_service or _default_config_service
        self._pool_size: int = pool_size
        self._pool: List[Any] = []

        # Get factory-level logger
        self._logger = self._logger_factory("ug_factory")
        self._logger.info("UniversalGatewayFactory initialized (EE 2.1)")

    def build_gateway(self) -> Any:
        """Build a new UniversalGateway instance.

        Returns:
            Initialized UniversalGateway instance

        Raises:
            ValueError: If required factories are not configured

        Example:
            factory = UniversalGatewayFactory()
            ug = factory.build_gateway()
        """
        from EE.universal_gateway.gateway import UniversalGateway
        from EE.universal_gateway.domain_gateway_factory import DomainGatewayFactory

        # Create domain gateway factory
        domain_gateway_factory = DomainGatewayFactory(
            get_logger=self._logger_factory,
            get_metrics=self._metrics_factory,
            get_config=self._config_service,
            call_operation=self._create_call_operation_placeholder(),
        )

        # Build UG with all dependencies
        ug = UniversalGateway(
            logger_factory=self._logger_factory,
            metrics_factory=self._metrics_factory,
            config_service=self._config_service,
            domain_gateway_factory=domain_gateway_factory,
        )

        self._logger.debug("Built new UniversalGateway instance")
        return ug

    def _create_call_operation_placeholder(self) -> Callable:
        """Create a placeholder call_operation function.

        This will be replaced by the actual UG.execute_operation method
        after the UG is built.

        Returns:
            Placeholder callable
        """
        def _placeholder(domain: str, interface: str, operation: str, **kwargs: Any) -> Any:
            raise RuntimeError(
                "call_operation not yet initialized. "
                "This will be replaced with UG.execute_operation after UG is built."
            )
        return _placeholder

    # ========================================================================
    # Pooling Support
    # ========================================================================

    def get_from_pool(self) -> Any:
        """Get a UG instance from the pool, or create new one if pool empty.

        Returns:
            UniversalGateway instance

        Example:
            ug = factory.get_from_pool()
            result = ug.execute_operation(...)
        """
        if self._pool:
            ug = self._pool.pop()
            self._logger.debug(f"Retrieved UG from pool (pool size: {len(self._pool)})")
            return ug

        # Pool empty, create new instance
        self._logger.debug("Pool empty, creating new UG instance")
        return self.build_gateway()

    def return_to_pool(self, ug: Any) -> None:
        """Return a UG instance to the pool.

        Args:
            ug: UniversalGateway instance to return

        Example:
            factory.return_to_pool(ug)
        """
        if len(self._pool) < self._pool_size:
            self._pool.append(ug)
            self._logger.debug(f"Returned UG to pool (pool size: {len(self._pool)})")
        else:
            self._logger.debug("Pool full, UG instance will be garbage collected")

    def clear_pool(self) -> None:
        """Clear all UG instances from the pool.

        Example:
            factory.clear_pool()
        """
        self._pool.clear()
        self._logger.debug("Cleared UG pool")

    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about the UG pool.

        Returns:
            Dictionary with pool statistics:
            {
                "pool_size": 3,
                "current_count": 2,
                "available": 2
            }

        Example:
            stats = factory.get_pool_stats()
            print(f"Pool: {stats['current_count']}/{stats['pool_size']}")
        """
        return {
            "pool_size": self._pool_size,
            "current_count": len(self._pool),
            "available": len(self._pool),
        }


__all__ = [
    'UniversalGatewayFactory',

    # Default factories (for reference)
    '_default_logger_factory',
    '_default_metrics_factory',
    '_default_config_service',
]
