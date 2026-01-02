"""
Domain Gateway - Base class for all domain gateways in UG architecture.

This module provides the base DomainGateway class that all domain-specific
gateways must inherit from. Each domain gateway manages interfaces within
its domain.

Architecture:
    UniversalGateway → DomainGateway → Interface → Operation

Type Hints:
    - Complete type coverage for all public methods
    - Generic return types for flexibility
    - Proper exception hierarchy
"""

from __future__ import annotations
from typing import Any, Dict, Callable, Optional, Protocol
from abc import ABC, abstractmethod


# ============================================================================
# Type Protocols
# ============================================================================

class LoggerFactory(Protocol):
    """Protocol for logger factory functions."""
    def __call__(self, name: str) -> Any: ...


class MetricsFactory(Protocol):
    """Protocol for metrics factory functions."""
    def __call__(self, name: str) -> Any: ...


class OperationCaller(Protocol):
    """Protocol for operation call functions."""
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...


class InterfaceFactory(Protocol):
    """Protocol for interface factory functions."""
    def __call__(
        self,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        get_config: 'ConfigFactory',
        call_operation: OperationCaller,
        domain_name: str,
        interface_name: str,
    ) -> Any: ...


class ConfigFactory(Protocol):
    """Protocol for config factory functions (EE 2.1)."""
    def __call__(self, key: str, default: Any = None) -> Any: ...


# ============================================================================
# Exceptions
# ============================================================================

class DomainGatewayError(Exception):
    """Base exception for domain gateway errors."""
    pass


class InterfaceNotFoundError(DomainGatewayError):
    """Raised when an interface is not found in a domain."""
    pass


class OperationNotFoundError(DomainGatewayError):
    """Raised when an operation is not found in an interface."""
    pass


# REMOVED: Legacy error classes (CommandNotFoundError, RouteNotFoundError, GatewayError)
# EE 2.1 uses only: DomainGatewayError, InterfaceNotFoundError, OperationNotFoundError


# ============================================================================
# Domain Gateway Base Class
# ============================================================================

class DomainGateway(ABC):
    """Base class for all domain gateways in UG architecture (EE 2.1).

    Each domain gateway is responsible for managing interfaces within its
    domain and executing operations through those interfaces.

    Key Features:
    - Interface registration and management
    - Dependency injection for cross-cutting concerns
    - Operation execution through interface factories
    - Clean error handling with descriptive messages
    - EE 2.1 compliant with get_config parameter

    Type Parameters:
        - Domain-specific configuration
        - Interface-specific operations

    Usage Example (EE 2.1):
        class ConfigGateway(DomainGateway):
            def __init__(
                self,
                domain_name: str,
                get_logger: Callable,
                get_metrics: Callable,
                get_config: Callable,
                call_operation: Callable,
            ):
                super().__init__(
                    domain_name=domain_name,
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    get_config=get_config,
                    call_operation=call_operation
                )
                # Register interfaces
                self.register_interface("config", ConfigInterfaceFactory)

        # Execute operation
        result = gateway.execute_domain_operation(
            interface="config",
            operation="get",
            key="database.host"
        )
    """

    def __init__(
        self,
        domain_name: str,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        get_config: ConfigFactory,
        call_operation: OperationCaller,
    ) -> None:
        """Initialize domain gateway with injected dependencies (EE 2.1).

        Args:
            domain_name: Unique identifier for this domain
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        self._domain_name: str = domain_name
        self._get_logger: LoggerFactory = get_logger
        self._get_metrics: MetricsFactory = get_metrics
        self._get_config: ConfigFactory = get_config
        self._call_operation: OperationCaller = call_operation
        self._interfaces: Dict[str, InterfaceFactory] = {}

        # Get domain-level logger and metrics
        self._logger = self._get_logger(f"domain.{domain_name}")
        self._metrics = self._get_metrics(f"domain.{domain_name}")

    @property
    def domain_name(self) -> str:
        """Get the domain name."""
        return self._domain_name

    def register_interface(
        self,
        interface_name: str,
        interface_factory: InterfaceFactory,
    ) -> None:
        """Register an interface factory for this domain.

        Args:
            interface_name: Unique identifier for the interface
            interface_factory: Factory function to create interface instances

        Raises:
            ValueError: If interface already registered
        """
        if interface_name in self._interfaces:
            raise ValueError(
                f"Interface '{interface_name}' already registered "
                f"in domain '{self._domain_name}'"
            )

        self._interfaces[interface_name] = interface_factory
        self._logger.debug(
            f"Registered interface: {self._domain_name}.{interface_name}"
        )

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute an operation in this domain.

        This method:
        1. Validates the interface exists
        2. Creates interface instance with injected dependencies
        3. Executes the operation on the interface
        4. Handles errors with clear messages

        Args:
            interface: Interface name (e.g., "config", "database")
            operation: Operation name (e.g., "get", "set", "query")
            **kwargs: Operation-specific parameters

        Returns:
            Operation result (type depends on operation)

        Raises:
            InterfaceNotFoundError: If interface not registered
            OperationNotFoundError: If operation not found
            DomainGatewayError: If execution fails

        Example:
            result = gateway.execute_domain_operation(
                interface="config",
                operation="get",
                key="database.host"
            )
        """
        # Validate interface
        if interface not in self._interfaces:
            available = list(self._interfaces.keys())
            raise InterfaceNotFoundError(
                f"Unknown interface '{interface}' in domain '{self._domain_name}'. "
                f"Available interfaces: {available}"
            )

        # Get interface factory
        interface_factory = self._interfaces[interface]

        try:
            # Build interface with injected dependencies (EE 2.1)
            interface_instance = interface_factory(
                get_logger=self._get_logger,
                get_metrics=self._get_metrics,
                get_config=self._get_config,
                call_operation=self._call_operation,
                domain_name=self._domain_name,
                interface_name=interface,
            )

            # Execute operation
            result = interface_instance.execute_operation(
                operation=operation,
                **kwargs
            )

            return result

        except AttributeError as e:
            if "execute_operation" in str(e):
                raise OperationNotFoundError(
                    f"Interface '{interface}' does not implement "
                    f"execute_operation() method"
                ) from e
            raise

        except Exception as e:
            # Re-raise known errors
            if isinstance(e, (InterfaceNotFoundError, OperationNotFoundError)):
                raise

            # Wrap unknown errors
            raise DomainGatewayError(
                f"Failed to execute operation '{operation}' "
                f"on interface '{interface}' "
                f"in domain '{self._domain_name}': {e}"
            ) from e

    def list_all(self) -> Dict[str, Any]:
        """List all interfaces in this domain.

        Returns:
            Dictionary containing domain info and available interfaces:
            {
                "domain": "config",
                "interfaces": ["config", "secrets", "validation"],
                "interface_count": 3
            }

        Example:
            info = gateway.list_all()
            print(f"Domain: {info['domain']}")
            print(f"Interfaces: {info['interfaces']}")
        """
        return {
            "domain": self._domain_name,
            "interfaces": list(self._interfaces.keys()),
            "interface_count": len(self._interfaces),
        }

    def has_interface(self, interface_name: str) -> bool:
        """Check if an interface is registered.

        Args:
            interface_name: Interface to check

        Returns:
            True if interface exists, False otherwise
        """
        return interface_name in self._interfaces

    def get_interface_names(self) -> list[str]:
        """Get list of registered interface names.

        Returns:
            List of interface names
        """
        return list(self._interfaces.keys())


# ============================================================================
# Convenience Base Classes
# ============================================================================

class SimpleDomainGateway(DomainGateway):
    """Simplified domain gateway for basic use cases.

    This class provides a simpler interface for domains that don't need
    complex interface management. Operations can be registered directly
    as methods.

    Usage:
        class MySimpleGateway(SimpleDomainGateway):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def my_operation(self, **kwargs):
                return {"result": "success"}

        gateway = MySimpleGateway(...)
        result = gateway.execute_domain_operation(
            interface="_direct",
            operation="my_operation",
            **kwargs
        )
    """

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute operation, supporting direct method calls.

        For the "_direct" interface, looks for methods on the gateway itself.
        """
        if interface == "_direct":
            # Try to execute as a method on this gateway
            if hasattr(self, operation):
                method = getattr(self, operation)
                if callable(method):
                    return method(**kwargs)

            raise OperationNotFoundError(
                f"Operation '{operation}' not found on gateway '{self._domain_name}'"
            )

        # Use standard interface execution
        return super().execute_domain_operation(interface, operation, **kwargs)


__all__ = [
    # Base classes
    'DomainGateway',
    'SimpleDomainGateway',

    # Type protocols
    'LoggerFactory',
    'MetricsFactory',
    'ConfigFactory',
    'OperationCaller',
    'InterfaceFactory',

    # Exceptions (EE 2.1 compliant - no legacy aliases)
    'DomainGatewayError',
    'InterfaceNotFoundError',
    'OperationNotFoundError',
]
