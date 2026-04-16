"""Batch Wrapper Functions

Direct access to batch operations (3 functions).
All functions execute via gateway internally.

NOTE: Batch operations now use GatewayInterface.DATA (consolidated with DATABASE)
CHANGES: 2026-03-25 - Updated from GatewayInterface.BATCH to GatewayInterface.DATA
"""

from typing import Any
from collections.abc import Callable

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def batch_batch_ha_calls(calls: list[dict[str, Any]], **kwargs: Any) -> list[Any]:
    """Batch Home Assistant API calls.

    Args:
        calls: List of call dictionaries
        **kwargs: Additional options

    Returns:
        List of results
    """
    return execute_operation(GatewayInterface.DATA, 'batch_ha_calls', operations=calls, **kwargs)


def batch_parallel_execute(tasks: list[Callable[[], Any]], max_workers: int = 5, **kwargs: Any) -> list[Any]:
    """Execute tasks in parallel.

    Args:
        tasks: List of callable tasks
        max_workers: Maximum parallel workers
        **kwargs: Additional options

    Returns:
        List of results
    """
    return execute_operation(GatewayInterface.DATA, 'parallel_execute', operations=tasks, max_workers=max_workers, **kwargs)


def batch_batch_process(items: list[Any], process_fn: Callable[[Any], Any], batch_size: int = 10, **kwargs: Any) -> list[Any]:
    """Process items in batches.

    Args:
        items: List of items to process
        process_fn: Processing function
        batch_size: Batch size
        **kwargs: Additional options

    Returns:
        List of results
    """
    return execute_operation(GatewayInterface.DATA, 'batch_process', items=items, process_fn=process_fn, batch_size=batch_size, **kwargs)


__all__ = [
    'batch_batch_ha_calls',
    'batch_parallel_execute',
    'batch_batch_process',
]
