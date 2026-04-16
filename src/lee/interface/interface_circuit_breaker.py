"""interface/interface_circuit_breaker.py
Version: 2025-12-13_2
Purpose: Circuit breaker interface router with Static Dictionary Dispatch System (DDS-1)
License: Apache 2.0

CHANGES (2026-03-22):
- Upgraded to Static DDS with metadata (func, category, description)
- Zero breaking changes - all existing operations preserved

CHANGES (2026-04-02):
- Updated imports to use consolidated circuit_breaker_manager module
- Removed dependency on deprecated circuit_breaker_generic module
"""

from typing import Any

from lee.interface.interface_common import validate_module_available

# Import protection
try:
    import importlib.util
    _CIRCUIT_BREAKER_AVAILABLE = importlib.util.find_spec("lee.circuit_breaker.circuit_breaker_manager") is not None
    _CIRCUIT_BREAKER_IMPORT_ERROR = None
except ImportError as e:
    _CIRCUIT_BREAKER_AVAILABLE = False
    _CIRCUIT_BREAKER_IMPORT_ERROR = str(e)


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for Circuit Breaker operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category (read/write/delete/admin)
    - description: Human-readable description
    """
    # pylint: disable=import-outside-toplevel
    from lee.circuit_breaker.circuit_breaker_manager import (
        execute_with_breaker_implementation,
        get_all_states_implementation,
        get_breaker_implementation,
        get_stats_implementation,
        reset_all_implementation,
        reset_implementation,
    )

    return {
        "get": {
            "func": get_breaker_implementation,
            "category": "read",
            "description": "Get circuit breaker instance by name",
        },
        "call": {
            "func": execute_with_breaker_implementation,
            "category": "write",
            "description": "Execute function with circuit breaker protection",
        },
        "get_all_states": {
            "func": get_all_states_implementation,
            "category": "read",
            "description": "Get states of all circuit breakers",
        },
        "reset_all": {
            "func": reset_all_implementation,
            "category": "delete",
            "description": "Reset all circuit breakers to closed state",
        },
        "get_stats": {
            "func": get_stats_implementation,
            "category": "read",
            "description": "Get circuit breaker statistics",
        },
        "reset": {
            "func": reset_implementation,
            "category": "delete",
            "description": "Reset specific circuit breaker to closed state",
        },
    }

_CIRCUIT_BREAKER_DISPATCH = _build_dispatch_dict() if _CIRCUIT_BREAKER_AVAILABLE else {}


def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any:
    """Route circuit breaker operations using enhanced dispatch dictionary pattern.

    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Circuit Breaker interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    validate_module_available("circuit_breaker", _CIRCUIT_BREAKER_AVAILABLE, _CIRCUIT_BREAKER_IMPORT_ERROR)

    if operation not in _CIRCUIT_BREAKER_DISPATCH:
        raise ValueError(
            f"Unknown circuit breaker operation: '{operation}'. "
            f"Valid: {', '.join(_CIRCUIT_BREAKER_DISPATCH.keys())}",
        )

    entry = _CIRCUIT_BREAKER_DISPATCH[operation]
    func = entry["func"]

    # Parameter validation for operations that require it
    if operation == "get":
        if "name" not in kwargs:
            raise ValueError("circuit_breaker.get requires 'name' parameter")
        if not isinstance(kwargs["name"], str):
            raise TypeError(f"'name' must be str, got {type(kwargs['name']).__name__}")

    elif operation == "call":
        if "name" not in kwargs:
            raise ValueError("circuit_breaker.call requires 'name' parameter")
        if "func" not in kwargs:
            raise ValueError("circuit_breaker.call requires 'func' parameter")
        if not isinstance(kwargs["name"], str):
            raise TypeError(f"'name' must be str, got {type(kwargs['name']).__name__}")
        if not callable(kwargs["func"]):
            raise TypeError(f"'func' must be callable, got {type(kwargs['func']).__name__}")

    return func(**kwargs)


__all__ = ["execute_circuit_breaker_operation"]
