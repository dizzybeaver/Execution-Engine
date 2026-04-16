"""cache_operations_split/adapters.py

Adapter functions for wrappers.
"""

from __future__ import annotations

from functools import wraps

from lee.lee_cache.cache_operations_split.standalone_functions import _get_cache_instance

def _cache_adapter(method_name: str):
    """Generic adapter decorator for cache operations.

    Consolidates duplicate adapter patterns by:
    1. Getting cache instance
    2. Wrapping method calls with correlation ID handling
    3. Providing consistent error handling

    Args:
        method_name: Name of the cache method to call

    Returns:
        Adapter function that wraps the cache method
    """
    @wraps(lambda *args, **kwargs: None)
    def adapter(*args, correlation_id: str = None, **kwargs):
        cache = _get_cache_instance(correlation_id=correlation_id)
        method = getattr(cache, method_name)
        return method(*args, correlation_id=correlation_id, **kwargs)
    return adapter


# Generate adapter functions using the generic decorator
_execute_get_implementation = _cache_adapter('get')
_execute_set_implementation = _cache_adapter('set')
_execute_exists_implementation = _cache_adapter('exists')
_execute_delete_implementation = _cache_adapter('delete')
_execute_clear_implementation = _cache_adapter('clear')
_execute_get_stats_implementation = _cache_adapter('get_stats')
_execute_reset_implementation = _cache_adapter('reset')
_execute_cleanup_expired_implementation = _cache_adapter('cleanup_expired')
_execute_get_metadata_implementation = _cache_adapter('get_metadata')
_execute_get_module_dependencies_implementation = _cache_adapter('get_module_dependencies')
_execute_keys_implementation = _cache_adapter('keys')
_execute_values_implementation = _cache_adapter('values')
_execute_items_implementation = _cache_adapter('items')
_execute_pop_implementation = _cache_adapter('pop')
_execute_update_implementation = _cache_adapter('update')
_execute_touch_implementation = _cache_adapter('touch')
_execute_increment_implementation = _cache_adapter('increment')
