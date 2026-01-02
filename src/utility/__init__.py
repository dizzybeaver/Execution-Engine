"""
utility/__init__.py
Version: 2025-12-13_1
Purpose: Utility module initialization
License: Apache 2.0
"""

from utility.utility_types import (
    UtilityOperation,
    UtilityMetrics,
    DEFAULT_USE_TEMPLATES,
    DEFAULT_USE_GENERIC_OPERATIONS,
    DEFAULT_MAX_JSON_CACHE_SIZE
)
from utility.utility_manager import (
    SharedUtilityCore,
    get_utility_manager
)
from utility.utility_response import (
    ResponseFormatter,
    format_response_fast,
    format_response,
    create_success_response,
    create_error_response
)
from utility.utility_core import (
    generate_uuid_implementation,
    get_timestamp_implementation,
    generate_correlation_id_implementation,
    parse_json_implementation,
    parse_json_safely_implementation,
    deep_merge_implementation,
    safe_get_implementation,
    format_bytes_implementation,
    validate_string_implementation,
    validate_data_structure_implementation,
    validate_operation_parameters_implementation,
    sanitize_data_implementation,
    safe_string_conversion_implementation,
    merge_dictionaries_implementation,
    extract_error_details_implementation,
    format_data_for_response_implementation,
    cleanup_cache_implementation,
    get_performance_stats_implementation,
    optimize_performance_implementation,
    configure_caching_implementation,
    get_stats_implementation,
    reset_implementation,
    render_template_implementation,
    config_get_implementation
)

__all__ = [
    'UtilityOperation',
    'UtilityMetrics',
    'DEFAULT_USE_TEMPLATES',
    'DEFAULT_USE_GENERIC_OPERATIONS',
    'DEFAULT_MAX_JSON_CACHE_SIZE',
    'SharedUtilityCore',
    'get_utility_manager',
    'ResponseFormatter',
    'format_response_fast',
    'format_response',
    'create_success_response',
    'create_error_response',
    'generate_uuid_implementation',
    'get_timestamp_implementation',
    'generate_correlation_id_implementation',
    'parse_json_implementation',
    'parse_json_safely_implementation',
    'deep_merge_implementation',
    'safe_get_implementation',
    'format_bytes_implementation',
    'validate_string_implementation',
    'validate_data_structure_implementation',
    'validate_operation_parameters_implementation',
    'sanitize_data_implementation',
    'safe_string_conversion_implementation',
    'merge_dictionaries_implementation',
    'extract_error_details_implementation',
    'format_data_for_response_implementation',
    'cleanup_cache_implementation',
    'get_performance_stats_implementation',
    'optimize_performance_implementation',
    'configure_caching_implementation',
    'get_stats_implementation',
    'reset_implementation',
    'render_template_implementation',
    'config_get_implementation',
]
