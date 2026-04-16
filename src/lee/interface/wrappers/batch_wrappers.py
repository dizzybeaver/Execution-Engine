"""batch_wrappers.py
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Purpose: Batch operations interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the batch router.
External modules MUST use gateway.execute_operation() instead of importing directly.

Batch Operations:
- Batch Home Assistant API calls for efficiency
- Parallel operation execution for performance
- Batch data processing with error handling

CONSOLIDATION:
- Removed duplicate correlation_id decorator implementation
- Uses base_wrapper.with_correlation_id
- Reduced code by ~5 lines
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional
from collections.abc import Callable

# Import correlation ID decorator from base_wrapper
from lee.interface.wrappers.base_wrapper import with_correlation_id

# Import protection - only work if batch core is available
try:
    # Check if batch modules are available
    _BATCH_AVAILABLE = True
    _BATCH_IMPORT_ERROR = None
except ImportError as e:
    _BATCH_AVAILABLE = False
    _BATCH_IMPORT_ERROR = str(e)


@with_correlation_id(scope_prefix="batch")
def batch_batch_ha_calls(
    operations: list[dict[str, Any]],
    correlation_id: Optional[str] = None,  # pylint: disable=unused-argument
    **kwargs
) -> list[dict[str, Any]]:
    """Execute multiple HA operations in batch - INTERNAL wrapper for batch router.

        operations: List of HA operation dictionaries with 'domain', 'service', 'data'
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional batch options (max_parallel, continue_on_error, etc.)

        List of result dictionaries for each operation

    Example:
        >>> results = batch_batch_ha_calls(
        ...     operations=[
        ...         {"domain": "light", "service": "turn_on", "service_data": {"entity_id": "light.bubs_bedroom_inside_light_switch_1"}},
        ...         {"domain": "light", "service": "turn_on", "service_data": {"entity_id": "light.kitchen"}}
        ...     ]
        ... )
    """
    if not _BATCH_AVAILABLE:
        raise RuntimeError(f"Batch operations unavailable: {_BATCH_IMPORT_ERROR}")

    # Get options
    max_parallel = kwargs.get("max_parallel", 5)
    continue_on_error = kwargs.get("continue_on_error", True)

    results = []

    # Execute HA operations in parallel
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all operations
        future_to_op = {}
        for op in operations:
            future = executor.submit(
                _execute_single_ha_operation,
                op,
                correlation_id
            )
            future_to_op[future] = op

        # Collect results as they complete
        for future in as_completed(future_to_op):
            op = future_to_op[future]
            try:
                result = future.result()
                results.append({
                    "operation": op,
                    "status": "success",
                    "result": result,
                })
            except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
                results.append({
                    "operation": op,
                    "status": "error",
                    "error": str(e),
                })

                if not continue_on_error:
                    raise

    return results


@with_correlation_id(scope_prefix="batch")
def batch_parallel_execute(
    operations: list[dict[str, Any]],
    correlation_id: Optional[str] = None,  # pylint: disable=unused-argument
    **kwargs
) -> list[dict[str, Any]]:
    """Execute operations in parallel - INTERNAL wrapper for batch router.

        operations: List of operation dictionaries with 'func' and 'args'
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional parallel options (max_workers, timeout, etc.)

        List of result dictionaries for each operation

    Example:
        >>> def task1(x): return x * 2
        >>> def task2(x): return x * 3
        >>> results = batch_parallel_execute(
        ...     operations=[
        ...         {"func": task1, "args": (5,)},
        ...         {"func": task2, "args": (5,)}
        ...     ]
        ... )
    """
    if not _BATCH_AVAILABLE:
        raise RuntimeError(f"Batch operations unavailable: {_BATCH_IMPORT_ERROR}")

    # Get options
    max_workers = kwargs.get("max_workers", min(10, len(operations)))
    timeout = kwargs.get("timeout", None)

    results = []

    # Execute operations in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all operations
        future_to_op = {}
        for op in operations:
            func = op["func"]
            args = op.get("args", ())
            kw = op.get("kwargs", {})

            future = executor.submit(func, *args, **kw)
            future_to_op[future] = op

        # Collect results as they complete
        for future in as_completed(future_to_op, timeout=timeout):
            op = future_to_op[future]
            try:
                result = future.result()
                results.append({
                    "operation": op,
                    "status": "success",
                    "result": result,
                })
            except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
                results.append({
                    "operation": op,
                    "status": "error",
                    "error": str(e),
                })

    return results


@with_correlation_id(scope_prefix="batch")
def batch_batch_process(
    items: list[Any],
    processor: Callable[[Any], Any],
    correlation_id: Optional[str] = None,
    **kwargs
) -> list[dict[str, Any]]:
    """Process multiple items in batch - INTERNAL wrapper for batch router.

        items: List of items to process
        processor: Function to apply to each item
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional batch options (batch_size, parallel, etc.)

        List of processed items with metadata

    Example:
        >>> def uppercase_processor(item):
        ...     return item.upper()
        >>> results = batch_batch_process(
        ...     items=["hello", "world"],
        ...     processor=uppercase_processor
        ... )
    """
    if not _BATCH_AVAILABLE:
        raise RuntimeError(f"Batch operations unavailable: {_BATCH_IMPORT_ERROR}")

    # Get options
    parallel = kwargs.get("parallel", False)
    batch_size = kwargs.get("batch_size", 100)

    results = []

    if parallel and len(items) > batch_size:
        # Process in parallel batches
        with ThreadPoolExecutor(max_workers=kwargs.get("max_workers", 5)) as executor:
            futures = []
            for item in items:
                future = executor.submit(processor, item)
                futures.append(future)

            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results.append({
                        "item": items[i],
                        "status": "success",
                        "result": result,
                    })
                except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
                    results.append({
                        "item": items[i],
                        "status": "error",
                        "error": str(e),
                    })
    else:
        # Process sequentially
        for item in items:
            try:
                result = processor(item)
                results.append({
                    "item": item,
                    "status": "success",
                    "result": result,
                })
            except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError) as e:
                results.append({
                    "item": item,
                    "status": "error",
                    "error": str(e),
                })

    return results


# ===== HELPER FUNCTIONS =====

def _execute_single_ha_operation(operation: dict[str, Any], correlation_id: str) -> Any:
    """Execute a single HA operation."""
    try:
        from lee.gateway import execute_operation  # pylint: disable=import-outside-toplevel

        domain = operation["domain"]
        service = operation["service"]
        service_data = operation.get("service_data", {})

        result = execute_operation(
            "HA_DEVICES",  # This would need to be GatewayInterface.HA_DEVICES
            "call_service",
            domain=domain,
            service=service,
            service_data=service_data,
            correlation_id=correlation_id,
        )

        return result
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, IndexError, ConnectionError, TimeoutError, ImportError, ModuleNotFoundError) as e:
        raise RuntimeError(f"HA operation failed: {str(e)}") from e


__all__ = [
    "batch_batch_ha_calls",
    "batch_parallel_execute",
    "batch_batch_process",
]
