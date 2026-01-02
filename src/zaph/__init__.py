"""
zaph/__init__.py
Version: 2025-12-14_1
Purpose: ZAPH (Zero-Abstraction Path for Hot operations) interface with debug tracing
"""

import os
from typing import Dict, Any, Optional, Callable, List

# Debug configuration
_DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
_ZAPH_DEBUG = _DEBUG_MODE and os.environ.get('ZAPH_DEBUG_MODE', 'true').lower() == 'true'


def _debug_log(corr_id: str, message: str, **context):
    """Log debug message if ZAPH_DEBUG_MODE enabled."""
    if _ZAPH_DEBUG:
        ctx_str = ', '.join(f'{k}={v}' for k, v in context.items())
        print(f"[ZAPH:{corr_id}] {message} | {ctx_str}")


# Lazy import of core
_fast_path_instance = None


def _get_instance():
    """Get fast path instance with lazy loading and debug trace."""
    global _fast_path_instance
    if _fast_path_instance is None:
        from zaph.zaph_core import LUGSAwareFastPath
        _fast_path_instance = LUGSAwareFastPath()
        if _ZAPH_DEBUG:
            print("[ZAPH:INIT] LUGSAwareFastPath instance created")
    return _fast_path_instance


def track_operation(
    operation_key: str,
    duration_ms: float,
    source_module: Optional[str] = None,
    correlation_id: str = "track"
) -> Any:
    """Track operation for heat detection."""
    _debug_log(correlation_id, "track_operation", 
              operation=operation_key, duration_ms=duration_ms, module=source_module)
    instance = _get_instance()
    result = instance.track_operation(operation_key, duration_ms, source_module)
    _debug_log(correlation_id, "track_operation_complete", heat_level=result.value)
    return result


def execute_fast_path(
    operation_key: str,
    func: Callable,
    *args,
    correlation_id: str = "execute",
    **kwargs
) -> Any:
    """Execute operation with fast-path optimization."""
    _debug_log(correlation_id, "execute_fast_path", operation=operation_key)
    instance = _get_instance()
    result = instance.execute_fast_path(operation_key, func, *args, **kwargs)
    _debug_log(correlation_id, "execute_fast_path_complete")
    return result


def register_fast_path(
    operation_key: str,
    fast_func: Callable,
    source_module: Optional[str] = None,
    correlation_id: str = "register"
) -> None:
    """Register fast path for operation."""
    _debug_log(correlation_id, "register_fast_path", 
              operation=operation_key, module=source_module)
    instance = _get_instance()
    instance.register_fast_path(operation_key, fast_func, source_module)
    _debug_log(correlation_id, "register_fast_path_complete")


def get_fast_path(operation_key: str, correlation_id: str = "get") -> Optional[Callable]:
    """Get fast path if available."""
    _debug_log(correlation_id, "get_fast_path", operation=operation_key)
    instance = _get_instance()
    result = instance.get_fast_path(operation_key)
    _debug_log(correlation_id, "get_fast_path_complete", found=result is not None)
    return result


def is_hot_operation(operation_key: str, correlation_id: str = "is_hot") -> bool:
    """Check if operation is hot."""
    instance = _get_instance()
    result = instance.is_hot_operation(operation_key)
    _debug_log(correlation_id, "is_hot_operation", operation=operation_key, is_hot=result)
    return result


def should_protect_module(module_name: str, correlation_id: str = "protect") -> bool:
    """Check if module should be protected."""
    instance = _get_instance()
    result = instance.should_protect_module(module_name)
    _debug_log(correlation_id, "should_protect_module", module=module_name, protected=result)
    return result


def get_heat_level(operation_key: str, correlation_id: str = "heat") -> Any:
    """Get operation heat level."""
    instance = _get_instance()
    result = instance.get_heat_level(operation_key)
    _debug_log(correlation_id, "get_heat_level", operation=operation_key, level=result.value)
    return result


def get_fast_path_stats(correlation_id: str = "stats") -> Dict[str, Any]:
    """Get fast path statistics."""
    _debug_log(correlation_id, "get_fast_path_stats")
    instance = _get_instance()
    result = instance.get_stats()
    _debug_log(correlation_id, "get_fast_path_stats_complete", 
              operations=result.get('total_operations', 0),
              hit_rate=result.get('hit_rate_percent', 0))
    return result


def get_hot_operations(limit: int = 10, correlation_id: str = "hot_ops") -> List:
    """Get most frequently called operations."""
    _debug_log(correlation_id, "get_hot_operations", limit=limit)
    instance = _get_instance()
    result = instance.get_hot_operations(limit)
    _debug_log(correlation_id, "get_hot_operations_complete", count=len(result))
    return result


def get_cached_operations(correlation_id: str = "cached") -> List:
    """Get operations in cache."""
    _debug_log(correlation_id, "get_cached_operations")
    instance = _get_instance()
    result = instance.get_cached_operations()
    _debug_log(correlation_id, "get_cached_operations_complete", count=len(result))
    return result


def configure_fast_path(
    enabled: Optional[bool] = None,
    cache_size: Optional[int] = None,
    warm_threshold: Optional[int] = None,
    hot_threshold: Optional[int] = None,
    critical_threshold: Optional[int] = None,
    correlation_id: str = "configure"
) -> Dict[str, Any]:
    """Configure fast path."""
    _debug_log(correlation_id, "configure_fast_path",
              enabled=enabled, cache_size=cache_size)
    instance = _get_instance()
    result = instance.configure(enabled, cache_size, warm_threshold, hot_threshold, critical_threshold)
    _debug_log(correlation_id, "configure_fast_path_complete")
    return result


def get_fast_path_config(correlation_id: str = "get_config") -> Dict[str, Any]:
    """Get configuration."""
    instance = _get_instance()
    result = instance.get_config()
    _debug_log(correlation_id, "get_fast_path_config", 
              enabled=result.get('enabled'), cache_size=result.get('cache_size_limit'))
    return result


def prewarm_cache(operation_keys: List, correlation_id: str = "prewarm") -> int:
    """Prewarm cache."""
    _debug_log(correlation_id, "prewarm_cache", key_count=len(operation_keys))
    instance = _get_instance()
    result = instance.prewarm(operation_keys)
    _debug_log(correlation_id, "prewarm_cache_complete", prewarmed=result)
    return result


def prewarm_common_operations(correlation_id: str = "prewarm_common") -> int:
    """Prewarm common operations."""
    _debug_log(correlation_id, "prewarm_common_operations")
    instance = _get_instance()
    result = instance.prewarm_common()
    _debug_log(correlation_id, "prewarm_common_operations_complete", prewarmed=result)
    return result


def clear_fast_path_cache(correlation_id: str = "clear") -> None:
    """Clear cache."""
    _debug_log(correlation_id, "clear_fast_path_cache")
    instance = _get_instance()
    instance.clear_cache()
    _debug_log(correlation_id, "clear_fast_path_cache_complete")


def reset_call_counts(correlation_id: str = "reset_counts") -> None:
    """Reset call counts."""
    _debug_log(correlation_id, "reset_call_counts")
    instance = _get_instance()
    instance.reset_call_counts()
    _debug_log(correlation_id, "reset_call_counts_complete")


def reset_stats(correlation_id: str = "reset_stats") -> None:
    """Reset statistics."""
    _debug_log(correlation_id, "reset_stats")
    instance = _get_instance()
    instance.reset_stats()
    _debug_log(correlation_id, "reset_stats_complete")


def optimize_fast_path(correlation_id: str = "optimize") -> Dict[str, Any]:
    """Run optimization."""
    _debug_log(correlation_id, "optimize_fast_path")
    instance = _get_instance()
    result = instance.optimize()
    _debug_log(correlation_id, "optimize_fast_path_complete", 
              optimizations=result.get('optimizations', 0))
    return result


# Re-export types
from zaph.zaph_core import OperationHeatLevel, OperationMetrics, LUGSAwareFastPath


__all__ = [
    # Core class
    'LUGSAwareFastPath',
    'OperationHeatLevel',
    'OperationMetrics',
    
    # Public functions
    'track_operation',
    'execute_fast_path',
    'register_fast_path',
    'get_fast_path',
    'is_hot_operation',
    'should_protect_module',
    'get_heat_level',
    'get_fast_path_stats',
    'get_hot_operations',
    'get_cached_operations',
    'configure_fast_path',
    'get_fast_path_config',
    'prewarm_cache',
    'prewarm_common_operations',
    'clear_fast_path_cache',
    'reset_call_counts',
    'reset_stats',
    'optimize_fast_path',
]

# EOF
