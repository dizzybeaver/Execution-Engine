# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_cache.py
Version: 2026-04-11_2
Purpose: Cache interface router with Static DDS
License: Apache 2.0
"""

from typing import Any

from lee.interface.interface_common import validate_module_available
from lee.interface.interface_errors import (
    UnknownOperationError,
    validate_string_parameter,
)
from lee.lee_security.sanitize import DataSanitizer
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.lee_cache')
def _import_cache():
    from lee.lee_cache import (
        cache_clear,
        cache_delete,
        cache_exists,
        cache_get,
        cache_get_many,
        cache_get_stats,
        cache_increment,
        cache_items,
        cache_keys,
        cache_mdelete,
        cache_mget,
        cache_mget_metadata,
        cache_mset,
        cache_pop,
        cache_set,
        cache_set_many,
        cache_touch,
        cache_update,
        cache_values,
        get_cache_compressor,
        get_cache_invalidator,
        get_cache_observability,
        get_cache_warmer,
        get_cache_warming_stats,
        get_l2_cache,
        get_stale_while_revalidate,
        get_stampede_protection,
        record_access,
        warm_predictive_data,
        warm_static_data,
        warm_trace_based,
    )
    return {
        'cache_clear': cache_clear,
        'cache_delete': cache_delete,
        'cache_exists': cache_exists,
        'cache_get': cache_get,
        'cache_get_many': cache_get_many,
        'cache_get_stats': cache_get_stats,
        'cache_increment': cache_increment,
        'cache_items': cache_items,
        'cache_keys': cache_keys,
        'cache_mdelete': cache_mdelete,
        'cache_mget': cache_mget,
        'cache_mget_metadata': cache_mget_metadata,
        'cache_mset': cache_mset,
        'cache_pop': cache_pop,
        'cache_set': cache_set,
        'cache_set_many': cache_set_many,
        'cache_touch': cache_touch,
        'cache_update': cache_update,
        'cache_values': cache_values,
        'get_cache_compressor': get_cache_compressor,
        'get_cache_invalidator': get_cache_invalidator,
        'get_cache_observability': get_cache_observability,
        'get_cache_warmer': get_cache_warmer,
        'get_cache_warming_stats': get_cache_warming_stats,
        'get_l2_cache': get_l2_cache,
        'get_stale_while_revalidate': get_stale_while_revalidate,
        'get_stampede_protection': get_stampede_protection,
        'record_access': record_access,
        'warm_predictive_data': warm_predictive_data,
        'warm_static_data': warm_static_data,
        'warm_trace_based': warm_trace_based,
    }


_cache_funcs = _import_cache()
_CACHE_AVAILABLE = _import_cache.__dict__.get('_CACHE_AVAILABLE', False)
_CACHE_IMPORT_ERROR = _import_cache.__dict__.get('_CACHE_IMPORT_ERROR', None)

if _CACHE_AVAILABLE:
    cache_clear = _cache_funcs['cache_clear']
    cache_delete = _cache_funcs['cache_delete']
    cache_exists = _cache_funcs['cache_exists']
    cache_get = _cache_funcs['cache_get']
    cache_get_many = _cache_funcs['cache_get_many']
    cache_get_stats = _cache_funcs['cache_get_stats']
    cache_increment = _cache_funcs['cache_increment']
    cache_items = _cache_funcs['cache_items']
    cache_keys = _cache_funcs['cache_keys']
    cache_mdelete = _cache_funcs['cache_mdelete']
    cache_mget = _cache_funcs['cache_mget']
    cache_mget_metadata = _cache_funcs['cache_mget_metadata']
    cache_mset = _cache_funcs['cache_mset']
    cache_pop = _cache_funcs['cache_pop']
    cache_set = _cache_funcs['cache_set']
    cache_set_many = _cache_funcs['cache_set_many']
    cache_touch = _cache_funcs['cache_touch']
    cache_update = _cache_funcs['cache_update']
    cache_values = _cache_funcs['cache_values']
    get_cache_compressor = _cache_funcs['get_cache_compressor']
    get_cache_invalidator = _cache_funcs['get_cache_invalidator']
    get_cache_observability = _cache_funcs['get_cache_observability']
    get_cache_warmer = _cache_funcs['get_cache_warmer']
    get_cache_warming_stats = _cache_funcs['get_cache_warming_stats']
    get_l2_cache = _cache_funcs['get_l2_cache']
    get_stale_while_revalidate = _cache_funcs['get_stale_while_revalidate']
    get_stampede_protection = _cache_funcs['get_stampede_protection']
    record_access = _cache_funcs['record_access']
    warm_predictive_data = _cache_funcs['warm_predictive_data']
    warm_static_data = _cache_funcs['warm_static_data']
    warm_trace_based = _cache_funcs['warm_trace_based']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        return {"success": False, "error": "Cache module unavailable"}

    cache_clear = _stub_unavailable
    cache_delete = _stub_unavailable
    cache_exists = _stub_unavailable
    cache_get = _stub_unavailable
    cache_get_many = _stub_unavailable
    cache_get_stats = _stub_unavailable
    cache_increment = _stub_unavailable
    cache_items = _stub_unavailable
    cache_keys = _stub_unavailable
    cache_mdelete = _stub_unavailable
    cache_mget = _stub_unavailable
    cache_mget_metadata = _stub_unavailable
    cache_mset = _stub_unavailable
    cache_pop = _stub_unavailable
    cache_set = _stub_unavailable
    cache_set_many = _stub_unavailable
    cache_touch = _stub_unavailable
    cache_update = _stub_unavailable
    cache_values = _stub_unavailable
    get_cache_compressor = _stub_unavailable
    get_cache_invalidator = _stub_unavailable
    get_cache_observability = _stub_unavailable
    get_cache_warmer = _stub_unavailable
    get_cache_warming_stats = _stub_unavailable
    get_l2_cache = _stub_unavailable
    get_stale_while_revalidate = _stub_unavailable
    get_stampede_protection = _stub_unavailable
    record_access = _stub_unavailable
    warm_predictive_data = _stub_unavailable
    warm_static_data = _stub_unavailable
    warm_trace_based = _stub_unavailable


def _is_sentinel_object(value: Any) -> bool:
    """Detect if value is object() sentinel."""
    return (
        type(value).__name__ == "object" and
        not isinstance(value, (
            str, int, float, bool, list, dict, tuple, set,
            type(None)
        )) and
        str(value).startswith("<object object")
    )


def _sanitize_value_deep(value: Any, path: str = "root") -> Any:
    """Recursively remove sentinel objects from data structure."""
    return DataSanitizer.sanitize_value_deep(value, path)


def _validate_key_param(
    kwargs: dict[str, Any],
    operation: str,
) -> None:
    """Validate key parameter exists and is string."""
    validate_string_parameter("cache", operation, kwargs, "key")


def _validate_set_params(kwargs: dict[str, Any]) -> None:
    """Validate and sanitize set operation parameters."""
    _validate_key_param(kwargs, "set")
    if "value" not in kwargs:
        raise ValueError("cache.set requires 'value' parameter")

    original_value = kwargs["value"]
    sanitized_value = _sanitize_value_deep(
        original_value,
        f"cache[{kwargs['key']}]"
    )
    kwargs["value"] = sanitized_value


def _build_dispatch_dict() -> dict[str, Any]:
    """Build Static Dispatch Dictionary for cache operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category (read/write/delete/admin)
    - description: Human-readable description
    """
    return {
        # Core operations
        "get": {
            "func": cache_get,
            "category": "read",
            "description": "Get value from cache",
        },
        "set": {
            "func": cache_set,
            "category": "write",
            "description": "Set value in cache",
        },
        "exists": {
            "func": cache_exists,
            "category": "read",
            "description": "Check if key exists in cache",
        },
        "delete": {
            "func": cache_delete,
            "category": "delete",
            "description": "Delete key from cache",
        },
        "clear": {
            "func": cache_clear,
            "category": "delete",
            "description": "Clear all cache entries",
        },
        "reset": {
            "func": cache_clear,
            "category": "delete",
            "description": "Reset cache (alias for clear)",
        },
        "reset_cache": {
            "func": cache_clear,
            "category": "delete",
            "description": "Reset cache (alias for clear)",
        },
        "get_stats": {
            "func": cache_get_stats,
            "category": "read",
            "description": "Get cache statistics",
        },
        "stats": {
            "func": cache_get_stats,
            "category": "read",
            "description": "Get cache statistics (alias)",
        },

        # Extended cache operations
        "keys": {
            "func": cache_keys,
            "category": "read",
            "description": "Get all cache keys",
        },
        "values": {
            "func": cache_values,
            "category": "read",
            "description": "Get all cache values",
        },
        "items": {
            "func": cache_items,
            "category": "read",
            "description": "Get all cache items",
        },
        "pop": {
            "func": cache_pop,
            "category": "delete",
            "description": "Pop value from cache",
        },
        "update": {
            "func": cache_update,
            "category": "write",
            "description": "Update multiple cache entries",
        },
        "touch": {
            "func": cache_touch,
            "category": "write",
            "description": "Touch cache entry TTL",
        },
        "increment": {
            "func": cache_increment,
            "category": "write",
            "description": "Increment numeric value",
        },
        "get_many": {
            "func": cache_get_many,
            "category": "read",
            "description": "Get multiple cache values",
        },
        "set_many": {
            "func": cache_set_many,
            "category": "write",
            "description": "Set multiple cache values",
        },

        # Phase 1: Stampede Protection & Stale-While-Revalidate
        "get_with_grace_period": {
            "func": lambda **kw: get_stale_while_revalidate()
            .get_with_grace_period(**kw),
            "category": "read",
            "description": "Get with stale-while-revalidate",
        },
        "get_or_compute": {
            "func": lambda **kw: get_stampede_protection()
            .get_or_compute(**kw),
            "category": "write",
            "description": "Get or compute with stampede protection",
        },
        "process_pending_refreshes": {
            "func": lambda **kw: get_stale_while_revalidate()
            .process_pending_refreshes(),
            "category": "write",
            "description": "Process pending cache refreshes",
        },

        # Phase 2: Batch operations
        "mget": {
            "func": cache_mget,
            "category": "read",
            "description": "Multi-get operation",
        },
        "mset": {
            "func": cache_mset,
            "category": "write",
            "description": "Multi-set operation",
        },
        "mdelete": {
            "func": cache_mdelete,
            "category": "delete",
            "description": "Multi-delete operation",
        },
        "mget_metadata": {
            "func": cache_mget_metadata,
            "category": "read",
            "description": "Multi-get with metadata",
        },

        # Phase 2 & 3: Singleton access
        "get_compressor": {
            "func": get_cache_compressor,
            "category": "admin",
            "description": "Get cache compressor singleton",
        },
        "get_l2_cache": {
            "func": get_l2_cache,
            "category": "admin",
            "description": "Get L2 cache singleton",
        },
        "get_invalidator": {
            "func": get_cache_invalidator,
            "category": "admin",
            "description": "Get cache invalidator singleton",
        },
        "get_warmer": {
            "func": get_cache_warmer,
            "category": "admin",
            "description": "Get cache warmer singleton",
        },
        "get_observability": {
            "func": get_cache_observability,
            "category": "admin",
            "description": "Get cache observability singleton",
        },

        # Phase 3: Cache warming operations
        "warm_static_data": {
            "func": warm_static_data,
            "category": "write",
            "description": "Warm static cache data",
        },
        "warm_predictive_data": {
            "func": warm_predictive_data,
            "category": "write",
            "description": "Warm predictive cache data",
        },
        "warm_trace_based": {
            "func": warm_trace_based,
            "category": "write",
            "description": "Warm cache based on trace data",
        },
        "record_access": {
            "func": record_access,
            "category": "write",
            "description": "Record cache access for warming",
        },
        "get_warming_stats": {
            "func": get_cache_warming_stats,
            "category": "read",
            "description": "Get cache warming statistics",
        },

        # Phase 3: Compression metrics
        "get_compression_metrics": {
            "func": lambda **kw: get_cache_observability()
            .get_compression_metrics(),
            "category": "read",
            "description": "Get compression metrics",
        },
    }


_CACHE_DISPATCH = (
    {op: entry['func'] for op, entry in _build_dispatch_dict().items()}
    if _CACHE_AVAILABLE else {}
)


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """Route cache operation requests using Static DDS.

    Args:
        operation: Cache operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Cache interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    validate_module_available("cache", _CACHE_AVAILABLE, _CACHE_IMPORT_ERROR)

    if operation not in _CACHE_DISPATCH:
        raise UnknownOperationError(
            "cache",
            operation,
            list(_CACHE_DISPATCH.keys()),
        )

    # Custom validation for specific operations
    key_operations = ["get", "set", "exists", "delete", "pop", "touch", "increment"]
    if operation in key_operations:
        _validate_key_param(kwargs, operation)

    if operation == "set":
        _validate_set_params(kwargs)
    elif operation == "update":
        if "items" not in kwargs:
            raise ValueError("cache.update requires 'items' parameter")
        if not isinstance(kwargs["items"], dict):
            raise ValueError("cache.update 'items' parameter must be a dict")
    elif operation == "increment":
        if "delta" in kwargs and not isinstance(kwargs["delta"], int):
            raise ValueError("cache.increment 'delta' parameter must be an int")

    func = _CACHE_DISPATCH[operation]
    return func(**kwargs)


def list_cache_operations() -> list[str]:
    """List all available cache operations."""
    return list(_CACHE_DISPATCH.keys())


__all__ = [
    "execute_cache_operation",
    "list_cache_operations",
]
