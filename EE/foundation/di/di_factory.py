"""
DI Factory - Foundation Domain

Dependency injection container implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- Thread-safe DI container
- NO cross-domain imports (uses call_operation callback)
"""

import logging
import threading
import inspect
from typing import Any, Dict, Optional, Callable, Type, List, Union
from enum import Enum, auto
from dataclasses import dataclass, field


class ServiceLifetime(Enum):
    """Service lifetime scope."""
    SINGLETON = auto()  # One instance for entire container
    TRANSIENT = auto()  # New instance each time
    SCOPED = auto()     # One instance per scope


@dataclass
class ServiceDescriptor:
    """Describes a registered service."""
    service_type: Type
    implementation: Union[Type, Callable]
    lifetime: ServiceLifetime
    instance: Optional[Any] = None
    factory: Optional[Callable] = None
    dependencies: List[Type] = field(default_factory=list)


class DIFactory:
    """Dependency injection container factory.

    Provides DI container functionality with:
    - Service registration (singleton, transient, scoped)
    - Automatic dependency injection
    - Circular dependency detection
    - Thread-safe operations

    UG-ISP Compliance:
    - Cross-domain calls via call_operation callback
    - Thread-safe operations
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize DI factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        self._services: Dict[Type, ServiceDescriptor] = {}
        self._lock = threading.RLock()

    def container_create(self, **kwargs) -> 'DIFactory':
        """Create new DI container.

        Args:
            **kwargs: Additional parameters

        Returns:
            New DI factory instance
        """
        return DIFactory(
            logger=self.logger,
            metrics=self.metrics,
            call_operation=self.call_operation
        )

    def register_singleton(
        self,
        service_type: Type,
        implementation: Type,
        **kwargs
    ) -> None:
        """Register singleton service.

        Args:
            service_type: Service type/interface
            implementation: Implementation class
            **kwargs: Additional parameters
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON,
            dependencies=self._get_dependencies(implementation)
        )

        with self._lock:
            self._services[service_type] = descriptor

        self.logger.info(f"Registered singleton: {service_type.__name__}")

    def register_transient(
        self,
        service_type: Type,
        implementation: Type,
        **kwargs
    ) -> None:
        """Register transient service.

        Args:
            service_type: Service type/interface
            implementation: Implementation class
            **kwargs: Additional parameters
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT,
            dependencies=self._get_dependencies(implementation)
        )

        with self._lock:
            self._services[service_type] = descriptor

        self.logger.info(f"Registered transient: {service_type.__name__}")

    def register_scoped(
        self,
        service_type: Type,
        implementation: Type,
        **kwargs
    ) -> None:
        """Register scoped service.

        Args:
            service_type: Service type/interface
            implementation: Implementation class
            **kwargs: Additional parameters
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED,
            dependencies=self._get_dependencies(implementation)
        )

        with self._lock:
            self._services[service_type] = descriptor

        self.logger.info(f"Registered scoped: {service_type.__name__}")

    def register_factory(
        self,
        service_type: Type,
        factory: Callable,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
        **kwargs
    ) -> None:
        """Register factory function.

        Args:
            service_type: Service type
            factory: Factory function
            lifetime: Service lifetime
            **kwargs: Additional parameters
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=factory,
            lifetime=lifetime,
            factory=factory
        )

        with self._lock:
            self._services[service_type] = descriptor

        self.logger.info(f"Registered factory: {service_type.__name__}")

    def resolve(self, service_type: Type, resolving: set = None, **kwargs) -> Any:
        """Resolve service instance.

        Args:
            service_type: Type to resolve
            resolving: Set of types being resolved (for circular detection)
            **kwargs: Additional parameters

        Returns:
            Service instance

        Raises:
            ValueError: If service not registered or circular dependency
        """
        resolving = resolving or set()

        # Check for circular dependencies
        if service_type in resolving:
            self.logger.error(f"Circular dependency detected: {service_type.__name__}")
            raise ValueError(f"Circular dependency detected: {service_type.__name__}")

        with self._lock:
            if service_type not in self._services:
                self.logger.error(f"Service not found: {service_type.__name__}")
                raise ValueError(f"Service {service_type.__name__} not registered")

            descriptor = self._services[service_type]

        # Return existing instance for singletons
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is not None:
                return descriptor.instance

        # Create instance
        instance = self._create_instance(descriptor, resolving | {service_type})

        # Store singleton instance
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            with self._lock:
                descriptor.instance = instance

        return instance

    def _create_instance(
        self,
        descriptor: ServiceDescriptor,
        resolving: set
    ) -> Any:
        """Create service instance."""
        # Use factory if available
        if descriptor.factory:
            return descriptor.factory()

        # Get constructor parameters
        if callable(descriptor.implementation):
            sig = inspect.signature(descriptor.implementation)
            params = {}

            # Inject dependencies
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue

                if param.annotation != inspect.Parameter.empty:
                    dep_type = param.annotation
                    try:
                        params[param_name] = self.resolve(dep_type, resolving)
                    except (ValueError, KeyError):
                        if param.default != inspect.Parameter.empty:
                            params[param_name] = param.default
                        else:
                            raise

            return descriptor.implementation(**params)

        # Simple instantiation
        return descriptor.implementation()

    def _get_dependencies(self, implementation: Union[Type, Callable]) -> List[Type]:
        """Extract dependencies from implementation."""
        dependencies = []

        if callable(implementation):
            sig = inspect.signature(implementation)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)

        return dependencies

    def is_registered(self, service_type: Type, **kwargs) -> bool:
        """Check if service is registered.

        Args:
            service_type: Service type
            **kwargs: Additional parameters

        Returns:
            True if registered
        """
        with self._lock:
            return service_type in self._services

    def get_services(self, **kwargs) -> List[Type]:
        """Get registered service types.

        Args:
            **kwargs: Additional parameters

        Returns:
            List of service types
        """
        with self._lock:
            return list(self._services.keys())

    def clear(self, **kwargs) -> None:
        """Clear all services.

        Args:
            **kwargs: Additional parameters
        """
        with self._lock:
            # Dispose singleton instances
            for descriptor in self._services.values():
                if descriptor.instance and hasattr(descriptor.instance, 'dispose'):
                    try:
                        descriptor.instance.dispose()
                    except Exception:
                        pass

            self._services.clear()
            self.logger.info("DI container cleared")


__all__ = [
    "DIFactory",
    "ServiceLifetime",
    "ServiceDescriptor",
]
