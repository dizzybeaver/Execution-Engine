"""
Utility Interface - Foundation Domain

EE 2.1 Architecture:
- This is an Interface class (not a function)
- Implements execute_operation(operation, **kwargs) method
- Uses factory pool for factory instances
- Factory contains actual implementation
"""

from typing import Any, Dict, Optional, Callable
import logging

from EE.foundation.utility.utility_factory import UtilityFactory


class UtilityInterface:
    """Utility Interface - Routes helper function operations.

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
        """Initialize Utility Interface.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations
        """
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation

        # Get interface-level logger
        self._logger = self._get_logger("foundation.utility")
        self._metrics = self._get_metrics("foundation.utility")

        # Factory pool - reuses factory instances
        self._factory_pool: Dict[int, UtilityFactory] = {}
        self._pool_lock = __import__("threading").RLock()

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """
        Execute utility operation (Interface Method).

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
                'json_to_string': factory.json_to_string,
                'json_from_string': factory.json_from_string,
                'generate_uuid': factory.generate_uuid,
                'validate_string': factory.validate_string,
                'validate_dict': factory.validate_dict,
                'sanitize_input': factory.sanitize_input,
            }

            handler = _DISPATCH.get(operation)

            if not handler:
                raise ValueError(
                    f"Unknown utility operation: {operation}. "
                    f"Valid operations: {list(_DISPATCH.keys())}"
                )

            return handler(**kwargs)

        finally:
            # Return factory to pool
            self._return_factory(factory)

    def _get_factory(self) -> UtilityFactory:
        """Get factory from pool or create new instance.

        Returns:
            UtilityFactory instance
        """
        thread_id = __import__("threading").get_ident()

        with self._pool_lock:
            if thread_id not in self._factory_pool:
                self._factory_pool[thread_id] = UtilityFactory(
                    logger=self._logger,
                    metrics=self._metrics,
                    call_operation=self._call_operation
                )

            return self._factory_pool[thread_id]

    def _return_factory(self, factory: UtilityFactory) -> None:
        """Return factory to pool (no-op for now).

        Args:
            factory: Factory instance to return
        """
        # Factory is kept in pool per-thread
        pass


__all__ = [
    'UtilityInterface',
]
