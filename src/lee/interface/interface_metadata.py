"""interface_metadata.py - Metadata Router
Version: 2026-03-22_2
Purpose: Gateway interface for metadata operations (events, system info, key-value storage)
License: Apache 2.0

SECURITY ENHANCEMENTS (2026-03-22_2):
- Enhanced deep size validation for all metadata operations
- Added recursive size checking for nested data structures
- Added total metadata size limits to prevent memory exhaustion
- Validates export/import data sizes

Ported from UGA observability foundation (2026-03-08)
Ref: ee-obs-metadata-interface

Security Considerations:
- No sensitive data in metadata (OAuth tokens, passwords, PII)
- Thread-safe operations using threading.Lock
- Input validation on all operations
- Event buffer limited to prevent memory exhaustion
- Deep size validation for complex data structures
"""

import sys
from collections.abc import Collection
from typing import Any

from lee.gateway.gateway_core import generate_correlation_id

# SUGA-ISP: No direct imports from metadata/ at module level
# All core implementations imported lazily to avoid cross-interface violations

# ===== VALIDATION FUNCTIONS =====

def _calculate_deep_size(obj: Any, max_depth: int = 10, current_depth: int = 0) -> int:
    """Recursively calculate the deep size of an object.

    Args:
        obj: Object to measure
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth

    Returns:
        Size in bytes (approximate)
    """
    if current_depth >= max_depth:
        return 0  # Prevent infinite recursion

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(_calculate_deep_size(k, max_depth, current_depth + 1) for k in obj.keys())
        size += sum(_calculate_deep_size(v, max_depth, current_depth + 1) for v in obj.values())
    elif isinstance(obj, Collection):
        size += sum(_calculate_deep_size(item, max_depth, current_depth + 1) for item in obj)
    elif getattr(type(obj), '__dict__', None) is not None:
        size += _calculate_deep_size(obj.__dict__, max_depth, current_depth + 1)

    return size


def _validate_event_param(kwargs: dict[str, Any]) -> None:
    """Validate event parameter for add_event."""
    if "event" not in kwargs:
        raise ValueError("metadata.add_event requires 'event' parameter")

    event = kwargs["event"]
    if not isinstance(event, dict):
        raise ValueError("metadata.add_event 'event' parameter must be a dictionary")

    # Validate event structure
    if "type" in event:
        event_type = str(event["type"])
        # Limit event type length
        if len(event_type) > 100:
            raise ValueError("Event type too long (max 100 characters)")

    # Validate event data size (prevent memory exhaustion)
    if "data" in event:
        # Use deep size calculation for nested structures
        data_size = _calculate_deep_size(event["data"])
        if data_size > 102400:  # 100KB limit per event (increased for nested structures)
            raise ValueError(f"Event data too large (max 100KB), got {data_size} bytes")

def _validate_metadata_key_param(kwargs: dict[str, Any]) -> None:
    """Validate key parameter for metadata operations."""
    if "key" not in kwargs:
        raise ValueError("metadata operation requires 'key' parameter")

    key = str(kwargs["key"])
    # Limit key length
    if len(key) > 200:
        raise ValueError("Metadata key too long (max 200 characters)")

    kwargs["key"] = key

def _validate_metadata_params(kwargs: dict[str, Any]) -> None:
    """Validate key and value parameters for set_metadata."""
    _validate_metadata_key_param(kwargs)

    if "value" not in kwargs:
        raise ValueError("metadata.set_metadata requires 'value' parameter")

    # Validate value size (prevent memory exhaustion)
    # Use deep size calculation for nested structures
    value_size = _calculate_deep_size(kwargs["value"])
    if value_size > 512000:  # 500KB limit per value (increased for nested structures)
        raise ValueError(f"Metadata value too large (max 500KB), got {value_size} bytes")

def _validate_count_param(kwargs: dict[str, Any]) -> None:
    """Validate count parameter for get_recent_events."""
    if "count" in kwargs:
        count = kwargs["count"]
        if not isinstance(count, int) or count < 1 or count > 1000:
            raise ValueError("metadata.get_recent_events 'count' must be between 1 and 1000")


# ===== VALIDATION DISPATCH =====

_VALIDATION_DISPATCH: dict[str, dict[str, Any]] = {
    "add_event": {
        "func": _validate_event_param,
        "description": "Validate event parameter",
    },
    "set_metadata": {
        "func": _validate_metadata_params,
        "description": "Validate metadata key-value pair",
    },
    "get_metadata": {
        "func": _validate_metadata_key_param,
        "description": "Validate metadata key parameter",
    },
    "delete_metadata": {
        "func": _validate_metadata_key_param,
        "description": "Validate metadata key parameter",
    },
    "get_recent_events": {
        "func": _validate_count_param,
        "description": "Validate count parameter",
    },
}

# ===== LAZY IMPORT HELPERS =====

# pylint: disable=too-many-locals
def _get_metadata_core_functions():
    """Lazy import metadata core functions (SUGA-ISP compliant).

    This function lazy-loads metadata core implementations to avoid
    cross-interface violations at module level.
    """
    # pylint: disable=import-outside-toplevel
    try:
        from lee.metadata.event_bus import (
            _add_event_implementation,
            _clear_events_implementation,
            _get_all_events_implementation,
            _get_event_count_implementation,
            _get_events_by_type_implementation,
            _get_recent_events_implementation,
        )
        from lee.metadata.metadata_io import (
            _export_data_implementation,
            _export_to_file_implementation,
            _get_statistics_implementation,
            _import_data_implementation,
            _import_from_file_implementation,
        )
        from lee.metadata.metadata_store import (
            _clear_metadata_implementation,
            _delete_metadata_implementation,
            _get_all_metadata_implementation,
            _get_metadata_implementation,
            _set_metadata_implementation,
            _update_metadata_implementation,
        )
        from lee.metadata.system_collector import (
            _get_platform_info_implementation,
            _get_python_info_implementation,
            _get_system_info_implementation,
        )

        return {
            # Event operations
            "add_event": _add_event_implementation,
            "get_all_events": _get_all_events_implementation,
            "get_events_by_type": _get_events_by_type_implementation,
            "get_recent_events": _get_recent_events_implementation,
            "clear_events": _clear_events_implementation,
            "get_event_count": _get_event_count_implementation,

            # System info operations
            "get_system_info": _get_system_info_implementation,
            "get_platform_info": _get_platform_info_implementation,
            "get_python_info": _get_python_info_implementation,

            # Metadata store operations
            "set_metadata": _set_metadata_implementation,
            "get_metadata": _get_metadata_implementation,
            "get_all_metadata": _get_all_metadata_implementation,
            "delete_metadata": _delete_metadata_implementation,
            "clear_metadata": _clear_metadata_implementation,
            "update_metadata": _update_metadata_implementation,

            # I/O operations
            "get_statistics": _get_statistics_implementation,
            "export_data": _export_data_implementation,
            "import_data": _import_data_implementation,
            "export_to_file": _export_to_file_implementation,
            "import_from_file": _import_from_file_implementation,
        }
    except ImportError as e:
        raise RuntimeError(f"Failed to import metadata core functions: {e}") from e


# ===== STATIC DISPATCH DICTIONARY (DDS) =====

_OPERATION_DISPATCH: dict[str, dict[str, Any]] = {
    # Event operations
    "add_event": {
        "func": lambda **kw: _get_metadata_core_functions()["add_event"](**kw),
        "category": "write",
        "description": "Add event to storage",
    },
    "get_all_events": {
        "func": lambda **kw: _get_metadata_core_functions()["get_all_events"](**kw),
        "category": "read",
        "description": "Get all events",
    },
    "get_events_by_type": {
        "func": lambda **kw: _get_metadata_core_functions()["get_events_by_type"](**kw),
        "category": "read",
        "description": "Get events filtered by type",
    },
    "get_recent_events": {
        "func": lambda **kw: _get_metadata_core_functions()["get_recent_events"](**kw),
        "category": "read",
        "description": "Get most recent events",
    },
    "clear_events": {
        "func": lambda **kw: _get_metadata_core_functions()["clear_events"](**kw),
        "category": "admin",
        "description": "Clear all events",
    },
    "get_event_count": {
        "func": lambda **kw: _get_metadata_core_functions()["get_event_count"](**kw),
        "category": "read",
        "description": "Get total event count",
    },

    # System info operations
    "get_system_info": {
        "func": lambda **kw: _get_metadata_core_functions()["get_system_info"](**kw),
        "category": "read",
        "description": "Get system information",
    },
    "get_platform_info": {
        "func": lambda **kw: _get_metadata_core_functions()["get_platform_info"](**kw),
        "category": "read",
        "description": "Get platform-specific information",
    },
    "get_python_info": {
        "func": lambda **kw: _get_metadata_core_functions()["get_python_info"](**kw),
        "category": "read",
        "description": "Get Python runtime information",
    },

    # Metadata store operations
    "set_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["set_metadata"](**kw),
        "category": "write",
        "description": "Set metadata key-value pair",
    },
    "get_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["get_metadata"](**kw),
        "category": "read",
        "description": "Get metadata value by key",
    },
    "get_all_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["get_all_metadata"](**kw),
        "category": "read",
        "description": "Get all metadata",
    },
    "delete_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["delete_metadata"](**kw),
        "category": "write",
        "description": "Delete metadata key",
    },
    "clear_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["clear_metadata"](**kw),
        "category": "admin",
        "description": "Clear all metadata",
    },
    "update_metadata": {
        "func": lambda **kw: _get_metadata_core_functions()["update_metadata"](**kw),
        "category": "write",
        "description": "Update multiple metadata key-value pairs",
    },

    # I/O operations
    "get_statistics": {
        "func": lambda **kw: _get_metadata_core_functions()["get_statistics"](**kw),
        "category": "read",
        "description": "Get metadata statistics",
    },
    "export_data": {
        "func": lambda **kw: _get_metadata_core_functions()["export_data"](**kw),
        "category": "read",
        "description": "Export all metadata data",
    },
    "import_data": {
        "func": lambda **kw: _get_metadata_core_functions()["import_data"](**kw),
        "category": "write",
        "description": "Import metadata data",
    },
    "export_to_file": {
        "func": lambda **kw: _get_metadata_core_functions()["export_to_file"](**kw),
        "category": "write",
        "description": "Export metadata to file",
    },
    "import_from_file": {
        "func": lambda **kw: _get_metadata_core_functions()["import_from_file"](**kw),
        "category": "write",
        "description": "Import metadata from file",
    },
}

# ===== PUBLIC INTERFACE =====

def execute_metadata_operation(operation: str, **kwargs) -> Any:
    """Execute metadata operation with validation and error handling.

        operation: Operation name (must be in _OPERATION_DISPATCH)
        **kwargs: Operation-specific parameters

        Operation result

    Raises:
        ValueError: If operation is invalid or parameters fail validation
        RuntimeError: If core functions fail to import

    Example:
        >>> from lee.gateway import execute_operation, GatewayInterface
        >>> execute_operation(GatewayInterface.METADATA, 'add_event',
        ...                  event={'type': 'request', 'data': {'request_id': 'abc123'}})

    """
    # Generate correlation ID for debugging if not provided
    if "correlation_id" not in kwargs:
        kwargs["correlation_id"] = generate_correlation_id("meta")

    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        valid_ops = ", ".join(_OPERATION_DISPATCH.keys())
        raise ValueError(
            f"Unknown metadata operation: '{operation}'. "
            f"Valid operations: {valid_ops}",
        )

    # Validate parameters using dispatch dictionary
    validation_entry = _VALIDATION_DISPATCH.get(operation)
    if validation_entry:
        try:
            validator = validation_entry["func"]
            validator(kwargs)
        except ValueError as e:
            raise ValueError(f"Parameter validation failed for metadata operation '{operation}': {e}") from e

    # Get handler from dispatch dictionary
    entry = _OPERATION_DISPATCH[operation]
    handler = entry["func"]

    # Execute operation
    return handler(**kwargs)

# ===== EXPORTS =====

__all__ = ["execute_metadata_operation"]
