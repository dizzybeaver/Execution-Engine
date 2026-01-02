"""
Plugins Interface Router - Infrastructure Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Protocol
from EE.infrastructure.plugins.plugins_factory import PluginsFactory, PluginState


# Type protocols for dependency injection
class LoggerFactory(Protocol):
    def __call__(self, name: str) -> Any: ...


class MetricsFactory(Protocol):
    def __call__(self, name: str) -> Any: ...


class OperationCaller(Protocol):
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...


def create_plugins_interface(
    get_logger: LoggerFactory,
    get_metrics: MetricsFactory,
    call_operation: OperationCaller,
    domain_name: str,
    interface_name: str,
) -> 'PluginsInterface':
    """Create plugins interface instance with injected dependencies.

    UG-ISP Compliant:
    - Factory function for interface creation
    - All dependencies injected
    - No direct imports outside domain

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        call_operation: Function to call operations in other domains
        domain_name: Name of the domain (infrastructure)
        interface_name: Name of the interface (plugins)

    Returns:
        Configured PluginsInterface instance
    """
    return PluginsInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


class PluginsInterface:
    """Plugins Interface - Router Layer.

    Uses DISPATCH dictionary pattern for O(1) operation routing.
    Factory contains actual implementation.
    """

    def __init__(
        self,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        call_operation: OperationCaller,
        domain_name: str,
        interface_name: str,
    ):
        """Initialize plugins interface with injected dependencies."""
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation
        self._domain_name = domain_name
        self._interface_name = interface_name

        # Get interface-level logger and metrics
        self._logger = get_logger(f"{domain_name}.{interface_name}")
        self._metrics = get_metrics(f"{domain_name}.{interface_name}")

        # Create factory instance
        self._factory = PluginsFactory(
            logger=self._logger,
            metrics=self._metrics,
            call_operation=call_operation,
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute plugins operation through DISPATCH router.

        UG-ISP Compliant:
        - DISPATCH dictionary for O(1) lookup
        - Factory contains implementation
        - Cross-domain via call_operation only

        Args:
            operation: Operation name (load, unload, list, get_info, reload, enable, disable)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation not found
        """
        # DISPATCH Dictionary (DD-1 Pattern)
        _DISPATCH = {
            'load': self._factory.load,
            'unload': self._factory.unload,
            'reload': self._factory.reload,
            'list': self._factory.list,
            'get_info': self._factory.get_info,
            'enable': self._factory.enable,
            'disable': self._factory.disable,
        }

        handler = _DISPATCH.get(operation)

        if not handler:
            raise ValueError(
                f"Unknown plugins operation: {operation}. "
                f"Valid operations: {list(_DISPATCH.keys())}"
            )

        return handler(**kwargs)


__all__ = [
    'create_plugins_interface',
    'PluginsInterface',
    'PluginState',
]
