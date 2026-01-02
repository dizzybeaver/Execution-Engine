"""
SDK Gateway Domain - EE SDK Domain Gateway

This module provides the SDK domain gateway implementation for the EE Universal
Gateway system. It integrates SDK functionality with the gateway registry
and enables both local and remote SDK operations through a unified interface.

Architecture Layer: Layer 1 - Domain Gateway
Part of: SDK Domain Gateway (gateway.sdk)

Routes:
    - sdk.initialize: Initialize SDK instance
    - sdk.call: Call SDK method
    - sdk.create: Create new SDK instance
    - sdk.shutdown: Shutdown SDK instance
    - sdk.list_operations: List all available operations
    - sdk.get_status: Get SDK status
    - sdk.validate_config: Validate SDK configuration
    - sdk.list_instances: List all SDK instances

Based on Gateway reference implementation patterns.
"""

from __future__ import annotations
import sys
import threading
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field

# REMOVED: sys.path.insert() - using proper imports

from EE.universal_gateway.domain_gateway import DomainGateway

# Import SDK components
from EE.sdk.sdk_factory import SDKFactory, create_sdk_factory
from EE.sdk.sdk_common import (
    SDKGatewayError,
    SDKConfigurationError,
    SDKNotFoundError,
)


class SDKGatewayDomain(DomainGateway):
    """SDK Domain Gateway for EE Universal Gateway System.

    This domain gateway provides SDK management and execution capabilities
    for the EE gateway system. It supports both local and remote SDK instances,
    manages their lifecycle, and integrates with the gateway registry.

    Attributes:
        factory: SDK factory for instance management
        _lock: Threading lock for thread-safe operations

    Routes:
        - sdk.create: Create new SDK instance
        - sdk.initialize: Initialize SDK instance
        - sdk.call: Call SDK method
        - sdk.shutdown: Shutdown SDK instance
        - sdk.get_status: Get SDK status
        - sdk.validate_config: Validate SDK configuration
        - sdk.list_instances: List all SDK instances
        - sdk.list_operations: List all SDK operations
        - sdk.remove_instance: Remove SDK instance

    Example:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> from EE.sdk import SDKGatewayDomain
        >>>
        >>> registry = EEDomainRegistry.get_instance()
        >>> sdk_gateway = SDKGatewayDomain(
        ...     domain_name="sdk",
        ...     get_logger=registry.get_logger,
        ...     get_metrics=registry.get_metrics,
        ...     get_config=registry.get_config,
        ...     call_operation=registry.call_operation
        ... )
        >>>
        >>> # Register SDK domain
        >>> registry.register("sdk", sdk_gateway)
        >>>
        >>> # Create local SDK
        >>> result = sdk_gateway.execute("sdk.create", {
        ...     "sdk_type": "local",
        ...     "name": "processor",
        ...     "config": {
        ...         "methods": {"process": my_handler},
        ...         "timeout": 30
        ...     }
        ... })
        >>>
        >>> # Call SDK method
        >>> result = sdk_gateway.execute("sdk.call", {
        ...     "sdk_name": "processor",
        ...     "method": "process",
        ...     "params": {"data": "input"}
        ... })
    """

    # MODIFIED: EE 2.1 uniform constructor signature
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ) -> None:
        """Initialize SDK Gateway Domain with EE 2.1 dependencies.

        Args:
            domain_name: Domain name for this gateway
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        # ADDED: Call parent __init__ with all EE 2.1 parameters
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation,
        )

        # SDK-specific initialization
        self.factory: SDKFactory = create_sdk_factory()
        self._lock = threading.Lock()

    def execute(self, route: str, payload: dict) -> Any:
        """Execute SDK gateway operation.

        Args:
            route: Operation route (e.g., "sdk.create", "sdk.call")
            payload: Operation parameters as dictionary

        Returns:
            Operation result

        Raises:
            GatewayError: If operation fails or route is unknown
        """
        try:
            if route == "sdk.create":
                return self._create_sdk(payload)
            elif route == "sdk.initialize":
                return self._initialize_sdk(payload)
            elif route == "sdk.call":
                return self._call_sdk(payload)
            elif route == "sdk.shutdown":
                return self._shutdown_sdk(payload)
            elif route == "sdk.get_status":
                return self._get_status(payload)
            elif route == "sdk.validate_config":
                return self._validate_config(payload)
            elif route == "sdk.list_instances":
                return self._list_instances(payload)
            elif route == "sdk.list_operations":
                return self.list_all()
            elif route == "sdk.remove_instance":
                return self._remove_instance(payload)
            else:
                raise GatewayError(f"Unknown SDK route: {route}")

        except GatewayError:
            # Re-raise GatewayError as-is
            raise
        except Exception as e:
            raise GatewayError(f"SDK gateway error: {e}") from e

    # ========================================================================
    # Route Implementations
    # ========================================================================

    def _create_sdk(self, payload: dict) -> Dict[str, Any]:
        """Create a new SDK instance.

        Args:
            payload: {
                "sdk_type": str,  # "local" or "remote"
                "name": str,  # Unique instance name
                "config": dict  # SDK configuration
            }

        Returns:
            Dictionary with creation result

        Raises:
            GatewayError: If creation fails
        """
        sdk_type = payload.get("sdk_type")
        name = payload.get("name")
        config = payload.get("config", {})

        if not sdk_type:
            raise GatewayError("sdk_type is required")
        if not name:
            raise GatewayError("name is required")
        if not config:
            raise GatewayError("config is required")

        try:
            instance = self.factory.create(
                sdk_type=sdk_type,
                name=name,
                config=config,
            )

            return {
                "success": True,
                "message": f"SDK '{name}' created successfully",
                "sdk_name": name,
                "sdk_type": sdk_type,
                "instance": instance.to_dict(),
            }

        except SDKConfigurationError as e:
            raise GatewayError(f"SDK configuration error: {e}") from e
        except SDKInitializationError as e:
            raise GatewayError(f"SDK initialization error: {e}") from e

    def _initialize_sdk(self, payload: dict) -> Dict[str, Any]:
        """Initialize an existing SDK instance.

        Note: SDKs are auto-initialized during creation, so this is mainly
        for re-initialization after shutdown.

        Args:
            payload: {
                "sdk_name": str  # SDK instance name
            }

        Returns:
            Dictionary with initialization result

        Raises:
            GatewayError: If initialization fails
        """
        sdk_name = payload.get("sdk_name")

        if not sdk_name:
            raise GatewayError("sdk_name is required")

        try:
            instance_wrapper = self.factory.get_instance(sdk_name)
            sdk = instance_wrapper.sdk

            sdk.initialize()
            instance_wrapper.mark_initialized()

            return {
                "success": True,
                "message": f"SDK '{sdk_name}' initialized successfully",
                "sdk_name": sdk_name,
            }

        except SDKNotFoundError as e:
            raise GatewayError(f"SDK not found: {e}") from e
        except Exception as e:
            raise GatewayError(f"Failed to initialize SDK: {e}") from e

    def _call_sdk(self, payload: dict) -> Any:
        """Call a method on an SDK instance.

        Args:
            payload: {
                "sdk_name": str,  # SDK instance name
                "method": str,  # Method name to call
                "params": dict,  # Method parameters (optional)
                "timeout": float,  # Timeout in seconds (optional)
                "http_method": str  # HTTP method for remote SDK (optional)
            }

        Returns:
            Method execution result

        Raises:
            GatewayError: If call fails
        """
        sdk_name = payload.get("sdk_name")
        method = payload.get("method")
        params = payload.get("params", {})
        timeout = payload.get("timeout")
        http_method = payload.get("http_method", "POST")

        if not sdk_name:
            raise GatewayError("sdk_name is required")
        if not method:
            raise GatewayError("method is required")

        try:
            sdk = self.factory.get(sdk_name)

            # Build kwargs for call
            call_kwargs = {"method": method, "params": params}
            if timeout is not None:
                call_kwargs["timeout"] = timeout

            # For remote SDKs, add http_method
            if http_method != "POST":
                call_kwargs["http_method"] = http_method

            result = sdk.call(**call_kwargs)

            return {
                "success": True,
                "result": result,
                "sdk_name": sdk_name,
                "method": method,
            }

        except SDKNotFoundError as e:
            raise GatewayError(f"SDK not found: {e}") from e
        except Exception as e:
            raise GatewayError(f"SDK call failed: {e}") from e

    def _shutdown_sdk(self, payload: dict) -> Dict[str, Any]:
        """Shutdown an SDK instance.

        Args:
            payload: {
                "sdk_name": str  # SDK instance name
            }

        Returns:
            Dictionary with shutdown result

        Raises:
            GatewayError: If shutdown fails
        """
        sdk_name = payload.get("sdk_name")

        if not sdk_name:
            raise GatewayError("sdk_name is required")

        try:
            self.factory.shutdown(sdk_name)

            return {
                "success": True,
                "message": f"SDK '{sdk_name}' shut down successfully",
                "sdk_name": sdk_name,
            }

        except SDKNotFoundError as e:
            raise GatewayError(f"SDK not found: {e}") from e
        except Exception as e:
            raise GatewayError(f"Failed to shutdown SDK: {e}") from e

    def _get_status(self, payload: dict) -> Dict[str, Any]:
        """Get status of an SDK instance.

        Args:
            payload: {
                "sdk_name": str  # SDK instance name
            }

        Returns:
            Dictionary with SDK status information

        Raises:
            GatewayError: If SDK not found
        """
        sdk_name = payload.get("sdk_name")

        if not sdk_name:
            raise GatewayError("sdk_name is required")

        try:
            sdk = self.factory.get(sdk_name)
            status = sdk.get_status()

            # Add instance metadata
            instance_wrapper = self.factory.get_instance(sdk_name)
            status.update(instance_wrapper.to_dict())

            return status

        except SDKNotFoundError as e:
            raise GatewayError(f"SDK not found: {e}") from e

    def _validate_config(self, payload: dict) -> Dict[str, Any]:
        """Validate SDK configuration without creating instance.

        Args:
            payload: {
                "sdk_type": str,  # "local" or "remote"
                "config": dict  # Configuration to validate
            }

        Returns:
            Dictionary with validation result

        Raises:
            GatewayError: If validation fails
        """
        sdk_type = payload.get("sdk_type")
        config = payload.get("config", {})

        if not sdk_type:
            raise GatewayError("sdk_type is required")
        if not config:
            raise GatewayError("config is required")

        try:
            # Validate based on SDK type
            if sdk_type == "local":
                from EE.sdk.sdk_local import create_local_sdk
                # Attempt to create to validate config
                # (We don't keep the instance)
                try:
                    test_sdk = create_local_sdk(config)
                    return {
                        "success": True,
                        "message": "Local SDK configuration is valid",
                        "sdk_type": sdk_type,
                    }
                except SDKConfigurationError as e:
                    return {
                        "success": False,
                        "message": str(e),
                        "sdk_type": sdk_type,
                    }

            elif sdk_type == "remote":
                from EE.sdk.sdk_remote import create_remote_sdk
                try:
                    test_sdk = create_remote_sdk(config)
                    return {
                        "success": True,
                        "message": "Remote SDK configuration is valid",
                        "sdk_type": sdk_type,
                    }
                except SDKConfigurationError as e:
                    return {
                        "success": False,
                        "message": str(e),
                        "sdk_type": sdk_type,
                    }

            else:
                return {
                    "success": False,
                    "message": f"Invalid SDK type: {sdk_type}",
                    "sdk_type": sdk_type,
                }

        except Exception as e:
            raise GatewayError(f"Configuration validation failed: {e}") from e

    def _list_instances(self, payload: dict) -> Dict[str, Any]:
        """List all SDK instances.

        Args:
            payload: Empty dictionary

        Returns:
            Dictionary with list of SDK instances
        """
        instances = self.factory.list_all()

        return {
            "instances": instances,
            "count": len(instances),
        }

    def _remove_instance(self, payload: dict) -> Dict[str, Any]:
        """Remove an SDK instance from the factory.

        This does not shutdown the SDK, just removes it from tracking.

        Args:
            payload: {
                "sdk_name": str  # SDK instance name
            }

        Returns:
            Dictionary with removal result

        Raises:
            GatewayError: If removal fails
        """
        sdk_name = payload.get("sdk_name")

        if not sdk_name:
            raise GatewayError("sdk_name is required")

        try:
            self.factory.remove(sdk_name)

            return {
                "success": True,
                "message": f"SDK '{sdk_name}' removed successfully",
                "sdk_name": sdk_name,
            }

        except SDKNotFoundError as e:
            raise GatewayError(f"SDK not found: {e}") from e
        except Exception as e:
            raise GatewayError(f"Failed to remove SDK: {e}") from e

    def list_all(self) -> Dict[str, Any]:
        """List all SDK gateway operations.

        Returns:
            Dictionary with operation metadata
        """
        return {
            "domain": "sdk",
            "description": "SDK domain gateway for local and remote SDK operations",
            "operations": [
                {
                    "route": "sdk.create",
                    "description": "Create new SDK instance",
                    "params": {
                        "sdk_type": "str (required) - SDK type: 'local' or 'remote'",
                        "name": "str (required) - Unique instance name",
                        "config": "dict (required) - SDK configuration",
                    },
                },
                {
                    "route": "sdk.initialize",
                    "description": "Initialize SDK instance",
                    "params": {
                        "sdk_name": "str (required) - SDK instance name",
                    },
                },
                {
                    "route": "sdk.call",
                    "description": "Call SDK method",
                    "params": {
                        "sdk_name": "str (required) - SDK instance name",
                        "method": "str (required) - Method name to call",
                        "params": "dict (optional) - Method parameters",
                        "timeout": "float (optional) - Timeout in seconds",
                        "http_method": "str (optional) - HTTP method for remote SDK",
                    },
                },
                {
                    "route": "sdk.shutdown",
                    "description": "Shutdown SDK instance",
                    "params": {
                        "sdk_name": "str (required) - SDK instance name",
                    },
                },
                {
                    "route": "sdk.get_status",
                    "description": "Get SDK status",
                    "params": {
                        "sdk_name": "str (required) - SDK instance name",
                    },
                },
                {
                    "route": "sdk.validate_config",
                    "description": "Validate SDK configuration",
                    "params": {
                        "sdk_type": "str (required) - SDK type: 'local' or 'remote'",
                        "config": "dict (required) - Configuration to validate",
                    },
                },
                {
                    "route": "sdk.list_instances",
                    "description": "List all SDK instances",
                    "params": {},
                },
                {
                    "route": "sdk.remove_instance",
                    "description": "Remove SDK instance from factory",
                    "params": {
                        "sdk_name": "str (required) - SDK instance name",
                    },
                },
                {
                    "route": "sdk.list_operations",
                    "description": "List all SDK gateway operations",
                    "params": {},
                },
            ],
        }


__all__ = [
    'SDKGatewayDomain',
]
