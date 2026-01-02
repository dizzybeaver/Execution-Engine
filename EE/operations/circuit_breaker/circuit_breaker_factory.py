"""
Circuit Breaker Factory - Operations Domain

Fault tolerance and circuit breaker pattern implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

from enum import Enum
from typing import Any, Dict, Optional, Callable
import threading
import time
import logging


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovery occurred


# =============================================================================
# Module-level circuit breaker storage (shared across all instances)
# =============================================================================

_CIRCUIT_BREAKERS: Dict[str, Dict] = {}
_CB_LOCK = threading.RLock()


# =============================================================================
# Circuit Breaker Factory Class
# =============================================================================

class CircuitBreakerFactory:
    """Circuit breaker operations factory.

    Implements circuit breaker pattern for fault tolerance.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    - Uses module-level storage for persistence
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize circuit breaker factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def execute(
        self,
        name: str,
        func: Callable,
        *args,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        **kwargs
    ) -> Any:
        """Execute function through circuit breaker.

        Args:
            name: Circuit breaker name
            func: Function to execute
            *args: Function arguments
            failure_threshold: Failures before opening
            timeout: Seconds to wait before trying again
            success_threshold: Successes to close circuit
            **kwargs: Additional parameters

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        with _CB_LOCK:
            # Get or create circuit breaker
            if name not in _CIRCUIT_BREAKERS:
                _CIRCUIT_BREAKERS[name] = {
                    "state": CircuitState.CLOSED,
                    "failure_count": 0,
                    "success_count": 0,
                    "last_failure_time": None,
                    "opened_at": None,
                }

            cb = _CIRCUIT_BREAKERS[name]

            # Check if circuit is open
            if cb["state"] == CircuitState.OPEN:
                # Check if timeout has passed
                if (
                    cb["opened_at"] is not None
                    and time.time() - cb["opened_at"] >= timeout
                ):
                    # Transition to half-open
                    cb["state"] = CircuitState.HALF_OPEN
                    cb["success_count"] = 0
                    self.logger.info(f"Circuit breaker '{name}' transitioned to HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker '{name}' is OPEN")

            # Execute function
            try:
                result = func(*args, **kwargs)

                # Success
                if cb["state"] == CircuitState.HALF_OPEN:
                    cb["success_count"] += 1
                    if cb["success_count"] >= success_threshold:
                        cb["state"] = CircuitState.CLOSED
                        cb["failure_count"] = 0
                        self.logger.info(f"Circuit breaker '{name}' transitioned to CLOSED")

                elif cb["state"] == CircuitState.CLOSED:
                    cb["failure_count"] = 0

                return result

            except Exception as e:
                # Failure
                cb["failure_count"] += 1
                cb["last_failure_time"] = time.time()

                if cb["failure_count"] >= failure_threshold:
                    old_state = cb["state"]
                    cb["state"] = CircuitState.OPEN
                    cb["opened_at"] = time.time()
                    self.logger.warning(
                        f"Circuit breaker '{name}' transitioned to OPEN "
                        f"after {cb['failure_count']} failures"
                    )

                raise e

    def get_state(self, name: str, **kwargs) -> Optional[str]:
        """Get circuit breaker state.

        Args:
            name: Circuit breaker name
            **kwargs: Additional parameters

        Returns:
            Circuit state or None if not found
        """
        with _CB_LOCK:
            cb = _CIRCUIT_BREAKERS.get(name)
            if cb:
                return cb["state"].value
            return None

    def reset(self, name: str, **kwargs) -> bool:
        """Reset circuit breaker to closed state.

        Args:
            name: Circuit breaker name
            **kwargs: Additional parameters

        Returns:
            True if reset successful
        """
        with _CB_LOCK:
            if name in _CIRCUIT_BREAKERS:
                _CIRCUIT_BREAKERS[name] = {
                    "state": CircuitState.CLOSED,
                    "failure_count": 0,
                    "success_count": 0,
                    "last_failure_time": None,
                    "opened_at": None,
                }
                self.logger.info(f"Circuit breaker '{name}' reset to CLOSED")
                return True
            return False

    def get_stats(self, name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get circuit breaker statistics.

        Args:
            name: Circuit breaker name
            **kwargs: Additional parameters

        Returns:
            Circuit breaker statistics or None if not found
        """
        with _CB_LOCK:
            cb = _CIRCUIT_BREAKERS.get(name)
            if cb:
                return {
                    "name": name,
                    "state": cb["state"].value,
                    "failure_count": cb["failure_count"],
                    "success_count": cb["success_count"],
                    "last_failure_time": cb["last_failure_time"],
                    "opened_at": cb["opened_at"],
                }
            return None


__all__ = [
    "CircuitBreakerFactory",
    "CircuitState",
]
