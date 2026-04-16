"""initialization/initialization_manager.py
Version: 2025-12-13_1
Purpose: Lambda initialization manager with singleton pattern (thread-safe)
License: Apache 2.0

CHANGES (2026-04-09):
- CRITICAL: Added thread safety with double-checked locking pattern
- Lambda CAN have concurrent executions - lock required
"""

import threading
import time
from collections import deque
from enum import Enum
from typing import Any, Optional

from lee.gateway.gateway_core import generate_correlation_id

# Lazy imports for gateway operations to avoid circular dependency
_gateway_imported = False
_GatewayInterface = None
_execute_operation = None

def _get_gateway():
    """Lazy import gateway functions to avoid circular dependency."""
    global _gateway_imported, _GatewayInterface, _execute_operation
    if not _gateway_imported:
        try:
            from lee.gateway import GatewayInterface, execute_operation
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _gateway_imported = True
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
    return _GatewayInterface, _execute_operation


class InitializationOperation(Enum):
    """Enumeration of all initialization operations."""

    INITIALIZE = "initialize"
    GET_CONFIG = "get_config"
    IS_INITIALIZED = "is_initialized"
    RESET = "reset"
    GET_STATUS = "get_status"
    GET_STATS = "get_stats"
    SET_FLAG = "set_flag"
    GET_FLAG = "get_flag"


class InitializationCore:
    """Main manager class for Lambda initialization with SINGLETON pattern and idempotency.

    Purpose:
    - Manage Lambda initialization lifecycle
    - Store configuration and flags
    - Enforce rate limits
    - Track initialization state
    """

    def __init__(self, correlation_id: str = None, **_kwargs):
        """Initialize InitializationCore."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="InitializationCore.__init__ called")

        self._initialized = False
        self._config: dict[str, Any] = {}
        self._flags: dict[str, Any] = {}
        self._init_timestamp: Optional[float] = None
        self._init_duration_ms: Optional[float] = None

        # Rate limiting (1000 ops/sec)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0

    def _check_rate_limit(self) -> bool:
        """Check if operation is within rate limit.

        Returns:
            True if allowed, False if rate limited
        """
        current_time_ms = int(time.time() * 1000)

        # Remove old entries
        while self._rate_limiter and (current_time_ms - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()

        # Check limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False

        self._rate_limiter.append(current_time_ms)
        return True

    def initialize(
        self, config: dict[str, Any] = None, correlation_id: str = None, **kwargs
    ) -> dict[str, Any]:
        """Initialize Lambda environment with idempotency guarantee.

        Args:
            config: Optional configuration dictionary
            correlation_id: Optional correlation ID for debug tracking
            **kwargs: Additional configuration items (merged with config)

        Returns:
            Initialization status dictionary
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="initialize called")

        if not self._check_rate_limit():
            return {"status": "rate_limited", "rate_limited_count": self._rate_limited_count}

        # Idempotency check
        if self._initialized:
            return {
                "status": "already_initialized",
                "cached": True,
                "timestamp": self._init_timestamp,
                "init_duration_ms": self._init_duration_ms,
                "uptime_seconds": time.time() - self._init_timestamp
                if self._init_timestamp
                else 0,
                "config_keys": list(self._config.keys()),
            }

        # Perform initialization
        start_time = time.time()
        self._init_timestamp = start_time

        # Merge config
        if config:
            self._config.update(config)
        if kwargs:
            self._config.update(kwargs)

        self._initialized = True
        end_time = time.time()
        self._init_duration_ms = (end_time - start_time) * 1000

        return {
            "status": "initialized",
            "cached": False,
            "timestamp": self._init_timestamp,
            "duration_ms": self._init_duration_ms,
            "config_keys": list(self._config.keys()),
        }

    def get_config(self, correlation_id: str = None) -> dict[str, Any]:
        """Get initialization configuration.

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Copy of configuration dictionary
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="get_config called")

        if not self._check_rate_limit():
            return {}

        return dict(self._config)

    def is_initialized(self, correlation_id: str = None) -> bool:
        """Check if Lambda environment is initialized.

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            True if initialized, False otherwise
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="is_initialized called")

        if not self._check_rate_limit():
            return False

        return self._initialized

    def reset(self, correlation_id: str = None) -> dict[str, Any]:
        """Reset initialization state (lifecycle management).

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Reset status dictionary
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="reset called")

        was_initialized = self._initialized

        self._initialized = False
        self._config.clear()
        self._flags.clear()
        self._init_timestamp = None
        self._init_duration_ms = None
        self._rate_limiter.clear()
        self._rate_limited_count = 0

        return {
            "status": "reset",
            "was_initialized": was_initialized,
            "timestamp": time.time(),
        }

    def get_status(self, correlation_id: str = None) -> dict[str, Any]:
        """Get comprehensive initialization status.

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Comprehensive status dictionary
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="get_status called")

        uptime_seconds = 0
        if self._init_timestamp:
            uptime_seconds = time.time() - self._init_timestamp

        return {
            "initialized": self._initialized,
            "config": dict(self._config),
            "flags": dict(self._flags),
            "init_timestamp": self._init_timestamp,
            "init_duration_ms": self._init_duration_ms,
            "uptime_seconds": uptime_seconds,
            "flag_count": len(self._flags),
            "config_keys": list(self._config.keys()),
            "rate_limited_count": self._rate_limited_count,
        }

    def get_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get initialization statistics (alias for get_status).

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Statistics dictionary (same as get_status())
        """
        return self.get_status(correlation_id=correlation_id)

    def set_flag(
        self, flag_name: str, value: Any, correlation_id: str = None
    ) -> dict[str, Any]:
        """Set an initialization flag with validation.

        Args:
            flag_name: Name of flag (required, non-empty string)
            value: Value to set
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Operation result dictionary
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="set_flag called", flag_name=flag_name)

        # Validation
        if not isinstance(flag_name, str) or not flag_name:
            return {
                "success": False,
                "error": "Flag name must be a non-empty string",
                "flag_name": flag_name,
            }

        if not self._check_rate_limit():
            return {"success": False, "error": "Rate limited", "flag_name": flag_name}

        old_value = self._flags.get(flag_name)
        was_new = flag_name not in self._flags
        self._flags[flag_name] = value

        return {
            "success": True,
            "flag_name": flag_name,
            "value": value,
            "old_value": old_value,
            "was_new": was_new,
        }

    def get_flag(
        self, flag_name: str, default: Any = None, correlation_id: str = None
    ) -> Any:
        """Get initialization flag value with validation.

        Args:
            flag_name: Name of flag (required, non-empty string)
            default: Default value if flag doesn't exist
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Flag value or default
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("init")

        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="INITIALIZATION",
                             message="get_flag called", flag_name=flag_name)

        # Validation
        if not isinstance(flag_name, str) or not flag_name:
            return default

        if not self._check_rate_limit():
            return default

        return self._flags.get(flag_name, default)


# Module-level singleton (thread-safe)
_manager_core = None
_manager_core_lock = threading.Lock()


def get_initialization_manager() -> InitializationCore:
    """Get SINGLETON initialization manager instance with thread-safe lazy initialization.

    Returns:
        The singleton manager instance

    Thread Safety:
        Uses double-checked locking for Lambda concurrent execution.
        Fast path: check without lock (read-only, safe in Python)
        Slow path: acquire lock only when initialization needed
    """
    global _manager_core

    try:
        _GatewayInterface, _execute_operation = _get_gateway()
        if _GatewayInterface and _execute_operation:
            # Try gateway SINGLETON registry first
            manager = _execute_operation(
                _GatewayInterface.SINGLETON, "get", name="initialization_manager"
            )
            if manager is None:
                # Fast path: check without lock (read-only, safe in Python)
                if _manager_core is not None:
                    manager = _manager_core
                else:
                    # Slow path: acquire lock for initialization
                    with _manager_core_lock:
                        # Double-check: another thread may have initialized while we waited
                        if _manager_core is not None:
                            manager = _manager_core
                        else:
                            _manager_core = InitializationCore()
                            manager = _manager_core

                _execute_operation(
                    _GatewayInterface.SINGLETON,
                    "set",
                    name="initialization_manager",
                    instance=_manager_core,
                )
                manager = _manager_core
            return manager
    except (ImportError, OSError, IOError, ValueError, TypeError):
        # Optional dependency - continue if unavailable
        # Catch specific exceptions instead of broad Exception
        ...

    # Fallback to module-level singleton (thread-safe)
    # Fast path: check without lock (read-only, safe in Python)
    if _manager_core is not None:
        return _manager_core

    # Slow path: acquire lock for initialization
    with _manager_core_lock:
        # Double-check: another thread may have initialized while we waited
        if _manager_core is not None:
            return _manager_core

        # Initialize singleton
        _manager_core = InitializationCore()

    return _manager_core


__all__ = [
    "InitializationOperation",
    "InitializationCore",
    "get_initialization_manager",
]
