"""interface/interface_utility.py
Version: 2025-12-13_3
Purpose: Utility interface router with Static Dictionary Dispatch System (DDS-1)
License: Apache 2.0

CHANGES (2025-12-13_2):
- Upgraded to Static DDS with metadata (func, category, description)
- Added category and description for each operation
- Zero breaking changes - all existing operations preserved

CHANGES (2026-03-22):
- Converted to direct domain imports (NOT wrappers)
- Follow blueprint pattern exactly
"""

from typing import Any

# Import protection
try:
    _UTILITY_AVAILABLE = True
    _UTILITY_IMPORT_ERROR = None
except ImportError as e:
    _UTILITY_AVAILABLE = False
    _UTILITY_IMPORT_ERROR = str(e)

# Direct imports from domain modules (using _implementation functions)
try:
    from lee.lee_utility.utility_generic import (
        cleanup_cache_implementation as cleanup_cache,
    )
    from lee.lee_utility.utility_generic import (
        config_get_implementation as config_get,
    )
    from lee.lee_utility.utility_generic import (
        configure_caching_implementation as configure_caching,
    )
    from lee.lee_utility.utility_generic import (
        create_success_response_implementation as create_success_response,
    )
    from lee.lee_utility.utility_generic import (
        deep_merge_implementation as deep_merge,
    )
    from lee.lee_utility.utility_generic import (
        extract_error_details_implementation as extract_error_details,
    )
    from lee.lee_utility.utility_generic import (
        format_bytes_implementation as format_bytes,
    )
    from lee.lee_utility.utility_generic import (
        format_data_for_response_implementation as format_data_for_response,
    )
    from lee.lee_utility.utility_generic import (
        generate_correlation_id_implementation as generate_correlation_id,
    )
    from lee.lee_utility.utility_generic import (
        generate_uuid_implementation as generate_uuid,
    )
    from lee.lee_utility.utility_generic import (
        get_module_prefix_implementation as get_module_prefix,
    )
    from lee.lee_utility.utility_generic import (
        get_performance_stats_implementation as get_performance_stats,
    )
    from lee.lee_utility.utility_generic import (
        get_stats_implementation as utility_get_stats,
    )
    from lee.lee_utility.utility_generic import (
        get_timestamp_implementation as get_timestamp,
    )
    from lee.lee_utility.utility_generic import (
        get_timestamp_numeric_implementation as get_timestamp_numeric,
    )
    from lee.lee_utility.utility_generic import (
        merge_dictionaries_implementation as merge_dictionaries,
    )
    from lee.lee_utility.utility_generic import (
        optimize_performance_implementation as optimize_performance,
    )
    from lee.lee_utility.utility_generic import (
        parse_json_implementation as parse_json,
    )
    from lee.lee_utility.utility_generic import (
        parse_json_safely_implementation as parse_json_safely,
    )
    from lee.lee_utility.utility_generic import (
        render_template_implementation as render_template,
    )
    from lee.lee_utility.utility_generic import (
        reset_implementation as utility_reset,
    )
    from lee.lee_utility.utility_generic import (
        safe_get_implementation as safe_get,
    )
    from lee.lee_utility.utility_generic import (
        safe_string_conversion_implementation as safe_string_conversion,
    )
    from lee.lee_utility.utility_generic import (
        safe_subprocess_run_implementation as safe_subprocess_run,
    )
    from lee.lee_utility.utility_generic import (
        sanitize_data_implementation as sanitize_data,
    )
    from lee.lee_utility.utility_generic import (
        validate_data_structure_implementation as validate_data_structure,
    )
    from lee.lee_utility.utility_generic import (
        validate_operation_parameters_implementation as validate_operation_parameters,
    )
    from lee.lee_utility.utility_generic import (
        validate_string_implementation as validate_string,
    )
    from lee.lee_utility.utility_response import (
        format_response,
    )
    _UTILITY_IMPORTS_AVAILABLE = True
except ImportError as e:
    _UTILITY_IMPORTS_AVAILABLE = False
    _UTILITY_IMPORT_ERROR = str(e)


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for Utility operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category
    - description: Human-readable description
    """
    return {
        # UUID and Timestamp
        "generate_uuid": {
            "func": generate_uuid,
            "category": "identity",
            "description": "Generate unique identifier (UUID)",
        },
        "get_timestamp": {
            "func": get_timestamp,
            "category": "identity",
            "description": "Get current timestamp",
        },
        "get_timestamp_numeric": {
            "func": get_timestamp_numeric,
            "category": "identity",
            "description": "Get current timestamp as Unix timestamp (seconds since epoch)",
        },
        "generate_correlation_id": {
            "func": generate_correlation_id,
            "category": "identity",
            "description": "Generate correlation ID for request tracking",
        },
        "get_module_prefix": {
            "func": get_module_prefix,
            "category": "identity",
            "description": "Get standardized correlation ID prefix for a module",
        },

        # Response Formatting
        "format_response": {
            "func": format_response,
            "category": "response",
            "description": "Format response data",
        },
        "create_success_response": {
            "func": create_success_response,
            "category": "response",
            "description": "Create standardized success response",
        },

        # Template and Configuration
        "render_template": {
            "func": render_template,
            "category": "template",
            "description": "Render template with context",
        },
        "config_get": {
            "func": config_get,
            "category": "config",
            "description": "Get configuration value",
        },

        # Data Operations
        "parse_json": {
            "func": parse_json,
            "category": "data",
            "description": "Parse JSON string",
        },
        "parse_json_safely": {
            "func": parse_json_safely,
            "category": "data",
            "description": "Parse JSON safely with error handling",
        },
        "json_loads": {
            "func": lambda json_string, **kw: __import__('json').loads(json_string),
            "category": "data",
            "description": "Parse JSON string (json.loads equivalent)",
        },
        "json_dumps": {
            "func": lambda obj, **kw: __import__('json').dumps(obj),
            "category": "data",
            "description": "Serialize object to JSON (json.dumps equivalent)",
        },
        "deep_merge": {
            "func": deep_merge,
            "category": "data",
            "description": "Deep merge dictionaries",
        },
        "safe_get": {
            "func": safe_get,
            "category": "data",
            "description": "Safely get nested dictionary value",
        },
        "format_bytes": {
            "func": format_bytes,
            "category": "data",
            "description": "Format bytes to human readable string",
        },
        "merge_dictionaries": {
            "func": merge_dictionaries,
            "category": "data",
            "description": "Merge multiple dictionaries",
        },
        "format_data_for_response": {
            "func": format_data_for_response,
            "category": "data",
            "description": "Format data for API response",
        },

        # Validation
        "validate_string": {
            "func": validate_string,
            "category": "validation",
            "description": "Validate string input",
        },
        "validate_data_structure": {
            "func": validate_data_structure,
            "category": "validation",
            "description": "Validate data structure",
        },
        "validate_operation_parameters": {
            "func": validate_operation_parameters,
            "category": "validation",
            "description": "Validate operation parameters",
        },

        # Sanitization
        "sanitize_data": {
            "func": sanitize_data,
            "category": "sanitization",
            "description": "Sanitize data for security",
        },
        "safe_string_conversion": {
            "func": safe_string_conversion,
            "category": "sanitization",
            "description": "Safely convert to string",
        },
        "extract_error_details": {
            "func": extract_error_details,
            "category": "sanitization",
            "description": "Extract error details from exception",
        },

        # Performance
        "cleanup_cache": {
            "func": cleanup_cache,
            "category": "performance",
            "description": "Clean up performance cache",
        },
        "get_performance_stats": {
            "func": get_performance_stats,
            "category": "performance",
            "description": "Get performance statistics",
        },
        "optimize_performance": {
            "func": optimize_performance,
            "category": "performance",
            "description": "Optimize performance settings",
        },
        "configure_caching": {
            "func": configure_caching,
            "category": "performance",
            "description": "Configure caching behavior",
        },
        "get_stats": {
            "func": utility_get_stats,
            "category": "performance",
            "description": "Get utility statistics",
        },
        "stats": {
            "func": utility_get_stats,
            "category": "performance",
            "description": "Get utility statistics (alias)",
        },
        "reset": {
            "func": utility_reset,
            "category": "performance",
            "description": "Reset utility statistics",
        },

        # Safe Subprocess
        "safe_subprocess_run": {
            "func": safe_subprocess_run,
            "category": "subprocess",
            "description": "Safely execute subprocess with security validation (no shell=True)",
        },
    }

_UTILITY_DISPATCH = _build_dispatch_dict() if (_UTILITY_AVAILABLE and _UTILITY_IMPORTS_AVAILABLE) else {}


# ZAPH module removed 2026-03-31 - unused dead code

def execute_utility_operation(operation: str, **kwargs) -> Any:
    """Route utility operation requests using Static DDS.

    Args:
        operation: The utility operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Utility interface unavailable
        ValueError: If operation unknown

    """
    operation_entry = _UTILITY_DISPATCH.get(operation)
    if not operation_entry:
        valid_ops = ", ".join(_UTILITY_DISPATCH.keys())
        raise ValueError(
            f"Unknown utility operation: '{operation}'. "
            f"Valid: {valid_ops}",
        )

    # get_module_prefix is always available (doesn't require utility core)
    if operation == "get_module_prefix":
        handler = operation_entry["func"]
        return handler(**kwargs)

    # Check availability for other operations
    if not _UTILITY_AVAILABLE:
        raise RuntimeError(
            f"Utility interface unavailable: {_UTILITY_IMPORT_ERROR}",
        )

    # Execute operation through dispatch handler (O(1) lookup)
    handler = operation_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_utility_operation"]
