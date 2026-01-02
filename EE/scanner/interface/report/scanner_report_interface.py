"""Report Interface Router - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Report interface with ReportFactory implementation
Type: EE 2.1 Interface Router
"""

from typing import Any, Callable
from EE.scanner.interface.report.report_factory import ReportFactory


class ReportInterface:
    """Report Interface - EE 2.1 Compliant.

    Routes report operations to ReportFactory which contains all business logic.
    """

    def __init__(
        self,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable
    ):
        """Initialize Report Interface with DI.

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
        self._factory = ReportFactory(
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute report operation.

        Args:
            operation: Report operation name (generate, last, list)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown
        """
        # Dispatch to factory methods
        if operation == 'generate':
            return self._factory.generate_report(
                kwargs.get('scan_id'),
                kwargs.get('output_format', 'markdown')
            )
        elif operation == 'last':
            return self._factory.report_last(
                kwargs.get('count', 1),
                kwargs.get('output_format', 'markdown')
            )
        elif operation == 'list':
            return self._factory.list_reports(kwargs.get('date'))
        else:
            raise ValueError(
                f"Unknown report operation: '{operation}'. "
                f"Valid: generate, last, list"
            )


def ReportInterfaceFactory(
    get_logger: Callable,
    get_metrics: Callable,
    get_config: Callable,
    call_operation: Callable
) -> ReportInterface:
    """Factory function to create ReportInterface instance.

    Args:
        get_logger: Logger getter function
        get_metrics: Metrics getter function
        get_config: Config getter function
        call_operation: Operation caller function

    Returns:
        ReportInterface instance
    """
    return ReportInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation
    )


__all__ = ['ReportInterface', 'ReportInterfaceFactory']
