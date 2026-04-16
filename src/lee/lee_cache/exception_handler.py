"""lee_cache/exception_handler.py
Version: 2026-04-01_2
Purpose: Specific exception handling helper for LEE cache operations
License: Apache 2.0

Provides standardized exception handling for nested gateway operations
in the cache system using the UnifiedErrorHandler base with cache-specific
categorization rules.

Exception Categories:
1. Gateway Unavailable: ImportError, AttributeError - acceptable for standalone usage
2. Cache Operations: CacheError, ConnectionError, TimeoutError - expected failures
3. Invalid Input: ValueError, TypeError, KeyError - parameter validation errors
4. Runtime Issues: RuntimeError, MemoryError - system-level errors
5. Unexpected Errors: Generic Exception - fallback for unknown issues

Patterns Provided:
- CacheExceptionHandler: Base class for cache-specific exception handling
- handle_cache_exception: Convenience function for exception handling
- cache_exception_handler: Decorator for automatic exception handling
- CacheExceptionContext: Context manager for exception handling
"""

from functools import wraps
from typing import Any
from collections.abc import Callable

try:
    from lee.gateway import GatewayInterface, execute_operation
    from lee.lee_utility.error_handler import UnifiedErrorHandler
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    GatewayInterface = None
    execute_operation = None
    UnifiedErrorHandler = object


class CacheExceptionHandler(UnifiedErrorHandler):
    """Standardized exception handling for nested cache operations.

    Extends UnifiedErrorHandler with cache-specific categorization rules.
    """

    # Cache-specific categorization rules
    _CACHE_CATEGORIZATION_RULES = {
        "Gateway Unavailable": ([ImportError, AttributeError], "debug"),
        "Cache Operation": ([ConnectionError, TimeoutError], "error"),
        "Invalid Input": ([ValueError, TypeError, KeyError], "warning"),
        "Runtime Error": ([RuntimeError, MemoryError], "critical"),
        "Unexpected Error": ([Exception], "warning"),
    }

    def __init__(self, operation_name: str = "cache_operation", correlation_id: str = None):
        """Initialize exception handler.

        Args:
            operation_name: Name of the cache operation for logging
            correlation_id: Request correlation ID for tracing
        """
        super().__init__(
            operation_name=operation_name,
            correlation_id=correlation_id,
            scope="CACHE_SYSTEM",
            categorization_rules=self._CACHE_CATEGORIZATION_RULES
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def handle_nested_exception(
        self,
        exception: Exception,
        context: str = "",
        gateway_interface: Any = None,
        execute_op: Any = None
    ) -> None:
        """Handle exception in nested cache operation with specific error types.

        This method provides specific exception handling for nested gateway
        operations, replacing generic Exception catching with targeted error
        diagnosis and recovery.

        Args:
            exception: The exception to handle
            context: Additional context about where error occurred
            gateway_interface: Gateway interface for logging (optional)
            execute_op: Execute operation function for logging (optional)

        Raises:
            Re-raises the original exception after logging
        """
        if gateway_interface is None:
            gateway_interface = GatewayInterface
        if execute_op is None:
            execute_op = execute_operation

        # Category 1: Gateway Unavailable (acceptable for standalone usage)
        if isinstance(exception, (ImportError, AttributeError)):
            # Gateway not available or missing method - acceptable
            return

        # Use base class handling for all other categories
        # pylint: disable=no-member
        super().handle_exception(
            exception=exception,
            context=context,
            gateway_interface=gateway_interface,
            execute_op=execute_op,
            re_raise=True
        )


# pylint: disable=too-many-arguments,too-many-positional-arguments
def handle_cache_exception(
    exception: Exception,
    operation_name: str = "cache_operation",
    context: str = "",
    correlation_id: str = None,
    gateway_interface: Any = None,
    execute_op: Any = None
) -> None:
    """Convenience function for handling cache exceptions.

    This is a drop-in replacement for the TODO exception handling pattern
    throughout the cache system. Usage:

        except Exception as e:
            handle_cache_exception(
                exception=e,
                operation_name="get",
                context="Primary cache lookup failed",
                correlation_id=corr_id
            )
            raise

    Args:
        exception: The exception to handle
        operation_name: Name of the cache operation for logging
        context: Additional context about where error occurred
        correlation_id: Request correlation ID for tracing
        gateway_interface: Gateway interface for logging (optional)
        execute_op: Execute operation function for logging (optional)

    Raises:
        Re-raises the original exception after logging
    """
    handler = CacheExceptionHandler(
        operation_name=operation_name,
        correlation_id=correlation_id
    )
    handler.handle_nested_exception(
        exception=exception,
        context=context,
        gateway_interface=gateway_interface,
        execute_op=execute_op
    )


class CacheExceptionContext:
    """Context manager for automatic exception handling in cache operations.

    Usage:
        with CacheExceptionContext("get", correlation_id="abc123"):
            result = cache.get(key)
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        operation_name: str = "cache_operation",
        context: str = "",
        correlation_id: str = None,
        gateway_interface: Any = None,
        execute_op: Any = None
    ):
        """Initialize exception context.

        Args:
            operation_name: Name of the cache operation for logging
            context: Additional context about where error occurred
            correlation_id: Request correlation ID for tracing
            gateway_interface: Gateway interface for logging (optional)
            execute_op: Execute operation function for logging (optional)
        """
        self.operation_name = operation_name
        self.context = context
        self.correlation_id = correlation_id
        self.gateway_interface = gateway_interface
        self.execute_op = execute_op
        self._handler = None

    def __enter__(self) -> "CacheExceptionContext":
        """Enter context, create handler instance."""
        self._handler = CacheExceptionHandler(
            operation_name=self.operation_name,
            correlation_id=self.correlation_id
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit context, handle exception if one occurred."""
        if exc_type is None:
            return False

        if self._handler is None:
            return False

        # Handle gateway unavailable exceptions (ImportError, AttributeError)
        # Suppress these exceptions - they're acceptable for standalone usage
        if isinstance(exc_val, (ImportError, AttributeError)):
            return True  # Suppress exception

        # Handle all other exceptions
        try:
            self._handler.handle_nested_exception(
                exception=exc_val,
                context=self.context,
                gateway_interface=self.gateway_interface,
                execute_op=self.execute_op
            )
        except RuntimeError as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'Exception occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

        return False  # Re-raise the original exception


def cache_exception_handler(
    operation_name: str = None,
    context: str = "",
    correlation_id: str = None,
    gateway_interface: Any = None,
    execute_op: Any = None
) -> Callable:
    """Decorator for automatic exception handling in cache functions.

    Usage:
        @cache_exception_handler(operation_name="get")
        def get(key, correlation_id=None):
            ...

        # Or with dynamic operation name from function name
        @cache_exception_handler()
        def delete(key, correlation_id=None):
            ...

    Args:
        operation_name: Name of the operation for logging (defaults to function name)
        context: Additional context about where error occurred
        correlation_id: Request correlation ID for tracing (from kwargs if None)
        gateway_interface: Gateway interface for logging (optional)
        execute_op: Execute operation function for logging (optional)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            corr_id = correlation_id or kwargs.get("correlation_id")

            try:
                return func(*args, **kwargs)
            except ImportError:
                # Gateway unavailable - suppress exception
                return None
            except AttributeError:
                # Gateway unavailable - suppress exception
                return None
            except Exception as e:
                # For all other exceptions, try to log but always re-raise
                try:
                    handler = CacheExceptionHandler(
                        operation_name=op_name,
                        correlation_id=corr_id
                    )
                    handler.handle_nested_exception(
                        exception=e,
                        context=context,
                        gateway_interface=gateway_interface,
                        execute_op=execute_op
                    )
                except (KeyError, AttributeError, RuntimeError):
                    # If logging fails, still re-raise the original exception
                    pass
                raise

        return wrapper
    return decorator


__all__ = [
    "CacheExceptionHandler",
    "handle_cache_exception",
    "CacheExceptionContext",
    "cache_exception_handler",
]
