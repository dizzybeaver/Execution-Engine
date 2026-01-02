"""Utility Interface Router - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Utility interface with UtilityFactory implementation
Type: EE 2.1 Interface Router
"""

from typing import Any, Callable
from EE.scanner.interface.utility.utility_factory import UtilityFactory


class UtilityInterface:
    """Utility Interface - EE 2.1 Compliant.

    Routes utility operations to UtilityFactory which contains all business logic.
    """

    def __init__(
        self,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable
    ):
        """Initialize Utility Interface with DI.

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
        self._factory = UtilityFactory(
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute utility operation.

        Args:
            operation: Utility operation name
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown
        """
        # Dispatch to factory methods
        # File operations
        if operation == 'read_file':
            return self._factory.read_file(kwargs.get('file_path'))
        elif operation == 'write_file':
            return self._factory.write_file(
                kwargs.get('file_path'),
                kwargs.get('content')
            )
        elif operation == 'list_files':
            return self._factory.list_files(
                kwargs.get('directory'),
                kwargs.get('pattern', '*')
            )
        elif operation == 'ensure_directory':
            return self._factory.ensure_directory(kwargs.get('directory'))

        # DateTime utilities
        elif operation == 'get_timestamp':
            return self._factory.get_timestamp()
        elif operation == 'get_date_string':
            return self._factory.get_date_string()
        elif operation == 'generate_scan_id':
            return self._factory.generate_scan_id()

        # Formatting utilities
        elif operation == 'format_json':
            return self._factory.format_json(
                kwargs.get('data'),
                kwargs.get('indent', 2)
            )
        elif operation == 'parse_json':
            return self._factory.parse_json(kwargs.get('json_str'))
        elif operation == 'format_markdown_table':
            return self._factory.format_markdown_table(
                kwargs.get('headers', []),
                kwargs.get('rows', [])
            )
        else:
            raise ValueError(
                f"Unknown utility operation: '{operation}'. "
                f"Valid: read_file, write_file, list_files, ensure_directory, "
                f"get_timestamp, get_date_string, generate_scan_id, "
                f"format_json, parse_json, format_markdown_table"
            )


def UtilityInterfaceFactory(
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable
) -> UtilityInterface:
    """Factory function to create UtilityInterface instance.

    Args:
        get_logger: Logger getter function
        get_metrics: Metrics getter function
        get_config: Config getter function
        call_operation: Operation caller function

    Returns:
        UtilityInterface instance
    """
    return UtilityInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation
    )


__all__ = ['UtilityInterface', 'UtilityInterfaceFactory']
