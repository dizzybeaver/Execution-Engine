"""
Domain Gateway Factory - Uniform construction of domain gateways (EE 2.1).

This module provides the DomainGatewayFactory class that creates domain
gateways with uniform constructor signature according to EE 2.1 architecture.

EE 2.1 Uniform Constructor Pattern:
    DomainGateway(
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    )

Usage:
    factory = DomainGatewayFactory(
        get_logger=ug.get_logger,
        get_metrics=ug.get_metrics,
        get_config=ug.get_config,
        call_operation=ug.execute_operation
    )

    gateway = factory.create_gateway(
        domain_class=FoundationGateway,
        domain_name="foundation"
    )
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Protocol
from EE.universal_gateway.domain_gateway import DomainGateway


# ============================================================================
# Type Protocols
# ============================================================================

class LoggerFactory(Protocol):
    """Protocol for logger factory functions."""
    def __call__(self, name: str) -> Any: ...


class MetricsFactory(Protocol):
    """Protocol for metrics factory functions."""
    def __call__(self, name: str) -> Any: ...


class ConfigFactory(Protocol):
    """Protocol for config factory functions."""
    def __call__(self, key: str, default: Any = None) -> Any: ...


class OperationCaller(Protocol):
    """Protocol for operation call functions."""
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...


# ============================================================================
# Domain Gateway Factory
# ============================================================================

class DomainGatewayFactory:
    """Factory for creating domain gateways with uniform signature (EE 2.1).

    This factory ensures all domain gateways are created with the same
    constructor signature, making the system consistent and maintainable.

    Benefits:
    - Uniform gateway construction
    - Automatic dependency injection
    - Type-safe gateway creation
    - Easy to test with mocks

    Usage:
        factory = DomainGatewayFactory(
            get_logger=ug.get_logger,
            get_metrics=ug.get_metrics,
            get_config=ug.get_config,
            call_operation=ug.execute_operation
        )

        # Create a gateway
        foundation_gateway = factory.create_gateway(
            domain_class=FoundationGateway,
            domain_name="foundation"
        )
    """

    def __init__(
        self,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        get_config: ConfigFactory,
        call_operation: OperationCaller,
    ) -> None:
        """Initialize the domain gateway factory.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        self._get_logger: LoggerFactory = get_logger
        self._get_metrics: MetricsFactory = get_metrics
        self._get_config: ConfigFactory = get_config
        self._call_operation: OperationCaller = call_operation

    def create_gateway(
        self,
        domain_class: type,
        domain_name: str,
        **kwargs: Any,
    ) -> DomainGateway:
        """Create a domain gateway with uniform signature (EE 2.1).

        Args:
            domain_class: Domain gateway class to instantiate
            domain_name: Domain name for the gateway
            **kwargs: Additional keyword arguments for the domain class

        Returns:
            Initialized domain gateway instance

        Raises:
            ValueError: If domain_class is not a DomainGateway subclass
            TypeError: If domain_class cannot be instantiated

        Example:
            foundation_gateway = factory.create_gateway(
                domain_class=FoundationGateway,
                domain_name="foundation"
            )
        """
        # Validate domain_class
        if not isinstance(domain_class, type):
            raise ValueError(
                f"domain_class must be a class, got {type(domain_class)}"
            )

        if not issubclass(domain_class, DomainGateway):
            raise ValueError(
                f"domain_class must be a subclass of DomainGateway, "
                f"got {domain_class.__name__}"
            )

        # Create gateway with uniform signature
        try:
            gateway = domain_class(
                domain_name=domain_name,
                get_logger=self._get_logger,
                get_metrics=self._get_metrics,
                get_config=self._get_config,
                call_operation=self._call_operation,
                **kwargs
            )
            return gateway

        except Exception as e:
            raise TypeError(
                f"Failed to create gateway for domain '{domain_name}' "
                f"using class {domain_class.__name__}: {e}"
            ) from e

    def create_gateways(
        self,
        domain_classes: Dict[str, type],
        **kwargs: Any,
    ) -> Dict[str, DomainGateway]:
        """Create multiple domain gateways at once.

        Args:
            domain_classes: Dictionary mapping domain names to domain classes
            **kwargs: Additional keyword arguments passed to all gateways

        Returns:
            Dictionary mapping domain names to gateway instances

        Example:
            gateways = factory.create_gateways({
                "foundation": FoundationGateway,
                "security": SecurityGateway,
                "observability": ObservabilityGateway,
            })
        """
        gateways: Dict[str, DomainGateway] = {}

        for domain_name, domain_class in domain_classes.items():
            gateways[domain_name] = self.create_gateway(
                domain_class=domain_class,
                domain_name=domain_name,
                **kwargs
            )

        return gateways


__all__ = [
    'DomainGatewayFactory',

    # Type protocols
    'LoggerFactory',
    'MetricsFactory',
    'ConfigFactory',
    'OperationCaller',
]
