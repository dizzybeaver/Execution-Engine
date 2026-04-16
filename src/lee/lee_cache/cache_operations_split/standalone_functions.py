"""cache_operations_split/standalone_functions.py

Singleton accessor for cache operations.
"""

from __future__ import annotations

import threading

from lee.lee_cache.cache_operations_split.models import _get_gateway
from lee.lee_cache.cache_operations_split.lugs_operations import LUGSIntegratedCacheOperations
from lee.lee_utility.debug_logging_helper import DebugLoggingHelper
from lee.gateway import execute_operation, GatewayInterface
from lee.gateway.gateway_core import generate_correlation_id

# Module-level singleton
_cache_instance = None
_cache_lock = threading.Lock()
_module_debug_helper = DebugLoggingHelper(scope="CACHE")

def _get_cache_instance(correlation_id: str = None, **_kwargs) -> LUGSIntegratedCacheOperations:
    """Get or create cache singleton instance via SINGLETON interface."""
    # SUGA-ISP compliance - lazy load gateway
    _GatewayInterface, _execute_operation = _get_gateway()

    if correlation_id is None:
        # time and random imported at module level
        correlation_id = generate_correlation_id("cache")

    # Set up module debug helper
    if _execute_operation and _GatewayInterface:
        _module_debug_helper.set_gateway(_execute_operation, _GatewayInterface)

    # Log start
    _module_debug_helper.log_operation_start(correlation_id, "_get_cache_instance")

    # Get timing context
    timing_ctx = _module_debug_helper.timing_context(correlation_id, "_get_cache_instance")

    with timing_ctx:
        try:
            # pylint: disable=global-statement
            # Singleton pattern requires global access
            global _cache_instance

            # Try gateway-based singleton first
            if _execute_operation and _GatewayInterface:
                try:
                    manager = _execute_operation(_GatewayInterface.SINGLETON, "get",
                                               name="cache_manager")
                    if manager is None:
                        manager = LUGSIntegratedCacheOperations(correlation_id=correlation_id)
                        _execute_operation(_GatewayInterface.SINGLETON, "set",
                                         name="cache_manager", instance=manager)

                    _module_debug_helper.log_operation_success(correlation_id, "_get_cache_instance",
                                                               using_gateway=True)
                    return manager
                except (ImportError, AttributeError, TypeError, ValueError) as e:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f'(ImportError, AttributeError, TypeError, ValueError) occurred: {e}',
                            corr_id=None
                        )
                    except (ImportError, AttributeError, RuntimeError):
                        pass  # Gateway not available

            # Fallback to module-level singleton
            with _cache_lock:
                if _cache_instance is None:
                    _cache_instance = LUGSIntegratedCacheOperations(correlation_id=correlation_id)

            _module_debug_helper.log_operation_success(correlation_id, "_get_cache_instance",
                                                       using_gateway=False, using_fallback=True)
            return _cache_instance
        except (ValueError, TypeError, AttributeError, RuntimeError) as e:
            # Safe debug log for error
            pass
            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="CACHE",
                                     message="_get_cache_instance failed",
                                     error_type=type(e).__name__, error=str(e))
                except (AttributeError, TypeError, ValueError):
                    # Optional dependency - continue if unavailable
                    ...
            raise
