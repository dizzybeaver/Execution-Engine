"""
FileIO Interface Router - Operations Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.operations.fileio.fileio_factory import FileIOFactory


def execute_fileio_operation(operation: str, **kwargs) -> Any:
    """
    Execute file I/O operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only

    Args:
        operation: Operation name (read, write, append, delete, exists)
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

    # Create factory instance
    factory = FileIOFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'read': factory.read,
        'write': factory.write,
        'append': factory.append,
        'delete': factory.delete,
        'exists': factory.exists,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown fileio operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_fileio_operation',
]
