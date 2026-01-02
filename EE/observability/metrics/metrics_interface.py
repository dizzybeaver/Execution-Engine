"""
Metrics Interface Router - Observability Domain

UG-ISP Architecture (EE 2.1):
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
- Receives factory functions (not instances) via DI
"""

from typing import Any, Dict, Optional, Callable
from EE.observability.metrics.metrics_factory import MetricsFactory


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Execute metrics operation (Router Interface) - EE 2.1 Compliant.

    UG-ISP Architecture (EE 2.1):
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only
    - Receives factory functions (get_logger, get_metrics) NOT instances

    Args:
        operation: Operation name (increment, gauge, timing, etc.)
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
    logger = get_logger("observability.metrics") if get_logger else None
    metrics = get_metrics("observability.metrics") if get_metrics else None

    # Create factory instance with instances (not factories)
    factory = MetricsFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'increment': factory.increment,
        'decrement': factory.decrement,
        'gauge': factory.gauge,
        'timing': factory.timing,
        'histogram': factory.histogram,
        'flush': factory.flush,
        'get_metrics': factory.get_metrics,
        'reset': factory.reset,
        'enable_cloudwatch': factory.enable_cloudwatch,
        'disable_cloudwatch': factory.disable_cloudwatch,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown metrics operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_metrics_operation',
]
