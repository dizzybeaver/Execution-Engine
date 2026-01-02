"""
Infrastructure Domain Gateway - EE 2.1 Compliant

Routes infrastructure operations to appropriate interfaces within the Infrastructure domain:
- plugins: Plugin loading, management, and lifecycle operations

EE 2.1 Compliance:
- Extends DomainGateway base class with proper __init__
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
- Uniform constructor signature with get_config parameter
- NO sys.path manipulation
- NO legacy execute() method
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass

# FIXED: Removed sys.path manipulation - using proper import path
from EE.universal_gateway.domain_gateway import DomainGateway, DomainGatewayError


class InfrastructureGateway(DomainGateway):
    """Infrastructure Domain Gateway.

    Provides infrastructure EE capabilities through the following interfaces:
    - plugins: Plugin operations (load, unload, list, get_info, reload, enable, disable)

    All operations follow EE 2.1 patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside infrastructure domain

    Example:
        gateway = InfrastructureGateway(
            domain_name="infrastructure",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=callback
        )

        # Load a plugin
        result = gateway.execute_domain_operation(
            "plugins", "load", name="my_plugin", path="/path/to/plugin"
        )

        # List all plugins
        plugins = gateway.execute_domain_operation(
            "plugins", "list"
        )
    """

    # FIXED: EE 2.1 Uniform Gateway Constructor Signature - REQUIRED parameters only
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize infrastructure gateway with injected dependencies (EE 2.1).

        Args:
            domain_name: Domain name (must be "infrastructure")
            get_logger: Factory function to create loggers (REQUIRED)
            get_metrics: Factory function to create metrics collectors (REQUIRED)
            get_config: Factory function to get config values (REQUIRED)
            call_operation: Function to call operations in other domains (REQUIRED)
        """
        # Initialize parent DomainGateway with uniform signature
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

        # Register interfaces
        from EE.infrastructure.plugins.plugins_interface import create_plugins_interface

        self.register_interface("plugins", create_plugins_interface)

        # Cache for interface instances to maintain state across calls
        self._interface_instances: Dict[str, Any] = {}

    # FIXED: Removed legacy execute() method - use execute_domain_operation instead

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using EE 2.1 pattern.

        Args:
            interface: Interface name (plugins)
            operation: Operation name (load, unload, list, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            DomainGatewayError: If interface or operation is invalid
        """
        # Inject dependencies into kwargs
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("get_config", self._get_config)
        kwargs.setdefault("call_operation", self._call_operation)

        # Get or create interface instance (cached for state management)
        if interface not in self._interface_instances:
            interface_factory = self._interfaces.get(interface)
            if not interface_factory:
                raise DomainGatewayError(f"Unknown interface: {interface}")

            self._interface_instances[interface] = interface_factory(
                get_logger=self._get_logger,
                get_metrics=self._get_metrics,
                call_operation=self._call_operation,
                domain_name=self._domain_name,
                interface_name=interface,
            )

        # Execute operation on cached interface
        interface_instance = self._interface_instances[interface]
        return interface_instance.execute_operation(operation, **kwargs)

    def list_all(self) -> Dict[str, Any]:
        """List all infrastructure domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": self._domain_name,
            "interfaces": {
                "plugins": {
                    "description": "Plugin loading and management",
                    "operations": [
                        {"operation": "load", "description": "Load a plugin"},
                        {"operation": "unload", "description": "Unload a plugin"},
                        {"operation": "reload", "description": "Reload a plugin"},
                        {"operation": "list", "description": "List all plugins"},
                        {"operation": "get_info", "description": "Get plugin information"},
                        {"operation": "enable", "description": "Enable a plugin"},
                        {"operation": "disable", "description": "Disable a plugin"},
                    ]
                },
            }
        }


__all__ = [
    "InfrastructureGateway",
]
