"""circuit_breaker/circuit_breaker_core.py
Version: 2026-03-28_1
Purpose: Circuit breaker with CBFuse (permanent trip history)
License: Apache 2.0

CBFuse System:
- Monitored breakers (enable_cbfuse=True): Blow fuse on trip, needs investigation
- Expected breakers (enable_cbfuse=False): No fuse, tripping is normal

CBFuse is a boolean flag that:
- Starts False on initialization (ONLY time it's set to False)
- Can be set True when circuit breaker trips (if enable_cbfuse=True)
- Stays True forever (until manually reset via reset_cbfuse())
- Survives circuit breaker resets - permanent trip history
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, Optional

# Lazy import gateway to avoid circular dependency
# gateway_core imports circuit_breaker, circuit_breaker_core imports gateway
# Moved inside methods that need gateway functions
GatewayInterface = None  # Type hint for runtime
execute_operation = None  # Type hint for runtime

if TYPE_CHECKING:
    from lee.circuit_breaker.circuit_breaker_config import CircuitBreakerConfig


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG mode is enabled.

    Returns:
        True if LEE_DEBUG environment variable is set to 'true'
    """
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


class CircuitBreaker:
    """Circuit breaker with permanent fuse tracking (CBFuse).

    CBFuse provides permanent trip history that survives circuit breaker resets.
    This allows health checks to distinguish between "never failed" and "recovered".

    Monitored vs Expected Breakers:
        - Monitored (enable_cbfuse=True): Tripping is unexpected, needs investigation
        - Expected (enable_cbfuse=False): Tripping is normal, no investigation needed

    Attributes:
        name: Circuit breaker identifier
        enable_cbfuse: Whether to blow fuse on trip (monitored vs expected)
        cbfuse: Permanent trip history flag (False -> True, never back to False)
        failure_threshold: Failures to trip circuit
        timeout: Seconds in OPEN before HALF_OPEN

    Example:
        >>> # Monitored breaker (has fuse)
        >>> obs_breaker = CircuitBreaker("observability", enable_cbfuse=True)
        >>> obs_breaker.record_failure(Exception("test"))  # Trip breaker
        >>> obs_breaker.cbfuse  # True - blown!
        >>> obs_breaker.reset()  # Reset breaker
        >>> obs_breaker.cbfuse  # STILL True - permanent history
        >>> obs_breaker.reset_cbfuse()  # Only way to reset fuse

        >>> # Expected breaker (no fuse)
        >>> rate_limiter = CircuitBreaker("rate_limiter", enable_cbfuse=False)
        >>> rate_limiter.record_failure(Exception("test"))  # Trip breaker
        >>> rate_limiter.cbfuse  # Still False - no fuse
        >>> rate_limiter.reset()  # Reset breaker

    COMPLIANCE:
        - AP-08: No threading locks (Lambda single-threaded)
        - DEC-04: Lambda single-threaded model
        - LESS-21: Rate limiting for DoS protection
    """

    def __init__(  # pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        config: Optional[CircuitBreakerConfig] = None,
        enable_cbfuse: bool = True,
        success_threshold: int = 2,
        rolling_window: float = 300.0,
        half_open_max_calls: int = 3,
        _max_failure_records: int = 100,
    ):
        """Initialize circuit breaker with CBFuse support.

            name: Circuit breaker identifier
            failure_threshold: Failures to trip circuit (default: 5)
            timeout: Seconds in OPEN before HALF_OPEN (default: 60)
            config: Optional CircuitBreakerConfig object (takes precedence)
            enable_cbfuse: Whether to blow fuse on trip (default: True)
                - True: Monitored breaker (tripping = problem, needs investigation)
                - False: Expected breaker (tripping = normal operation)
            success_threshold: Consecutive successes to close (default: 2)
            rolling_window: Time window for failure counting (default: 300.0)
            half_open_max_calls: Max trial calls in HALF_OPEN (default: 3)
            max_failure_records: Maximum failure records to keep (default: 100)

        Backward Compatibility:
            Existing code using CircuitBreaker(name, 5, 60) continues to work.
            New enable_cbfuse parameter defaults to True (monitored by default).

        """
        _ = _max_failure_records  # Reserved for future use
        self.name = name
        self.enable_cbfuse = enable_cbfuse

        # Determine configuration (config object takes precedence)
        if config is not None:
            self._config = config
            self.failure_threshold = config.failure_threshold
            self.timeout = int(config.timeout)
            self.success_threshold = config.success_threshold
            self.half_open_max_calls = config.half_open_max_calls
            self.rolling_window = config.rolling_window_seconds
        else:
            # Legacy path: direct parameters
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.success_threshold = success_threshold
            self.half_open_max_calls = half_open_max_calls
            self.rolling_window = rolling_window
            self._config = None

        # State tracking
        self._disabled = False  # Circuit state (False = closed, True = open)
        self.failure_count = 0
        self._last_failure_time = None
        self._last_failure_error = None
        self._consecutive_successes = 0
        self._half_open_call_count = 0

        # CBFuse state (ONLY set to False here - NEVER again!)
        self.cbfuse = False

        # Statistics
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._rejected_calls = 0

    def record_success(self):
        """Record successful operation.

        Resets failure count on success. In HALF_OPEN state, tracks consecutive
        successes to close circuit.
        """
        self._successful_calls += 1

        if self._disabled:
            # Test if circuit should reset
            if self._should_attempt_reset():
                self._attempt_reset()
        else:
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = 0
                self._consecutive_successes += 1

    def record_failure(self, error: Exception, correlation_id: str = None):
        """Record failure and potentially trip breaker.

        If failure threshold is exceeded, trips breaker and blows cbfuse
        if this is a monitored breaker (enable_cbfuse=True).

            error: The exception that occurred
            correlation_id: Optional correlation ID for tracing

        """
        # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
        _failure_time = time.time()

        self._failed_calls += 1
        self.failure_count += 1
        self._last_failure_time = _failure_time
        self._last_failure_error = error
        self._consecutive_successes = 0  # Reset on any failure

        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = f"cbfuse_{int(_failure_time * 1000)}"

        # Check if breaker should trip
        if self.failure_count >= self.failure_threshold and not self._disabled:
            self._trip_breaker(error, correlation_id)

    def _trip_breaker(self, error: Exception, correlation_id: str):
        """Trip the circuit breaker and optionally blow the fuse.

            error: The exception that caused the trip
            correlation_id: Correlation ID for tracing

        """
        self._disabled = True

        # Route to appropriate trip handler based on breaker type
        if self.enable_cbfuse:
            self._trip_monitored_breaker(error, correlation_id)
        else:
            self._trip_expected_breaker(error, correlation_id)

    def _trip_monitored_breaker(self, error: Exception, correlation_id: str) -> None:
        """Handle trip for monitored breaker (has fuse).

        For monitored breakers, tripping is unexpected and needs investigation.
        The fuse permanently records that a trip occurred.

            error: The exception that caused the trip
            correlation_id: Correlation ID for tracing

        """
        if not self.cbfuse:
            # First trip - blow the fuse
            self.cbfuse = True
            self._log_trip_event(
                correlation_id=correlation_id,
                log_level="log_error",
                message=(
                    f"CIRCUIT BREAKER TRIPPED: {self.name} - "
                    f"CBFUSE BLOWN (cbfuse={self.cbfuse}) - "
                    f"This is a MONITORED breaker - tripping indicates a problem. "
                    f"Failures: {self.failure_count}, Error: {error}"
                ),
                cbfuse_state="blown",
            )
        else:
            # Fuse already blown - recurring trips
            self._log_trip_event(
                correlation_id=correlation_id,
                log_level="log_error",
                message=(
                    f"CIRCUIT BREAKER TRIPPED AGAIN: {self.name} - "
                    f"CBFUSE ALREADY BLOWN (cbfuse={self.cbfuse}) - "
                    f"Recurring trips - root cause not fixed. "
                    f"Failures: {self.failure_count}, Error: {error}"
                ),
                cbfuse_state="already_blown",
            )

    def _trip_expected_breaker(self, error: Exception, correlation_id: str) -> None:
        """Handle trip for expected breaker (no fuse).

        For expected breakers, tripping is normal operation (e.g., rate limiters).
        No fuse is blown because trips are expected.

            error: The exception that caused the trip
            correlation_id: Correlation ID for tracing

        """
        self._log_trip_event(
            correlation_id=correlation_id,
            log_level="log_debug",
            message=(
                f"CIRCUIT BREAKER TRIPPED: {self.name} - "
                f"EXPECTED trip (no cbfuse) - This breaker has no fuse because "
                f"tripping is part of normal operation. "
                f"Failures: {self.failure_count}, Error: {error}"
            ),
            cbfuse_state="not_enabled",
        )

    def _log_trip_event(self, correlation_id: str, log_level: str,
                        message: str, cbfuse_state: str) -> None:
        """Log circuit breaker trip event with gateway integration.

        Centralized logging method for all trip events to reduce code duplication
        and handle potential gateway failures gracefully.

            correlation_id: Correlation ID for tracing
            log_level: Gateway logging level (log_error or log_debug)
            message: Log message
            cbfuse_state: State of cbfuse for logging context

        """
        try:
            # Lazy import to avoid circular dependency
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            execute_operation(
                GatewayInterface.LOGGING,
                log_level,
                message=message,
                correlation_id=correlation_id,
                breaker=self.name,
                cbfuse_state=cbfuse_state,
                failure_count=self.failure_count,
            )
        except ImportError:
            # Gateway not available during initialization
            ...
        except (AttributeError, KeyError, TypeError) as exc:
            # Gateway interface mismatch - log to stderr
            print(f"[CIRCUIT_BREAKER] Gateway call failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        except RuntimeError as exc:
            # Gateway runtime error (e.g., circuit breaker in logging path)
            print(f"[CIRCUIT_BREAKER] Gateway runtime error: {type(exc).__name__}: {exc}", file=sys.stderr)

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset.

            bool: True if timeout has expired

        """
        if self._last_failure_time is None:
            return True

        return (time.time() - self._last_failure_time) > self.timeout

    def _attempt_reset(self):
        """Attempt to reset circuit breaker to CLOSED state."""
        if self._should_attempt_reset():
            self._disabled = False
            self.failure_count = 0
            self._consecutive_successes = 0
            self._half_open_call_count = 0

    def reset(self):
        """Reset circuit breaker (but NOT cbfuse).

        Resets the circuit breaker to operational state, but cbfuse remains
        True if it was blown. This preserves permanent trip history.

        Example:
            >>> breaker.record_failure(Exception("test"))  # Trip
            >>> breaker.cbfuse  # True
            >>> breaker.reset()  # Reset breaker
            >>> breaker.cbfuse  # STILL True - permanent history

        """
        self._disabled = False
        self.failure_count = 0
        self._consecutive_successes = 0
        self._half_open_call_count = 0
        # NOTE: cbfuse stays True! Permanent trip history

    def reset_cbfuse(self, correlation_id: str = None):
        """Manually reset cbfuse (ONLY after fixing root cause).

        This is the ONLY method that can set cbfuse back to False.
        Should only be called after investigating and fixing the root cause
        of why the monitored breaker tripped.

            correlation_id: Optional correlation ID for tracing

        Example:
            >>> breaker.cbfuse  # True
            >>> # ... fix root cause ...
            >>> breaker.reset_cbfuse()
            >>> breaker.cbfuse  # False - clean history

        """
        if self.cbfuse:
            self.cbfuse = False
            try:
                # Lazy import to avoid circular dependency
                from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_info",
                    message=f"CBFUSE RESET: {self.name} - Root cause fixed, fuse replaced",
                    correlation_id=correlation_id,
                    breaker=self.name,
                    cbfuse_state="reset",
                )
            except ImportError:
                # Gateway not available during initialization
                ...
            except (AttributeError, KeyError, TypeError) as e:
                # Gateway interface mismatch
                import sys
                print(f"[CIRCUIT_BREAKER] CBFUSE reset logging failed: {type(e).__name__}: {e}", file=sys.stderr)
            except RuntimeError as e:
                # Gateway runtime error
                import sys
                print(f"[CIRCUIT_BREAKER] CBFUSE reset runtime error: {type(e).__name__}: {e}", file=sys.stderr)

    def is_healthy(self) -> bool:
        """Check if circuit breaker is currently working.

            bool: True if circuit is closed (operational), False if open

        """
        return not self._disabled

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status including cbfuse.

            Dict containing:
                - name: Circuit breaker identifier
                - healthy: True if circuit is closed
                - failure_count: Current failure count
                - last_error: Last error message (if any)
                - cbfuse: Permanent trip history flag
                - cbfuse_interpretation: Human-readable cbfuse status
                - enable_cbfuse: Whether fuse is enabled for this breaker
                - threshold: Failure threshold
                - timeout: Timeout in seconds

        Example:
            >>> status = breaker.get_status()
            >>> print(status['cbfuse_interpretation'])
            'TRIPPED at some point - investigate root cause'

        """
        return {
            "name": self.name,
            "healthy": not self._disabled,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_error": str(self._last_failure_error) if self._last_failure_error else None,
            "cbfuse": self.cbfuse,
            "cbfuse_interpretation": self._interpret_cbfuse(),
            "enable_cbfuse": self.enable_cbfuse,
        }

    def _interpret_cbfuse(self) -> str:
        """Interpret cbfuse status for health reports.

            Human-readable interpretation of cbfuse state

        Example:
            >>> breaker._interpret_cbfuse()
            'Never tripped (clean history)'
            >>> breaker.record_failure(Exception("test"))
            >>> breaker._interpret_cbfuse()
            'TRIPPED at some point - investigate root cause'

        """
        if not self.enable_cbfuse:
            return "Expected breaker - no fuse (tripping is normal)"

        if not self.cbfuse:
            return "Never tripped (clean history)"
        return "TRIPPED at some point - investigate root cause"

    def call(self, func: Callable, rate_limit_check: Callable,
             correlation_id: str, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.

            func: Function to execute
            rate_limit_check: Callable that returns True if within rate limit
            correlation_id: Correlation ID for debug tracking
            *args, **kwargs: Arguments for func

            Function result
        Raises:
            Exception: If circuit is open or function fails

        """
        # Check rate limit first
        self._check_rate_limit(rate_limit_check, correlation_id)
        self._total_calls += 1

        # Check circuit state and attempt reset if needed
        if self._disabled:
            self._handle_disabled_circuit(correlation_id)

        # Execute function with timing
        return self._execute_with_timing(func, correlation_id, *args, **kwargs)

    def _check_rate_limit(self, rate_limit_check: Callable, correlation_id: str) -> None:
        """Check rate limit and raise exception if exceeded.

            rate_limit_check: Callable that returns True if within rate limit
            correlation_id: Correlation ID for debug tracking

        Raises:
            Exception: If rate limit exceeded

        """
        if not rate_limit_check():
            self._log_debug(
                correlation_id=correlation_id,
                message="Rate limit exceeded",
            )
            raise ConnectionError(f"Circuit breaker '{self.name}': Rate limit exceeded")

    def _handle_disabled_circuit(self, correlation_id: str) -> None:
        """Handle call when circuit is disabled (OPEN state).

        Checks if timeout has expired and attempts reset, or rejects the call.

            correlation_id: Correlation ID for debug tracking

        Raises:
            Exception: If circuit is OPEN and timeout has not expired

        """
        if self._should_attempt_reset():
            # Timeout expired - attempt reset
            self._log_debug(
                correlation_id=correlation_id,
                message="Attempting reset after timeout",
            )
            self._attempt_reset()
        else:
            # Circuit still OPEN - reject call
            self._rejected_calls += 1
            self._log_debug(
                correlation_id=correlation_id,
                message="Circuit OPEN - rejecting call",
                failure_count=self.failure_count,
            )
            raise ConnectionError(f"Circuit breaker '{self.name}' is OPEN")

    def _execute_with_timing(self, func: Callable, correlation_id: str,
                            *args, **kwargs) -> Any:
        """Execute function with timing and circuit breaker tracking.

            func: Function to execute
            correlation_id: Correlation ID for debug tracking
            *args, **kwargs: Arguments for func

            Function result
        Raises:
            Exception: If function fails

        """
        # Get timing context (fallback to nullcontext if gateway unavailable)
        timing_ctx = self._get_timing_context(correlation_id)

        with timing_ctx:
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError, RuntimeError) as e:
                # Expected errors from user functions
                self.record_failure(e, correlation_id)
                raise

    def _get_timing_context(self, correlation_id: str):
        """Get timing context from gateway or nullcontext fallback.

            correlation_id: Correlation ID for debug tracking

            Timing context manager (gateway timing or nullcontext)

        """
        try:
            # Lazy import to avoid circular dependency
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            return execute_operation(
                GatewayInterface.DEBUG,
                "timing",
                correlation_id=correlation_id,
                operation_name=f"call:{self.name}",
            )
        except ImportError:
            # Gateway not available
            return nullcontext()
        except (AttributeError, KeyError, TypeError) as exc:
            # Gateway interface mismatch
            print(f"[CIRCUIT_BREAKER] Timing context unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
            return nullcontext()
        except RuntimeError:
            # Gateway runtime error
            return nullcontext()

    def _log_debug(self, correlation_id: str, message: str, **kwargs) -> None:
        """Log debug message with gateway integration.

        Centralized logging method to reduce code duplication.

            correlation_id: Correlation ID for debug tracking
            message: Log message
            **kwargs: Additional logging parameters

        """
        if not _is_debug_mode():
            return

        try:
            # Lazy import to avoid circular dependency
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            log_params = {
                "corr_id": correlation_id,
                "scope": "CIRCUIT_BREAKER",
                "message": message,
                "breaker": self.name,
                **kwargs
            }
            execute_operation(GatewayInterface.DEBUG, "log", **log_params)
        except ImportError:
            # Gateway not available - skip debug logging
            ...
        except (AttributeError, KeyError, TypeError) as exc:
            # Gateway interface mismatch
            print(f"[CIRCUIT_BREAKER] Debug log failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        except RuntimeError:
            # Gateway runtime error - skip debug logging
            ...


__all__ = ["CircuitBreaker"]
