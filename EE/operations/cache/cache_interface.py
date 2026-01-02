"""
Cache Interface Router - Operations Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.operations.cache.cache_factory import CacheFactory


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """
    Execute cache operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (get, set, delete, clear, stats, exists)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # EE 2.1: Get factory functions instead of instances
    get_logger = kwargs.get("get_logger")
    get_metrics = kwargs.get("get_metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance with factory functions
    factory = CacheFactory(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'get': factory.get,
        'set': factory.set,
        'delete': factory.delete,
        'clear': factory.clear,
        'stats': factory.stats,
        'exists': factory.exists,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown cache operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_cache_operation',
]
