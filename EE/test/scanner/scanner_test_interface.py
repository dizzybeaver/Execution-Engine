"""
Scanner Test Interface Router - Test Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Protocol
from EE.test.scanner.scanner_test_factory import ScannerTestFactory


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


def create_scanner_test_interface(
    get_logger: LoggerFactory,
    get_metrics: MetricsFactory,
    call_operation: OperationCaller,
    domain_name: str,
    interface_name: str,
) -> 'ScannerTestInterface':
    """Create scanner test interface instance with injected dependencies.

    UG-ISP Compliant:
    - Factory function for interface creation
    - All dependencies injected
    - No direct imports outside domain

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        call_operation: Function to call operations in other domains
        domain_name: Name of the domain (test)
        interface_name: Name of the interface (scanner)

    Returns:
        Configured ScannerTestInterface instance
    """
    return ScannerTestInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


class ScannerTestInterface:
    """Scanner Test Interface - Router Layer.

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
        """Initialize scanner test interface with injected dependencies."""
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation
        self._domain_name = domain_name
        self._interface_name = interface_name

        # Get interface-level logger and metrics
        self._logger = get_logger(f"{domain_name}.{interface_name}")
        self._metrics = get_metrics(f"{domain_name}.{interface_name}")

        # Create factory instance
        self._factory = ScannerTestFactory(
            logger=self._logger,
            metrics=self._metrics,
            call_operation=call_operation,
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute scanner test operation through DISPATCH router.

        UG-ISP Compliant:
        - DISPATCH dictionary for O(1) lookup
        - Factory contains implementation
        - Cross-domain via call_operation only

        Args:
            operation: Operation name (scan_all, scan_gateway, compile_all, generate_report)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation not found
        """
        # DISPATCH Dictionary (DD-1 Pattern)
        _DISPATCH = {
            'scan_all': self._factory.scan_all,
            'scan_gateway': self._factory.scan_gateway,
            'compile_all': self._factory.compile_all,
            'generate_report': self._factory.generate_report,
        }

        handler = _DISPATCH.get(operation)

        if not handler:
            raise ValueError(
                f"Unknown scanner test operation: {operation}. "
                f"Valid operations: {list(_DISPATCH.keys())}"
            )

        return handler(**kwargs)


__all__ = [
    'create_scanner_test_interface',
    'ScannerTestInterface',
]
