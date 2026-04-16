"""utility/utility_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for utility interface
License: Apache 2.0
"""

from typing import Any, Optional

# Initialize operation classes
from lee.gateway import GatewayInterface, execute_operation
from lee.lee_config.constants import STRING_MAX_LENGTH
from lee.lee_utility.utility_data import UtilityDataOperations
from lee.lee_utility.utility_manager import get_utility_manager
from lee.lee_utility.utility_response import format_response
from lee.lee_utility.utility_sanitize import UtilitySanitizeOperations
from lee.lee_utility.utility_validation import UtilityValidationOperations


def _get_data_ops():
    """Get data operations instance."""
    return UtilityDataOperations(get_utility_manager())


def _get_validation_ops():
    """Get validation operations instance."""
    return UtilityValidationOperations(get_utility_manager())


def _get_sanitize_ops():
    """Get sanitize operations instance."""
    return UtilitySanitizeOperations(get_utility_manager())


# === MODULE PREFIX ===

def get_module_prefix_implementation(module_name: str, _correlation_id: str = None, **_kwargs) -> str:
    """Generate module prefix for correlation IDs.

        module_name: Module name (defaults to 'gw' for gateway)
        _correlation_id: Correlation ID for tracking (unused)

        Short module prefix for correlation ID

    """
    if not module_name or module_name == "":
        return "gw"  # Gateway prefix
    # Return first 3 characters of module name, lowercase
    return module_name[:3].lower()


# === UUID AND TIMESTAMP ===

def generate_uuid_implementation(correlation_id: str = None, **_kwargs) -> str:
    """Generate UUID."""
    return get_utility_manager().generate_uuid(correlation_id)


def get_timestamp_implementation(correlation_id: str = None, **_kwargs) -> str:
    """Get current timestamp."""
    return get_utility_manager().get_timestamp(correlation_id)


def get_timestamp_numeric_implementation(correlation_id: str = None, **_kwargs) -> float:
    """Get current timestamp as Unix timestamp (seconds since epoch)."""
    return get_utility_manager().get_timestamp_numeric(correlation_id)


def generate_correlation_id_implementation(prefix: Optional[str] = None, **_kwargs) -> str:
    """Generate correlation ID."""
    return get_utility_manager().generate_correlation_id_impl(prefix)


# === TEMPLATE RENDERING ===

def render_template_implementation(template: dict, data: dict,
                                   correlation_id: str = None, **_kwargs) -> dict:
    """Render template with data substitution."""
    return get_utility_manager().render_template_impl(template, data, correlation_id)


# === CONFIG RETRIEVAL ===

def config_get_implementation(key: str, default=None,
                             correlation_id: str = None, **_kwargs):
    """Get typed configuration value."""
    return get_utility_manager().config_get_impl(key, default, correlation_id)


# === DATA OPERATIONS ===

def parse_json_implementation(data: str, correlation_id: str = None, **_kwargs) -> dict:
    """Parse JSON string."""
    # FIXED: Add input validation (MEDIUM-005) - SUGA-ISP compliant
    execute_operation(GatewayInterface.SECURITY, "validate_string",
                     value=data, min_length=1, max_length=STRING_MAX_LENGTH, name="JSON data")
    return _get_data_ops().parse_json(data, correlation_id)


def parse_json_safely_implementation(json_str: str, use_cache: bool = True,
                                    correlation_id: str = None, **_kwargs):
    """Parse JSON safely with optional caching."""
    return _get_data_ops().parse_json_safely(json_str, use_cache, correlation_id)


def deep_merge_implementation(dict1: dict[str, Any], dict2: dict[str, Any],
                              correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    # Type validation happens at call site via type hints
    # SECURITY.validate_data_structure operation doesn't exist - removed call
    return _get_data_ops().deep_merge(dict1, dict2, correlation_id)


def safe_get_implementation(dictionary: dict, key_path: str, default: Any = None,
                           correlation_id: str = None, **_kwargs):
    """Safely get nested dictionary value."""
    return _get_data_ops().safe_get(dictionary, key_path, default, correlation_id)


def format_bytes_implementation(size: int, correlation_id: str = None, **_kwargs) -> str:
    """Format bytes to human-readable string."""
    # FIXED: Add input validation (MEDIUM-005) - SUGA-ISP compliant
    execute_operation(GatewayInterface.SECURITY, "validate_number_range",
                     value=size, min_val=0, max_val=1099511627776, name="size")  # Max 1TB
    return _get_data_ops().format_bytes(size, correlation_id)


def merge_dictionaries_implementation(*dicts: dict[str, Any],
                                     correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Merge multiple dictionaries safely."""
    return _get_data_ops().merge_dictionaries(*dicts, correlation_id=correlation_id)


def format_data_for_response_implementation(data: Any, format_type: str = "json",
                                           include_metadata: bool = True,
                                           correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Format data for response."""
    return _get_data_ops().format_data_for_response(data, format_type, include_metadata, correlation_id)


def cleanup_cache_implementation(max_age_seconds: int = 3600,
                                 correlation_id: str = None, **_kwargs) -> int:
    """Clean up old cached utility data."""
    return _get_data_ops().cleanup_cache(max_age_seconds, correlation_id)


def optimize_performance_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Optimize utility performance."""
    return _get_data_ops().optimize_performance(correlation_id)


def configure_caching_implementation(enabled: bool, ttl: int = 300,
                                    correlation_id: str = None, **_kwargs) -> bool:
    """Configure utility caching settings."""
    return _get_data_ops().configure_caching(enabled, ttl, correlation_id)


# === VALIDATION ===

def validate_string_implementation(value: str, min_length: int = 0, max_length: int = 1000,
                                  correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Validate string input."""
    return _get_validation_ops().validate_string(value, min_length, max_length, correlation_id)


def validate_data_structure_implementation(data: Any, expected_type: type,
                                          required_fields: Optional[list[str]] = None,
                                          correlation_id: str = None, **_kwargs) -> bool:
    """Validate data structure."""
    return _get_validation_ops().validate_data_structure(data, expected_type, required_fields, correlation_id)


def validate_operation_parameters_implementation(required_params: list[str],
                                                optional_params: Optional[list[str]] = None,
                                                correlation_id: str = None,
                                                **_kwargs) -> dict[str, Any]:
    """Generic parameter validation."""
    return _get_validation_ops().validate_operation_parameters(
        required_params, optional_params, correlation_id,
    )


# === SANITIZATION ===

def sanitize_data_implementation(data: dict[str, Any],
                                 correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Sanitize response data."""
    return _get_sanitize_ops().sanitize_data(data, correlation_id)


def safe_string_conversion_implementation(data: Any, max_length: int = 10000,
                                         correlation_id: str = None, **_kwargs) -> str:
    """Safely convert data to string."""
    return _get_sanitize_ops().safe_string_conversion(data, max_length, correlation_id)


def extract_error_details_implementation(error: Exception,
                                        correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Extract detailed error information."""
    return _get_sanitize_ops().extract_error_details(error, correlation_id)


# === PERFORMANCE AND STATS ===

def get_performance_stats_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get utility performance statistics."""
    return get_utility_manager().get_performance_stats(correlation_id)


def get_stats_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get utility statistics."""
    return get_utility_manager().get_stats(correlation_id)


def reset_implementation(correlation_id: str = None, **_kwargs) -> bool:
    """Reset utility manager state."""
    return get_utility_manager().reset(correlation_id)


# === SAFE SUBPROCESS ===

def safe_subprocess_run_implementation(  # pylint: disable=too-many-arguments too-many-positional-arguments
    command: list, timeout: int = 30,
    capture_output: bool = True, check: bool = False,
    cwd: str = None, env: dict = None,
    correlation_id: str = None, **_kwargs
) -> dict:
    """Safely execute subprocess with comprehensive security validation.

    SECURITY:
    - NEVER uses shell=True (prevents command injection)
    - Validates NO shell metacharacters: |, &, ;, $, `, \n, \r
    - Forces list format for commands (no string parsing)
    - Sanitizes environment variables if provided
    - Logs all subprocess execution via gateway

        command: Command as list (e.g., ['python', '-m', 'pytest'])
        timeout: Timeout in seconds (default: 30)
        capture_output: Capture stdout/stderr (default: True)
        check: Raise exception on non-zero exit (default: False)
        cwd: Working directory (optional)
        env: Environment variables dict (optional, will be sanitized)
        correlation_id: Correlation ID for logging (optional)

        dict with keys:
            - stdout: str (decoded if capture_output=True)
            - stderr: str (decoded if capture_output=True)
            - returncode: int
            - success: bool

    Raises:
        ValueError: If command contains shell metacharacters
        TypeError: If command is not a list
        subprocess.TimeoutExpired: If timeout exceeded
        subprocess.CalledProcessError: If check=True and non-zero exit

    """
    return get_utility_manager().safe_subprocess_run(
        command=command, timeout=timeout, capture_output=capture_output,
        check=check, cwd=cwd, env=env, correlation_id=correlation_id,
    )


__all__ = [
    "cleanup_cache_implementation",
    "config_get_implementation",
    "configure_caching_implementation",
    "create_success_response_implementation",
    "deep_merge_implementation",
    "extract_error_details_implementation",
    "format_bytes_implementation",
    "format_data_for_response_implementation",
    "format_response_implementation",
    "generate_correlation_id_implementation",
    "generate_uuid_implementation",
    "get_module_prefix_implementation",
    "get_performance_stats_implementation",
    "get_stats_implementation",
    "get_timestamp_implementation",
    "get_timestamp_numeric_implementation",
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
    "validate_string_implementation",
]


def format_response_implementation(status_code: int, body: Any, headers: Optional[dict] = None) -> dict[str, Any]:
    """Implementation for format_response utility operation."""
    return format_response(status_code, body, headers)


def create_success_response_implementation(message: str, data: Optional[dict] = None, **kwargs) -> dict[str, Any]:
    """Create a standardized success response.

        message: Success message
        data: Optional data dictionary to merge into response
        **kwargs: Additional fields to include in response

        Formatted success response dictionary with status_code, success, message, and data

    """
    response = {
        "status_code": 200,
        "success": True,
        "message": message,
    }

    if data:
        response.update(data)

    # Add any additional fields from kwargs
    if kwargs:
        response.update(kwargs)

    return response
