"""
Redis Interface Router - Networking Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.networking.protocols.redis.redis_factory import RedisFactory


def execute_redis_operation(operation: str, **kwargs) -> Any:
    """
    Execute Redis operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (get, set, delete, exists, keys, hget, hset, hgetall, lpush, rpush, lrange, publish)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # Get injected dependencies
    get_logger = kwargs.get("get_logger")
    get_metrics = kwargs.get("get_metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance
    factory = RedisFactory(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'get': factory.get,
        'set': factory.set,
        'delete': factory.delete,
        'exists': factory.exists,
        'keys': factory.keys,
        'hget': factory.hget,
        'hset': factory.hset,
        'hgetall': factory.hgetall,
        'lpush': factory.lpush,
        'rpush': factory.rpush,
        'lrange': factory.lrange,
        'publish': factory.publish,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown Redis operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_redis_operation',
]
