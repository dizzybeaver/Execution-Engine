"""
gateway_wrappers_singleton.py - SINGLETON Interface Wrappers
Version: 2025.11.20.01
Description: Convenience wrappers for SINGLETON interface operations

CHANGELOG:
- 2025.11.20.01: CRITICAL FIX - Added missing singleton_register function
  - ADDED: singleton_register as alias for singleton_set
  - Fixes import error: "cannot import name 'singleton_register' from 'gateway'"
  - Used by logging_manager.py and singleton_core.py

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation
# NEW: Add debug system for exact failure point identification
from debug import debug_log, debug_timing, generate_correlation_id


# ===== SINGLETON OPERATIONS =====

def singleton_get(key: str, correlation_id: str = None) -> Any:
    """Get singleton instance."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_get called", key=key)

    with debug_timing(correlation_id, "SINGLETON", "singleton_get", key=key):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'get', name=key)
            debug_log(correlation_id, "SINGLETON", "singleton_get completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_get failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_set(key: str, instance: Any, correlation_id: str = None) -> None:
    """Set singleton instance."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_set called", key=key, instance_type=type(instance).__name__)

    with debug_timing(correlation_id, "SINGLETON", "singleton_set", key=key):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'set', name=key, instance=instance)
            debug_log(correlation_id, "SINGLETON", "singleton_set completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_set failed", error_type=type(e).__name__, error=str(e))
            raise


# ADDED: Missing function that was causing import errors
def singleton_register(key: str, instance: Any, correlation_id: str = None) -> None:
    """
    Register singleton instance (alias for singleton_set).

    This function provides semantic naming for singleton registration
    while maintaining compatibility with code that imports singleton_register.

    Args:
        key: Singleton name
        instance: Instance to register
    """
    singleton_set(key, instance, correlation_id)


def singleton_has(key: str, correlation_id: str = None) -> bool:
    """Check if singleton exists."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_has called", key=key)

    with debug_timing(correlation_id, "SINGLETON", "singleton_has", key=key):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'has', name=key)
            debug_log(correlation_id, "SINGLETON", "singleton_has completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_has failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_delete(key: str, correlation_id: str = None) -> bool:
    """Delete singleton instance."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_delete called", key=key)

    with debug_timing(correlation_id, "SINGLETON", "singleton_delete", key=key):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'delete', name=key)
            debug_log(correlation_id, "SINGLETON", "singleton_delete completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_delete failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_clear(correlation_id: str = None) -> None:
    """Clear all singletons."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_clear called")

    with debug_timing(correlation_id, "SINGLETON", "singleton_clear"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'clear')
            debug_log(correlation_id, "SINGLETON", "singleton_clear completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_clear failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_stats(correlation_id: str = None) -> Dict[str, Any]:
    """Get singleton statistics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_stats called")

    with debug_timing(correlation_id, "SINGLETON", "singleton_stats"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'stats')
            debug_log(correlation_id, "SINGLETON", "singleton_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_get_stats(correlation_id: str = None) -> Dict[str, Any]:
    """Get singleton statistics (alias for singleton_stats)."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_get_stats called")

    with debug_timing(correlation_id, "SINGLETON", "singleton_get_stats"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'get_stats')
            debug_log(correlation_id, "SINGLETON", "singleton_get_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_get_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def singleton_reset(correlation_id: str = None) -> bool:
    """Reset SINGLETON manager state (lifecycle management)."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "singleton_reset called")

    with debug_timing(correlation_id, "SINGLETON", "singleton_reset"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'reset')
            debug_log(correlation_id, "SINGLETON", "singleton_reset completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "singleton_reset failed", error_type=type(e).__name__, error=str(e))
            raise


# ===== MEMORY MONITORING OPERATIONS =====

def get_memory_stats(correlation_id: str = None) -> Dict[str, Any]:
    """Get current memory statistics."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "get_memory_stats called")

    with debug_timing(correlation_id, "SINGLETON", "get_memory_stats"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'get_memory_stats')
            debug_log(correlation_id, "SINGLETON", "get_memory_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "get_memory_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def get_comprehensive_memory_stats(correlation_id: str = None) -> Dict[str, Any]:
    """Get comprehensive memory statistics including GC info."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "get_comprehensive_memory_stats called")

    with debug_timing(correlation_id, "SINGLETON", "get_comprehensive_memory_stats"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'get_comprehensive_memory_stats')
            debug_log(correlation_id, "SINGLETON", "get_comprehensive_memory_stats completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "get_comprehensive_memory_stats failed", error_type=type(e).__name__, error=str(e))
            raise


def check_lambda_memory_compliance(correlation_id: str = None) -> Dict[str, Any]:
    """Check if memory usage is within Lambda 128MB limit."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "check_lambda_memory_compliance called")

    with debug_timing(correlation_id, "SINGLETON", "check_lambda_memory_compliance"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'check_lambda_memory_compliance')
            debug_log(correlation_id, "SINGLETON", "check_lambda_memory_compliance completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "check_lambda_memory_compliance failed", error_type=type(e).__name__, error=str(e))
            raise


def force_memory_cleanup(correlation_id: str = None) -> Dict[str, Any]:
    """Force aggressive memory cleanup."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "force_memory_cleanup called")

    with debug_timing(correlation_id, "SINGLETON", "force_memory_cleanup"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'force_memory_cleanup')
            debug_log(correlation_id, "SINGLETON", "force_memory_cleanup completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "force_memory_cleanup failed", error_type=type(e).__name__, error=str(e))
            raise


def optimize_memory(correlation_id: str = None) -> Dict[str, Any]:
    """Optimize memory usage with multi-strategy approach."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "optimize_memory called")

    with debug_timing(correlation_id, "SINGLETON", "optimize_memory"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'optimize_memory')
            debug_log(correlation_id, "SINGLETON", "optimize_memory completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "optimize_memory failed", error_type=type(e).__name__, error=str(e))
            raise


def force_comprehensive_memory_cleanup(correlation_id: str = None) -> Dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "force_comprehensive_memory_cleanup called")

    with debug_timing(correlation_id, "SINGLETON", "force_comprehensive_memory_cleanup"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'force_comprehensive_memory_cleanup')
            debug_log(correlation_id, "SINGLETON", "force_comprehensive_memory_cleanup completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "force_comprehensive_memory_cleanup failed", error_type=type(e).__name__, error=str(e))
            raise


def emergency_memory_preserve(correlation_id: str = None) -> Dict[str, Any]:
    """Emergency memory preservation for critical situations."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SINGLETON", "emergency_memory_preserve called")

    with debug_timing(correlation_id, "SINGLETON", "emergency_memory_preserve"):
        try:
            result = execute_operation(GatewayInterface.SINGLETON, 'emergency_memory_preserve')
            debug_log(correlation_id, "SINGLETON", "emergency_memory_preserve completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "emergency_memory_preserve failed", error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    # Singleton operations
    'singleton_get',
    'singleton_set',
    'singleton_register',  # ADDED: Export the new function
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'singleton_get_stats',
    'singleton_reset',
    
    # Memory monitoring operations
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
]
