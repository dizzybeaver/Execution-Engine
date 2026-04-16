# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-04 - Create gateway operation handler decorator

"""decorators.py

Gateway operation handler decorator for standardizing logging and error handling.

Eliminates repetitive boilerplate code across gateway operations by providing
a decorator that handles:
- Correlation ID generation
- Operation logging (entry/exit/error)
- Timing instrumentation
- Standard error handling
- Exception sanitization

Usage:
    @gateway_operation_handler(GatewayInterface.CACHE, 'cache_get')
    def cache_get_impl(key: str, correlation_id: str = None, **kwargs):
        # Implementation here
        return result
"""

import functools
import os
import random
import time
from typing import Any, Optional
from collections.abc import Callable

from lee.gateway import GatewayInterface, execute_operation


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG mode is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def gateway_operation_handler(
    _gateway_interface: GatewayInterface,
    operation_name: str,
    log_scope: str = "INTERFACE",
    log_params: Optional[list[str]] = None
) -> Callable:
    """Decorator for gateway operation handlers with standard logging and error handling.

    Args:
        gateway_interface: Gateway interface enum value
        operation_name: Name of the operation for logging
        log_scope: Scope for log messages (default: "INTERFACE")
        log_params: List of parameter names to log (e.g., ['key', 'name'])

    Returns:
        Decorated function with standard logging and error handling

    Example:
        @gateway_operation_handler(GatewayInterface.CACHE, 'cache_get', log_params=['key'])
        def cache_get_impl(key: str, correlation_id: str = None, **kwargs):
            # Implementation
            return cache.get(key)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate correlation ID if not provided
            correlation_id = kwargs.get('correlation_id')
            if not correlation_id:
                # Correlation ID - non-security-critical, use fast random
                # Performance: secrets.token_hex() takes ~400ms, random.randbytes() takes ~0.4ms
                correlation_id = f"int_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"
                kwargs['correlation_id'] = correlation_id

            # Log operation entry
            log_args = {
                "corr_id": correlation_id,
                "scope": log_scope,
                "message": f"{operation_name} called"
            }

            # Add specified parameters to log
            if log_params:
                for param in log_params:
                    if param in kwargs:
                        value = kwargs[param]
                        # Sanitize sensitive values
                        if param in ['token', 'password', 'code', 'api_key']:
                            log_args[param] = "***REDACTED***"
                        elif param == "instance" and "instance" in kwargs:
                            log_args["instance_type"] = type(value).__name__
                        else:
                            log_args[param] = str(value)[:100]  # Limit length

            # Only log if debug mode is enabled
            if _is_debug_mode():
                execute_operation(GatewayInterface.DEBUG, "log", **log_args)

            # Execute with timing
            if _is_debug_mode():
                with execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name=operation_name) as _:
                    try:
                        result = func(*args, **kwargs)

                        # Log successful completion
                        execute_operation(GatewayInterface.DEBUG, "log",
                                          corr_id=correlation_id,
                                          scope=log_scope,
                                          message=f"{operation_name} completed",
                                          success=True)
                        return result

                    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError) as e:
                        # Log expected error types
                        execute_operation(GatewayInterface.DEBUG, "log",
                                          corr_id=correlation_id,
                                          scope=log_scope,
                                          message=f"{operation_name} operation error",
                                          error_type=type(e).__name__,
                                          error=str(e)[:200])  # Limit error length
                        raise
            else:
                # Execute without timing/debug overhead
                try:
                    result = func(*args, **kwargs)
                    return result
                except (AttributeError, KeyError, RuntimeError, ValueError, TypeError):
                    raise

                except Exception as e:
                    # Log unexpected errors
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                      message=f"{operation_name} unexpected error",
                                      error_type=type(e).__name__,
                                      error=str(e)[:200])
                    raise

        return wrapper
    return decorator


def cached_gateway_operation(ttl_seconds: int = 300) -> Callable:
    """Decorator for caching gateway operation results.

    Args:
        ttl_seconds: Time-to-live for cached results (default: 5 minutes)

    Returns:
        Decorated function with caching

    Example:
        @cached_gateway_operation(ttl_seconds=60)
        def expensive_operation(param: str):
            # Expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        cache = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from args
            cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))

            # Check cache
            if cache_key in cache:
                cached_result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return cached_result

            # Execute and cache
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())

            return result

        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, backoff_seconds: float = 1.0) -> Callable:
    """Decorator for retrying gateway operations on failure.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_seconds: Initial backoff delay in seconds (default: 1.0)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_on_failure(max_retries=3, backoff_seconds=2.0)
        def flaky_operation():
            # Operation that might fail temporarily
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        time.sleep(backoff_seconds * (2 ** attempt))
                    else:
                        # Final attempt failed, re-raise
                        raise last_exception

        return wrapper
    return decorator


def singleton_operation(operation_type: str) -> Callable:
    """Decorator for singleton operations with standard error handling.

    Args:
        operation_type: Type of singleton operation ('get', 'set', 'has', 'delete')

    Returns:
        Decorated function with singleton-specific handling

    Example:
        @singleton_operation('get')
        def get_singleton(name: str):
            return singletons.get(name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except KeyError:
                # Singleton not found
                return None
            except (RuntimeError, ValueError) as e:
                # Singleton operation error
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                  message=f"Singleton {operation_type} failed",
                                  error=str(e))
                raise

        return wrapper
    return decorator
