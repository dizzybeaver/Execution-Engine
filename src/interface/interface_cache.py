"""
interface_cache.py
Version: 2025-12-08_1
Purpose: Cache interface router with sentinel sanitization
License: Apache 2.0
"""

from typing import Any, Callable, Dict

try:
    from cache.cache_operations import (
        _execute_get_implementation,
        _execute_set_implementation,
        _execute_exists_implementation,
        _execute_delete_implementation,
        _execute_clear_implementation,
        _execute_reset_implementation,
        _execute_cleanup_expired_implementation,
        _execute_get_stats_implementation,
        _execute_get_metadata_implementation
    )
    _CACHE_AVAILABLE = True
    _CACHE_IMPORT_ERROR = None
except ImportError as e:
    _CACHE_AVAILABLE = False
    _CACHE_IMPORT_ERROR = str(e)
    _execute_get_implementation = None
    _execute_set_implementation = None
    _execute_exists_implementation = None
    _execute_delete_implementation = None
    _execute_clear_implementation = None
    _execute_reset_implementation = None
    _execute_cleanup_expired_implementation = None
    _execute_get_stats_implementation = None
    _execute_get_metadata_implementation = None


def _is_sentinel_object(value: Any) -> bool:
    """Detect if value is object() sentinel."""
    return (
        type(value).__name__ == 'object' and
        not isinstance(value, (str, int, float, bool, list, dict, tuple, set, type(None))) and
        str(value).startswith('<object object')
    )


def _sanitize_value_deep(value: Any, path: str = "root") -> Any:
    """Recursively remove sentinel objects from data structure."""
    if _is_sentinel_object(value):
        try:
            from gateway import log_warning
            log_warning(f"[CACHE_SANITIZE] Removed sentinel at path: {path}")
        except:
            pass
        return None
    
    if isinstance(value, dict):
        return {
            k: _sanitize_value_deep(v, f"{path}.{k}")
            for k, v in value.items()
            if not _is_sentinel_object(v)
        }
    
    if isinstance(value, (list, tuple)):
        sanitized = [
            _sanitize_value_deep(item, f"{path}[{i}]")
            for i, item in enumerate(value)
            if not _is_sentinel_object(item)
        ]
        return type(value)(sanitized)
    
    if isinstance(value, set):
        return {
            _sanitize_value_deep(item, f"{path}.item")
            for item in value
            if not _is_sentinel_object(item)
        }
    
    return value


def _validate_key_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate key parameter exists and is string."""
    if 'key' not in kwargs:
        raise ValueError(f"cache.{operation} requires 'key' parameter")
    if not isinstance(kwargs['key'], str):
        raise TypeError(
            f"cache.{operation} 'key' must be str, got {type(kwargs['key']).__name__}"
        )


def _validate_set_params(kwargs: Dict[str, Any]) -> None:
    """Validate and sanitize set operation parameters."""
    _validate_key_param(kwargs, 'set')
    if 'value' not in kwargs:
        raise ValueError("cache.set requires 'value' parameter")
    
    original_value = kwargs['value']
    sanitized_value = _sanitize_value_deep(original_value, f"cache[{kwargs['key']}]")
    kwargs['value'] = sanitized_value


def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for cache operations."""
    return {
        'get': lambda **kwargs: (
            _validate_key_param(kwargs, 'get'),
            _sanitize_value_deep(
                _execute_get_implementation(**kwargs),
                f"cache[{kwargs['key']}]"
            )
        )[1],
        
        'set': lambda **kwargs: (
            _validate_set_params(kwargs),
            _execute_set_implementation(**kwargs)
        )[1],
        
        'exists': lambda **kwargs: (
            _validate_key_param(kwargs, 'exists'),
            _execute_exists_implementation(**kwargs)
        )[1],
        
        'delete': lambda **kwargs: (
            _validate_key_param(kwargs, 'delete'),
            _execute_delete_implementation(**kwargs)
        )[1],
        
        'get_metadata': lambda **kwargs: (
            _validate_key_param(kwargs, 'get_metadata'),
            _execute_get_metadata_implementation(**kwargs)
        )[1],
        
        'clear': _execute_clear_implementation,
        'reset': _execute_reset_implementation,
        'reset_cache': _execute_reset_implementation,
        'cleanup_expired': _execute_cleanup_expired_implementation,
        'get_stats': _execute_get_stats_implementation,
    }


_OPERATION_DISPATCH = _build_dispatch_dict() if _CACHE_AVAILABLE else {}


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """Route cache operation requests using dispatch dictionary pattern."""
    if not _CACHE_AVAILABLE:
        raise RuntimeError(
            f"Cache interface unavailable: {_CACHE_IMPORT_ERROR}. "
            "This may indicate missing cache_core module or circular import."
        )
    
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown cache operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_cache_operation']

# EOF
