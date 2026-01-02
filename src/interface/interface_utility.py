"""
interface/interface_utility.py
Version: 2025-12-13_1
Purpose: Utility interface router with import protection
License: Apache 2.0
"""

from typing import Dict, Any, Callable

# Import protection
try:
    import utility
    _UTILITY_AVAILABLE = True
    _UTILITY_IMPORT_ERROR = None
except ImportError as e:
    _UTILITY_AVAILABLE = False
    _UTILITY_IMPORT_ERROR = str(e)


def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for utility operations."""
    return {
        # UUID and timestamp
        'generate_uuid': utility.generate_uuid_implementation,
        'get_timestamp': utility.get_timestamp_implementation,
        'generate_correlation_id': utility.generate_correlation_id_implementation,
        
        # Template and config
        'render_template': utility.render_template_implementation,
        'config_get': utility.config_get_implementation,
        
        # Data operations
        'parse_json': utility.parse_json_implementation,
        'parse_json_safely': utility.parse_json_safely_implementation,
        'deep_merge': utility.deep_merge_implementation,
        'safe_get': utility.safe_get_implementation,
        'format_bytes': utility.format_bytes_implementation,
        'merge_dictionaries': utility.merge_dictionaries_implementation,
        'format_data_for_response': utility.format_data_for_response_implementation,
        
        # Validation
        'validate_string': utility.validate_string_implementation,
        'validate_data_structure': utility.validate_data_structure_implementation,
        'validate_operation_parameters': utility.validate_operation_parameters_implementation,
        
        # Sanitization
        'sanitize_data': utility.sanitize_data_implementation,
        'safe_string_conversion': utility.safe_string_conversion_implementation,
        'extract_error_details': utility.extract_error_details_implementation,
        
        # Performance
        'cleanup_cache': utility.cleanup_cache_implementation,
        'get_performance_stats': utility.get_performance_stats_implementation,
        'optimize_performance': utility.optimize_performance_implementation,
        'configure_caching': utility.configure_caching_implementation,
        'get_stats': utility.get_stats_implementation,
        'reset': utility.reset_implementation,
    }

_UTILITY_DISPATCH = _build_dispatch_dict() if _UTILITY_AVAILABLE else {}


def execute_utility_operation(operation: str, **kwargs) -> Any:
    """
    Route utility operation requests using dispatch dictionary pattern.
    
    Args:
        operation: Utility operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Utility interface unavailable
        ValueError: If operation unknown
    """
    if not _UTILITY_AVAILABLE:
        raise RuntimeError(
            f"Utility interface unavailable: {_UTILITY_IMPORT_ERROR}"
        )
    
    if operation not in _UTILITY_DISPATCH:
        raise ValueError(
            f"Unknown utility operation: '{operation}'. "
            f"Valid: {', '.join(sorted(_UTILITY_DISPATCH.keys()))}"
        )
    
    return _UTILITY_DISPATCH[operation](**kwargs)


__all__ = ['execute_utility_operation']
