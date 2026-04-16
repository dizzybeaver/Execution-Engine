"""Debug Wrapper Functions

Provides direct access to debug and profiling operations through gateway.
All functions execute via execute_operation(GatewayInterface.DEBUG, ...) internally.

Usage:
    from lee.gateway.wrappers import debug

    # Timing context manager
    with debug.timing(corr_id=corr_id, operation_name="my_operation"):
        # Your code here

    # Log debug messages
    debug.log(message="Operation completed", scope="INTERFACE", corr_id=corr_id)

    # Get profiler statistics
    stats = debug.profiler_get_stats(operation_name="cache_get")
"""

from functools import wraps
from typing import Any, TypeVar, Optional
from collections.abc import Callable

from lee.gateway.gateway_core import GatewayInterface, execute_operation

T = TypeVar('T')

# Context manager for timing operations
class timing:
    """Context manager for timing operations.

    Usage:
        with debug.timing(corr_id=corr_id, operation_name="my_operation"):
            # Your code here
    """

    def __init__(self, corr_id: str, operation_name: str, **kwargs: Any) -> None:
        """Initialize timing context manager.

        Args:
            corr_id: Correlation ID for tracking
            operation_name: Name of operation to time
            **kwargs: Additional keyword arguments
        """
        self.corr_id = corr_id
        self.operation_name = operation_name
        self.extra_kwargs = kwargs

    def __enter__(self) -> "timing":
        """Enter timing context.

        Returns:
            Self for context manager protocol
        """
        execute_operation(
            GatewayInterface.DEBUG,
            "timing",
            corr_id=self.corr_id,
            operation_name=self.operation_name,
            **self.extra_kwargs
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit timing context.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised

        Returns:
            False to propagate exceptions
        """
        # Timing is automatically recorded on exit by the interface
        return False


# Generic debug wrapper for universal instrumentation
def instrumented(operation_name: str, correlation_id: str, scope: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Generic decorator for automatic debug instrumentation of any function.

    This decorator handles the complete debug instrumentation pattern:
    - Timing measurement
    - Success/failure logging
    - Error tracking
    - Automatic correlation ID propagation

    Usage:
        @debug.instrumented(operation_name="my_operation", correlation_id=corr_id, scope="INTERFACE")
        def my_function(arg1, arg2):
            return do_something(arg1, arg2)

        # Or as a function wrapper
        result = debug.instrumented(operation_name="cache_get", correlation_id=corr_id, scope="CACHE")(
            lambda: cache.get(key='test')
        )

    Args:
        operation_name: Name of the operation for timing and logging
        correlation_id: Correlation ID for request tracking
        scope: Optional scope identifier (e.g., "INTERFACE", "CACHE", "SINGLETON")

    Returns:
        Decorator function that wraps the target function with instrumentation
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with timing(corr_id=correlation_id, operation_name=operation_name):
                try:
                    result = func(*args, **kwargs)
                    log(
                        corr_id=correlation_id,
                        message=f"{operation_name} completed",
                        scope=scope,
                        success=True
                    )
                    return result
                except (ValueError, TypeError, KeyError, AttributeError, ImportError, RuntimeError) as e:
                    log(
                        corr_id=correlation_id,
                        message=f"{operation_name} failed",
                        scope=scope,
                        error_type=type(e).__name__,
                        error=str(e)
                    )
                    raise
                except Exception as e:
                    log(
                        corr_id=correlation_id,
                        message=f"{operation_name} failed with unexpected error",
                        scope=scope,
                        error_type=type(e).__name__,
                        error=str(e)
                    )
                    raise

        return wrapper

    return decorator


def execute_with_instrumentation(
    operation_name: str,
    correlation_id: str,
    func: Callable[..., T],
    scope: Optional[str] = None,
    **func_kwargs: Any
) -> T:
    """Execute a function with complete debug instrumentation.

    This is a non-decorator version of instrumented() for direct execution.
    Handles timing, success/failure logging, and error tracking automatically.

    Usage:
        result = debug.execute_with_instrumentation(
            operation_name="singleton_has",
            correlation_id=corr_id,
            func=singleton_generic.has_implementation,
            scope="INTERFACE",
            name="my_singleton",
            correlation_id=corr_id  # Function's own correlation_id param
        )

    Args:
        operation_name: Name of the operation for timing and logging
        correlation_id: Correlation ID for request tracking
        func: Function to execute
        scope: Optional scope identifier (e.g., "INTERFACE", "CACHE", "SINGLETON")
        **func_kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function execution

    Raises:
        Exception: Re-raises any exception from the executed function
    """
    with timing(corr_id=correlation_id, operation_name=operation_name):
        try:
            result = func(**func_kwargs)
            log(
                corr_id=correlation_id,
                message=f"{operation_name} completed",
                scope=scope,
                success=True
            )
            return result
        except (ValueError, TypeError, KeyError, AttributeError, ImportError, RuntimeError) as e:
            log(
                corr_id=correlation_id,
                message=f"{operation_name} failed",
                scope=scope,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise
        except Exception as e:
            log(
                corr_id=correlation_id,
                message=f"{operation_name} failed with unexpected error",
                scope=scope,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise


# Core debug operations
def log(message: str, corr_id: Optional[str] = None, scope: Optional[str] = None, **context: Any) -> None:
    """Log debug message with correlation ID and optional scope.

    Args:
        message: Debug message to log
        corr_id: Correlation ID for tracking
        scope: Optional scope identifier (e.g., "INTERFACE", "CACHE")
        **context: Additional context key-value pairs
    """
    execute_operation(
        GatewayInterface.DEBUG,
        "log",
        corr_id=corr_id,
        message=message,
        scope=scope,
        **context
    )


def generate_trace_id(**kwargs) -> str:
    """Generate unique trace ID for request tracking.

    Returns:
        Unique trace ID string
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "generate_trace_id",
        **kwargs
    )


def set_trace_context(trace_id: str, **context: Any) -> None:
    """Set trace context for debugging.

    Args:
        trace_id: Trace identifier
        **context: Context key-value pairs to store
    """
    execute_operation(
        GatewayInterface.DEBUG,
        "set_trace_context",
        trace_id=trace_id,
        **context
    )


def get_trace_context(trace_id: str, **kwargs) -> dict:
    """Get trace context by trace ID.

    Args:
        trace_id: Trace identifier

    Returns:
        Trace context dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "get_trace_context",
        trace_id=trace_id,
        **kwargs
    )


def clear_trace_context(trace_id: Optional[str] = None, **kwargs) -> None:
    """Clear trace context (specific or all).

    Args:
        trace_id: Optional specific trace ID to clear, or None for all
    """
    execute_operation(
        GatewayInterface.DEBUG,
        "clear_trace_context",
        trace_id=trace_id,
        **kwargs
    )


# Gateway profiler operations
def profiler_get_stats(operation_name: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """Get profiler statistics (p50/p95/p99 timing).

    Args:
        operation_name: Optional specific operation name, or None for all operations

    Returns:
        Dictionary with p50, p95, p99 timing percentiles and count
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "profiler_get_stats",
        operation_name=operation_name,
        **kwargs
    )


def profiler_reset(**kwargs) -> dict[str, Any]:
    """Reset profiler data.

    Returns:
        Confirmation dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "profiler_reset",
        **kwargs
    )


def profiler_get_summary(**kwargs) -> dict[str, Any]:
    """Get profiler summary statistics.

    Returns:
        Summary statistics dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "profiler_get_summary",
        **kwargs
    )


# Call stack tracker operations
def get_call_stack(corr_id: str, **kwargs) -> dict[str, Any]:
    """Get call stack for correlation ID.

    Args:
        corr_id: Correlation ID to look up

    Returns:
        Call stack dictionary with function calls and timings
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "get_call_stack",
        corr_id=corr_id,
        **kwargs
    )


def clear_call_stack(corr_id: str, **kwargs) -> bool:
    """Clear call stack for correlation ID.

    Args:
        corr_id: Correlation ID to clear

    Returns:
        True if successful
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "clear_call_stack",
        corr_id=corr_id,
        **kwargs
    )


def get_call_stack_stats(**kwargs) -> dict[str, Any]:
    """Get call stack tracker statistics.

    Returns:
        Statistics about tracked call stacks
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "get_call_stack_stats",
        **kwargs
    )


def enable_call_tracking(enabled: bool = True, **kwargs) -> bool:
    """Enable or disable call tracking.

    Args:
        enabled: True to enable, False to disable

    Returns:
        Previous state of call tracking
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "enable_call_tracking",
        enabled=enabled,
        **kwargs
    )


# Hot path detector operations
def hot_path_get_top_n(n: int = 10, **kwargs) -> list[dict[str, Any]]:
    """Get top N most-called operations (Pareto analysis).

    Args:
        n: Number of top operations to return (default: 10)

    Returns:
        List of top N operations with call counts
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "hot_path_get_top_n",
        n=n,
        **kwargs
    )


def hot_path_get_distribution(**kwargs) -> dict[str, int]:
    """Get operation call distribution.

    Returns:
        Dictionary mapping operation names to call counts
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "hot_path_get_distribution",
        **kwargs
    )


def hot_path_get_stats(**kwargs) -> dict[str, Any]:
    """Get hot path detector statistics.

    Returns:
        Statistics about operation call patterns
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "hot_path_get_stats",
        **kwargs
    )


def hot_path_reset(**kwargs) -> dict[str, Any]:
    """Reset hot path detector data.

    Returns:
        Confirmation dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "hot_path_reset",
        **kwargs
    )


# Request tracing operations
def start_trace(correlation_id: str, **kwargs) -> dict[str, Any]:
    """Start a new request trace.

    Args:
        correlation_id: Correlation ID for the trace

    Returns:
        Trace initialization dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "start_trace",
        correlation_id=correlation_id,
        **kwargs
    )


def add_trace_step(correlation_id: str, step_name: str, duration_ms: float, success: bool, **kwargs) -> None:
    """Add a step to an existing trace.

    Args:
        correlation_id: Trace correlation ID
        step_name: Name of the step/operation
        duration_ms: Step duration in milliseconds
        success: Whether the step succeeded
    """
    execute_operation(
        GatewayInterface.DEBUG,
        "add_trace_step",
        correlation_id=correlation_id,
        step_name=step_name,
        duration_ms=duration_ms,
        success=success,
        **kwargs
    )


def end_trace(correlation_id: str, **kwargs) -> bool:
    """End a request trace.

    Args:
        correlation_id: Trace correlation ID to end

    Returns:
        True if successful
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "end_trace",
        correlation_id=correlation_id,
        **kwargs
    )


def analyze_trace(correlation_id: str, **kwargs) -> dict[str, Any]:
    """Analyze a completed trace.

    Args:
        correlation_id: Trace correlation ID to analyze

    Returns:
        Analysis results with bottlenecks and insights
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "analyze_trace",
        correlation_id=correlation_id,
        **kwargs
    )


def get_trace(correlation_id: str, **kwargs) -> Optional[dict[str, Any]]:
    """Get trace by correlation ID.

    Args:
        correlation_id: Trace correlation ID

    Returns:
        Trace dictionary or None if not found
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "get_trace",
        correlation_id=correlation_id,
        **kwargs
    )


def get_all_traces(**kwargs) -> list[dict[str, Any]]:
    """Get all stored traces.

    Returns:
        List of all trace dictionaries
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "get_all_traces",
        **kwargs
    )


def clear_traces(**kwargs) -> dict[str, Any]:
    """Clear all stored traces.

    Returns:
        Confirmation dictionary
    """
    return execute_operation(
        GatewayInterface.DEBUG,
        "clear_traces",
        **kwargs
    )


__all__ = [
    # Context manager
    'timing',

    # Generic instrumentation
    'instrumented',
    'execute_with_instrumentation',

    # Core debug operations
    'log',
    'generate_trace_id',
    'set_trace_context',
    'get_trace_context',
    'clear_trace_context',

    # Gateway profiler operations
    'profiler_get_stats',
    'profiler_reset',
    'profiler_get_summary',

    # Call stack tracker operations
    'get_call_stack',
    'clear_call_stack',
    'get_call_stack_stats',
    'enable_call_tracking',

    # Hot path detector operations
    'hot_path_get_top_n',
    'hot_path_get_distribution',
    'hot_path_get_stats',
    'hot_path_reset',

    # Request tracing operations
    'start_trace',
    'add_trace_step',
    'end_trace',
    'analyze_trace',
    'get_trace',
    'get_all_traces',
    'clear_traces',
]
