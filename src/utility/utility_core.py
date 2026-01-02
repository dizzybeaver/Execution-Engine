"""
utility/utility_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for utility interface
License: Apache 2.0
"""

from typing import Dict, Any, Optional, List

from utility.utility_manager import get_utility_manager
from utility.utility_data import UtilityDataOperations
from utility.utility_validation import UtilityValidationOperations
from utility.utility_sanitize import UtilitySanitizeOperations


# Initialize operation classes
def _get_data_ops():
    """Get data operations instance."""
    return UtilityDataOperations(get_utility_manager())


def _get_validation_ops():
    """Get validation operations instance."""
    return UtilityValidationOperations(get_utility_manager())


def _get_sanitize_ops():
    """Get sanitize operations instance."""
    return UtilitySanitizeOperations(get_utility_manager())


# === UUID AND TIMESTAMP ===

def generate_uuid_implementation(correlation_id: str = None, **kwargs) -> str:
    """Generate UUID."""
    return get_utility_manager().generate_uuid(correlation_id)


def get_timestamp_implementation(correlation_id: str = None, **kwargs) -> str:
    """Get current timestamp."""
    return get_utility_manager().get_timestamp(correlation_id)


def generate_correlation_id_implementation(prefix: Optional[str] = None,
                                          correlation_id: str = None, **kwargs) -> str:
    """Generate correlation ID."""
    return get_utility_manager().generate_correlation_id_impl(prefix, correlation_id)


# === TEMPLATE RENDERING ===

def render_template_implementation(template: dict, data: dict,
                                   correlation_id: str = None, **kwargs) -> dict:
    """Render template with data substitution."""
    # FIXED: Add input validation (MEDIUM-005)
    from gateway import validate_data_structure
    validate_data_structure(template, dict, "template")
    validate_data_structure(data, dict, "data")
    return get_utility_manager().render_template_impl(template, data, correlation_id, **kwargs)


# === CONFIG RETRIEVAL ===

def config_get_implementation(key: str, default=None,
                              correlation_id: str = None, **kwargs) -> Any:
    """Get typed configuration value."""
    return get_utility_manager().config_get_impl(key, default, correlation_id, **kwargs)


# === DATA OPERATIONS ===

def parse_json_implementation(data: str, correlation_id: str = None, **kwargs) -> Dict:
    """Parse JSON string."""
    # FIXED: Add input validation (MEDIUM-005)
    from gateway import validate_string
    validate_string(data, min_length=1, max_length=10000, name="JSON data")
    return _get_data_ops().parse_json(data, correlation_id)


def parse_json_safely_implementation(json_str: str, use_cache: bool = True,
                                     correlation_id: str = None, **kwargs) -> Optional[Dict[str, Any]]:
    """Parse JSON safely with optional caching."""
    return _get_data_ops().parse_json_safely(json_str, use_cache, correlation_id)


def deep_merge_implementation(dict1: Dict[str, Any], dict2: Dict[str, Any],
                              correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    # FIXED: Add input validation (MEDIUM-005)
    from gateway import validate_data_structure
    validate_data_structure(dict1, dict, "dict1")
    validate_data_structure(dict2, dict, "dict2")
    return _get_data_ops().deep_merge(dict1, dict2, correlation_id)


def safe_get_implementation(dictionary: Dict, key_path: str, default: Any = None,
                           correlation_id: str = None, **kwargs) -> Any:
    """Safely get nested dictionary value."""
    return _get_data_ops().safe_get(dictionary, key_path, default, correlation_id)


def format_bytes_implementation(size: int, correlation_id: str = None, **kwargs) -> str:
    """Format bytes to human-readable string."""
    # FIXED: Add input validation (MEDIUM-005)
    from gateway import validate_number_range
    validate_number_range(size, min_val=0, max_val=1099511627776, name="size")  # Max 1TB
    return _get_data_ops().format_bytes(size, correlation_id)


def merge_dictionaries_implementation(*dicts: Dict[str, Any],
                                     correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Merge multiple dictionaries safely."""
    return _get_data_ops().merge_dictionaries(*dicts, correlation_id=correlation_id)


def format_data_for_response_implementation(data: Any, format_type: str = "json",
                                           include_metadata: bool = True,
                                           correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Format data for response."""
    return _get_data_ops().format_data_for_response(data, format_type, include_metadata, correlation_id)


def cleanup_cache_implementation(max_age_seconds: int = 3600,
                                 correlation_id: str = None, **kwargs) -> int:
    """Clean up old cached utility data."""
    return _get_data_ops().cleanup_cache(max_age_seconds, correlation_id)


def optimize_performance_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Optimize utility performance."""
    return _get_data_ops().optimize_performance(correlation_id)


def configure_caching_implementation(enabled: bool, ttl: int = 300,
                                    correlation_id: str = None, **kwargs) -> bool:
    """Configure utility caching settings."""
    return _get_data_ops().configure_caching(enabled, ttl, correlation_id)


# === VALIDATION ===

def validate_string_implementation(value: str, min_length: int = 0, max_length: int = 1000,
                                  correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Validate string input."""
    return _get_validation_ops().validate_string(value, min_length, max_length, correlation_id)


def validate_data_structure_implementation(data: Any, expected_type: type,
                                          required_fields: Optional[List[str]] = None,
                                          correlation_id: str = None, **kwargs) -> bool:
    """Validate data structure."""
    return _get_validation_ops().validate_data_structure(data, expected_type, required_fields, correlation_id)


def validate_operation_parameters_implementation(required_params: List[str],
                                                optional_params: Optional[List[str]] = None,
                                                correlation_id: str = None,
                                                **kwargs) -> Dict[str, Any]:
    """Generic parameter validation."""
    return _get_validation_ops().validate_operation_parameters(
        required_params, optional_params, correlation_id, **kwargs
    )


# === SANITIZATION ===

def sanitize_data_implementation(data: Dict[str, Any],
                                 correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Sanitize response data."""
    return _get_sanitize_ops().sanitize_data(data, correlation_id)


def safe_string_conversion_implementation(data: Any, max_length: int = 10000,
                                         correlation_id: str = None, **kwargs) -> str:
    """Safely convert data to string."""
    return _get_sanitize_ops().safe_string_conversion(data, max_length, correlation_id)


def extract_error_details_implementation(error: Exception,
                                        correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Extract detailed error information."""
    return _get_sanitize_ops().extract_error_details(error, correlation_id)


# === PERFORMANCE AND STATS ===

def get_performance_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get utility performance statistics."""
    return get_utility_manager().get_performance_stats(correlation_id)


def get_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get utility statistics."""
    return get_utility_manager().get_stats(correlation_id)


def reset_implementation(correlation_id: str = None, **kwargs) -> bool:
    """Reset utility manager state."""
    return get_utility_manager().reset(correlation_id)


__all__ = [
    'generate_uuid_implementation',
    'get_timestamp_implementation',
    'generate_correlation_id_implementation',
    'render_template_implementation',
    'config_get_implementation',
    'parse_json_implementation',
    'parse_json_safely_implementation',
    'deep_merge_implementation',
    'safe_get_implementation',
    'format_bytes_implementation',
    'merge_dictionaries_implementation',
    'format_data_for_response_implementation',
    'cleanup_cache_implementation',
    'optimize_performance_implementation',
    'configure_caching_implementation',
    'validate_string_implementation',
    'validate_data_structure_implementation',
    'validate_operation_parameters_implementation',
    'sanitize_data_implementation',
    'safe_string_conversion_implementation',
    'extract_error_details_implementation',
    'get_performance_stats_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
