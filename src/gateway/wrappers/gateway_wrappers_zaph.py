"""
gateway_wrappers_zaph.py
Version: 2025-12-14_1
Purpose: Gateway wrappers for ZAPH (Zero-Abstraction Path for Hot operations) interface
"""

from typing import Dict, Any, Optional, Callable, List


def zaph_track_operation(
    operation_key: str,
    duration_ms: float,
    source_module: Optional[str] = None,
    correlation_id: str = "track"
) -> Any:
    """Track operation for heat detection."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'track_operation',
        operation_key=operation_key,
        duration_ms=duration_ms,
        source_module=source_module,
        correlation_id=correlation_id
    )


def zaph_execute(
    operation_key: str,
    func: Callable,
    *args,
    correlation_id: str = "execute",
    **kwargs
) -> Any:
    """Execute operation with fast-path optimization."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'execute',
        operation_key=operation_key,
        func=func,
        args=args,
        func_kwargs=kwargs,
        correlation_id=correlation_id
    )


def zaph_register(
    operation_key: str,
    fast_func: Callable,
    source_module: Optional[str] = None,
    correlation_id: str = "register"
) -> None:
    """Register fast path for operation."""
    import interface.interface_zaph
    interface.interface_zaph.execute_zaph_operation(
        'register',
        operation_key=operation_key,
        fast_func=fast_func,
        source_module=source_module,
        correlation_id=correlation_id
    )


def zaph_get(operation_key: str, correlation_id: str = "get") -> Optional[Callable]:
    """Get fast path if available."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'get',
        operation_key=operation_key,
        correlation_id=correlation_id
    )


def zaph_is_hot(operation_key: str, correlation_id: str = "is_hot") -> bool:
    """Check if operation is hot."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'is_hot',
        operation_key=operation_key,
        correlation_id=correlation_id
    )


def zaph_should_protect(module_name: str, correlation_id: str = "protect") -> bool:
    """Check if module should be protected."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'should_protect',
        module_name=module_name,
        correlation_id=correlation_id
    )


def zaph_heat_level(operation_key: str, correlation_id: str = "heat") -> Any:
    """Get operation heat level."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'heat_level',
        operation_key=operation_key,
        correlation_id=correlation_id
    )


def zaph_stats(correlation_id: str = "stats") -> Dict[str, Any]:
    """Get fast path statistics."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'stats',
        correlation_id=correlation_id
    )


def zaph_hot_operations(limit: int = 10, correlation_id: str = "hot_ops") -> List:
    """Get most frequently called operations."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'hot_operations',
        limit=limit,
        correlation_id=correlation_id
    )


def zaph_cached_operations(correlation_id: str = "cached") -> List:
    """Get operations in cache."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'cached_operations',
        correlation_id=correlation_id
    )


def zaph_configure(
    enabled: Optional[bool] = None,
    cache_size: Optional[int] = None,
    warm_threshold: Optional[int] = None,
    hot_threshold: Optional[int] = None,
    critical_threshold: Optional[int] = None,
    correlation_id: str = "configure"
) -> Dict[str, Any]:
    """Configure fast path."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'configure',
        enabled=enabled,
        cache_size=cache_size,
        warm_threshold=warm_threshold,
        hot_threshold=hot_threshold,
        critical_threshold=critical_threshold,
        correlation_id=correlation_id
    )


def zaph_config(correlation_id: str = "get_config") -> Dict[str, Any]:
    """Get configuration."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'config',
        correlation_id=correlation_id
    )


def zaph_prewarm(operation_keys: List, correlation_id: str = "prewarm") -> int:
    """Prewarm cache."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'prewarm',
        operation_keys=operation_keys,
        correlation_id=correlation_id
    )


def zaph_prewarm_common(correlation_id: str = "prewarm_common") -> int:
    """Prewarm common operations."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'prewarm_common',
        correlation_id=correlation_id
    )


def zaph_clear(correlation_id: str = "clear") -> None:
    """Clear cache."""
    import interface.interface_zaph
    interface.interface_zaph.execute_zaph_operation(
        'clear',
        correlation_id=correlation_id
    )


def zaph_reset_counts(correlation_id: str = "reset_counts") -> None:
    """Reset call counts."""
    import interface.interface_zaph
    interface.interface_zaph.execute_zaph_operation(
        'reset_counts',
        correlation_id=correlation_id
    )


def zaph_reset_stats(correlation_id: str = "reset_stats") -> None:
    """Reset statistics."""
    import interface.interface_zaph
    interface.interface_zaph.execute_zaph_operation(
        'reset_stats',
        correlation_id=correlation_id
    )


def zaph_optimize(correlation_id: str = "optimize") -> Dict[str, Any]:
    """Run optimization."""
    import interface.interface_zaph
    return interface.interface_zaph.execute_zaph_operation(
        'optimize',
        correlation_id=correlation_id
    )


__all__ = [
    'zaph_track_operation',
    'zaph_execute',
    'zaph_register',
    'zaph_get',
    'zaph_is_hot',
    'zaph_should_protect',
    'zaph_heat_level',
    'zaph_stats',
    'zaph_hot_operations',
    'zaph_cached_operations',
    'zaph_configure',
    'zaph_config',
    'zaph_prewarm',
    'zaph_prewarm_common',
    'zaph_clear',
    'zaph_reset_counts',
    'zaph_reset_stats',
    'zaph_optimize',
]

# EOF
