# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_singleton.py
Version: 2026-04-11_2
Purpose: Singleton interface router (SUGA-ISP) with Static DDS
License: Apache 2.0

SUGA-ISP Pattern: Gateway -> Interface -> Domain
Interface acts as router for singleton operations

CHANGES (2026-04-11_2):
- Refactored to use @graceful_import decorator
- Reduced import protection code
"""

from collections.abc import Callable
from typing import Any

from lee.interface.interface_common import validate_module_available
from lee.interface.interface_errors import (
    UnknownOperationError,
    validate_string_parameter,
)
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.singleton')
def _import_singleton():
    from lee.singleton import (
        clear_implementation,
        delete_implementation,
        get_implementation,
        get_stats_implementation,
        has_implementation,
        reset_implementation,
        set_implementation,
    )
    return {
        'clear': clear_implementation,
        'delete': delete_implementation,
        'get': get_implementation,
        'get_stats': get_stats_implementation,
        'has': has_implementation,
        'reset': reset_implementation,
        'set': set_implementation,
    }


_singleton_funcs = _import_singleton()
_SINGLETON_AVAILABLE = _import_singleton.__dict__.get(
    '_SINGLETON_AVAILABLE',
    False
)
_SINGLETON_IMPORT_ERROR = _import_singleton.__dict__.get(
    '_SINGLETON_IMPORT_ERROR',
    None
)

if _SINGLETON_AVAILABLE:
    clear_implementation = _singleton_funcs['clear']
    delete_implementation = _singleton_funcs['delete']
    get_implementation = _singleton_funcs['get']
    get_stats_implementation = _singleton_funcs['get_stats']
    has_implementation = _singleton_funcs['has']
    reset_implementation = _singleton_funcs['reset']
    set_implementation = _singleton_funcs['set']
else:
    def clear_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def delete_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def get_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def get_stats_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def has_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def reset_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}

    def set_implementation(**_kwargs):
        return {"success": False, "error": "Singleton not available"}


# Static Dictionary Dispatch System (DDS-1)
# Each operation entry: {'func': callable, 'category': str,
#                       'description': str}
_SINGLETON_DISPATCH: dict[str, dict[str, Any]] = {
    # Core Singleton Operations
    "get": {
        "func": get_implementation,
        "category": "core",
        "description": "Get singleton instance by name",
    },
    "set": {
        "func": set_implementation,
        "category": "core",
        "description": "Set singleton instance by name",
    },
    "has": {
        "func": has_implementation,
        "category": "core",
        "description": "Check if singleton exists",
    },
    "delete": {
        "func": delete_implementation,
        "category": "core",
        "description": "Delete singleton instance",
    },
    "clear": {
        "func": clear_implementation,
        "category": "core",
        "description": "Clear all singleton instances",
    },

    # Statistics and Management
    "get_stats": {
        "func": get_stats_implementation,
        "category": "stats",
        "description": "Get detailed singleton statistics",
    },
    "reset": {
        "func": reset_implementation,
        "category": "stats",
        "description": "Reset singleton statistics",
    },
}


def execute_singleton_operation(
    operation: str,
    **kwargs: Any,
) -> Any:
    """Route singleton operation requests to domain implementations.

    SUGA-ISP: Interface router dispatches to domain function.

    Args:
        operation: The singleton operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Singleton interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    validate_module_available(
        "singleton",
        _SINGLETON_AVAILABLE,
        _SINGLETON_IMPORT_ERROR
    )

    operation_entry = _SINGLETON_DISPATCH.get(operation)
    if not operation_entry:
        raise UnknownOperationError(
            "singleton",
            operation,
            list(_SINGLETON_DISPATCH.keys()),
        )

    if operation in ["get", "set", "has", "delete"]:
        validate_string_parameter(
            "singleton",
            operation,
            kwargs,
            "name",
        )

    if operation == "set":
        if "instance" not in kwargs:
            raise ValueError(
                f"singleton.{operation} requires 'instance' parameter"
            )

    handler: Callable = operation_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_singleton_operation"]
