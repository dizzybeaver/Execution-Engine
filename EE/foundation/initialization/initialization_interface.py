"""
Initialization Interface - Foundation Domain

EE 2.1 Architecture:
- This is an Interface class (not a function)
- Implements execute_operation(operation, **kwargs) method
- Uses factory pool for factory instances
- Factory contains actual implementation
"""

from typing import Any, Dict, Optional, Callable
import logging

from EE.foundation.initialization.initialization_factory import InitializationFactory


class InitializationInterface:
    """Initialization Interface - Routes system initialization operations.

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
        """Initialize Initialization Interface.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations
        """
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation

        # Get interface-level logger
        self._logger = self._get_logger("foundation.initialization")
        self._metrics = self._get_metrics("foundation.initialization")

        # Factory pool - reuses factory instances
        self._factory_pool: Dict[int, InitializationFactory] = {}
        self._pool_lock = __import__("threading").RLock()

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """
        Execute initialization operation (Interface Method).

        EE 2.1 Architecture:
        - Interface implements execute_operation() method
        - Uses factory pool for efficiency
        - Factory contains implementation

        Args:
            operation: Operation name
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
                'initialize': factory.initialize,
                'shutdown': factory.shutdown,
                'get_status': factory.get_status,
                'get_health': factory.get_health,
            }

            handler = _DISPATCH.get(operation)

            if not handler:
                raise ValueError(
                    f"Unknown initialization operation: {operation}. "
                    f"Valid operations: {list(_DISPATCH.keys())}"
                )

            return handler(**kwargs)

        finally:
            # Return factory to pool
            self._return_factory(factory)

    def _get_factory(self) -> InitializationFactory:
        """Get factory from pool or create new instance.

        Returns:
            InitializationFactory instance
        """
        thread_id = __import__("threading").get_ident()

        with self._pool_lock:
            if thread_id not in self._factory_pool:
                self._factory_pool[thread_id] = InitializationFactory(
                    logger=self._logger,
                    metrics=self._metrics,
                    call_operation=self._call_operation
                )

            return self._factory_pool[thread_id]

    def _return_factory(self, factory: InitializationFactory) -> None:
        """Return factory to pool (no-op for now).

        Args:
            factory: Factory instance to return
        """
        # Factory is kept in pool per-thread
        pass


__all__ = [
    'InitializationInterface',
]
