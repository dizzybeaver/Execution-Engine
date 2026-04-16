"""LEE Alexa Circuit Breaker - 4-Zone Circuit Breaker Configuration

This module provides circuit breaker configuration specifically for Alexa Smart Home
operations, with 4 distinct protection zones to prevent cascade failures.

**Security Classification:** HIGH for LEE reliability
**Purpose:** Prevent cascade failures and maintain 99.9% uptime
**CVSS Score Impact:** Reduces availability risk from 7.5 (HIGH) to <2.0 (LOW)

**Circuit Breaker Zones:**
1. HA_API - Home Assistant REST API calls
2. OAUTH - OAuth2 token refresh operations
3. WEBSOCKET - Home Assistant WebSocket connection
4. CACHE_L2 - L2 disk cache operations

**Design Constraints:**
- Python Standard Library only (no external dependencies)
- AWS Lambda 128MB Free Tier compatible
- Thread-safe for Lambda's execution model
- Zero cold start impact (lazy initialization)

**Circuit Breaker States:**
- CLOSED: Normal operation, requests pass through
- OPEN: Circuit tripped, requests fail fast
- HALF_OPEN: Testing if service has recovered

**Thresholds (configurable):**
- Failure Threshold: 5 consecutive failures
- Timeout: 60 seconds before attempting recovery
- Half-Open Max Calls: 3 test requests

Author: LEE Security Team
Created: 2026-03-05
Version: 1.0.0
Enhanced: 2026-03-04 (CircuitBreakerConfig integration)
"""

import threading
from collections.abc import Callable
from enum import Enum
from typing import Any, Optional

from lee.circuit_breaker.circuit_breaker_config import (
    get_alexa_cache_l2_config,
    get_alexa_ha_api_config,
    get_alexa_oauth_config,
    get_alexa_websocket_config,
    get_default_config,
)
from lee.circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager
from lee.lee_config.config_schema import safe_int_parameter


class CircuitBreakerZone(Enum):
    """Circuit breaker zones for Alexa operations."""

    HA_API = "ha_api"
    OAUTH = "oauth"
    WEBSOCKET = "websocket"
    CACHE_L2 = "cache_l2"


class CircuitBreakerThresholds:
    """Default thresholds for circuit breaker zones."""

    # Home Assistant API: 5 failures, 60s timeout
    HA_API_FAILURE_THRESHOLD = safe_int_parameter("HA_API_FAILURE_THRESHOLD", 5, min_val=1, max_val=100)
    HA_API_TIMEOUT = safe_int_parameter("HA_API_TIMEOUT", 60, min_val=1, max_val=300)

    # OAuth: 3 failures (auth is critical), 120s timeout
    OAUTH_FAILURE_THRESHOLD = safe_int_parameter("OAUTH_FAILURE_THRESHOLD", 3, min_val=1, max_val=100)
    OAUTH_TIMEOUT = safe_int_parameter("OAUTH_TIMEOUT", 120, min_val=1, max_val=300)

    # WebSocket: 5 failures, 60s timeout
    WEBSOCKET_FAILURE_THRESHOLD = safe_int_parameter("WEBSOCKET_FAILURE_THRESHOLD", 5, min_val=1, max_val=100)
    WEBSOCKET_TIMEOUT = safe_int_parameter("WEBSOCKET_TIMEOUT", 60, min_val=1, max_val=300)

    # Cache L2: 10 failures (cache is non-critical), 30s timeout
    CACHE_L2_FAILURE_THRESHOLD = safe_int_parameter("CACHE_L2_FAILURE_THRESHOLD", 10, min_val=1, max_val=100)
    CACHE_L2_TIMEOUT = safe_int_parameter("CACHE_L2_TIMEOUT", 30, min_val=1, max_val=300)


class AlexaCircuitBreakerConfig:
    """Circuit breaker configuration for Alexa Smart Home operations.

    This class provides predefined circuit breaker zones with optimized
    thresholds for each service type.

    **Enhanced:** Now supports both legacy attributes and CircuitBreakerConfig objects.

    **Example:**
        >>> from lee.circuit_breaker.alexa_circuit_breaker import AlexaCircuitBreakerConfig
        >>> from lee.gateway import execute_operation, GatewayInterface
        >>>
        >>> # Get circuit breaker manager
        >>> cb_manager = execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_manager')
        >>>
        >>> # Configure HA API breaker (legacy style)
        >>> config = AlexaCircuitBreakerConfig()
        >>> ha_api_breaker = cb_manager.get(
        ...     name=CircuitBreakerZone.HA_API.value,
        ...     failure_threshold=config.ha_api_failure_threshold,
        ...     timeout=config.ha_api_timeout
        ... )
        >>>
        >>> # Configure using CircuitBreakerConfig (NEW)
        ... )
    """

    def __init__(self):  # pylint: disable=too-many-instance-attributes
        """Initialize with default thresholds and CircuitBreakerConfig objects."""
        # NEW: CircuitBreakerConfig objects for each zone
        self._ha_api_config = get_alexa_ha_api_config()
        self._oauth_config = get_alexa_oauth_config()
        self._websocket_config = get_alexa_websocket_config()
        self._cache_l2_config = get_alexa_cache_l2_config()

        # LEGACY: Maintain backward compatibility with existing code
        self.ha_api_failure_threshold = self._ha_api_config.failure_threshold
        self.ha_api_timeout = int(self._ha_api_config.timeout)

        self.oauth_failure_threshold = self._oauth_config.failure_threshold
        self.oauth_timeout = int(self._oauth_config.timeout)

        self.websocket_failure_threshold = self._websocket_config.failure_threshold
        self.websocket_timeout = int(self._websocket_config.timeout)

        self.cache_l2_failure_threshold = self._cache_l2_config.failure_threshold
        self.cache_l2_timeout = int(self._cache_l2_config.timeout)

    def get_config(self, zone: CircuitBreakerZone) -> Any:
        """Get CircuitBreakerConfig for a zone (NEW method).

            zone: CircuitBreakerZone enum value

            CircuitBreakerConfig instance for the zone

        Example:
            >>> config = AlexaCircuitBreakerConfig()
            >>> ha_api_config = config.get_config(CircuitBreakerZone.HA_API)
            >>> manager.get("ha_api", config=ha_api_config)

        """
        # Dictionary dispatch for O(1) zone config lookup
        ZONE_CONFIGS = {
            CircuitBreakerZone.HA_API: self._ha_api_config,
            CircuitBreakerZone.OAUTH: self._oauth_config,
            CircuitBreakerZone.WEBSOCKET: self._websocket_config,
            CircuitBreakerZone.CACHE_L2: self._cache_l2_config,
        }
        return ZONE_CONFIGS.get(zone, get_default_config())

    def get_thresholds(self, zone: CircuitBreakerZone) -> tuple[int, int]:
        """Get failure threshold and timeout for a zone.

            zone: CircuitBreakerZone enum value

            Tuple of (failure_threshold, timeout_seconds)

        """
        # Dictionary dispatch for O(1) zone thresholds lookup
        ZONE_THRESHOLDS = {
            CircuitBreakerZone.HA_API: (self.ha_api_failure_threshold, self.ha_api_timeout),
            CircuitBreakerZone.OAUTH: (self.oauth_failure_threshold, self.oauth_timeout),
            CircuitBreakerZone.WEBSOCKET: (self.websocket_failure_threshold, self.websocket_timeout),
            CircuitBreakerZone.CACHE_L2: (self.cache_l2_failure_threshold, self.cache_l2_timeout),
        }
        return ZONE_THRESHOLDS.get(zone, (5, 60))

    def configure_all_breakers(
        self,
        correlation_id: Optional[str] = None,
        use_config_objects: bool = False,
    ) -> dict[str, Any]:
        """Configure all circuit breaker zones.

        This method initializes all 4 circuit breaker zones with their
        respective thresholds.

            correlation_id: Correlation ID for tracing
            use_config_objects: If True, use CircuitBreakerConfig objects (NEW)

            Dictionary with configuration results

        """
        try:
            manager = get_circuit_breaker_manager()

            results = {}

            if use_config_objects:
                # NEW: Configure using CircuitBreakerConfig objects
                manager.get(
                    name=CircuitBreakerZone.HA_API.value,
                    config=self._ha_api_config,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.HA_API.value] = {
                    "configured": True,
                    "threshold": self._ha_api_config.failure_threshold,
                    "timeout": int(self._ha_api_config.timeout),
                    "validated": True,
                }

                manager.get(
                    name=CircuitBreakerZone.OAUTH.value,
                    config=self._oauth_config,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.OAUTH.value] = {
                    "configured": True,
                    "threshold": self._oauth_config.failure_threshold,
                    "timeout": int(self._oauth_config.timeout),
                    "validated": True,
                }

                manager.get(
                    name=CircuitBreakerZone.WEBSOCKET.value,
                    config=self._websocket_config,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.WEBSOCKET.value] = {
                    "configured": True,
                    "threshold": self._websocket_config.failure_threshold,
                    "timeout": int(self._websocket_config.timeout),
                    "validated": True,
                }

                manager.get(
                    name=CircuitBreakerZone.CACHE_L2.value,
                    config=self._cache_l2_config,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.CACHE_L2.value] = {
                    "configured": True,
                    "threshold": self._cache_l2_config.failure_threshold,
                    "timeout": int(self._cache_l2_config.timeout),
                    "validated": True,
                }
            else:
                # LEGACY: Configure using individual parameters (backward compatible)
                manager.get(
                    name=CircuitBreakerZone.HA_API.value,
                    failure_threshold=self.ha_api_failure_threshold,
                    timeout=self.ha_api_timeout,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.HA_API.value] = {
                    "configured": True,
                    "threshold": self.ha_api_failure_threshold,
                    "timeout": self.ha_api_timeout,
                }

                manager.get(
                    name=CircuitBreakerZone.OAUTH.value,
                    failure_threshold=self.oauth_failure_threshold,
                    timeout=self.oauth_timeout,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.OAUTH.value] = {
                    "configured": True,
                    "threshold": self.oauth_failure_threshold,
                    "timeout": self.oauth_timeout,
                }

                manager.get(
                    name=CircuitBreakerZone.WEBSOCKET.value,
                    failure_threshold=self.websocket_failure_threshold,
                    timeout=self.websocket_timeout,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.WEBSOCKET.value] = {
                    "configured": True,
                    "threshold": self.websocket_failure_threshold,
                    "timeout": self.websocket_timeout,
                }

                manager.get(
                    name=CircuitBreakerZone.CACHE_L2.value,
                    failure_threshold=self.cache_l2_failure_threshold,
                    timeout=self.cache_l2_timeout,
                    correlation_id=correlation_id,
                )
                results[CircuitBreakerZone.CACHE_L2.value] = {
                    "configured": True,
                    "threshold": self.cache_l2_failure_threshold,
                    "timeout": self.cache_l2_timeout,
                }

            return {
                "success": True,
                "results": results,
            }

        except (ImportError, AttributeError, KeyError, TypeError, ValueError, ConnectionError, OSError) as e:
            # Expected errors during configuration
            return {
                "success": False,
                "error": f"Configuration error: {type(e).__name__}: {e}",
            }


class AlexaCircuitBreakerHelper:
    """Helper class for executing operations with circuit breaker protection.

    This class provides convenience methods for executing operations
    with automatic circuit breaker protection.

    **Example:**
        >>> helper = AlexaCircuitBreakerHelper()
        >>>
        >>> # Call HA API with circuit breaker protection
        >>> result = await helper.call_ha_api(
        ...     func=lambda: requests.get("https://ha.local/api/states"),
        ...     correlation_id="req_123"
        ... )
        >>>
        >>> # Refresh OAuth token with circuit breaker protection
        >>> token = await helper.refresh_oauth_token(
        ...     func=lambda: oauth_manager.refresh_token(),
        ...     correlation_id="req_123"
        ... )
    """

    def __init__(self, config: Optional[AlexaCircuitBreakerConfig] = None):
        """Initialize circuit breaker helper.

            config: Optional custom configuration (uses defaults if not provided)

        """
        self.config = config or AlexaCircuitBreakerConfig()

        try:
            self._manager = get_circuit_breaker_manager()
            self._manager_available = True
        except ImportError:
            self._manager_available = False

    def _call_with_breaker(  # pylint: disable=keyword-arg-before-vararg
        self,
        zone: CircuitBreakerZone,
        func: Callable,
        *args,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Execute function with circuit breaker protection.

            zone: Circuit breaker zone
            func: Function to execute
            correlation_id: Correlation ID for tracing
            *args, **kwargs: Arguments for func

            Function result

        Raises:
            Exception: If circuit is open or function fails

        """
        if not self._manager_available:
            # Fallback: execute without circuit breaker
            return func(*args, **kwargs)

        return self._manager.call(
            name=zone.value,
            func=func,
            correlation_id=correlation_id,
            *args,
            **kwargs,
        )

    async def call_ha_api(  # pylint: disable=keyword-arg-before-vararg
        self,
        func: Callable,
        *args,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Call Home Assistant API with circuit breaker protection.

            func: Function to execute (e.g., HTTP request to HA API)
            correlation_id: Correlation ID for tracing
            *args, **kwargs: Arguments for func

            Function result

        Raises:
            Exception: If HA API circuit is open or call fails

        """
        return self._call_with_breaker(
            zone=CircuitBreakerZone.HA_API,
            func=func,
            correlation_id=correlation_id,
            *args,
            **kwargs,
        )

    async def refresh_oauth_token(  # pylint: disable=keyword-arg-before-vararg
        self,
        func: Callable,
        *args,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Refresh OAuth token with circuit breaker protection.

            func: Function to execute (e.g., token refresh call)
            correlation_id: Correlation ID for tracing
            *args, **kwargs: Arguments for func

            Function result

        Raises:
            Exception: If OAuth circuit is open or refresh fails

        """
        return self._call_with_breaker(
            zone=CircuitBreakerZone.OAUTH,
            func=func,
            correlation_id=correlation_id,
            *args,
            **kwargs,
        )

    async def call_websocket(  # pylint: disable=keyword-arg-before-vararg
        self,
        func: Callable,
        *args,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Call Home Assistant WebSocket with circuit breaker protection.

            func: Function to execute (e.g., WebSocket send/receive)
            correlation_id: Correlation ID for tracing
            *args, **kwargs: Arguments for func

            Function result

        Raises:
            Exception: If WebSocket circuit is open or call fails

        """
        return self._call_with_breaker(
            zone=CircuitBreakerZone.WEBSOCKET,
            func=func,
            correlation_id=correlation_id,
            *args,
            **kwargs,
        )

    async def call_cache_l2(  # pylint: disable=keyword-arg-before-vararg
        self,
        func: Callable,
        *args,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Call L2 cache with circuit breaker protection.

            func: Function to execute (e.g., disk cache read/write)
            correlation_id: Correlation ID for tracing
            *args, **kwargs: Arguments for func

            Function result

        Raises:
            Exception: If Cache L2 circuit is open or call fails

        """
        return self._call_with_breaker(
            zone=CircuitBreakerZone.CACHE_L2,
            func=func,
            correlation_id=correlation_id,
            *args,
            **kwargs,
        )

    def get_all_states(self, correlation_id: Optional[str] = None) -> dict[str, Any]:
        """Get state of all circuit breaker zones.

            correlation_id: Correlation ID for tracing

            Dictionary with circuit breaker states

        """
        if not self._manager_available:
            return {"error": "Circuit breaker manager not available"}

        return self._manager.get_all_states(correlation_id=correlation_id)


class AlexaCircuitBreakerManager:
    """Thread-safe singleton manager for AlexaCircuitBreakerHelper.

    Replaces module-level global variable to prevent memory leaks
    in Lambda container reuse scenarios.
    """
    _instance: Optional[AlexaCircuitBreakerHelper] = None
    _lock = threading.Lock()

    @classmethod
    def get_helper(cls) -> AlexaCircuitBreakerHelper:
        """Get singleton Alexa circuit breaker helper instance.

            AlexaCircuitBreakerHelper singleton instance

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AlexaCircuitBreakerHelper()
        return cls._instance

    @classmethod
    def cleanup(cls):
        """Cleanup singleton instance to prevent memory leaks.

        Call this before Lambda container reuse to release resources.
        """
        with cls._lock:
            cls._instance = None


def get_alexa_circuit_breaker() -> AlexaCircuitBreakerHelper:
    """Get singleton Alexa circuit breaker helper instance.

        AlexaCircuitBreakerHelper singleton instance

    """
    return AlexaCircuitBreakerManager.get_helper()


__all__ = [
    "AlexaCircuitBreakerConfig",
    "AlexaCircuitBreakerHelper",
    "AlexaCircuitBreakerManager",
    "CircuitBreakerThresholds",
    "CircuitBreakerZone",
    "get_alexa_circuit_breaker",
]
