"""
Singleton Interface - Foundation Domain

EE 2.1 Architecture:
- This is an Interface class (not a function)
- Implements execute_operation(operation, **kwargs) method
- Uses factory pool for factory instances
- Factory contains actual implementation
"""

from typing import Any, Dict, Optional, Callable
import logging

from EE.foundation.singleton.singleton_factory import SingletonFactory


class SingletonInterface:
    """Singleton Interface - Routes singleton management operations.

    EE 2.1 Architecture:
    - Interface IS a class with execute_operation() method
    - Maintains factory pool for efficient execution
    - Factory contains implementation
    """

    def __init__(
        self,
        get_logger: Callable,
        get_metrics: Callable,
        call_operation: Callable
    ):
        """Initialize Singleton Interface.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations
        """
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation

        # Get interface-level logger
        self._logger = self._get_logger("foundation.singleton")
        self._metrics = self._get_metrics("foundation.singleton")

        # Factory pool - reuses factory instances
        self._factory_pool: Dict[int, SingletonFactory] = {}
        self._pool_lock = __import__("threading").RLock()

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """
        Execute singleton operation (Interface Method).

        EE 2.1 Architecture:
        - Interface implements execute_operation() method
        - Uses factory pool for efficiency
        - Factory contains implementation

        Args:
            operation: Operation name (get, set, delete, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation not found
        """
        # Inject dependencies into kwargs
        kwargs.setdefault("logger", self._logger)
        kwargs.setdefault("metrics", self._metrics)
        kwargs.setdefault("call_operation", self._call_operation)

        # Get factory from pool or create new
        factory = self._get_factory()

        try:
            # DISPATCH Dictionary (DD-1 Pattern)
            _DISPATCH = {
                'get': factory.get,
                'set': factory.set,
                'delete': factory.delete,
                'exists': factory.exists,
                'list_all': factory.list_all,
                'clear': factory.clear,
            }

            handler = _DISPATCH.get(operation)

            if not handler:
                raise ValueError(
                    f"Unknown singleton operation: {operation}. "
                    f"Valid operations: {list(_DISPATCH.keys())}"
                )

            return handler(**kwargs)

        finally:
            # Return factory to pool
            self._return_factory(factory)

    def _get_factory(self) -> SingletonFactory:
        """Get factory from pool or create new instance.

        Returns:
            SingletonFactory instance
        """
        thread_id = __import__("threading").get_ident()

        with self._pool_lock:
            if thread_id not in self._factory_pool:
                self._factory_pool[thread_id] = SingletonFactory(
                    logger=self._logger,
                    metrics=self._metrics,
                    call_operation=self._call_operation
                )

            return self._factory_pool[thread_id]

    def _return_factory(self, factory: SingletonFactory) -> None:
        """Return factory to pool (no-op for now).

        Args:
            factory: Factory instance to return
        """
        # Factory is kept in pool per-thread
        pass


__all__ = [
    'SingletonInterface',
]
