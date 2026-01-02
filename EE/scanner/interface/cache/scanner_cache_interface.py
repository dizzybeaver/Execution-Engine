"""Cache Interface Router - EE 2.1 Compliant.

Version: 2.1.0
Date: 2025-12-31
Purpose: Cache interface router with factory-based implementation
Type: EE 2.1 Interface Router

UG-ISP Pattern: Gateway -> Interface (Router) -> Factory (Implementation)
"""

from typing import Any, Callable
from EE.scanner.interface.cache.cache_factory import CacheFactory


class CacheInterface:
    """Cache Interface - EE 2.1 Compliant.

    Routes cache operations to CacheFactory which contains
    all business logic for cache operations.

    UG-ISP Pattern:
    - Gateway calls execute_operation()
    - Interface routes to factory methods
    - Factory contains actual implementation
    """

    def __init__(
        self,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable
    ):
        """Initialize Cache Interface with DI.

        Args:
            get_logger: Logger getter function
            get_metrics: Metrics getter function
            get_config: Config getter function
            call_operation: Operation caller function
        """
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

        # Create factory instance
        self._factory = None

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute cache operation.

        Args:
            operation: Cache operation name (get, set, delete, clear, get_stats)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown

        Example:
            # Called by Gateway via execute_operation()
            result = interface.execute_operation('get', key='ast_cache:file.py')
        """
        # Lazy factory initialization
        if self._factory is None:
            self._factory = CacheFactory(
                get_logger=self._get_logger,
                get_metrics=self._get_metrics,
                get_config=self._get_config,
                call_operation=self._call_operation
            )

        # Dispatch to factory methods
        if operation == 'get':
            return self._factory.get(kwargs.get('key'))
        elif operation == 'set':
            return self._factory.set(kwargs.get('key'), kwargs.get('value'))
        elif operation == 'delete':
            return self._factory.delete(kwargs.get('key'))
        elif operation == 'clear':
            return self._factory.clear()
        elif operation == 'get_stats':
            return self._factory.get_stats()
        else:
            raise ValueError(
                f"Unknown cache operation: '{operation}'. "
                f"Valid: get, set, delete, clear, get_stats"
            )


def CacheInterfaceFactory(
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable
) -> CacheInterface:
    """Factory function to create CacheInterface instance.

    Args:
        get_logger: Logger getter function
        get_metrics: Metrics getter function
        get_config: Config getter function
        call_operation: Operation caller function

    Returns:
        CacheInterface instance
    """
    return CacheInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation
    )


__all__ = ['CacheInterface', 'CacheInterfaceFactory']
