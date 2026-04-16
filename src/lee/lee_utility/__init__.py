"""utility/__init__.py
Version: 2025-12-13_1
Purpose: Utility module initialization
License: Apache 2.0
"""

from lee.lee_utility.utility_generic import (
    cleanup_cache_implementation,
    config_get_implementation,
    configure_caching_implementation,
    create_success_response_implementation,
    deep_merge_implementation,
    extract_error_details_implementation,
    format_bytes_implementation,
    format_data_for_response_implementation,
    generate_correlation_id_implementation,
    generate_uuid_implementation,
    get_performance_stats_implementation,
    get_stats_implementation,
    get_timestamp_implementation,
    merge_dictionaries_implementation,
    optimize_performance_implementation,
    parse_json_implementation,
    parse_json_safely_implementation,
    render_template_implementation,
    reset_implementation,
    safe_get_implementation,
    safe_string_conversion_implementation,
    safe_subprocess_run_implementation,  # NEW: Safe subprocess (2026-03-09)
    sanitize_data_implementation,
    validate_data_structure_implementation,
    validate_operation_parameters_implementation,
    validate_string_implementation,
)
from lee.lee_utility.utility_manager import SharedUtilityCore, get_utility_manager
from lee.lee_utility.utility_response import (
    ResponseFormatter,
    create_error_response,
    create_success_response,
    format_response,
    format_response_fast,
)
from lee.lee_utility.utility_types import (
    DEFAULT_MAX_JSON_CACHE_SIZE,
    DEFAULT_USE_GENERIC_OPERATIONS,
    DEFAULT_USE_TEMPLATES,
    UtilityMetrics,
    UtilityOperation,
)

__all__ = [
    "DEFAULT_MAX_JSON_CACHE_SIZE",
    "DEFAULT_USE_GENERIC_OPERATIONS",
    "DEFAULT_USE_TEMPLATES",
    "ResponseFormatter",
    "SharedUtilityCore",
    "UtilityMetrics",
    "UtilityOperation",
    "cleanup_cache_implementation",
    "config_get_implementation",
    "configure_caching_implementation",
    "create_error_response",
    "create_success_response",
    "create_success_response_implementation",
    "deep_merge_implementation",
    "extract_error_details_implementation",
    "format_bytes_implementation",
    "format_data_for_response_implementation",
    "format_response",
    "format_response_fast",
    "generate_correlation_id_implementation",
    "generate_uuid_implementation",
    "get_performance_stats_implementation",
    "get_stats_implementation",
    "get_timestamp_implementation",
    "get_utility_manager",
    "merge_dictionaries_implementation",
    "optimize_performance_implementation",
    "parse_json_implementation",
    "parse_json_safely_implementation",
    "render_template_implementation",
    "reset_implementation",
    "safe_get_implementation",
    "safe_string_conversion_implementation",
    "safe_subprocess_run_implementation",  # NEW: Safe subprocess (2026-03-09)
    "sanitize_data_implementation",
    "validate_data_structure_implementation",
    "validate_operation_parameters_implementation",
    "validate_string_implementation",
]
