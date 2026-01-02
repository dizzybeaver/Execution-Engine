"""Validate Interface Router - EE 2.1 Compliant (STUB)

Architecture validation operations.

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

from EE.scanner.interface.validate.validate_factory import ValidateFactory


# =============================================================================
# Validate Interface Router - EE 2.1 Compliant (STUB)
# =============================================================================

class ValidateInterface:
    """Validate interface router (EE 2.1 compliant).

    Responsibilities:
    - Route operations to ValidateFactory
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
        """Initialize validate interface with DI.

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
        self.logger = get_logger("scanner.validate.interface")

        # Create factory instance with DI
        self._factory = ValidateFactory(
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation,
        )

    # Main router method
    def execute_operation(self, operation: str, **kwargs) -> Any:
        """Route validate operation to factory.

        Args:
            operation: Operation name (architecture, imports, patterns)
            **kwargs: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation unknown

        EE 2.1 Pattern:
        - Routes to ValidateFactory methods
        - No business logic in interface
        - Factory handles all implementation
        """
        self.logger.debug(f"Routing validate.{operation}")

        # Route to factory methods
        if operation == 'architecture':
            return self._factory.validate_architecture(
                path=kwargs.get('path', '.')
            )
        elif operation == 'imports':
            return self._factory.validate_imports(
                path=kwargs.get('path', '.')
            )
        elif operation == 'patterns':
            return self._factory.validate_patterns(
                path=kwargs.get('path', '.')
            )
        else:
            raise ValueError(
                f"Unknown validate operation: '{operation}'. "
                f"Valid: architecture, imports, patterns"
            )


# =============================================================================
# Interface Factory Function (for gateway registration)
# =============================================================================

def ValidateInterfaceFactory(
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str, Any], Any],
    call_operation: Callable[..., Any],
    domain_name: str,
    interface_name: str,
) -> ValidateInterface:
    """Factory function to create ValidateInterface instances.

    This function is registered with ScannerGateway and called
    to create interface instances with injected dependencies.

    Args:
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Callback for cross-domain operations
        domain_name: Domain name ("scanner")
        interface_name: Interface name ("validate")

    Returns:
        ValidateInterface instance with DI injected (STUB)
    """
    return ValidateInterface(
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,
        call_operation=call_operation,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    'ValidateInterface',
    'ValidateInterfaceFactory',
]


# =============================================================================
# End of File
# =============================================================================

