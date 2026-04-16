"""circuit_breaker/circuit_breaker_state.py
Version: 2025-12-13_1
Enhanced: 2026-03-04 (Rolling window, failure records, configurable thresholds)
Purpose: Circuit breaker state and individual breaker implementation
License: Apache 2.0

Enhancements based on UGA circuit breaker patterns:
- Rolling window failure tracking (configurable time window)
- Failure record preservation (exception details with timestamps)
- Configurable success threshold (consecutive successes required)
- Half-open max calls limiting (blast radius control)
"""

from __future__ import annotations

import os
import sys
import time
from collections import deque
from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from lee.gateway import GatewayInterface, execute_operation

if TYPE_CHECKING:
    from lee.circuit_breaker.circuit_breaker_config import CircuitBreakerConfig


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG mode is enabled.

    Returns:
        True if LEE_DEBUG environment variable is set to 'true'
    """
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class FailureRecord:
    """Record of a failure with timestamp and exception details.

    This dataclass preserves failure information for post-mortem analysis
    and rolling window failure tracking.

    Attributes:
        timestamp: Unix timestamp (seconds since epoch) from time.time()
        exception: The actual exception object
        error_type: Exception class name for quick analysis

    Example:
        >>> record = FailureRecord(
        ...     timestamp=time.time(),
        ...     exception=ValueError("test"),
        ...     error_type="ValueError"
        ... )

    """

    timestamp: float
    exception: Exception
    error_type: str


class CircuitBreaker:  # pylint: disable=too-many-instance-attributes
    """Single circuit breaker instance.

    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-21: Rate limiting for DoS protection
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        config: Optional[CircuitBreakerConfig] = None,
        success_threshold: int = 2,
        rolling_window: float = 300.0,
        half_open_max_calls: int = 3,
        max_failure_records: int = 100,
    ):
        """Initialize circuit breaker with enhanced configuration.

            name: Circuit breaker identifier
            failure_threshold: Failures to trip circuit (default: 5)
            timeout: Seconds in OPEN before HALF_OPEN (default: 60)
            config: Optional CircuitBreakerConfig object (takes precedence)
            success_threshold: Consecutive successes to close (default: 2)
            rolling_window: Time window for failure counting in seconds (default: 300.0)
            half_open_max_calls: Max trial calls in HALF_OPEN (default: 3)
            max_failure_records: Maximum failure records to keep (default: 100)

        Backward Compatibility:
            Existing code using CircuitBreaker(name, 5, 60) continues to work.
            New parameters are optional with sensible defaults.

        """
        self.name = name

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
        self.state = CircuitState.CLOSED

        # NEW: Rolling window failure tracking (replaces simple counter)
        self._failure_records: deque[FailureRecord] = deque(maxlen=max_failure_records)
        self._failure_count = 0  # Count within rolling window

        # NEW: Track consecutive successes for configurable threshold
        self._consecutive_successes = 0

        # NEW: Track half-open calls for max calls limiting
        self._half_open_call_count = 0

        # DEPRECATED: Kept for backward compatibility in get_state()
        # Use self._failure_count and self._failure_records[-1].timestamp instead
        self.failures = 0  # Will be set to _failure_count
        self.last_failure_time = None  # Will be derived from _failure_records

        # Statistics (unchanged)
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._rejected_calls = 0

        # NEW: State transition tracking (2026-03-25 enhancement)
        self._last_state_change_time = time.time()
        self._previous_state: Optional[CircuitState] = None
        self._state_transitions: dict[str, int] = {
            "closed_to_open": 0,
            "open_to_half_open": 0,
            "half_open_to_closed": 0,
            "half_open_to_open": 0,
        }
        self._transition_history: list[dict[str, Any]] = []
        self._max_transition_history = 20

        # Initialize previous state to current state for proper transition tracking
        self._previous_state = self.state

    def _record_state_transition(
        self,
        new_state: CircuitState,
        reason: str = "",
        correlation_id: str = None,
    ) -> None:
        """Record a state transition with timestamp and metadata.

            new_state: The new circuit state
            reason: Human-readable reason for transition
            correlation_id: Optional correlation ID for tracing

        """
        # Capture current state before transition
        old_state = self.state

        # Create transition key
        if old_state:
            transition_key = f"{old_state.value}_to_{new_state.value}"
        else:
            transition_key = f"initial_to_{new_state.value}"

        # Update transition counters
        if transition_key in self._state_transitions:
            self._state_transitions[transition_key] += 1
        else:
            self._state_transitions[transition_key] = 1

        # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
        _transition_time = time.time()

        # Record transition in history
        transition_record = {
            "timestamp": _transition_time,
            "from_state": old_state.value if old_state else "initial",
            "to_state": new_state.value,
            "reason": reason,
            "correlation_id": correlation_id,
        }
        self._transition_history.append(transition_record)

        # Trim history if needed
        if len(self._transition_history) > self._max_transition_history:
            self._transition_history.pop(0)

        # Update state tracking (store old state as previous)
        self._previous_state = old_state
        self._last_state_change_time = _transition_time

    def _clean_stale_failures(self) -> None:
        """Remove failure records outside the rolling window.

        Lambda single-threaded: No lock needed (AP-08 compliant).

        This method evicts failure records that are older than the rolling
        window period, ensuring that only recent failures count toward
        the threshold. This prevents stale failures from keeping the
        circuit open indefinitely.

        Side effects:
            - Updates self._failure_records (removes stale entries)
            - Updates self._failure_count (count of remaining records)
            - Updates self.failures (for backward compatibility)

        Example:
            >>> breaker = CircuitBreaker("test", rolling_window=5.0)
            >>> # After 10 failures and 6 seconds...
            >>> breaker._clean_stale_failures()
            >>> assert breaker._failure_count == 0  # All evicted

        """
        if not self._failure_records:
            self._failure_count = 0
            self.failures = 0  # Backward compatibility
            return

        now = time.time()
        cutoff = now - self.rolling_window

        # Evict stale failures from the left side of the deque
        # O(1) per eviction with deque.popleft()
        while self._failure_records and self._failure_records[0].timestamp <= cutoff:
            self._failure_records.popleft()

        # Update count and backward compatibility attribute
        self._failure_count = len(self._failure_records)
        self.failures = self._failure_count

    def call(  # pylint: disable=too-many-branches,too-many-statements
        self,
        func: Callable,
        rate_limit_check: Callable,
        correlation_id: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection.

            func: Function to execute
            rate_limit_check: Callable that returns True if within rate limit
            correlation_id: Correlation ID for debug tracking
            *args, **kwargs: Arguments for func

            Function result
        Raises:
            Exception: If circuit is open or function fails

        """
        # SUGA-ISP COMPLIANT: Debug via Gateway

        # Rate limit check
        if not rate_limit_check():
            if _is_debug_mode():
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="CIRCUIT_BREAKER",
                                     message="Rate limit exceeded", breaker=self.name)
                except ImportError:
                    # Gateway not available
                    ...
                except (AttributeError, KeyError, TypeError) as e:
                    # Gateway interface mismatch
                    print(f"[CIRCUIT_BREAKER] Rate limit log failed: {type(e).__name__}: {e}", file=sys.stderr)
                except RuntimeError:
                    # Gateway runtime error
                    ...
            raise RuntimeError(f"Circuit breaker '{self.name}': Rate limit exceeded")

        self._total_calls += 1

        # Check circuit state
        if self.state == CircuitState.OPEN:
            # NEW: Get last failure time from records
            last_failure_time = (
                self._failure_records[-1].timestamp if self._failure_records else 0
            )

            if time.time() - last_failure_time > self.timeout:
                # Transition to HALF_OPEN
                if _is_debug_mode():
                    try:
                        execute_operation(
                            GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id,
                            scope="CIRCUIT_BREAKER",
                            message="Transitioning to HALF_OPEN",
                            breaker=self.name,
                        )
                    except (ImportError, AttributeError):
                        # Optional dependency - continue if unavailable
                        ...
                self._record_state_transition(
                    CircuitState.HALF_OPEN,
                    reason="Timeout exceeded, attempting recovery",
                    correlation_id=correlation_id,
                )
                self.state = CircuitState.HALF_OPEN
                self._half_open_call_count = 0
                self._consecutive_successes = 0
            else:
                self._rejected_calls += 1
                if _is_debug_mode():
                    try:
                        execute_operation(
                            GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id,
                            scope="CIRCUIT_BREAKER",
                            message="Circuit OPEN - rejecting call",
                            breaker=self.name,
                            failure_count=self._failure_count,
                        )
                    except (ImportError, AttributeError):
                        # Optional dependency - continue if unavailable
                        ...
                raise RuntimeError(f"Circuit breaker '{self.name}' is OPEN")

        # NEW: Check half-open call limit
        if self.state == CircuitState.HALF_OPEN:
            if self._half_open_call_count >= self.half_open_max_calls:
                self._rejected_calls += 1
                try:
                    execute_operation(
                        GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id,
                        scope="CIRCUIT_BREAKER",
                        message="HALF_OPEN call limit exceeded - rejecting",
                        breaker=self.name,
                        call_count=self._half_open_call_count,
                        max_calls=self.half_open_max_calls,
                    )
                except (ImportError, AttributeError):
                    # Optional dependency - continue if unavailable
                    ...
                raise RuntimeError(f"Circuit breaker '{self.name}' HALF_OPEN call limit exceeded")

            self._half_open_call_count += 1
            try:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=correlation_id,
                    scope="CIRCUIT_BREAKER",
                    message=f"HALF_OPEN call #{self._half_open_call_count}/{self.half_open_max_calls}",
                    breaker=self.name,
                    call_count=self._half_open_call_count,
                    max_calls=self.half_open_max_calls,
                )
            except ImportError:
                # Gateway not available
                ...
            except (AttributeError, KeyError, TypeError) as e:
                # Gateway interface mismatch
                print(f"[CIRCUIT_BREAKER] Gateway debug log failed: {type(e).__name__}: {e}", file=sys.stderr)
            except RuntimeError:
                # Gateway runtime error
                ...

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CIRCUIT_BREAKER",
                             message="Executing protected call",
                             breaker=self.name, state=self.state.value)
        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        # Execute with timing
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                          correlation_id=correlation_id,
                                          operation_name=f"call:{self.name}")
        except (ImportError, AttributeError):
            timing_ctx = nullcontext()
        with timing_ctx:
            try:
                result = func(*args, **kwargs)

                # Record success metrics
                try:
                    execute_operation(
                        GatewayInterface.OBSERVABILITY,
                        "increment",
                        name="circuit_breaker_call_success",
                        value=1,
                        tags={
                            "breaker": self.name,
                            "correlation_id": correlation_id,
                        },
                    )
                except ImportError:
                    # Gateway not available
                    ...
                except (AttributeError, KeyError, TypeError) as e:
                    # Gateway interface mismatch
                    print(f"[CIRCUIT_BREAKER] Observability increment failed: {type(e).__name__}: {e}", file=sys.stderr)
                except RuntimeError:
                    # Gateway runtime error
                    ...

                self._on_success(correlation_id)
                return result

            except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                # Record failure metrics
                try:
                    execute_operation(
                        GatewayInterface.OBSERVABILITY,
                        "increment",
                        name="circuit_breaker_call_failure",
                        value=1,
                        tags={
                            "breaker": self.name,
                            "correlation_id": correlation_id,
                        },
                    )

                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_error",
                        message=f"Circuit breaker call failed: {e!s}",
                        correlation_id=correlation_id,
                        breaker=self.name,
                    )
                except ImportError:
                    # Gateway not available
                    ...
                except (AttributeError, KeyError, TypeError) as err:
                    # Gateway interface mismatch
                    print(f"[CIRCUIT_BREAKER] Error logging failed: {type(err).__name__}: {err}", file=sys.stderr)
                except RuntimeError:
                    # Gateway runtime error
                    ...

                self._on_failure(correlation_id, e)
                raise

    def _on_success(self, correlation_id: str):
        """Handle successful call with configurable success threshold.

        In CLOSED state: Clears all failures immediately.
        In HALF_OPEN state: Requires N consecutive successes to close circuit.
            correlation_id: Request correlation ID for tracing

        """

        self._successful_calls += 1

        if self.state == CircuitState.HALF_OPEN:
            # NEW: Increment consecutive success counter
            self._consecutive_successes += 1

            try:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=correlation_id,
                    scope="CIRCUIT_BREAKER",
                    message=f"Success in HALF_OPEN ({self._consecutive_successes}/{self.success_threshold})",
                    breaker=self.name,
                    consecutive_successes=self._consecutive_successes,
                    success_threshold=self.success_threshold,
                )
            except ImportError:
                # Gateway not available
                ...
            except (AttributeError, KeyError, TypeError) as e:
                # Gateway interface mismatch
                print(f"[CIRCUIT_BREAKER] Gateway debug log failed: {type(e).__name__}: {e}", file=sys.stderr)
            except RuntimeError:
                # Gateway runtime error
                ...

            # NEW: Require N consecutive successes to close
            if self._consecutive_successes >= self.success_threshold:
                try:
                    execute_operation(
                        GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id,
                        scope="CIRCUIT_BREAKER",
                        message="Success threshold reached - closing circuit",
                        breaker=self.name,
                    )
                except (ImportError, AttributeError):
                    # Optional dependency - continue if unavailable
                    ...
                self._record_state_transition(
                    CircuitState.CLOSED,
                    reason=f"Success threshold reached: {self._consecutive_successes}/{self.success_threshold}",
                    correlation_id=correlation_id,
                )
                self.state = CircuitState.CLOSED
                self._consecutive_successes = 0
                self._failure_records.clear()
                self._failure_count = 0
                self.failures = 0
                self._half_open_call_count = 0
        else:
            # CLOSED state: clear failures on success (standard pattern)
            self._failure_records.clear()
            self._failure_count = 0
            self.failures = 0

    def _on_failure(self, correlation_id: str, error: Exception):
        """Handle failed call with rolling window failure tracking.

        Records failure details, cleans stale failures, and trips circuit
        if threshold exceeded within the rolling window.

            error: The exception that occurred

        """

        self._failed_calls += 1

        # NEW: Create FailureRecord for post-mortem analysis
        failure_record = FailureRecord(
            timestamp=time.time(),
            exception=error,
            error_type=type(error).__name__,
        )

        # NEW: Add to rolling window
        self._failure_records.append(failure_record)
        self._failure_count = len(self._failure_records)

        # NEW: Clean stale failures before threshold check
        self._clean_stale_failures()

        # NEW: Update backward compatibility attributes
        self.failures = self._failure_count
        self.last_failure_time = (
            self._failure_records[-1].timestamp if self._failure_records else None
        )

        # NEW: Reset consecutive successes on any failure
        self._consecutive_successes = 0

        # Log failure with rolling window context
        try:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id,
                scope="CIRCUIT_BREAKER",
                message=f"Call failed - failures: {self._failure_count}/{self.failure_threshold} (window: {self.rolling_window}s)",
                breaker=self.name,
                error=str(error),
                error_type=type(error).__name__,
                failure_count=self._failure_count,
            )
        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        # NEW: Handle HALF_OPEN failure (conservative: immediate OPEN)
        if self.state == CircuitState.HALF_OPEN:
            try:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=correlation_id,
                    scope="CIRCUIT_BREAKER",
                    message="Failure in HALF_OPEN - reopening circuit",
                    breaker=self.name,
                )
            except ImportError:
                # Gateway not available
                ...
            except (AttributeError, KeyError, TypeError) as e:
                # Gateway interface mismatch
                print(f"[CIRCUIT_BREAKER] Gateway debug log failed: {type(e).__name__}: {e}", file=sys.stderr)
            except RuntimeError:
                # Gateway runtime error
                ...
            self._record_state_transition(
                CircuitState.OPEN,
                reason="Failure in HALF_OPEN state",
                correlation_id=correlation_id,
            )
            self.state = CircuitState.OPEN
            self._half_open_call_count = 0
            return  # Early return, skip threshold check

        # Use rolling window count for threshold comparison
        if self._failure_count >= self.failure_threshold:
            try:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=correlation_id,
                    scope="CIRCUIT_BREAKER",
                    message="Threshold exceeded - opening circuit",
                    breaker=self.name,
                    failure_count=self._failure_count,
                )
            except ImportError:
                # Gateway not available
                ...
            except (AttributeError, KeyError, TypeError) as e:
                # Gateway interface mismatch
                print(f"[CIRCUIT_BREAKER] Gateway debug log failed: {type(e).__name__}: {e}", file=sys.stderr)
            except RuntimeError:
                # Gateway runtime error
                ...
            self._record_state_transition(
                CircuitState.OPEN,
                reason=f"Failure threshold exceeded: {self._failure_count}/{self.failure_threshold}",
                correlation_id=correlation_id,
            )
            self.state = CircuitState.OPEN
            self._half_open_call_count = 0

    def reset(self):
        """Reset circuit breaker state to initial conditions.

        Clears all failure records, resets counters, and returns circuit
        to CLOSED state.
        """
        self.state = CircuitState.CLOSED
        self._failure_records.clear()
        self._failure_count = 0
        self.failures = 0  # Backward compatibility
        self.last_failure_time = None  # Backward compatibility
        self._consecutive_successes = 0
        self._half_open_call_count = 0

    def get_state(self) -> dict[str, Any]:
        """Get current circuit breaker state with enhanced reporting.

            Dict containing:
                - name: Circuit breaker identifier
                - state: Current state (closed/open/half_open)
                - failures: Rolling window failure count
                - threshold: Failure threshold
                - timeout: Timeout in seconds
                - last_failure: Timestamp of most recent failure
                - config: Configuration parameters
                - half_open: HALF_OPEN state details (if applicable)
                - recent_failures: Last 10 failure records
                - statistics: Call statistics

        """
        # Get last failure timestamp from records
        last_failure = (
            self._failure_records[-1].timestamp if self._failure_records else None
        )

        # Build state dictionary
        state_dict = {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failure_count,  # Rolling window count
            "threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure": last_failure,
            # NEW: Configuration snapshot
            "config": {
                "success_threshold": self.success_threshold,
                "rolling_window": self.rolling_window,
                "half_open_max_calls": self.half_open_max_calls,
                "max_failure_records": self._failure_records.maxlen,
            },
            # NEW: Half-open tracking (only present when in HALF_OPEN)
            "half_open": {
                "consecutive_successes": self._consecutive_successes,
                "call_count": self._half_open_call_count,
            } if self.state == CircuitState.HALF_OPEN else None,
            # NEW: Recent failures (last 10) for debugging
            "recent_failures": [
                {
                    "timestamp": f.timestamp,
                    "error_type": f.error_type,
                    "error": str(f.exception),
                }
                for f in list(self._failure_records)[-10:]
            ] if self._failure_records else [],
            # Statistics (unchanged)
            "statistics": {
                "total_calls": self._total_calls,
                "successful_calls": self._successful_calls,
                "failed_calls": self._failed_calls,
                "rejected_calls": self._rejected_calls,
            },
            # NEW: State transition metrics (2026-03-25 enhancement)
            "state_transitions": {
                "transition_counts": dict(self._state_transitions),
                "last_state_change": self._last_state_change_time,
                "current_state_duration": time.time() - self._last_state_change_time,
                "previous_state": self._previous_state.value if self._previous_state else None,
            },
            # NEW: Recent transition history (last 20 transitions)
            "transition_history": list(self._transition_history),
        }

        return state_dict


__all__ = ["CircuitBreaker", "CircuitState"]
