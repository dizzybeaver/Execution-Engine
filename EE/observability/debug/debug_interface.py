"""
Debug Interface Router - Observability Domain

UG-ISP Architecture (EE 2.1):
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
- Receives factory functions (not instances) via DI
"""

from typing import Any, Dict, Optional, Callable
from EE.observability.debug.debug_factory import DebugFactory


def execute_debug_operation(operation: str, **kwargs) -> Any:
    """
    Execute debug operation (Router Interface) - EE 2.1 Compliant.

    UG-ISP Architecture (EE 2.1):
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only
    - Receives factory functions (get_logger, get_metrics) NOT instances

    Args:
        operation: Operation name (enable_debug, set_correlation_id, etc.)
        **kwargs: Operation parameters including:
                  - get_logger: Factory function to create loggers
                  - get_metrics: Factory function to create metrics
                  - call_operation: Cross-domain operation callback

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # EE 2.1: Extract factory functions from kwargs
    get_logger = kwargs.pop("get_logger", None)
    get_metrics = kwargs.pop("get_metrics", None)
    call_operation = kwargs.pop("call_operation", None)

    # EE 2.1: Create logger and metrics instances from factory functions
    logger = get_logger("observability.debug") if get_logger else None
    metrics = get_metrics("observability.debug") if get_metrics else None

    # Create factory instance with instances (not factories)
    factory = DebugFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'enable_debug': factory.enable_debug,
        'disable_debug': factory.disable_debug,
        'is_debug_enabled': factory.is_debug_enabled,
        'set_correlation_id': factory.set_correlation_id,
        'get_correlation_id': factory.get_correlation_id,
        'clear_correlation_id': factory.clear_correlation_id,
        'start_trace': factory.start_trace,
        'end_trace': factory.end_trace,
        'get_trace_context': factory.get_trace_context,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown debug operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_debug_operation',
]
