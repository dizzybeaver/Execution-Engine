"""
HTTP Interface Router - Networking Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.networking.http_client.http_factory import HTTPFactory


def execute_http_operation(operation: str, **kwargs) -> Any:
    """
    Execute HTTP operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (get, post, put, delete, request)
        **kwargs: Operation parameters

    Returns:
        Operation result (response dict with status, headers, body)

    Raises:
        ValueError: If operation not found
        RuntimeError: If requests library not available
    """
    # Get injected dependencies
    get_logger = kwargs.get("get_logger")
    get_metrics = kwargs.get("get_metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance
    factory = HTTPFactory(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'get': factory.get,
        'post': factory.post,
        'put': factory.put,
        'delete': factory.delete,
        'request': factory.request,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown HTTP operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_http_operation',
]
