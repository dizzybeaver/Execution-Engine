"""
gateway_wrappers_cache.py
Version: 2025-12-15_1
Purpose: CACHE interface gateway wrappers with comprehensive debug tracing
License: Apache 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation
# NEW: Add debug system for exact failure point identification
from debug import debug_log, debug_timing, generate_correlation_id


def cache_get(key: str, correlation_id: str = None) -> Any:
    """Get cached value."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_get called", key=key)

    with debug_timing(correlation_id, "CACHE", "cache_get", key=key):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'get', key=key)
            debug_log(correlation_id, "CACHE", "cache_get completed", key=key, success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_get failed", key=key, error_type=type(e).__name__, error=str(e))
            raise


def cache_set(key: str, value: Any, ttl: Optional[float] = None, correlation_id: str = None, **kwargs) -> None:
    """Set cached value."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_set called", key=key, ttl=ttl)

    with debug_timing(correlation_id, "CACHE", "cache_set", key=key, ttl=ttl):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl, **kwargs)
            debug_log(correlation_id, "CACHE", "cache_set completed", key=key, success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_set failed", key=key, error_type=type(e).__name__, error=str(e))
            raise


def cache_exists(key: str, correlation_id: str = None) -> bool:
    """Check if cache key exists."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_exists called", key=key)

    with debug_timing(correlation_id, "CACHE", "cache_exists", key=key):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'exists', key=key)
            debug_log(correlation_id, "CACHE", "cache_exists completed", key=key, success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_exists failed", key=key, error_type=type(e).__name__, error=str(e))
            raise


def cache_delete(key: str, correlation_id: str = None) -> bool:
    """Delete cache key."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_delete called", key=key)

    with debug_timing(correlation_id, "CACHE", "cache_delete", key=key):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'delete', key=key)
            debug_log(correlation_id, "CACHE", "cache_delete completed", key=key, success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_delete failed", key=key, error_type=type(e).__name__, error=str(e))
            raise


def cache_clear(correlation_id: str = None) -> None:
    """Clear all cache."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_clear called")

    with debug_timing(correlation_id, "CACHE", "cache_clear"):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'clear')
            debug_log(correlation_id, "CACHE", "cache_clear completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_clear failed", error_type=type(e).__name__, error=str(e))
            raise


def cache_stats(correlation_id: str = None) -> Dict[str, Any]:
    """Get cache statistics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CACHE", "cache_stats called")

    with debug_timing(correlation_id, "CACHE", "cache_stats"):
        try:
            result = execute_operation(GatewayInterface.CACHE, 'get_stats')
            debug_log(correlation_id, "CACHE", "cache_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CACHE", "cache_stats failed", error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
]

# EOF
