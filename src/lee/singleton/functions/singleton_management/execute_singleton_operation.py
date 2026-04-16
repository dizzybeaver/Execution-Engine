"""singleton/functions/singleton_management/execute_singleton_operation.py
Version: 2025.12.13.01
Description: Universal singleton operation executor with error handling

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


from lee.gateway import GatewayInterface, execute_operation
from lee.singleton.enums.SingletonOperation import SingletonOperation
from lee.singleton.singleton_manager import get_singleton_manager


def _execute_and_log_get(manager, correlation_id, **kwargs):
    """Execute GET operation with logging."""
    result = manager.get(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="GET")
    return result


def _execute_and_log_set(manager, correlation_id, **kwargs):
    """Execute SET operation with logging."""
    result = manager.set(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="SET")
    return result


def _execute_and_log_has(manager, correlation_id, **kwargs):
    """Execute HAS operation with logging."""
    result = manager.has(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="HAS")
    return result


def _execute_and_log_delete(manager, correlation_id, **kwargs):
    """Execute DELETE operation with logging."""
    result = manager.delete(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="DELETE")
    return result


def _execute_and_log_clear(manager, correlation_id, **kwargs):
    """Execute CLEAR operation with logging."""
    result = manager.clear(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="CLEAR")
    return result


def _execute_and_log_get_stats(manager, correlation_id, **kwargs):
    """Execute GET_STATS operation with logging."""
    result = manager.get_stats(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="GET_STATS")
    return result


def _execute_and_log_reset(manager, correlation_id, **kwargs):
    """Execute RESET operation with logging."""
    result = manager.reset(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="RESET")
    return result


def _execute_and_log_reset_all(manager, correlation_id, **kwargs):
    """Execute RESET_ALL operation with logging."""
    result = manager.reset_all(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="RESET_ALL")
    return result


def _execute_and_log_exists(manager, correlation_id, **kwargs):
    """Execute EXISTS operation with logging."""
    result = manager.exists(correlation_id=correlation_id, **kwargs)
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="execute_singleton_operation completed",
                     success=True, operation="EXISTS")
    return result


# Dictionary dispatch for singleton operations (O(1) lookup)
_SINGLETON_OPERATION_HANDLERS = {
    SingletonOperation.GET: _execute_and_log_get,
    SingletonOperation.SET: _execute_and_log_set,
    SingletonOperation.HAS: _execute_and_log_has,
    SingletonOperation.DELETE: _execute_and_log_delete,
    SingletonOperation.CLEAR: _execute_and_log_clear,
    SingletonOperation.GET_STATS: _execute_and_log_get_stats,
    SingletonOperation.RESET: _execute_and_log_reset,
    SingletonOperation.RESET_ALL: _execute_and_log_reset_all,
    SingletonOperation.EXISTS: _execute_and_log_exists,
}


def execute_singleton_operation(operation: SingletonOperation,
                                correlation_id: str = None, **kwargs):
    """Universal singleton operation executor with error handling.

    Args:
        operation: SingletonOperation enum value (GET, SET, HAS, DELETE, CLEAR,
                 GET_STATS, RESET, RESET_ALL, EXISTS)
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional parameters passed to manager method

    Returns:
        Result from manager method

    Raises:
        ValueError: If operation is unknown
        Exception: If operation fails

    Performance: O(1) dictionary lookup instead of O(n) if/elif chain
    """
    with execute_operation(GatewayInterface.DEBUG, "timing",
                          corr_id=correlation_id, scope="SINGLETON",
                          operation="execute_singleton_operation",
                          operation_type=operation.value) as _:
        try:
            manager = get_singleton_manager()

            handler = _SINGLETON_OPERATION_HANDLERS.get(operation)
            if handler is None:
                raise ValueError(f"Unknown singleton operation: {operation}")

            return handler(manager, correlation_id, **kwargs)

        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="SINGLETON",
                             message=f"Operation failed: {e!s}",
                             operation=operation.value, error_type=type(e).__name__)
            raise RuntimeError(f"Singleton operation '{operation.value}' failed: {e}") from e


__all__ = ["execute_singleton_operation"]
