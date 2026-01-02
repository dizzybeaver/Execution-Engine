"""Test Interface Router - EE 2.1 Compliant (STUB)

Test execution operations.

EE 2.1 Architecture:
- Interface is a thin router only (no business logic)
- Factory contains all implementation
- Pool management for factory instances
- DI propagation to factory

PHASE 3 COMPLETE: Factory implementation integrated.

Based on:
- EE/operations/cache/cache_interface.py (router pattern reference)
"""

from __future__ import annotations

from typing import Any, Callable

from EE.scanner.interface.test.test_factory import TestFactory


# =============================================================================
# Test Interface Router - EE 2.1 Compliant (STUB)
# =============================================================================

class TestInterface:
    """Test interface router (EE 2.1 compliant).

    Responsibilities:
    - Route operations to TestFactory
    - NO business logic (routing only)
    - Factory pool management (single instance for simplicity)

    EE 2.1 Compliance:
    - Receives DI in constructor
    - Routes to factory methods
    - No direct imports from gateway
    - Uses call_operation for cross-domain calls
    """

    # EE 2.1 compliant constructor with DI
    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ) -> None:
        """Initialize test interface with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        # Store DI functions
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

        # Create logger for interface
        self.logger = get_logger("scanner.test.interface")

        # Create factory instance with DI
        self._factory = TestFactory(
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation,
        )

    # Main router method
    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Route test operation to factory.

        Args:
            operation: Operation name
            **kwargs: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown

        EE 2.1 Pattern:
        - Routes to TestFactory methods
        - No business logic in interface
        - Factory handles all implementation
        """
        self.logger.debug(f"Routing test.{operation}")

        # Route to factory methods
        if operation == 'all':
            return self._factory.test_all(
                path=kwargs.get('path', '.'),
                verbose=kwargs.get('verbose', False)
            )
        elif operation == 'suite':
            return self._factory.test_suite(
                suite_name=kwargs.get('suite_name'),
                base_path=kwargs.get('base_path', '.'),
                verbose=kwargs.get('verbose', False)
            )
        elif operation == 'file':
            return self._factory.test_file(
                file_path=kwargs.get('file_path'),
                verbose=kwargs.get('verbose', False)
            )
        elif operation.startswith('ha_'):
            # HA functional tests
            test_type = operation[3:]  # Remove 'ha_' prefix
            return self._factory.test_ha(test_type, **kwargs)
        else:
            raise ValueError(
                f"Unknown test operation: '{operation}'. "
                f"Valid: all, suite, file, ha_<type>"
            )


# =============================================================================
# Interface Factory Function (for gateway registration)
# =============================================================================

def TestInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> TestInterface:
    """Factory function to create TestInterface instances.

    This function is registered with ScannerGateway and called
    to create interface instances with injected dependencies.

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name ("scanner")
        interface_name: Interface name ("test")

    Returns:
        TestInterface instance with DI injected (STUB)
    """
    return TestInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    'TestInterface',
    'TestInterfaceFactory',
]


# =============================================================================
# End of File
# =============================================================================

