"""
Object Pool Interface Router - Operations Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.operations.object_pool.object_pool_factory import ObjectPoolFactory


def execute_object_pool_operation(operation: str, **kwargs) -> Any:
    """
    Execute object pool operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only

    Args:
        operation: Operation name (create_pool, acquire, release, etc.)
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

    # Create factory instance (singleton for pool management)
    factory = ObjectPoolFactory.get_instance(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'create_pool': factory.create_pool,
        'acquire': factory.acquire,
        'release': factory.release,
        'delete_pool': factory.delete_pool,
        'get_stats': factory.get_stats,
        'list_pools': factory.list_pools,
        'clear_pool': factory.clear_pool,
        'resize_pool': factory.resize_pool,
        'warm_pool': factory.warm_pool,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown object_pool operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_object_pool_operation',
]
