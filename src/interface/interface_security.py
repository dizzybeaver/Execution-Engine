"""
interface/interface_security.py
Version: 2025-12-13_1
Purpose: Security interface router with import protection
License: Apache 2.0
"""

from typing import Any, Callable, Dict

# Import protection
try:
    import security
    _SECURITY_AVAILABLE = True
    _SECURITY_IMPORT_ERROR = None
except ImportError as e:
    _SECURITY_AVAILABLE = False
    _SECURITY_IMPORT_ERROR = str(e)


def _validate_request_param(kwargs: Dict[str, Any]) -> None:
    """Validate request parameter exists."""
    if 'request' not in kwargs:
        raise ValueError("security.validate_request requires 'request' parameter")


def _validate_token_param(kwargs: Dict[str, Any]) -> None:
    """Validate token parameter exists and is string."""
    if 'token' not in kwargs:
        raise ValueError("security.validate_token requires 'token' parameter")
    if not isinstance(kwargs['token'], str):
        raise TypeError("security.validate_token 'token' must be string")


def _validate_hash_params(kwargs: Dict[str, Any]) -> None:
    """Validate hash verification parameters."""
    if 'data' not in kwargs:
        raise ValueError("security.verify_hash requires 'data' parameter")
    if 'hash_value' not in kwargs:
        raise ValueError("security.verify_hash requires 'hash_value' parameter")


def _validate_data_string_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate data parameter is string."""
    if 'data' not in kwargs:
        raise ValueError(f"security.{operation} requires 'data' parameter")
    if not isinstance(kwargs['data'], str):
        raise TypeError(f"security.{operation} 'data' must be str, got {type(kwargs['data']).__name__}")


def _validate_value_string_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate value parameter is string."""
    if 'value' not in kwargs:
        raise ValueError(f"security.{operation} requires 'value' parameter")
    if not isinstance(kwargs['value'], str):
        raise TypeError(f"security.{operation} 'value' must be str, got {type(kwargs['value']).__name__}")


def _validate_sanitize_data_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate data parameter for sanitize operations."""
    if 'data' not in kwargs:
        raise ValueError(f"security.{operation} requires 'data' parameter")


def _validate_cache_key_param(kwargs: Dict[str, Any]) -> None:
    """Validate cache key parameter."""
    if 'key' not in kwargs:
        raise ValueError("security.validate_cache_key requires 'key' parameter")
    if not isinstance(kwargs['key'], str):
        raise TypeError(f"security.validate_cache_key 'key' must be str, got {type(kwargs['key']).__name__}")


def _validate_ttl_param(kwargs: Dict[str, Any]) -> None:
    """Validate TTL parameter."""
    if 'ttl' not in kwargs:
        raise ValueError("security.validate_ttl requires 'ttl' parameter")
    if not isinstance(kwargs['ttl'], (int, float)):
        raise TypeError(f"security.validate_ttl 'ttl' must be numeric, got {type(kwargs['ttl']).__name__}")


def _validate_module_name_param(kwargs: Dict[str, Any]) -> None:
    """Validate module name parameter."""
    if 'module_name' not in kwargs:
        raise ValueError("security.validate_module_name requires 'module_name' parameter")
    if not isinstance(kwargs['module_name'], str):
        raise TypeError(f"security.validate_module_name 'module_name' must be str, got {type(kwargs['module_name']).__name__}")


def _validate_number_range_params(kwargs: Dict[str, Any]) -> None:
    """Validate number range parameters."""
    if 'value' not in kwargs:
        raise ValueError("security.validate_number_range requires 'value' parameter")
    if 'min_val' not in kwargs:
        raise ValueError("security.validate_number_range requires 'min_val' parameter")
    if 'max_val' not in kwargs:
        raise ValueError("security.validate_number_range requires 'max_val' parameter")


def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for security operations."""
    return {
        'validate_request': lambda **kwargs: (
            _validate_request_param(kwargs),
            security.validate_request_implementation(**kwargs)
        )[1],
        
        'validate_token': lambda **kwargs: (
            _validate_token_param(kwargs),
            security.validate_token_implementation(**kwargs)
        )[1],
        
        'encrypt': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'encrypt'),
            security.encrypt_implementation(**kwargs)
        )[1],
        
        'decrypt': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'decrypt'),
            security.decrypt_implementation(**kwargs)
        )[1],
        
        'hash': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'hash'),
            security.hash_implementation(**kwargs)
        )[1],
        
        'verify_hash': lambda **kwargs: (
            _validate_hash_params(kwargs),
            security.verify_hash_implementation(**kwargs)
        )[1],
        
        'sanitize': lambda **kwargs: (
            _validate_sanitize_data_param(kwargs, 'sanitize'),
            security.sanitize_implementation(**kwargs)
        )[1],
        
        'sanitize_data': lambda **kwargs: (
            _validate_sanitize_data_param(kwargs, 'sanitize_data'),
            security.sanitize_implementation(**kwargs)
        )[1],
        
        'generate_correlation_id': security.generate_correlation_id_implementation,
        
        'validate_string': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_string'),
            security.validate_string_implementation(**kwargs)
        )[1],
        
        'validate_email': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_email'),
            security.validate_email_implementation(**kwargs)
        )[1],
        
        'validate_url': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_url'),
            security.validate_url_implementation(**kwargs)
        )[1],
        
        'get_stats': security.get_security_stats_implementation,
        
        'validate_cache_key': lambda **kwargs: (
            _validate_cache_key_param(kwargs),
            security.validate_cache_key_implementation(**kwargs)
        )[1],
        
        'validate_ttl': lambda **kwargs: (
            _validate_ttl_param(kwargs),
            security.validate_ttl_implementation(**kwargs)
        )[1],
        
        'validate_module_name': lambda **kwargs: (
            _validate_module_name_param(kwargs),
            security.validate_module_name_implementation(**kwargs)
        )[1],
        
        'validate_number_range': lambda **kwargs: (
            _validate_number_range_params(kwargs),
            security.validate_number_range_implementation(**kwargs)
        )[1],
        
        'reset': security.security_reset_implementation,
        'reset_security': security.security_reset_implementation,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _SECURITY_AVAILABLE else {}


def execute_security_operation(operation: str, **kwargs) -> Any:
    """
    Route security operation requests using dispatch dictionary pattern.
    
    Args:
        operation: Security operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Security interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    if not _SECURITY_AVAILABLE:
        raise RuntimeError(
            f"Security interface unavailable: {_SECURITY_IMPORT_ERROR}"
        )
    
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_security_operation']
