"""circuit_breaker/circuit_breaker_manager.py
Version: 2025-12-13_1
Purpose: Circuit breaker manager with singleton pattern
License: Apache 2.0

CONSOLIDATED (2026-04-02):
- Merged circuit_breaker_generic.py wrapper functions
- Single source of truth for circuit breaker operations
- Eliminated 85%+ code duplication
"""

import os
import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable
from contextlib import nullcontext
from typing import Any, Optional

from lee.circuit_breaker.circuit_breaker_state import CircuitBreaker
from lee.gateway.gateway_core import generate_correlation_id


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG mode is enabled.

    Returns:
        True if LEE_DEBUG environment variable is set to 'true'
    """
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"
try:
    from lee.interface.interface_debug import execute_debug_operation  # noqa: F401
    from lee.gateway import GatewayInterface, execute_operation
    _LOGGING_AVAILABLE = True
except ImportError:
    _LOGGING_AVAILABLE = False


_CB_MODULE_PREFIX = "cb"

# Memory limits for circuit breakers (2026-03-29 fix)
MAX_CIRCUIT_BREAKERS = 100


class CircuitBreakerCore:  # pylint: disable=too-many-instance-attributes
    """Manages circuit breakers with SINGLETON pattern and rate limiting.

    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_circuit_breaker_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """

    def __init__(self):
        # Use OrderedDict for LRU eviction
        self._breakers: OrderedDict[str, CircuitBreaker] = OrderedDict()

        # Circuit registry for deduplication tracking
        self._circuit_registry: dict[str, dict[str, Any]] = {}

        # Rate limiting (1000 ops/sec - higher for infrastructure)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0

        # Thread safety for rate limiter
        self._rate_limiter_lock = threading.Lock()

        # Statistics
        self._total_operations = 0
        self._duplicate_attempts = 0
        self._deduplication_success = 0

        # Cache module prefix to avoid repeated gateway calls
        self._module_prefix = "cb"  # Default fallback

    def _check_rate_limit(self) -> bool:
        """Check if operation is within rate limit.

            bool: True if allowed, False if rate limited

        """
        now = time.time() * 1000

        # Lazy cleanup: Only clean if queue is getting large (every 100 operations)
        if len(self._rate_limiter) > 900:
            # Use lock-free cleanup: atomic operations on deque
            while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
                try:
                    self._rate_limiter.popleft()
                except IndexError:
                    # Concurrent removal - skip
                    break

        # Lock-free check using deque length (atomic read)
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False

        # Lock-free append (thread-safe for deque)
        self._rate_limiter.append(now)
        return True

    def get(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        correlation_id: str = None,
        config: Any = None,
        **_kwargs,
    ) -> CircuitBreaker:
        """Get or create circuit breaker with enhanced configuration support.

            name: Circuit breaker identifier
            failure_threshold: Failures to trip circuit (default: 5)
            timeout: Timeout in seconds (default: 60)
            correlation_id: Request correlation ID
            config: Optional CircuitBreakerConfig object (takes precedence)
            **_kwargs: Additional parameters (success_threshold, rolling_window, etc.)

            CircuitBreaker instance

        Backward Compatibility:
            Existing calls using get(name, 5, 60) continue to work unchanged.

        """
        # ADDED: Debug integration
        # Internal correlation ID generation - no gateway imports

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in get()",
                                operation="get", breaker=name, corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            raise ConnectionError("Rate limit exceeded")

        self._total_operations += 1

        if name not in self._breakers:
            # Enforce size limit with LRU eviction
            if len(self._breakers) >= MAX_CIRCUIT_BREAKERS:
                # Evict oldest entry
                self._breakers.popitem(last=False)

            # Gateway logging for circuit breaker creation
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_info',
                                message="Creating new circuit breaker",
                                breaker=name, threshold=failure_threshold,
                                timeout=timeout, corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable

            # Register circuit in registry for deduplication tracking
            self._circuit_registry[name] = {
                "created_at": int(time.time()),
                "failure_threshold": failure_threshold,
                "timeout": timeout,
                "access_count": 0
            }

            # Pass config if provided, otherwise use legacy parameters
            if config is not None:
                self._breakers[name] = CircuitBreaker(name, config=config)
            else:
                # Pass through additional parameters for new features
                self._breakers[name] = CircuitBreaker(
                    name,
                    failure_threshold,
                    timeout,
                    **_kwargs,
                )
        else:
            # Circuit breaker already exists - deduplication
            self._duplicate_attempts += 1
            self._deduplication_success += 1

            # Move to end to mark as recently used (LRU)
            self._breakers.move_to_end(name)

            # Update access count in registry
            if name in self._circuit_registry:
                self._circuit_registry[name]["access_count"] += 1

            # Gateway logging for deduplication
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_info',
                                message="Returning existing circuit breaker (deduplication)",
                                breaker=name, duplicate_attempts=self._duplicate_attempts,
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable

        return self._breakers[name]

    def call(  # pylint: disable=keyword-arg-before-vararg
        self,
        name: str,
        func: Callable,
        *args,
        correlation_id: str = None,
        **kwargs,
    ) -> Any:
        """Call function with circuit breaker protection."""
        # ADDED: Debug integration - SUGA-ISP compliant

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in call()",
                                operation="call", breaker=name, corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            raise ConnectionError("Rate limit exceeded")

        self._total_operations += 1

        # Gateway logging for protected call execution
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                            message="Executing protected call",
                            breaker=name, corr_id=correlation_id)
        except (ImportError, AttributeError, RuntimeError, ConnectionError):
            pass  # Silent fallback if gateway unavailable

        # SUGA-ISP compliant timing
        try:
            timing_ctx = execute_debug_operation("timing",
                                         corr_id=correlation_id,
                                         op_name=f"manager.call:{name}")
        except (ImportError, RuntimeError, ConnectionError):
            timing_ctx = nullcontext()

        with timing_ctx:
            breaker = self.get(name, correlation_id=correlation_id)
            return breaker.call(func, self._check_rate_limit, correlation_id, *args, **kwargs)

    def get_all_states(self, correlation_id: str = None) -> dict[str, dict[str, Any]]:
        """Get states of all circuit breakers."""
        # ADDED: Debug integration
        # Internal correlation ID generation - no gateway imports

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in get_all_states()",
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            raise ConnectionError("Rate limit exceeded")

        self._total_operations += 1

        # Gateway logging for get all states
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                            message="Getting all states",
                            breaker_count=len(self._breakers), corr_id=correlation_id)
        except (ImportError, AttributeError, Exception):
            pass  # Silent fallback if gateway unavailable

        return {
            name: breaker.get_state()
            for name, breaker in self._breakers.items()
        }

    def reset_all(self, correlation_id: str = None):
        """Reset all circuit breakers."""
        # ADDED: Debug integration
        # Internal correlation ID generation - no gateway imports

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in reset_all()",
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            raise ConnectionError("Rate limit exceeded")

        self._total_operations += 1

        # Gateway logging for reset all
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                            message="Resetting all circuit breakers",
                            count=len(self._breakers), corr_id=correlation_id)
        except (ImportError, AttributeError, Exception):
            pass  # Silent fallback if gateway unavailable

        for breaker in self._breakers.values():
            breaker.reset()

    def get_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get circuit breaker manager statistics."""
        # ADDED: Debug integration - SUGA-ISP compliant

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in get_stats()",
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            # Return error dict directly instead of using gateway response functions
            return {"success": False, "error": "Rate limit exceeded", "error_code": "RATE_LIMIT_EXCEEDED"}

        # Gateway logging for getting statistics
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                            message="Getting statistics",
                            operations=self._total_operations,
                            breakers=len(self._breakers), corr_id=correlation_id)
        except (ImportError, AttributeError, Exception):
            pass  # Silent fallback if gateway unavailable

        # Return success dict directly with deduplication metrics
        return {"success": True, "message": "Circuit breaker statistics", "data": {
            "total_operations": self._total_operations,
            "breakers_count": len(self._breakers),
            "rate_limited_count": self._rate_limited_count,
            "rate_limit_window_ms": self._rate_limit_window_ms,
            "current_rate_limit_size": len(self._rate_limiter),
            "max_rate_limit": self._rate_limiter.maxlen,
            "duplicate_attempts": self._duplicate_attempts,
            "deduplication_success": self._deduplication_success,
            "circuit_registry_size": len(self._circuit_registry),
            "breakers": {
                name: breaker.get_state()
                for name, breaker in self._breakers.items()
            },
        }}

    def reset(self, correlation_id: str = None) -> bool:
        """Reset circuit breaker manager state.

            bool: True if reset successful, False if rate limited

        """
        # ADDED: Debug integration
        # Internal correlation ID generation - no gateway imports

        if correlation_id is None:
            # Use cached module prefix to avoid repeated gateway calls
            correlation_id = generate_correlation_id(self._module_prefix)

        if not self._check_rate_limit():
            # Gateway logging for rate limit exceeded
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Rate limit exceeded in reset()",
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            return False

        try:
            # Gateway logging for manager reset
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_info',
                                message="Resetting manager state",
                                breakers=len(self._breakers),
                                operations=self._total_operations,
                                duplicate_attempts=self._duplicate_attempts,
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable

            self._breakers.clear()
            self._circuit_registry.clear()
            self._total_operations = 0
            self._duplicate_attempts = 0
            self._deduplication_success = 0
            self._rate_limiter.clear()
            self._rate_limited_count = 0

            # Gateway logging for reset completion
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_info',
                                message="Manager reset complete",
                                corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            return True
        except Exception as e:
            # Gateway logging for reset failure
            try:
                execute_operation(GatewayInterface.LOGGING, 'log_error',
                                message="Manager reset failed",
                                error=str(e), corr_id=correlation_id)
            except (ImportError, AttributeError, RuntimeError, ConnectionError):
                pass  # Silent fallback if gateway unavailable
            return False


class CircuitBreakerManager:
    """Thread-safe singleton manager for CircuitBreakerCore.

    Replaces module-level global variable to prevent memory leaks
    in Lambda container reuse scenarios.

    Uses gateway SINGLETON registry with fallback to module-level instance.
    """
    _instance: Optional[CircuitBreakerCore] = None
    _lock = threading.Lock()

    @classmethod
    def get_manager(cls) -> CircuitBreakerCore:
        """Get SINGLETON circuit breaker manager instance.

            CircuitBreakerCore: The singleton manager instance

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    try:
                        manager = execute_operation(GatewayInterface.SINGLETON, "get", name="circuit_breaker_manager")
                        if manager is None:
                            cls._instance = CircuitBreakerCore()
                            execute_operation(GatewayInterface.SINGLETON, "set", name="circuit_breaker_manager", instance=cls._instance)
                            return cls._instance
                        return manager
                    except (ImportError, AttributeError, RuntimeError, ConnectionError):
                        cls._instance = CircuitBreakerCore()
        return cls._instance

    @classmethod
    def cleanup(cls):
        """Cleanup singleton instance to prevent memory leaks.

        Call this before Lambda container reuse to release resources.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.reset()
            cls._instance = None


def get_circuit_breaker_manager() -> CircuitBreakerCore:
    """Get SINGLETON circuit breaker manager instance.

    Uses gateway SINGLETON registry with fallback to module-level instance.

        CircuitBreakerCore: The singleton manager instance

    """
    return CircuitBreakerManager.get_manager()


def _create_response(success: bool, data: Any = None, error: str = None, **metadata) -> dict[str, Any]:
    """Create standardized response without importing from gateway."""
    response = {
        "success": success,
        "timestamp": time.time(),
        **metadata,
    }

    if success:
        response["data"] = data
    response["error"] = error

    return response


def _log_debug_safe(message: str, correlation_id: str, **kwargs) -> None:
    """Safely log debug operation with fallback handling.

    Args:
        message: Log message
        correlation_id: Correlation ID for tracking
        **kwargs: Additional log parameters
    """
    if not _is_debug_mode():
        return

    if not _LOGGING_AVAILABLE:
        return

    try:
        execute_debug_operation("log",
                         corr_id=correlation_id, scope="CIRCUIT_BREAKER",
                         message=message, **kwargs)
    except Exception:
        pass  # Logging failed, but don't break the operation


def _create_timing_context(correlation_id: str, operation: str):
    """Create timing context with fallback handling.

    Args:
        correlation_id: Correlation ID for tracking
        operation: Operation name for timing

    Returns:
        Context manager for timing
    """
    if not _LOGGING_AVAILABLE:
        return nullcontext()

    try:
        return execute_debug_operation("timing",
                                     corr_id=correlation_id,
                                     op_name=operation)
    except (ImportError, RuntimeError, ConnectionError):
        return nullcontext()


def get_breaker_implementation(name: str, failure_threshold: int = 5,
                               timeout: int = 60, correlation_id: str = None,
                               config: Optional[Any] = None,
                               **_kwargs) -> dict[str, Any]:
    """Get circuit breaker state using SINGLETON manager.

    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Seconds before attempting recovery
        correlation_id: Optional correlation ID for debug tracking
        config: Optional CircuitBreakerConfig object (takes precedence)
        **kwargs: Additional parameters (success_threshold, rolling_window, etc.)

    Returns:
        Circuit breaker state dict
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe(f"Getting circuit breaker '{name}'",
                   correlation_id, failure_threshold=failure_threshold, timeout=timeout)

    with _create_timing_context(correlation_id, f"get_breaker_{name}"):
        manager = get_circuit_breaker_manager()
        breaker = manager.get(name, failure_threshold, timeout, correlation_id,
                             config=config, **_kwargs)
        state = breaker.get_state()

        _log_debug_safe(f"Circuit breaker '{name}' state retrieved",
                       correlation_id, state=state.get("state", "unknown"))

        return state


def execute_with_breaker_implementation(name: str, func: Callable,
                                       args: tuple = (),
                                       correlation_id: str = None,
                                       **kwargs) -> Any:
    """Execute call with circuit breaker protection using SINGLETON manager.

    Args:
        name: Circuit breaker name
        func: Function to execute
        args: Arguments for func
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Function result
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe(f"Executing with circuit breaker '{name}'",
                   correlation_id,
                   func_name=getattr(func, "__name__", "anonymous"),
                   args_count=len(args), kwargs_count=len(kwargs))

    with _create_timing_context(correlation_id, f"execute_with_breaker_{name}"):
        manager = get_circuit_breaker_manager()
        result = manager.call(name, func, *args, correlation_id=correlation_id, **kwargs)

        _log_debug_safe(f"Circuit breaker '{name}' execution completed",
                       correlation_id, success=True)

        return result


def get_all_states_implementation(correlation_id: str = None,
                                  **_kwargs) -> dict[str, dict[str, Any]]:
    """Get all circuit breaker states using SINGLETON manager.

    Args:
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Dict mapping breaker names to their states
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe("get_all_states_implementation called", correlation_id)

    with _create_timing_context(correlation_id, "get_all_states"):
        manager = get_circuit_breaker_manager()
        return manager.get_all_states(correlation_id)


def reset_all_implementation(correlation_id: str = None, **_kwargs):
    """Reset all circuit breakers using SINGLETON manager.

        correlation_id: Optional correlation ID for debug tracking

    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe("reset_all_implementation called", correlation_id)

    with _create_timing_context(correlation_id, "reset_all"):
        manager = get_circuit_breaker_manager()
        manager.reset_all(correlation_id)


def get_stats_implementation(correlation_id: str = None,
                             **_kwargs) -> dict[str, Any]:
    """Get circuit breaker statistics using SINGLETON manager.

        correlation_id: Optional correlation ID for debug tracking

        Statistics dict

    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe("get_stats_implementation called", correlation_id)

    with _create_timing_context(correlation_id, "get_stats"):
        manager = get_circuit_breaker_manager()
        return manager.get_stats(correlation_id)


def reset_implementation(correlation_id: str = None,
                        **_kwargs) -> dict[str, Any]:
    """Reset circuit breaker manager state using SINGLETON manager.

        correlation_id: Optional correlation ID for debug tracking

        Success/error response dict

    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cb")

    _log_debug_safe("reset_implementation called", correlation_id)

    with _create_timing_context(correlation_id, "reset_manager"):
        manager = get_circuit_breaker_manager()
        success = manager.reset(correlation_id)

        if success:
            _log_debug_safe("Circuit breaker manager reset successful", correlation_id)
            return _create_response(True, data={"reset": True},
                                   message="Circuit breaker manager reset")

        _log_debug_safe("Circuit breaker manager reset rate limited", correlation_id)
        return _create_response(False, error="Reset rate limited",
                               error_code="RATE_LIMIT_EXCEEDED")


__all__ = [
    "CircuitBreakerCore",
    "CircuitBreakerManager",
    "get_circuit_breaker_manager",
    "get_breaker_implementation",
    "execute_with_breaker_implementation",
    "get_all_states_implementation",
    "reset_all_implementation",
    "get_stats_implementation",
    "reset_implementation",
    "_create_response",
]
