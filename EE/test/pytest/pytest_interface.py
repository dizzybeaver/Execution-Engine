"""
Pytest Interface Router - Test Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Protocol
from EE.pytest_factory import PytestFactory


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


def create_pytest_interface(
    get_logger: LoggerFactory,
    get_metrics: MetricsFactory,
    call_operation: OperationCaller,
    domain_name: str,
    interface_name: str,
) -> 'PytestInterface':
    """Create pytest interface instance with injected dependencies.

    UG-ISP Compliant:
    - Factory function for interface creation
    - All dependencies injected
    - No direct imports outside domain

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        call_operation: Function to call operations in other domains
        domain_name: Name of the domain (test)
        interface_name: Name of the interface (pytest)

    Returns:
        Configured PytestInterface instance
    """
    return PytestInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation,
        domain_name=domain_name,
        interface_name=interface_name,
    )


class PytestInterface:
    """Pytest Interface - Router Layer.

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
        """Initialize pytest interface with injected dependencies."""
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._call_operation = call_operation
        self._domain_name = domain_name
        self._interface_name = interface_name

        # Get interface-level logger and metrics
        self._logger = get_logger(f"{domain_name}.{interface_name}")
        self._metrics = get_metrics(f"{domain_name}.{interface_name}")

        # Create factory instance
        self._factory = PytestFactory(
            logger=self._logger,
            metrics=self._metrics,
            call_operation=call_operation,
        )

    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute pytest operation through DISPATCH router.

        UG-ISP Compliant:
        - DISPATCH dictionary for O(1) lookup
        - Factory contains implementation
        - Cross-domain via call_operation only

        Args:
            operation: Operation name (run_all, run_suite, run_file, get_results)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation not found
        """
        # DISPATCH Dictionary (DD-1 Pattern)
        _DISPATCH = {
            'run_all': self._factory.run_all,
            'run_suite': self._factory.run_suite,
            'run_file': self._factory.run_file,
            'get_results': self._factory.get_results,
        }

        handler = _DISPATCH.get(operation)

        if not handler:
            raise ValueError(
                f"Unknown pytest operation: {operation}. "
                f"Valid operations: {list(_DISPATCH.keys())}"
            )

        return handler(**kwargs)


__all__ = [
    'create_pytest_interface',
    'PytestInterface',
]
