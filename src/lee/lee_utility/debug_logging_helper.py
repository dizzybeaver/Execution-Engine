"""lee_utility/debug_logging_helper.py
Debug logging consolidation helper - eliminates duplicate debug logging code
Version: 2026-04-01
License: Apache 2.0
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface


class DebugLoggingHelper:
    """Consolidated debug logging helper to eliminate duplicate code.

    This class provides safe, standardized methods for debug logging,
    metrics recording, and timing operations through the gateway pattern.
    All methods handle missing gateway dependencies gracefully and include
    comprehensive error handling.

    Usage Example:
        helper = DebugLoggingHelper(scope="CACHE")
        helper.log_debug(correlation_id, "get called", key="my_key")
        with helper.timing_context(correlation_id, "get"):
            # ... operation code ...
    """

    def __init__(
        self,
        scope: str,
        execute_operation: Any = None,
        gateway_interface: Any = None
    ):
        """Initialize debug logging helper.

        Args:
            scope: Logging scope identifier (e.g., "CACHE", "HTTP")
            execute_operation: Gateway execute_operation function
            gateway_interface: GatewayInterface enum
        """
        self.scope = scope
        self._execute_operation = execute_operation
        self._gateway_interface = gateway_interface

    def set_gateway(
        self,
        execute_operation: Any,
        gateway_interface: Any
    ) -> None:
        """Set or update gateway functions (for lazy loading).

        Args:
            execute_operation: Gateway execute_operation function
            gateway_interface: GatewayInterface enum
        """
        self._execute_operation = execute_operation
        self._gateway_interface = gateway_interface

    def log_debug(
        self,
        correlation_id: Optional[str],
        message: str,
        **kwargs
    ) -> None:
        """Safely log debug message through gateway.

        Args:
            correlation_id: Correlation ID for request tracking
            message: Debug message to log
            **kwargs: Additional context data to log
        """
        if not self._execute_operation or not self._gateway_interface:
            return
        try:
            self._execute_operation(
                self._gateway_interface.DEBUG,
                "log",
                corr_id=correlation_id,
                scope=self.scope,
                message=message,
                **kwargs
            )
        except (AttributeError, TypeError, ValueError) as e:
            try:
                # Import at module level to avoid redefining outer scope
                from lee.gateway import execute_operation as _exec_op
                _exec_op(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(AttributeError, TypeError, ValueError) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

    def log_error(
        self,
        correlation_id: Optional[str],
        error_message: str,
        **kwargs
    ) -> None:
        """Safely log error message through gateway.

        Args:
            correlation_id: Correlation ID for request tracking
            error_message: Error message to log
            **kwargs: Additional context data to log
        """
        if not self._execute_operation or not self._gateway_interface:
            return
        try:
            self._execute_operation(
                self._gateway_interface.LOGGING,
                "log_error",
                message=error_message,
                corr_id=correlation_id,
                **kwargs
            )
        except (AttributeError, TypeError, ValueError) as e:
            try:
                # Import at module level to avoid redefining outer scope
                from lee.gateway import execute_operation as _exec_op
                _exec_op(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(AttributeError, TypeError, ValueError) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

    def log_info(
        self,
        correlation_id: Optional[str],
        message: str,
        **kwargs
    ) -> None:
        """Safely log info message through gateway.

        Args:
            correlation_id: Correlation ID for request tracking
            message: Info message to log
            **kwargs: Additional context data to log
        """
        if not self._execute_operation or not self._gateway_interface:
            return
        try:
            self._execute_operation(
                self._gateway_interface.LOGGING,
                "log_info",
                message=message,
                corr_id=correlation_id,
                **kwargs
            )
        except (AttributeError, TypeError, ValueError) as e:
            try:
                # Import at module level to avoid redefining outer scope
                from lee.gateway import execute_operation as _exec_op
                _exec_op(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(AttributeError, TypeError, ValueError) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

    def record_metrics(self, **kwargs) -> None:
        """Safely record metrics through gateway.

        Args:
            **kwargs: Metrics data (operation_name, hit, miss, etc.)
        """
        if not self._execute_operation or not self._gateway_interface:
            return
        try:
            # Try record_cache operation first
            self._execute_operation(
                self._gateway_interface.METRICS,
                "record_cache",
                **kwargs
            )
        except (AttributeError, TypeError, ValueError, KeyError, RuntimeError):
            # If record_cache fails, try record_cache_metric alias
            try:
                self._execute_operation(
                    self._gateway_interface.METRICS,
                    "record_cache_metric",
                    **kwargs
                )
            except (AttributeError, TypeError, ValueError, KeyError, RuntimeError) as e:
                try:
                    # Import at module level to avoid redefining outer scope
                    from lee.gateway import execute_operation as _exec_op
                    _exec_op(
                        GatewayInterface.LOGGING,
                        'log_error',
                        message=f'(AttributeError, TypeError, ValueError, KeyError, RuntimeError) occurred: {e}',
                        corr_id=None
                    )
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Gateway not available

    def increment_metrics(
        self,
        metric_name: str,
        value: float = 1.0
    ) -> None:
        """Safely increment counter metric through gateway.

        Args:
            metric_name: Name of metric to increment
            value: Value to increment by (default 1.0)
        """
        if not self._execute_operation or not self._gateway_interface:
            return
        try:
            self._execute_operation(
                self._gateway_interface.METRICS,
                "increment_counter",
                name=metric_name,
                value=value
            )
        except (AttributeError, TypeError, ValueError, KeyError) as e:
            try:
                # Import at module level to avoid redefining outer scope
                from lee.gateway import execute_operation as _exec_op
                _exec_op(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(AttributeError, TypeError, ValueError, KeyError) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

    def timing_context(
        self,
        correlation_id: Optional[str],
        operation: str,
        **kwargs
    ):
        """Create a timing context manager for operation timing.

        Args:
            correlation_id: Correlation ID for request tracking
            operation: Operation name for timing
            **kwargs: Additional context data

        Returns:
            Context manager for timing measurement
        """
        if not self._execute_operation or not self._gateway_interface:
            # Return no-op context manager if gateway unavailable
            return _NoOpContextManager()

        try:
            return self._execute_operation(
                self._gateway_interface.DEBUG,
                "timing",
                corr_id=correlation_id,
                scope=self.scope,
                operation=operation,
                **kwargs
            )
        except (AttributeError, TypeError, ValueError):
            # Return no-op context manager on error
            return _NoOpContextManager()

    def log_operation_start(
        self,
        correlation_id: Optional[str],
        operation: str,
        **kwargs
    ) -> None:
        """Log operation start with standardized format.

        Args:
            correlation_id: Correlation ID for request tracking
            operation: Operation name
            **kwargs: Additional context data
        """
        self.log_debug(correlation_id, f"{operation} called", **kwargs)

    def log_operation_success(
        self,
        correlation_id: Optional[str],
        operation: str,
        **kwargs
    ) -> None:
        """Log operation success with standardized format.

        Args:
            correlation_id: Correlation ID for request tracking
            operation: Operation name
            **kwargs: Additional context data
        """
        self.log_debug(
            correlation_id,
            f"{operation} completed",
            success=True,
            **kwargs
        )

    def log_operation_failure(
        self,
        correlation_id: Optional[str],
        operation: str,
        error: Exception,
        **kwargs
    ) -> None:
        """Log operation failure with standardized format.

        Args:
            correlation_id: Correlation ID for request tracking
            operation: Operation name
            error: Exception that caused failure
            **kwargs: Additional context data
        """
        self.log_debug(
            correlation_id,
            f"{operation} failed",
            error_type=type(error).__name__,
            error=str(error),
            **kwargs
        )


class _NoOpContextManager:
    """No-op context manager for when gateway is unavailable."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
