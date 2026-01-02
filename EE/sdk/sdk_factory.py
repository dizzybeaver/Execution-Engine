"""
SDK Factory - EE SDK Instance Creation Layer

This module provides the factory pattern for creating SDK instances with
configuration validation, lifecycle management, and instance tracking.

Architecture Layer: SDK Domain - Factory Layer

Based on Gateway reference implementation patterns.

Integration:
    - Uses SDKGatewayError from sdk_common
    - Provides SDK instance creation and management
    - Supports both local and remote SDK types
    - Handles configuration validation and initialization

Usage:
    >>> from EE.sdk import create_sdk_factory
    >>>
    >>> # Create factory
    >>> factory = create_sdk_factory()
    >>>
    >>> # Create local SDK
    >>> local_sdk = factory.create(
    ...     sdk_type="local",
    ...     name="processor",
    ...     config={...}
    ... )
    >>>
    >>> # Create remote SDK
    >>> remote_sdk = factory.create(
    ...     sdk_type="remote",
    ...     name="remote_processor",
    ...     config={...}
    ... )
    >>>
    >>> # Get SDK by name
    >>> sdk = factory.get("processor")
    >>>
    >>> # List all SDKs
    >>> all_sdks = factory.list_all()
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import threading

from EE.sdk.sdk_common import (
    SDKGatewayError,
    SDKInitializationError,
    SDKConfigurationError,
    SDKNotFoundError,
)


@dataclass
class SDKInstance:
    """Represents a single SDK instance with metadata and lifecycle state.

    An SDKInstance encapsulates all information about a running SDK instance,
    including its type, configuration, state, and execution statistics.

    Attributes:
        name: Unique instance name/identifier
        sdk_type: Type of SDK ("local" or "remote")
        sdk: The actual SDK instance (LocalSDK or RemoteSDK)
        config: Configuration used to initialize the SDK
        created_at: Timestamp when instance was created
        initialized_at: Timestamp when initialization completed (None if not initialized)
        status: Current status ("created", "initialized", "error", "shutdown")
        error: Error message if status is "error"
        stats: Execution statistics (call count, success rate, etc.)

    Example:
        >>> instance = SDKInstance(
        ...     name="processor",
        ...     sdk_type="local",
        ...     sdk=local_sdk,
        ...     config={"timeout": 30}
        ... )
        >>> print(f"Status: {instance.status}")
        >>> print(f"Created: {instance.created_at}")
    """
    name: str
    sdk_type: str
    sdk: Any
    config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    initialized_at: Optional[datetime] = None
    status: str = "created"
    error: Optional[str] = None
    stats: Dict[str, Any] = field(default_factory=dict)

    def mark_initialized(self) -> None:
        """Mark instance as successfully initialized."""
        self.initialized_at = datetime.now()
        self.status = "initialized"
        self.error = None

    def mark_error(self, error_message: str) -> None:
        """Mark instance as having an error."""
        self.status = "error"
        self.error = error_message

    def mark_shutdown(self) -> None:
        """Mark instance as shut down."""
        self.status = "shutdown"

    def update_stats(self, key: str, value: Any) -> None:
        """Update execution statistics."""
        self.stats[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary representation.

        Returns:
            Dictionary with all instance information (excluding the SDK object itself)
        """
        return {
            "name": self.name,
            "sdk_type": self.sdk_type,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "initialized_at": self.initialized_at.isoformat() if self.initialized_at else None,
            "status": self.status,
            "error": self.error,
            "stats": self.stats,
        }


class SDKFactory:
    """Factory for creating and managing SDK instances.

    The SDKFactory provides centralized management of SDK instances with:
    - Instance creation with configuration validation
    - Lifecycle tracking (created, initialized, error, shutdown)
    - Statistics collection
    - Thread-safe instance management

    Attributes:
        instances: Dictionary of managed SDK instances by name
        _lock: Threading lock for thread-safe operations

    Example:
        >>> factory = SDKFactory()
        >>>
        >>> # Create SDK instance
        >>> instance = factory.create(
        ...     sdk_type="local",
        ...     name="processor",
        ...     config={"handler": my_handler}
        ... )
        >>>
        >>> # Get instance
        >>> sdk = factory.get("processor")
        >>>
        >>> # Shutdown instance
        >>> factory.shutdown("processor")
    """

    def __init__(self) -> None:
        """Initialize SDK Factory."""
        self.instances: Dict[str, SDKInstance] = {}
        self._lock = threading.Lock()

    def create(
        self,
        *,
        sdk_type: str,
        name: str,
        config: Dict[str, Any],
    ) -> SDKInstance:
        """Create a new SDK instance.

        Args:
            sdk_type: Type of SDK ("local" or "remote")
            name: Unique instance name/identifier
            config: SDK configuration dictionary

        Returns:
            SDKInstance wrapper

        Raises:
            SDKConfigurationError: If SDK already exists or config is invalid
            SDKInitializationError: If SDK initialization fails

        Example:
            >>> instance = factory.create(
            ...     sdk_type="local",
            ...     name="processor",
            ...     config={
            ...         "handler": my_handler,
            ...         "timeout": 30
            ...     }
            ... )
        """
        with self._lock:
            # Check if SDK already exists
            if name in self.instances:
                raise SDKConfigurationError(
                    message=f"SDK '{name}' already exists",
                    sdk_type=sdk_type,
                    config=config,
                )

            # Validate SDK type
            if sdk_type not in ("local", "remote"):
                raise SDKConfigurationError(
                    message=f"Invalid SDK type: {sdk_type}. Must be 'local' or 'remote'",
                    sdk_type=sdk_type,
                    config=config,
                )

            # Import SDK classes
            try:
                if sdk_type == "local":
                    from EE.sdk.sdk_local import LocalSDK, create_local_sdk
                    sdk = create_local_sdk(config=config)
                else:  # remote
                    from EE.sdk.sdk_remote import RemoteSDK, create_remote_sdk
                    sdk = create_remote_sdk(config=config)
            except ImportError as e:
                raise SDKInitializationError(
                    message=f"Failed to import SDK module for type '{sdk_type}'",
                    sdk_type=sdk_type,
                    sdk_name=name,
                    reason=str(e),
                ) from e

            # Create instance wrapper
            instance = SDKInstance(
                name=name,
                sdk_type=sdk_type,
                sdk=sdk,
                config=config,
            )

            # Initialize SDK
            try:
                sdk.initialize()
                instance.mark_initialized()
            except Exception as e:
                instance.mark_error(str(e))
                raise SDKInitializationError(
                    message=f"Failed to initialize SDK '{name}'",
                    sdk_type=sdk_type,
                    sdk_name=name,
                    reason=str(e),
                ) from e

            # Store instance
            self.instances[name] = instance

            return instance

    def get(self, name: str) -> Any:
        """Get SDK instance by name.

        Args:
            name: SDK instance name

        Returns:
            SDK instance (LocalSDK or RemoteSDK)

        Raises:
            SDKNotFoundError: If SDK instance not found

        Example:
            >>> sdk = factory.get("processor")
            >>> result = sdk.call("process_data", {...})
        """
        with self._lock:
            if name not in self.instances:
                available = list(self.instances.keys())
                raise SDKNotFoundError(
                    sdk_name=name,
                    available_sdks=available,
                )

            instance = self.instances[name]
            return instance.sdk

    def get_instance(self, name: str) -> SDKInstance:
        """Get SDKInstance wrapper by name.

        Use this to access metadata and statistics.

        Args:
            name: SDK instance name

        Returns:
            SDKInstance wrapper with metadata

        Raises:
            SDKNotFoundError: If SDK instance not found

        Example:
            >>> instance = factory.get_instance("processor")
            >>> print(f"Status: {instance.status}")
            >>> print(f"Stats: {instance.stats}")
        """
        with self._lock:
            if name not in self.instances:
                available = list(self.instances.keys())
                raise SDKNotFoundError(
                    sdk_name=name,
                    available_sdks=available,
                )

            return self.instances[name]

    def shutdown(self, name: str) -> None:
        """Shutdown SDK instance.

        Args:
            name: SDK instance name

        Raises:
            SDKNotFoundError: If SDK instance not found
            SDKGatewayError: If shutdown fails

        Example:
            >>> factory.shutdown("processor")
        """
        with self._lock:
            if name not in self.instances:
                raise SDKNotFoundError(
                    sdk_name=name,
                    available_sdks=list(self.instances.keys()),
                )

            instance = self.instances[name]

            try:
                instance.sdk.shutdown()
                instance.mark_shutdown()
            except Exception as e:
                raise SDKGatewayError(
                    message=f"Failed to shutdown SDK '{name}'",
                    error_code="SDK_SHUTDOWN_ERROR",
                    context={"sdk_name": name},
                    sdk_name=name,
                    operation="shutdown",
                ) from e

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all SDK instances.

        Returns:
            Dictionary mapping SDK names to their metadata

        Example:
            >>> all_sdks = factory.list_all()
            >>> for name, info in all_sdks.items():
            ...     print(f"{name}: {info['status']}")
        """
        with self._lock:
            return {
                name: instance.to_dict()
                for name, instance in self.instances.items()
            }

    def remove(self, name: str) -> None:
        """Remove SDK instance from factory.

        This does not shutdown the SDK, just removes it from tracking.

        Args:
            name: SDK instance name

        Raises:
            SDKNotFoundError: If SDK instance not found

        Example:
            >>> factory.remove("processor")
        """
        with self._lock:
            if name not in self.instances:
                raise SDKNotFoundError(
                    sdk_name=name,
                    available_sdks=list(self.instances.keys()),
                )

            del self.instances[name]

    def clear(self) -> None:
        """Clear all SDK instances from factory.

        Example:
            >>> factory.clear()
        """
        with self._lock:
            self.instances.clear()


def create_sdk_factory() -> SDKFactory:
    """Factory function to create an SDKFactory.

    This provides a clean interface for creating an SDK factory.

    Returns:
        New SDKFactory instance

    Example:
        >>> factory = create_sdk_factory()
        >>> instance = factory.create(
        ...     sdk_type="local",
        ...     name="processor",
        ...     config={...}
        ... )
    """
    return SDKFactory()


__all__ = [
    'SDKInstance',
    'SDKFactory',
    'create_sdk_factory',
]
