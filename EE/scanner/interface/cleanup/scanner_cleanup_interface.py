"""Cleanup Interface Router - EE 2.1 Compliant.

Version: 2.1.0
Date: 2025-12-31
Purpose: Cleanup interface router with factory-based implementation
Type: EE 2.1 Interface Router

UG-ISP Pattern: Gateway -> Interface (Router) -> Factory (Implementation)
"""

from typing import Any, Callable
from EE.scanner.interface.cleanup.cleanup_factory import CleanupFactory


class CleanupInterface:
    """Cleanup Interface - EE 2.1 Compliant.

    Routes cleanup operations to CleanupFactory which contains
    all business logic for cleanup operations.

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
        """Initialize Cleanup Interface with DI.

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
        """Execute cleanup operation.

        Args:
            operation: Cleanup operation name (all, pycache, compiled)
            **kwargs: Operation parameters (e.g., path)

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown

        Example:
            # Called by Gateway via execute_operation()
            result = interface.execute_operation('all', path='.')
        """
        # Lazy factory initialization
        if self._factory is None:
            self._factory = CleanupFactory(
                get_logger=self._get_logger,
                get_metrics=self._get_metrics,
                get_config=self._get_config,
                call_operation=self._call_operation
            )

        # Dispatch to factory methods
        if operation == 'all':
            return self._factory.cleanup_all(kwargs.get('path', '.'))
        elif operation == 'pycache':
            return self._factory.cleanup_pycache(kwargs.get('path', '.'))
        elif operation == 'compiled':
            return self._factory.cleanup_compiled(kwargs.get('path', '.'))
        else:
            raise ValueError(
                f"Unknown cleanup operation: '{operation}'. "
                f"Valid: all, pycache, compiled"
            )


def CleanupInterfaceFactory(
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable
) -> CleanupInterface:
    """Factory function to create CleanupInterface instance.

    Args:
        get_logger: Logger getter function
        get_metrics: Metrics getter function
        get_config: Config getter function
        call_operation: Operation caller function

    Returns:
        CleanupInterface instance
    """
    return CleanupInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation
    )


__all__ = ['CleanupInterface', 'CleanupInterfaceFactory']
