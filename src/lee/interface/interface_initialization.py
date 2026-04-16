# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_initialization.py
Version: 2026-04-11_2
Purpose: Initialization interface router with Static DDS
License: Apache 2.0
"""

import re
from collections.abc import Callable
from typing import Any

from lee.utils.graceful_import import graceful_import


@graceful_import('lee.initialization')
def _import_initialization():
    from lee.initialization import (
        execute_initialization_operation as _core_execute_initialization_operation,
        get_config_implementation,
        get_flag_implementation,
        get_stats_implementation,
        get_status_implementation,
        initialize_implementation,
        is_initialized_implementation,
        reset_implementation,
        set_flag_implementation,
    )
    return {
        'execute_initialization_operation': _core_execute_initialization_operation,
        'get_config': get_config_implementation,
        'get_flag': get_flag_implementation,
        'get_stats': get_stats_implementation,
        'get_status': get_status_implementation,
        'initialize': initialize_implementation,
        'is_initialized': is_initialized_implementation,
        'reset': reset_implementation,
        'set_flag': set_flag_implementation,
    }


_init_funcs = _import_initialization()
_INITIALIZATION_AVAILABLE = _import_initialization.__dict__.get(
    '_INITIALIZATION_AVAILABLE',
    False
)
_INITIALIZATION_IMPORT_ERROR = _import_initialization.__dict__.get(
    '_INITIALIZATION_IMPORT_ERROR',
    None
)

if _INITIALIZATION_AVAILABLE:
    _core_execute_initialization_operation = _init_funcs[
        'execute_initialization_operation'
    ]
    get_config_implementation = _init_funcs['get_config']
    get_flag_implementation = _init_funcs['get_flag']
    get_stats_implementation = _init_funcs['get_stats']
    get_status_implementation = _init_funcs['get_status']
    initialize_implementation = _init_funcs['initialize']
    is_initialized_implementation = _init_funcs['is_initialized']
    reset_implementation = _init_funcs['reset']
    set_flag_implementation = _init_funcs['set_flag']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        return {"success": False, "error": "Initialization module unavailable"}

    _core_execute_initialization_operation = _stub_unavailable
    get_config_implementation = _stub_unavailable
    get_flag_implementation = _stub_unavailable
    get_stats_implementation = _stub_unavailable
    get_status_implementation = _stub_unavailable
    initialize_implementation = _stub_unavailable
    is_initialized_implementation = _stub_unavailable
    reset_implementation = _stub_unavailable
    set_flag_implementation = _stub_unavailable


# Allowed flag name pattern: alphanumeric, underscore, hyphen, dot
_FLAG_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+$')
_MAX_FLAG_NAME_LENGTH = 100


def _validate_flag_name_format(flag_name: str) -> None:
    """Validate flag name format to prevent malicious names.

    Args:
        flag_name: Flag name to validate

    Raises:
        ValueError: If flag name contains invalid characters or is too long
        TypeError: If flag name is not a string
    """
    if not isinstance(flag_name, str):
        raise TypeError(f"Flag name must be string, got {type(flag_name).__name__}")

    if len(flag_name) > _MAX_FLAG_NAME_LENGTH:
        raise ValueError(
            f"Flag name too long (max {_MAX_FLAG_NAME_LENGTH} characters), "
            f"got {len(flag_name)}"
        )

    if not flag_name:
        raise ValueError("Flag name cannot be empty")

    if not _FLAG_NAME_PATTERN.match(flag_name):
        raise ValueError(
            f"Flag name '{flag_name}' contains invalid characters. "
            "Allowed: alphanumeric, underscore, hyphen, dot"
        )

    # Prevent path-like patterns
    dangerous_patterns = ['../', '..\\', '/', '\\']
    flag_name_lower = flag_name.lower()
    for pattern in dangerous_patterns:
        if pattern in flag_name_lower:
            raise ValueError(
                f"Flag name '{flag_name}' contains path-like pattern '{pattern}'"
            )


def _validate_flag_params(kwargs: dict, operation: str) -> None:
    """Validate flag_name parameter for flag operations."""
    if "flag_name" not in kwargs:
        raise ValueError(f"initialization.{operation} requires 'flag_name' parameter")
    if not isinstance(kwargs["flag_name"], str):
        raise TypeError(
            f"'flag_name' must be str, got {type(kwargs['flag_name']).__name__}"
        )

    # Validate flag name format
    _validate_flag_name_format(kwargs["flag_name"])


def _validate_set_flag_params(kwargs: dict) -> None:
    """Validate parameters for set_flag operation."""
    _validate_flag_params(kwargs, "set_flag")
    if "value" not in kwargs:
        raise ValueError("initialization.set_flag requires 'value' parameter")


# Static Dictionary Dispatch System (DDS-1)
# Each operation entry: {'func': callable, 'category': str, 'description': str}
_INITIALIZATION_DISPATCH: dict[str, dict[str, Any]] = {
    # Core Initialization
    "initialize": {
        "func": initialize_implementation,
        "category": "core",
        "description": "Initialize the gateway system",
    },
    "is_initialized": {
        "func": is_initialized_implementation,
        "category": "core",
        "description": "Check if gateway is initialized",
    },
    "reset": {
        "func": reset_implementation,
        "category": "core",
        "description": "Reset gateway to uninitialized state",
    },

    # Configuration
    "get_config": {
        "func": get_config_implementation,
        "category": "config",
        "description": "Get gateway configuration",
    },

    # Status and Statistics
    "get_status": {
        "func": get_status_implementation,
        "category": "status",
        "description": "Get gateway initialization status",
    },
    "get_stats": {
        "func": get_stats_implementation,
        "category": "status",
        "description": "Get initialization statistics",
    },

    # Feature Flags
    "set_flag": {
        "func": lambda **kw: (
            _validate_set_flag_params(kw),
            set_flag_implementation(**kw),
        )[1],
        "category": "flags",
        "description": "Set a feature flag",
    },
    "get_flag": {
        "func": lambda **kw: (
            _validate_flag_params(kw, "get_flag"),
            get_flag_implementation(**kw),
        )[1],
        "category": "flags",
        "description": "Get a feature flag value",
    },
} if _INITIALIZATION_AVAILABLE else {}


def execute_initialization_operation(operation: str, **kwargs) -> Any:
    """Route initialization operation requests using Static DDS.

    Args:
        operation: Initialization operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Initialization interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    if not _INITIALIZATION_AVAILABLE:
        raise RuntimeError(
            f"Initialization interface unavailable: {_INITIALIZATION_IMPORT_ERROR}",
        )

    operation_entry = _INITIALIZATION_DISPATCH.get(operation)
    if not operation_entry:
        valid_ops = ", ".join(_INITIALIZATION_DISPATCH.keys())
        raise ValueError(
            f"Unknown initialization operation: '{operation}'. "
            f"Valid: {valid_ops}",
        )

    handler: Callable = operation_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_initialization_operation"]
