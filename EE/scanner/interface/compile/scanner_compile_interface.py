"""Compile Interface Router - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Compile interface with CompileFactory implementation
Type: EE 2.1 Interface Router
"""

from typing import Any, Callable
from EE.scanner.interface.compile.compile_factory import CompileFactory


class CompileInterface:
    """Compile Interface - EE 2.1 Compliant.

    Routes compile operations to CompileFactory which contains all business logic.
    """

    def __init__(
        self,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable
    ):
        """Initialize Compile Interface with DI.

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
        self._factory = CompileFactory(
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute compile operation.

        Args:
            operation: Compile operation name (all, interface, file)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown
        """
        # Dispatch to factory methods
        if operation == 'all':
            return self._factory.compile_all(kwargs.get('path', '.'))
        elif operation == 'interface':
            return self._factory.compile_interface(
                kwargs.get('interface_name'),
                kwargs.get('base_path', '.')
            )
        elif operation == 'file':
            return self._factory.compile_file(kwargs.get('file_path'))
        else:
            raise ValueError(
                f"Unknown compile operation: '{operation}'. "
                f"Valid: all, interface, file"
            )


def CompileInterfaceFactory(
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable
) -> CompileInterface:
    """Factory function to create CompileInterface instance.

    Args:
        get_logger: Logger getter function
        get_metrics: Metrics getter function
        get_config: Config getter function
        call_operation: Operation caller function

    Returns:
        CompileInterface instance
    """
    return CompileInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation
    )


__all__ = ['CompileInterface', 'CompileInterfaceFactory']
