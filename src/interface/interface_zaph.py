"""
interface_zaph.py
Version: 2025-12-14_1
Purpose: ZAPH (Zero-Abstraction Path for Hot operations) interface router
"""

from typing import Dict, Any, Optional, Callable, List

# Operation dispatch dictionary
DISPATCH = {
    'track_operation': lambda **kwargs: _execute_track_operation(**kwargs),
    'execute': lambda **kwargs: _execute_fast_path(**kwargs),
    'register': lambda **kwargs: _execute_register(**kwargs),
    'get': lambda **kwargs: _execute_get(**kwargs),
    'is_hot': lambda **kwargs: _execute_is_hot(**kwargs),
    'should_protect': lambda **kwargs: _execute_should_protect(**kwargs),
    'heat_level': lambda **kwargs: _execute_heat_level(**kwargs),
    'stats': lambda **kwargs: _execute_stats(**kwargs),
    'hot_operations': lambda **kwargs: _execute_hot_operations(**kwargs),
    'cached_operations': lambda **kwargs: _execute_cached_operations(**kwargs),
    'configure': lambda **kwargs: _execute_configure(**kwargs),
    'config': lambda **kwargs: _execute_config(**kwargs),
    'prewarm': lambda **kwargs: _execute_prewarm(**kwargs),
    'prewarm_common': lambda **kwargs: _execute_prewarm_common(**kwargs),
    'clear': lambda **kwargs: _execute_clear(**kwargs),
    'reset_counts': lambda **kwargs: _execute_reset_counts(**kwargs),
    'reset_stats': lambda **kwargs: _execute_reset_stats(**kwargs),
    'optimize': lambda **kwargs: _execute_optimize(**kwargs),
}


def execute_zaph_operation(operation: str, **kwargs) -> Any:
    """Execute ZAPH operation via dispatch dictionary."""
    handler = DISPATCH.get(operation)
    if not handler:
        raise ValueError(f"Unknown ZAPH operation: {operation}")
    return handler(**kwargs)


# Implementation functions
def _execute_track_operation(**kwargs) -> Any:
    """Track operation implementation."""
    from zaph import track_operation
    return track_operation(
        kwargs['operation_key'],
        kwargs['duration_ms'],
        kwargs.get('source_module'),
        kwargs.get('correlation_id', 'track')
    )


def _execute_fast_path(**kwargs) -> Any:
    """Execute fast path implementation."""
    from zaph import execute_fast_path
    return execute_fast_path(
        kwargs['operation_key'],
        kwargs['func'],
        *kwargs.get('args', ()),
        correlation_id=kwargs.get('correlation_id', 'execute'),
        **kwargs.get('func_kwargs', {})
    )


def _execute_register(**kwargs) -> None:
    """Register fast path implementation."""
    from zaph import register_fast_path
    register_fast_path(
        kwargs['operation_key'],
        kwargs['fast_func'],
        kwargs.get('source_module'),
        kwargs.get('correlation_id', 'register')
    )


def _execute_get(**kwargs) -> Optional[Callable]:
    """Get fast path implementation."""
    from zaph import get_fast_path
    return get_fast_path(
        kwargs['operation_key'],
        kwargs.get('correlation_id', 'get')
    )


def _execute_is_hot(**kwargs) -> bool:
    """Check if hot operation implementation."""
    from zaph import is_hot_operation
    return is_hot_operation(
        kwargs['operation_key'],
        kwargs.get('correlation_id', 'is_hot')
    )


def _execute_should_protect(**kwargs) -> bool:
    """Should protect module implementation."""
    from zaph import should_protect_module
    return should_protect_module(
        kwargs['module_name'],
        kwargs.get('correlation_id', 'protect')
    )


def _execute_heat_level(**kwargs) -> Any:
    """Get heat level implementation."""
    from zaph import get_heat_level
    return get_heat_level(
        kwargs['operation_key'],
        kwargs.get('correlation_id', 'heat')
    )


def _execute_stats(**kwargs) -> Dict[str, Any]:
    """Get stats implementation."""
    from zaph import get_fast_path_stats
    return get_fast_path_stats(
        kwargs.get('correlation_id', 'stats')
    )


def _execute_hot_operations(**kwargs) -> List:
    """Get hot operations implementation."""
    from zaph import get_hot_operations
    return get_hot_operations(
        kwargs.get('limit', 10),
        kwargs.get('correlation_id', 'hot_ops')
    )


def _execute_cached_operations(**kwargs) -> List:
    """Get cached operations implementation."""
    from zaph import get_cached_operations
    return get_cached_operations(
        kwargs.get('correlation_id', 'cached')
    )


def _execute_configure(**kwargs) -> Dict[str, Any]:
    """Configure implementation."""
    from zaph import configure_fast_path
    return configure_fast_path(
        kwargs.get('enabled'),
        kwargs.get('cache_size'),
        kwargs.get('warm_threshold'),
        kwargs.get('hot_threshold'),
        kwargs.get('critical_threshold'),
        kwargs.get('correlation_id', 'configure')
    )


def _execute_config(**kwargs) -> Dict[str, Any]:
    """Get config implementation."""
    from zaph import get_fast_path_config
    return get_fast_path_config(
        kwargs.get('correlation_id', 'get_config')
    )


def _execute_prewarm(**kwargs) -> int:
    """Prewarm implementation."""
    from zaph import prewarm_cache
    return prewarm_cache(
        kwargs['operation_keys'],
        kwargs.get('correlation_id', 'prewarm')
    )


def _execute_prewarm_common(**kwargs) -> int:
    """Prewarm common implementation."""
    from zaph import prewarm_common_operations
    return prewarm_common_operations(
        kwargs.get('correlation_id', 'prewarm_common')
    )


def _execute_clear(**kwargs) -> None:
    """Clear cache implementation."""
    from zaph import clear_fast_path_cache
    clear_fast_path_cache(
        kwargs.get('correlation_id', 'clear')
    )


def _execute_reset_counts(**kwargs) -> None:
    """Reset counts implementation."""
    from zaph import reset_call_counts
    reset_call_counts(
        kwargs.get('correlation_id', 'reset_counts')
    )


def _execute_reset_stats(**kwargs) -> None:
    """Reset stats implementation."""
    from zaph import reset_stats
    reset_stats(
        kwargs.get('correlation_id', 'reset_stats')
    )


def _execute_optimize(**kwargs) -> Dict[str, Any]:
    """Optimize implementation."""
    from zaph import optimize_fast_path
    return optimize_fast_path(
        kwargs.get('correlation_id', 'optimize')
    )


__all__ = ['execute_zaph_operation', 'DISPATCH']

# EOF
