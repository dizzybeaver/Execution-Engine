"""Circuit Breaker Configuration System

This module provides immutable configuration classes for LEE circuit breakers,
with comprehensive validation and builder pattern support.

Based on UGA's circuit breaker configuration patterns, adapted for LEE's
Lambda single-threaded architecture.

Reference:
    UGA: K:/uga/uga_core/foundation/fault_tolerance/circuit_breaker/core/classes/circuit_breaker_config.py
"""

from dataclasses import dataclass, field

from lee.lee_config.constants import (
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS,
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
)
from lee.lee_config.variables import (
    CIRCUIT_BREAKER_ALEXA_HA_API_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_ALEXA_HA_API_TIMEOUT,
    CIRCUIT_BREAKER_ALEXA_OAUTH_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_ALEXA_OAUTH_TIMEOUT,
)


@dataclass(frozen=True)
class CircuitBreakerConfig:
    """Immutable configuration for LEE circuit breaker behavior.

    This frozen dataclass ensures configuration consistency by preventing
    runtime modifications. All parameters are validated during construction.

    Configuration Parameters:
        failure_threshold: Number of failures to trip circuit (CLOSED → OPEN)
        timeout: Seconds in OPEN state before attempting HALF_OPEN transition
        success_threshold: Consecutive successes required to close (HALF_OPEN → CLOSED)
        half_open_max_calls: Maximum trial calls allowed in HALF_OPEN state
        rolling_window_seconds: Time window for failure counting (0 = consecutive only)

    Example:
        >>> config = CircuitBreakerConfig(failure_threshold=5, timeout=60.0)
        >>> conservative = config.with_failure_threshold(10).with_timeout(120.0)

    """

    # Core thresholds (matching current LEE parameters)
    failure_threshold: int = field(default=CIRCUIT_BREAKER_FAILURE_THRESHOLD)
    timeout: float = field(default=float(CIRCUIT_BREAKER_RECOVERY_TIMEOUT))

    # Enhanced parameters for future capabilities
    success_threshold: int = field(default=2)
    half_open_max_calls: int = field(default=CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS)
    rolling_window_seconds: float = field(default=300.0)

    def __post_init__(self) -> None:  # pylint: disable=too-many-branches
        """Validate all configuration parameters with clear error messages.

        Raises:
            TypeError: If parameter has incorrect type
            ValueError: If parameter value is outside valid range

        """
        # Validate failure_threshold: > 0 and <= 1000
        if not isinstance(self.failure_threshold, int):
            raise TypeError(
                f"failure_threshold must be int, got {type(self.failure_threshold).__name__}",
            )
        if self.failure_threshold <= 0:
            raise ValueError(
                f"failure_threshold must be positive (got {self.failure_threshold}). "
                f"Circuit breaker with threshold <= 0 would never trip.",
            )
        if self.failure_threshold > 1000:
            raise ValueError(
                f"failure_threshold too large (max 1000, got {self.failure_threshold}). "
                f"Extremely high thresholds defeat the purpose of circuit breaking.",
            )

        # Validate timeout: > 0 and <= 3600 (1 hour)
        if not isinstance(self.timeout, (int, float)):
            raise TypeError(
                f"timeout must be int or float, got {type(self.timeout).__name__}",
            )
        if self.timeout <= 0:
            raise ValueError(
                f"timeout must be positive (got {self.timeout}). "
                f"Zero/negative timeout would prevent recovery testing.",
            )
        if self.timeout > 3600:
            raise ValueError(
                f"timeout too large (max 3600 seconds = 1 hour, got {self.timeout}). "
                f"Consider using exponential backoff for extended outages.",
            )

        # Validate success_threshold: > 0 and <= 100
        if not isinstance(self.success_threshold, int):
            raise TypeError(
                f"success_threshold must be int, got {type(self.success_threshold).__name__}",
            )
        if self.success_threshold <= 0:
            raise ValueError(
                f"success_threshold must be positive (got {self.success_threshold}). "
                f"Zero threshold would prevent circuit closure.",
            )
        if self.success_threshold > 100:
            raise ValueError(
                f"success_threshold too large (max 100, got {self.success_threshold}). "
                f"High success thresholds delay recovery unnecessarily.",
            )

        # Validate half_open_max_calls: > 0 and <= 1000
        if not isinstance(self.half_open_max_calls, int):
            raise TypeError(
                f"half_open_max_calls must be int, got {type(self.half_open_max_calls).__name__}",
            )
        if self.half_open_max_calls <= 0:
            raise ValueError(
                f"half_open_max_calls must be positive (got {self.half_open_max_calls}). "
                f"Zero calls would prevent HALF_OPEN state evaluation.",
            )
        if self.half_open_max_calls > 1000:
            raise ValueError(
                f"half_open_max_calls too large (max 1000, got {self.half_open_max_calls}). "
                f"Excessive HALF_OPEN calls could overwhelm recovering services.",
            )

        # Validate rolling_window_seconds: > 0 and <= 3600
        if not isinstance(self.rolling_window_seconds, (int, float)):
            raise TypeError(
                f"rolling_window_seconds must be int or float, got {type(self.rolling_window_seconds).__name__}",
            )
        if self.rolling_window_seconds <= 0:
            raise ValueError(
                f"rolling_window_seconds must be positive (got {self.rolling_window_seconds}). "
                f"Zero/negative window would break failure rate calculations.",
            )
        if self.rolling_window_seconds > 3600:
            raise ValueError(
                f"rolling_window_seconds too large (max 3600 seconds = 1 hour, got {self.rolling_window_seconds}). "
                f"Large windows reduce sensitivity to recent failures.",
            )

    def with_failure_threshold(self, value: int) -> "CircuitBreakerConfig":
        """Create new config with different failure threshold.

        Args:
            value: New failure threshold (must be > 0 and <= 1000)

        Returns:
            New CircuitBreakerConfig instance with updated threshold

        Example:
            >>> config = CircuitBreakerConfig()
            >>> strict = config.with_failure_threshold(3)

        """
        return CircuitBreakerConfig(
            failure_threshold=value,
            timeout=self.timeout,
            success_threshold=self.success_threshold,
            half_open_max_calls=self.half_open_max_calls,
            rolling_window_seconds=self.rolling_window_seconds,
        )

    def with_timeout(self, value: float) -> "CircuitBreakerConfig":
        """Create new config with different timeout (seconds).

        Args:
            value: New timeout in seconds (must be > 0 and <= 3600)

        Returns:
            New CircuitBreakerConfig instance with updated timeout

        Example:
            >>> config = CircuitBreakerConfig()
            >>> patient = config.with_timeout(120.0)

        """
        return CircuitBreakerConfig(
            failure_threshold=self.failure_threshold,
            timeout=value,
            success_threshold=self.success_threshold,
            half_open_max_calls=self.half_open_max_calls,
            rolling_window_seconds=self.rolling_window_seconds,
        )

    def with_success_threshold(self, value: int) -> "CircuitBreakerConfig":
        """Create new config with different success threshold.

        Args:
            value: New success threshold (must be > 0 and <= 100)

        Returns:
            New CircuitBreakerConfig instance with updated success threshold

        Example:
            >>> config = CircuitBreakerConfig()
            >>> conservative = config.with_success_threshold(3)

        """
        return CircuitBreakerConfig(
            failure_threshold=self.failure_threshold,
            timeout=self.timeout,
            success_threshold=value,
            half_open_max_calls=self.half_open_max_calls,
            rolling_window_seconds=self.rolling_window_seconds,
        )

    def with_half_open_max_calls(self, value: int) -> "CircuitBreakerConfig":
        """Create new config with different HALF_OPEN max calls.

        Args:
            value: New max calls in HALF_OPEN (must be > 0 and <= 1000)

        Returns:
            New CircuitBreakerConfig instance with updated max calls

        Example:
            >>> config = CircuitBreakerConfig()
            >>> limited = config.with_half_open_max_calls(2)

        """
        return CircuitBreakerConfig(
            failure_threshold=self.failure_threshold,
            timeout=self.timeout,
            success_threshold=self.success_threshold,
            half_open_max_calls=value,
            rolling_window_seconds=self.rolling_window_seconds,
        )

    def with_rolling_window_seconds(self, value: float) -> "CircuitBreakerConfig":
        """Create new config with different rolling window (seconds).

        Args:
            value: New rolling window in seconds (must be > 0 and <= 3600)

        Returns:
            New CircuitBreakerConfig instance with updated rolling window

        Example:
            >>> config = CircuitBreakerConfig()
            >>> short_window = config.with_rolling_window_seconds(60.0)

        """
        return CircuitBreakerConfig(
            failure_threshold=self.failure_threshold,
            timeout=self.timeout,
            success_threshold=self.success_threshold,
            half_open_max_calls=self.half_open_max_calls,
            rolling_window_seconds=value,
        )


# ============================================================================
# Default Configuration
# ============================================================================

DEFAULT_CONFIG = CircuitBreakerConfig()


def get_default_config() -> CircuitBreakerConfig:
    """Get default circuit breaker configuration.

    Returns:
        Default CircuitBreakerConfig instance with all default values

    Example:
        >>> config = get_default_config()
        >>> assert config.failure_threshold == 5
        >>> assert config.timeout == 60.0

    """
    return DEFAULT_CONFIG


# ============================================================================
# Alexa Smart Home Preset Configurations
# ============================================================================

def get_alexa_ha_api_config() -> CircuitBreakerConfig:
    """Get optimized config for Home Assistant REST API.

    Zone: HA_API
    Failure Threshold: 5 (standard reliability)
    Timeout: 60 seconds (standard recovery)

    Returns:
        CircuitBreakerConfig tuned for HA API calls

    Example:
        >>> config = get_alexa_ha_api_config()
        >>> assert config.failure_threshold == 5
        >>> assert config.timeout == 60.0

    """
    return CircuitBreakerConfig(
        failure_threshold=CIRCUIT_BREAKER_ALEXA_HA_API_FAILURE_THRESHOLD,
        timeout=CIRCUIT_BREAKER_ALEXA_HA_API_TIMEOUT,
    )


def get_alexa_oauth_config() -> CircuitBreakerConfig:
    """Get optimized config for OAuth2 token refresh.

    Zone: OAUTH
    Failure Threshold: 3 (stricter - auth is critical)
    Timeout: 120 seconds (auth requires patience)

    Returns:
        CircuitBreakerConfig tuned for OAuth operations

    Example:
        >>> config = get_alexa_oauth_config()
        >>> assert config.failure_threshold == 3
        >>> assert config.timeout == 120.0

    """
    return CircuitBreakerConfig(
        failure_threshold=CIRCUIT_BREAKER_ALEXA_OAUTH_FAILURE_THRESHOLD,
        timeout=CIRCUIT_BREAKER_ALEXA_OAUTH_TIMEOUT,
    )


def get_alexa_websocket_config() -> CircuitBreakerConfig:
    """Get optimized config for Home Assistant WebSocket.

    Zone: WEBSOCKET
    Failure Threshold: 5 (standard reliability)
    Timeout: 60 seconds (standard recovery)

    Returns:
        CircuitBreakerConfig tuned for WebSocket connections

    Example:
        >>> config = get_alexa_websocket_config()
        >>> assert config.failure_threshold == 5
        >>> assert config.timeout == 60.0

    """
    return CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60.0,
    )


def get_alexa_cache_l2_config() -> CircuitBreakerConfig:
    """Get optimized config for L2 disk cache.

    Zone: CACHE_L2
    Failure Threshold: 10 (lenient - cache is non-critical)
    Timeout: 30 seconds (fast retry for cache)

    Returns:
        CircuitBreakerConfig tuned for L2 cache operations

    Example:
        >>> config = get_alexa_cache_l2_config()
        >>> assert config.failure_threshold == 10
        >>> assert config.timeout == 30.0

    """
    return CircuitBreakerConfig(
        failure_threshold=10,
        timeout=30.0,
    )
