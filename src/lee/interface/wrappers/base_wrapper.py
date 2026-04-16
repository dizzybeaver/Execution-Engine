"""base_wrapper.py - Base wrapper utilities for interface wrappers
Version: 2026-04-11_1
Purpose: Consolidate duplicate wrapper code across all interface wrappers
License: Apache 2.0

This module provides common utilities for wrapper functions
to eliminate code duplication.
All interface wrappers should use these utilities instead of duplicating code.

Patterns consolidated:
- Import protection with availability checking
- Correlation ID generation
- Error handling
- Logging
- Module availability tracking
"""

import random
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar
from collections.abc import Callable as CallableType


# ===== CORRELATION ID GENERATION =====


def generate_correlation_id(prefix: str = "corr") -> str:
    """Generate a correlation ID for request tracking.

    Correlation IDs don't need cryptographic randomness, just uniqueness.
    Uses fast random instead of CSPRNG for performance (400ms -> 0.4ms).

    Args:
        prefix: Prefix for the correlation ID (e.g., "cache", "batch")

    Returns:
        A unique correlation ID string

    Examples:
        >>> generate_correlation_id()
        'corr1741234567890_a1b2c3d4'
        >>> generate_correlation_id(prefix="request")
        'request1741234567890_e5f6g7h8'
    """
    timestamp = int(time.time() * 1000)
    # Correlation ID - non-security-critical, use fast random
    random_suffix = random.randbytes(4).hex()
    return f"{prefix}{timestamp}_{random_suffix}"


def with_correlation_id(scope_prefix: str = "wrapper"):
    """Decorator to automatically add correlation IDs to wrapper functions.

    Args:
        scope_prefix: Prefix for correlation ID generation

    Example:
        @with_correlation_id(scope_prefix="cache")
        def cache_get(key: str, correlation_id: str = None) -> Any:
            # If correlation_id is None, it will be auto-generated
            ...

    """

    def decorator(func: CallableType) -> CallableType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Auto-generate correlation_id if not provided
            if "correlation_id" not in kwargs or \
                    kwargs["correlation_id"] is None:
                kwargs["correlation_id"] = \
                    generate_correlation_id(prefix=scope_prefix)

            return func(*args, **kwargs)
        return wrapper
    return decorator


# ===== MODULE IMPORT PROTECTION =====


class ModuleAvailability:
    """Track module availability and import errors for wrapper functions."""

    def __init__(self, module_name: str):
        """Initialize module availability tracker.

        Args:
            module_name: Name of the module for error messages
        """
        self.module_name = module_name
        self.available = False
        self.import_error: Optional[str] = None
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if module is available (override in subclasses)."""

    def check_available(self) -> None:
        """Raise error if module is unavailable.

        Raises:
            RuntimeError: If module is not available
        """
        if not self.available:
            raise RuntimeError(
                f"{self.module_name} unavailable: {self.import_error}"
            )


class DynamicModuleAvailability(ModuleAvailability):
    """Track module availability with dynamic import checking."""

    def __init__(
        self,
        module_name: str,
        import_func: Callable[[], bool]
    ):
        """Initialize with dynamic import function.

        Args:
            module_name: Name of the module for error messages
            import_func: Function that attempts import and returns
                         True if successful
        """
        self._import_func = import_func
        super().__init__(module_name)

    def _check_availability(self) -> None:
        """Check module availability by calling import function."""
        try:
            self.available = self._import_func()
        except ImportError as e:
            self.available = False
            self.import_error = str(e)


# ===== WRAPPER FUNCTION FACTORY =====

F = TypeVar('F', bound=CallableType)


def create_simple_wrapper(
    operation_name: str,
    implementation_func: CallableType,
    availability_checker: Optional[ModuleAvailability] = None,
    scope_prefix: str = "wrapper"
) -> CallableType:
    """Create a simple wrapper function with standard error handling.

    Args:
        operation_name: Name of the operation (e.g., 'cache_get')
        implementation_func: Function that implements the operation
        availability_checker: Optional module availability checker
        scope_prefix: Prefix for correlation ID generation

    Returns:
        Wrapper function with standard error handling

    Example:
        def my_implementation(key: str, correlation_id: str = None) -> Any:
            return get_value(key)

        cache_get = create_simple_wrapper(
            operation_name="cache_get",
            implementation_func=my_implementation,
            availability_checker=cache_availability,
            scope_prefix="cache"
        )
    """
    @with_correlation_id(scope_prefix=scope_prefix)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if availability_checker:
            availability_checker.check_available()

        return implementation_func(*args, **kwargs)

    wrapper.__name__ = operation_name
    wrapper.__doc__ = f"{operation_name} wrapper function"
    return wrapper


# ===== LEGACY WRAPPER CREATION =====


def create_legacy_wrapper(
    new_wrapper_func: CallableType,
    legacy_name: str
) -> CallableType:
    """Create a legacy wrapper function that calls the new implementation.

    Args:
        new_wrapper_func: New wrapper function to call
        legacy_name: Name for the legacy wrapper

    Returns:
        Legacy wrapper function

    Example:
        switch_config_preset = create_legacy_wrapper(
            new_wrapper_func=config_switch_preset,
            legacy_name="switch_config_preset"
        )
    """
    @wraps(new_wrapper_func)
    def legacy_wrapper(*args: Any, **kwargs: Any) -> Any:
        return new_wrapper_func(*args, **kwargs)

    legacy_wrapper.__name__ = legacy_name
    return legacy_wrapper


# ===== ERROR HANDLING =====


def handle_wrapper_error(
    error: Exception,
    operation_name: str,
    correlation_id: Optional[str] = None,
    raise_error: bool = True
) -> None:
    """Handle errors in wrapper functions with consistent logging.

    Args:
        error: Exception that occurred
        operation_name: Name of the operation that failed
        correlation_id: Correlation ID for tracking
        raise_error: Whether to re-raise the error

    Example:
        try:
            result = risky_operation()
        except Exception as e:
            handle_wrapper_error(e, "cache_get", correlation_id)
    """
    try:
        from lee.gateway import (  # pylint: disable=import-outside-toplevel
            GatewayInterface,
            execute_operation,
        )
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"{operation_name} operation error",
            error_type=type(error).__name__,
            error=str(error),
            corr_id=correlation_id,
        )
    except (ImportError, AttributeError, RuntimeError):
        pass  # Gateway not available, ignore logging error

    if raise_error:
        raise


__all__ = [
    "generate_correlation_id",
    "with_correlation_id",
    "ModuleAvailability",
    "DynamicModuleAvailability",
    "create_simple_wrapper",
    "create_legacy_wrapper",
    "handle_wrapper_error",
]
