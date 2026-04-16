"""cache_l2_disk_split/circuit_breaker_integration.py

Circuit breaker integration for L2 disk cache operations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from lee.circuit_breaker import get_alexa_cache_l2_config
    from lee.gateway import GatewayInterface, execute_operation
    _CIRCUIT_BREAKER_AVAILABLE = True
except ImportError:
    _CIRCUIT_BREAKER_AVAILABLE = False
    execute_operation = None
    GatewayInterface = None


class CircuitBreakerIntegration:
    """Circuit breaker integration for L2 cache operations."""

    def __init__(self, correlation_id: str = None):
        """Initialize circuit breaker integration.

        Args:
            correlation_id: Optional correlation ID for tracking

        """
        self._gateway_available = _CIRCUIT_BREAKER_AVAILABLE
        if self._gateway_available:
            self._gateway_interface = GatewayInterface
            self._execute_operation = execute_operation

        # Circuit breaker name for L2 cache operations
        self._circuit_breaker_name = "cache_l2"

        # Register circuit breaker
        self._register_circuit_breaker(correlation_id=correlation_id)

    def _register_circuit_breaker(self, correlation_id: str = None) -> None:
        """Register cache_l2 circuit breaker with optimized L2 configuration.

        This ensures the circuit breaker uses the correct thresholds:
        - failure_threshold=10 (lenient for non-critical cache)
        - timeout=30 (fast retry for cache operations)

        Args:
            correlation_id: Optional correlation ID for tracking

        """
        if not _CIRCUIT_BREAKER_AVAILABLE:
            return

        try:
            # Get optimized L2 cache config
            config = get_alexa_cache_l2_config()

            # Register circuit breaker with config
            if execute_operation is not None:
                execute_operation(
                    GatewayInterface.CIRCUIT_BREAKER,
                    "get",
                    name=self._circuit_breaker_name,
                    config=config,
                    correlation_id=correlation_id,
                )

            # Log successful registration
            try:
                if execute_operation is not None:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_info",
                        message=f"L2 cache circuit breaker registered with config: "
                               f"threshold={config.failure_threshold}, timeout={config.timeout}",
                        correlation_id=correlation_id,
                    )
            except (ValueError, TypeError, AttributeError, KeyError, ImportError) as e:
                # Expected logging errors
                if execute_operation is not None:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"L2 cache circuit breaker registration logging failed: {e}",
                            extra_context={"operation": "register_circuit_breaker", "circuit": self._circuit_breaker_name},
                        )
                    except (AttributeError, RuntimeError, ValueError, TypeError, KeyError):
                        # Logging unavailable - silent fail
                        ...
                raise
            except Exception as e:
                # Unexpected logging errors
                if execute_operation is not None:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"L2 cache circuit breaker registration logging failed unexpectedly: {e}",
                            extra_context={"operation": "register_circuit_breaker", "circuit": self._circuit_breaker_name, "error_type": type(e).__name__},
                        )
                    except (AttributeError, RuntimeError, ValueError, TypeError, KeyError):
                        # Logging unavailable - silent fail
                        ...
                raise

        except (ValueError, TypeError, AttributeError, KeyError, ImportError, OSError) as e:
            # Expected registration errors - fall back to default config
            pass
            # The circuit breaker will still work with default values (5, 60)
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message=f"L2 cache circuit breaker registration failed: {e}. Using default config.",
                    extra_context={"operation": "register_circuit_breaker", "circuit": self._circuit_breaker_name},
                    correlation_id=correlation_id,
                )
            except (AttributeError, RuntimeError, ValueError, TypeError, KeyError):
                # Logging unavailable - silent fail
                pass
        except OSError as e:
            # Unexpected registration errors - fall back to default config
            pass
            # The circuit breaker will still work with default values (5, 60)
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message=f"L2 cache circuit breaker registration failed: {e}. Using default config.",
                    correlation_id=correlation_id,
                )
            except (RuntimeError, ValueError, AttributeError, TypeError, KeyError) as e2:
                # Circuit breaker registration failed with specific error
                pass
                if execute_operation is not None:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"L2 cache circuit breaker registration logging failed: {e2}",
                            extra_context={"operation": "register_circuit_breaker_fallback", "circuit": self._circuit_breaker_name},
                        )
                    except (AttributeError, RuntimeError, ValueError, TypeError, KeyError):
                        # Logging unavailable - silent fail
                        pass
                raise

    def get_circuit_state(self) -> dict[str, Any]:
        """Get circuit breaker state and statistics for monitoring.

        Returns a dictionary containing the current state of the circuit breaker
        protecting L2 cache operations. This is useful for monitoring and debugging.

        Returns:
            Dictionary with circuit breaker state information:
            - state: Current state ('CLOSED', 'OPEN', 'HALF_OPEN', 'UNAVAILABLE', 'UNKNOWN')
            - failure_count: Number of recorded failures
            - last_failure_time: Timestamp of last failure (if any)
            - last_success_time: Timestamp of last success (if any)

        Example:
            >>> cb = CircuitBreakerIntegration()
            >>> state = cb.get_circuit_state()
            >>> print(f"Circuit state: {state['state']}")
            >>> print(f"Failures: {state['failure_count']}")

        """
        if not _CIRCUIT_BREAKER_AVAILABLE:
            return {
                "state": "UNAVAILABLE",
                "message": "Circuit breaker module not available",
            }

        try:
            # Get circuit breaker instance
            breaker = execute_operation(
                GatewayInterface.CIRCUIT_BREAKER,
                "get",
                name=self._circuit_breaker_name,
            )

            # Get detailed state from circuit breaker
            state_info = breaker.get_state()

            # Return formatted state information
            return {
                "state": state_info.get("state", "UNKNOWN"),
                "failure_count": state_info.get("failure_count", 0),
                "last_failure_time": state_info.get("last_failure_time"),
                "last_success_time": state_info.get("last_success_time"),
                "circuit_breaker_name": self._circuit_breaker_name,
            }

        except (ValueError, TypeError, AttributeError, KeyError, ImportError, OSError) as e:
            # Expected query errors
            return {
                "state": "UNKNOWN",
                "error": str(e),
                "message": "Failed to query circuit breaker state",
                "circuit_breaker_name": self._circuit_breaker_name,
            }
        except OSError as e:
            # Unexpected query errors
            return {
                "state": "UNKNOWN",
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Unexpected error querying circuit breaker state",
            }

    def execute_with_circuit_breaker(self, func: Callable, operation_name: str,
                                      correlation_id: str = None) -> Any:
        """Execute a disk I/O operation with circuit breaker protection.

        Args:
            func: Function to execute (typically disk I/O)
            operation_name: Human-readable operation name for logging
            correlation_id: Optional correlation ID for tracking

        Returns:
            Function result, or None if circuit is open

        """
        if not _CIRCUIT_BREAKER_AVAILABLE:
            # Circuit breaker not available, execute directly
            return func()

        try:
            return execute_operation(
                GatewayInterface.CIRCUIT_BREAKER,
                "call",
                name=self._circuit_breaker_name,
                func=func,
                correlation_id=correlation_id,
            )
        except (ValueError, TypeError, AttributeError, KeyError, ImportError, ConnectionError, TimeoutError) as e:
            # Expected circuit breaker errors
            pass
            # Log the degradation but don't crash
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message=f"L2 cache circuit breaker error for '{operation_name}'. Degrading gracefully.",
                    error=str(e),
                    correlation_id=correlation_id,
                )
            except (RuntimeError, ConnectionError, ValueError, TypeError, AttributeError, KeyError):
                # Circuit breaker opened - log and degrade gracefully
                pass
        except Exception as e:
            # Log all exceptions with correlation ID
            if execute_operation is not None:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"L2 cache circuit breaker: {type(e).__name__}: {e}",
                    extra_context={
                        "operation": "l2_cache",
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "correlation_id": correlation_id
                    }
                )
            # Re-raise for proper error handling
            raise
