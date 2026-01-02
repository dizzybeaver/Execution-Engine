"""
Foundation Domain Gateway - EE 2.1 Compliant

Routes operations to appropriate interfaces within the Foundation domain:
- config: Configuration management
- singleton: Instance management
- utility: Helper functions
- di: Dependency injection
- initialization: System bootstrap

EE 2.1 Compliance:
- Extends DomainGateway base class with proper __init__
- Uses register_interface() for all interfaces
- Interfaces are classes with execute_operation() method
- Cross-domain calls via call_operation callback
- No legacy execute() method
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable

from EE.universal_gateway.domain_gateway import DomainGateway

# Import interface classes (not functions!)
from EE.foundation.config.config_interface import ConfigInterface
from EE.foundation.singleton.singleton_interface import SingletonInterface
from EE.foundation.utility.utility_interface import UtilityInterface
from EE.foundation.di.di_interface import DIInterface
from EE.foundation.initialization.initialization_interface import InitializationInterface


class FoundationGateway(DomainGateway):
    """Foundation Domain Gateway.

    Provides fundamental EE capabilities through the following interfaces:
    - config: Configuration management (get, set, delete, reload)
    - singleton: Instance management (get, set, delete, list)
    - utility: Helper functions (json, uuid, validation)
    - di: Dependency injection (register, resolve, inject)
    - initialization: System bootstrap (init, shutdown)

    All operations follow EE 2.1 patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside foundation domain

    Example:
        gateway = FoundationGateway(
            domain_name="foundation",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=operation_caller
        )

        # Get configuration
        cache_config = gateway.execute_domain_operation(
            "config", "get", category="cache"
        )

        # Resolve dependency
        db = gateway.execute_domain_operation(
            "di", "resolve", service_type=Database
        )
    """

    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable
    ):
        """Initialize Foundation Gateway with injected dependencies.

        Args:
            domain_name: Domain name (should be "foundation")
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get config values
            call_operation: Function to call operations in other domains
        """
        # Call base class __init__ with uniform signature
        # FIXED: Added get_config parameter to pass to base class
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

        # Store get_config for interface use
        self._get_config = get_config

        # Register interfaces using base class registry
        self._register_interfaces()

    def _register_interfaces(self) -> None:
        """Register all foundation interfaces.

        Uses base class register_interface() method to register each interface.
        Each interface factory receives the DI dependencies.
        """
        # Config interface
        self.register_interface(
            "config",
            lambda get_logger, get_metrics, call_operation, domain_name, interface_name:
                ConfigInterface(
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    call_operation=call_operation
                )
        )

        # Singleton interface
        self.register_interface(
            "singleton",
            lambda get_logger, get_metrics, call_operation, domain_name, interface_name:
                SingletonInterface(
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    call_operation=call_operation
                )
        )

        # Utility interface
        self.register_interface(
            "utility",
            lambda get_logger, get_metrics, call_operation, domain_name, interface_name:
                UtilityInterface(
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    call_operation=call_operation
                )
        )

        # DI interface
        self.register_interface(
            "di",
            lambda get_logger, get_metrics, call_operation, domain_name, interface_name:
                DIInterface(
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    call_operation=call_operation
                )
        )

        # Initialization interface
        self.register_interface(
            "initialization",
            lambda get_logger, get_metrics, call_operation, domain_name, interface_name:
                InitializationInterface(
                    get_logger=get_logger,
                    get_metrics=get_metrics,
                    call_operation=call_operation
                )
        )

    def list_all(self) -> Dict[str, Any]:
        """List all foundation domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": self._domain_name,
            "interfaces": {
                "config": {
                    "description": "Configuration management",
                    "operations": [
                        {"operation": "get", "description": "Get configuration value"},
                        {"operation": "get_value", "description": "Get config by dot path"},
                        {"operation": "set", "description": "Set configuration value"},
                        {"operation": "delete", "description": "Delete configuration"},
                        {"operation": "get_all", "description": "Get all configuration"},
                        {"operation": "reload", "description": "Reload configuration"},
                        {"operation": "validate", "description": "Validate configuration"},
                    ]
                },
                "singleton": {
                    "description": "Instance management",
                    "operations": [
                        {"operation": "get", "description": "Get singleton instance"},
                        {"operation": "set", "description": "Set singleton instance"},
                        {"operation": "delete", "description": "Delete singleton"},
                        {"operation": "exists", "description": "Check if exists"},
                        {"operation": "list_all", "description": "List all singletons"},
                        {"operation": "clear", "description": "Clear all singletons"},
                    ]
                },
                "utility": {
                    "description": "Helper functions",
                    "operations": [
                        {"operation": "json_to_string", "description": "Serialize to JSON"},
                        {"operation": "json_from_string", "description": "Deserialize JSON"},
                        {"operation": "generate_uuid", "description": "Generate UUID"},
                        {"operation": "validate_string", "description": "Validate string"},
                        {"operation": "validate_dict", "description": "Validate dict"},
                        {"operation": "sanitize_input", "description": "Sanitize input"},
                    ]
                },
                "di": {
                    "description": "Dependency injection",
                    "operations": [
                        {"operation": "container_create", "description": "Create container"},
                        {"operation": "register_singleton", "description": "Register singleton"},
                        {"operation": "register_transient", "description": "Register transient"},
                        {"operation": "register_scoped", "description": "Register scoped"},
                        {"operation": "register_factory", "description": "Register factory"},
                        {"operation": "resolve", "description": "Resolve service"},
                        {"operation": "is_registered", "description": "Check registration"},
                        {"operation": "get_services", "description": "Get all services"},
                        {"operation": "clear", "description": "Clear container"},
                    ]
                },
                "initialization": {
                    "description": "System initialization",
                    "operations": [
                        {"operation": "initialize", "description": "Initialize system"},
                        {"operation": "shutdown", "description": "Shutdown system"},
                        {"operation": "get_status", "description": "Get status"},
                        {"operation": "get_health", "description": "Get health check"},
                    ]
                },
            }
        }


__all__ = [
    "FoundationGateway",
]
