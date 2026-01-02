"""
Universal Gateway (UG) - Central entry point for all EE operations.

This module provides the UniversalGateway class, which is the SINGLE entry
point for all operations in the EE system. The UG manages domain gateways
and provides dependency injection for cross-cutting concerns.

Architecture:
    Application Code
        ↓ execute_operation(domain, interface, operation, **kwargs)
    UniversalGateway (this module)
        ↓ get domain gateway
    DomainGateway
        ↓ execute domain operation
    Interface
        ↓ execute operation
    Implementation

Key Principles:
1. Single entry point - execute_operation() only
2. NO backward compatibility - no execute(route, payload)
3. Dependency injection for cross-cutting concerns
4. Type-safe with proper error handling
5. Clean separation of concerns

Usage:
    # Create UG instance
    ug = UniversalGateway(
        logger_factory=my_logger_factory,
        metrics_factory=my_metrics_factory
    )

    # Register domain gateways
    ug.register_domain_gateway("config", config_gateway)
    ug.register_domain_gateway("security", security_gateway)

    # Execute operations
    result = ug.execute_operation(
        domain="config",
        interface="config",
        operation="get",
        key="database.host"
    )
"""

from __future__ import annotations
from typing import Any, Dict, Callable, Optional, Protocol
import logging


# ============================================================================
# Type Protocols
# ============================================================================

class LoggerFactory(Protocol):
    """Protocol for logger factory functions.

    The logger factory creates logger instances for components.
    """
    def __call__(self, name: str) -> logging.Logger: ...


class MetricsFactory(Protocol):
    """Protocol for metrics factory functions.

    The metrics factory creates metrics collectors for components.
    """
    def __call__(self, name: str) -> Any: ...


class ConfigFactory(Protocol):
    """Protocol for config factory functions (EE 2.1).

    The config factory retrieves configuration values.
    """
    def __call__(self, key: str, default: Any = None) -> Any: ...


# ============================================================================
# Exceptions
# ============================================================================

class UniversalGatewayError(Exception):
    """Base exception for UniversalGateway errors."""
    pass


class DomainNotFoundError(UniversalGatewayError):
    """Raised when a domain is not found."""
    pass


class InvalidOperationError(UniversalGatewayError):
    """Raised when an operation cannot be executed."""
    pass


# ============================================================================
# Universal Gateway Class
# ============================================================================

class UniversalGateway:
    """Universal Gateway - SINGLE entry point for all EE operations.

    The UniversalGateway (UG) is the central hub for all operations in the
    EE system. It manages domain gateways, provides dependency injection for
    cross-cutting concerns (logging, metrics), and ensures clean architecture.

    Key Features:
    - Single entry point via execute_operation()
    - Domain gateway management
    - Dependency injection for loggers and metrics
    - Cross-domain operation support
    - Type-safe error handling

    Architecture Pattern:
        execute_operation(domain, interface, operation, **kwargs)
        - NO backward compatibility methods
        - Clean separation of concerns
        - Dependency injection throughout

    Thread Safety:
        The gateway is thread-safe for read operations (execute_operation,
        get_logger, get_metrics). Domain registration should be done during
        initialization and not modified during concurrent execution.

    Usage:
        # Create UG instance
        ug = UniversalGateway(
            logger_factory=lambda name: logging.getLogger(name),
            metrics_factory=lambda name: MyMetricsCollector(name)
        )

        # Register domain gateways
        config_gateway = ConfigGateway(
            get_logger=ug.get_logger,
            get_metrics=ug.get_metrics,
            call_operation=ug.execute_operation
        )
        ug.register_domain_gateway("config", config_gateway)

        # Execute operations
        result = ug.execute_operation(
            domain="config",
            interface="config",
            operation="get",
            key="database.host"
        )

    Cross-Domain Operations:
        Domains can call operations in other domains through the injected
        call_operation function. This enables clean separation while allowing
        necessary inter-domain communication.
    """

    def __init__(
        self,
        logger_factory: LoggerFactory,
        metrics_factory: MetricsFactory,
        config_service: ConfigFactory,
        domain_gateway_factory: Optional[Any] = None,
    ) -> None:
        """Initialize the Universal Gateway (EE 2.1).

        Args:
            logger_factory: Factory function to create loggers
            metrics_factory: Factory function to create metrics collectors
            config_service: Factory function to get configuration values
            domain_gateway_factory: Optional factory for creating domain gateways

        Raises:
            ValueError: If factory functions are None

        Example:
            ug = UniversalGateway(
                logger_factory=lambda name: logging.getLogger(f"EE.{name}"),
                metrics_factory=lambda name: PrometheusMetrics(name),
                config_service=lambda key, default=None: get_config(key)
            )
        """
        if logger_factory is None:
            raise ValueError("logger_factory cannot be None")
        if metrics_factory is None:
            raise ValueError("metrics_factory cannot be None")
        if config_service is None:
            raise ValueError("config_service cannot be None")

        self._logger_factory: LoggerFactory = logger_factory
        self._metrics_factory: MetricsFactory = metrics_factory
        self._config_service: ConfigFactory = config_service
        self._domain_gateway_factory: Optional[Any] = domain_gateway_factory
        self._domains: Dict[str, Any] = {}

        # Get UG-level logger
        self._logger = self._logger_factory("ug")
        self._logger.info("Universal Gateway initialized (EE 2.1)")

    # ========================================================================
    # Domain Gateway Management
    # ========================================================================

    def register_domain_gateway(
        self,
        domain_name: str,
        gateway: Any,
    ) -> None:
        """Register a domain gateway.

        Args:
            domain_name: Unique domain identifier (e.g., "config", "security")
            gateway: Domain gateway instance

        Raises:
            ValueError: If domain_name is empty or gateway is None
            ValueError: If domain already registered

        Example:
            config_gateway = ConfigGateway(...)
            ug.register_domain_gateway("config", config_gateway)
        """
        if not domain_name:
            raise ValueError("Domain name cannot be empty")

        if gateway is None:
            raise ValueError("Gateway cannot be None")

        if domain_name in self._domains:
            raise ValueError(
                f"Domain '{domain_name}' is already registered. "
                f"Cannot register duplicate domains."
            )

        self._domains[domain_name] = gateway
        self._logger.info(f"Registered domain gateway: {domain_name}")

    def has_domain(self, domain_name: str) -> bool:
        """Check if a domain gateway is registered.

        Args:
            domain_name: Domain identifier

        Returns:
            True if domain exists, False otherwise

        Example:
            if ug.has_domain("config"):
                result = ug.execute_operation("config", ...)
        """
        return domain_name in self._domains

    def get_domain_gateways(self) -> Dict[str, Any]:
        """Get all registered domain gateways.

        Returns:
            Dictionary mapping domain names to gateway instances

        Example:
            gateways = ug.get_domain_gateways()
            for domain, gateway in gateways.items():
                print(f"Domain: {domain}")
        """
        return self._domains.copy()

    # ========================================================================
    # Dependency Injection
    # ========================================================================

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a component.

        Args:
            name: Component name (e.g., "config", "security.auth")

        Returns:
            Logger instance

        Example:
            logger = ug.get_logger("config")
            logger.info("Configuration loaded")
        """
        return self._logger_factory(name)

    def get_metrics(self, name: str) -> Any:
        """Get metrics collector for a component.

        Args:
            name: Component name

        Returns:
            Metrics collector instance

        Example:
            metrics = ug.get_metrics("config")
            metrics.increment("config.get")
        """
        return self._metrics_factory(name)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value (EE 2.1).

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            timeout = ug.get_config("timeout", 30)
            db_host = ug.get_config("database.host")
        """
        return self._config_service(key, default)

    # ========================================================================
    # Operation Execution
    # ========================================================================

    def execute_operation(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute operation using UG pattern.

        This is the MAIN entry point for all EE operations.
        NO backward compatibility - this is the only pattern.

        Args:
            domain: Domain name (e.g., "config", "security", "logging")
            interface: Interface name (e.g., "config", "auth", "database")
            operation: Operation name (e.g., "get", "set", "query")
            **kwargs: Operation-specific parameters

        Returns:
            Operation result (type depends on operation)

        Raises:
            DomainNotFoundError: If domain not registered
            InvalidOperationError: If operation execution fails

        Example:
            # Get configuration value
            config_value = ug.execute_operation(
                domain="config",
                interface="config",
                operation="get",
                key="database.host"
            )

            # Authenticate user
            auth_result = ug.execute_operation(
                domain="security",
                interface="auth",
                operation="authenticate",
                username="john",
                password="secret"
            )

            # Log message
            ug.execute_operation(
                domain="logging",
                interface="log",
                operation="info",
                message="Server started"
            )

            # Increment metric
            ug.execute_operation(
                domain="metrics",
                interface="counter",
                operation="increment",
                name="requests",
                value=1
            )

        Cross-Domain Calls:
            Domains can call other domains through the call_operation parameter
            passed during gateway initialization:

            class MyDomainGateway:
                def __init__(self, call_operation):
                    self._call_operation = call_operation

                def my_method(self):
                    # Call another domain
                    result = self._call_operation(
                        domain="config",
                        interface="config",
                        operation="get",
                        key="some.key"
                    )
        """
        # Validate domain exists
        if domain not in self._domains:
            available = list(self._domains.keys())
            raise DomainNotFoundError(
                f"Unknown domain: '{domain}'. "
                f"Available domains: {available}"
            )

        # Get domain gateway
        gateway = self._domains[domain]

        # Execute operation
        try:
            self._logger.debug(
                f"Executing: {domain}.{interface}.{operation}()"
            )

            result = gateway.execute_domain_operation(
                interface=interface,
                operation=operation,
                **kwargs
            )

            self._logger.debug(
                f"Completed: {domain}.{interface}.{operation}()"
            )

            return result

        except Exception as e:
            # Wrap in UG exception
            raise InvalidOperationError(
                f"Failed to execute operation "
                f"'{domain}.{interface}.{operation}()': {e}"
            ) from e

    # ========================================================================
    # Listing and Discovery
    # ========================================================================

    def list_all(self) -> Dict[str, Any]:
        """List all available operations from all domains.

        Returns:
            Dictionary mapping domain names to their operations:
            {
                "config": {
                    "domain": "config",
                    "interfaces": ["config", "secrets"],
                    "interface_count": 2
                },
                "security": {
                    "domain": "security",
                    "interfaces": ["auth", "encryption"],
                    "interface_count": 2
                },
                ...
            }

        Example:
            all_ops = ug.list_all()
            for domain, info in all_ops.items():
                print(f"{domain}: {info['interface_count']} interfaces")
        """
        result = {}

        for domain_name, gateway in self._domains.items():
            try:
                result[domain_name] = gateway.list_all()
            except Exception as e:
                result[domain_name] = {
                    "error": f"Failed to list operations: {e}"
                }

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics.

        Returns:
            Dictionary with gateway statistics:
            {
                "total_domains": 5,
                "domains": ["config", "security", "logging", "metrics", "debug"],
                "domain_stats": {
                    "config": {...},
                    "security": {...},
                    ...
                }
            }

        Example:
            stats = ug.get_stats()
            print(f"Total domains: {stats['total_domains']}")
        """
        domain_stats = {}

        for domain_name, gateway in self._domains.items():
            try:
                if hasattr(gateway, 'get_stats'):
                    domain_stats[domain_name] = gateway.get_stats()
                else:
                    domain_stats[domain_name] = gateway.list_all()
            except Exception as e:
                domain_stats[domain_name] = {"error": str(e)}

        return {
            "total_domains": len(self._domains),
            "domains": list(self._domains.keys()),
            "domain_stats": domain_stats,
        }


__all__ = [
    'UniversalGateway',

    # Type protocols
    'LoggerFactory',
    'MetricsFactory',
    'ConfigFactory',

    # Exceptions
    'UniversalGatewayError',
    'DomainNotFoundError',
    'InvalidOperationError',
]
