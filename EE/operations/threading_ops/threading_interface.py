"""
Threading Interface Router - Operations Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.operations.threading_ops.threading_factory import ThreadingFactory


def execute_threading_operation(operation: str, **kwargs) -> Any:
    """
    Execute threading operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only

    Args:
        operation: Operation name (submit, map, shutdown, get_stats)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # Get injected dependencies
    logger = kwargs.get("logger")
    metrics = kwargs.get("metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance (singleton for thread pool management)
    factory = ThreadingFactory.get_instance(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'submit': factory.submit,
        'map': factory.map,
        'shutdown': factory.shutdown,
        'get_stats': factory.get_stats,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown threading operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_threading_operation',
]
