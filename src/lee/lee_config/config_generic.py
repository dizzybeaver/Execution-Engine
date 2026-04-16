# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-08 - Fixed thread safety, added debug tracing, removed print statements

"""config/config_core.py
Version: 2025-12-09_1
Purpose: Core configuration management with singleton pattern
License: Apache 2.0
"""

import os
import time
import threading
from collections import deque
from contextlib import nullcontext
from typing import Any

from lee.lee_config.config_state import ConfigurationState
from lee.lee_config.config_validator import ConfigurationValidator

# Lazy imports for gateway operations to avoid circular dependency
_gateway_imported = False
_GatewayInterface = None
_execute_operation = None
_generate_correlation_id = None

# Cache debug mode check at module load time
_DEBUG_MODE_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled (cached value)."""
    return _DEBUG_MODE_ENABLED

def _get_gateway():
    """Lazy import gateway functions to avoid circular dependency."""
    global _gateway_imported, _GatewayInterface, _execute_operation, _generate_correlation_id
    if not _gateway_imported:
        try:
            from lee.gateway import GatewayInterface, execute_operation
            from lee.gateway.gateway_core import generate_correlation_id
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _generate_correlation_id = generate_correlation_id
            _gateway_imported = True
        except ImportError:
            # Optional dependency - continue if unavailable
            pass
    return _GatewayInterface, _execute_operation

_config_core = None

class ConfigurationCore:
    """Configuration system core with rate limiting."""

    def __init__(self, correlation_id: str = None, **_kwargs):
        # Ensure gateway is imported before use
        _GatewayInterface, _execute_operation = _get_gateway()

        # NEW: Add debug tracing for exact failure point identification
        if correlation_id is None:
            # SUGA-ISP compliant correlation ID generation
            correlation_id = _generate_correlation_id("cfg") if _generate_correlation_id else f"cfg_{int(time.time() * 1000)}"

        # SUGA-ISP compliant debug logging
        if _is_debug_mode() and _execute_operation:
            try:
                _execute_operation(_GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="CONFIG",
                               message="ConfigurationCore.__init__ called")
            except (ImportError, AttributeError, RuntimeError):
                # Optional dependency - continue if unavailable
                pass

        # SUGA-ISP compliant timing
        if _is_debug_mode() and _execute_operation:
            try:
                timing_ctx = _execute_operation(_GatewayInterface.DEBUG, "timing",
                                             corr_id=correlation_id, scope="CONFIG",
                                             operation="ConfigurationCore.__init__")
            except (ImportError, Exception):
                timing_ctx = nullcontext()
        else:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                self._config: dict[str, Any] = {}
                self._state = ConfigurationState()
                self._validator = ConfigurationValidator()
                self._cache_prefix = "config_"
                self._initialized = False
                self._use_parameter_store = False
                self._parameter_prefix = "/lambda-execution-engine"

                # Rate limiting with thread safety
                self._rate_limiter_lock = threading.Lock()
                self._rate_limiter = deque(maxlen=1000)
                self._rate_limit_window_ms = 1000
                self._rate_limited_count = 0

                if _is_debug_mode() and _execute_operation:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="CONFIG",
                                       message="ConfigurationCore.__init__ completed", success=True)
                    except (ImportError, AttributeError, RuntimeError):
                        # Optional dependency - continue if unavailable
                        pass
            except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                if _is_debug_mode() and _execute_operation:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="CONFIG",
                                       message="ConfigurationCore.__init__ failed",
                                       error_type=type(e).__name__, error=str(e))
                    except (ImportError, AttributeError, RuntimeError):
                        # Optional dependency - continue if unavailable
                        pass
                raise

    def _check_rate_limit(self, correlation_id: str = None, **_kwargs) -> bool:
        """Check if operation should be rate limited."""
        if correlation_id is None:
            # SUGA-ISP compliant correlation ID generation
            correlation_id = _generate_correlation_id("cfg") if _generate_correlation_id else f"cfg_{int(time.time() * 1000)}"

        # Lazy import gateway to avoid circular dependency
        try:
            _GatewayInterface, _execute_operation = _get_gateway()
        except ImportError:
            _GatewayInterface = None
            _execute_operation = None

        # SUGA-ISP compliant debug logging
        if _execute_operation:
            try:
                _execute_operation(_GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="CONFIG",
                               message="_check_rate_limit called")
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                # Gateway operations may fail during initialization or if gateway unavailable
                pass

        # SUGA-ISP compliant timing
        timing_ctx = nullcontext()
        if _execute_operation:
            try:
                timing_ctx = _execute_operation(_GatewayInterface.DEBUG, "timing",
                                             corr_id=correlation_id, scope="CONFIG",
                                             operation="_check_rate_limit")
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                # Gateway operations may fail during initialization or if gateway unavailable
                pass
                timing_ctx = nullcontext()

        with timing_ctx:
            try:
                # Thread-safe rate limit check
                with self._rate_limiter_lock:
                    current_time_ms = int(time.time() * 1000)

                    # Remove old entries
                    while self._rate_limiter and \
                          (current_time_ms - self._rate_limiter[0]) > self._rate_limit_window_ms:
                        self._rate_limiter.popleft()

                    # Check limit
                    if len(self._rate_limiter) >= 1000:
                        self._rate_limited_count += 1
                        if _is_debug_mode() and _execute_operation:
                            try:
                                _execute_operation(_GatewayInterface.DEBUG, "log",
                                               corr_id=correlation_id, scope="CONFIG",
                                               message="_check_rate_limit completed",
                                               success=False, reason="Rate limit exceeded",
                                               rate_limited_count=self._rate_limited_count)
                            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                                pass
                        return True

                    self._rate_limiter.append(current_time_ms)
                    if _is_debug_mode() and _execute_operation:
                        try:
                            _execute_operation(_GatewayInterface.DEBUG, "log",
                                           corr_id=correlation_id, scope="CONFIG",
                                           message="_check_rate_limit completed",
                                           success=True, rate_limited=False)
                        except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                            pass
                    return False
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError, ValueError) as e:
                if _is_debug_mode() and _execute_operation:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="CONFIG",
                                       message="_check_rate_limit failed",
                                       error_type=type(e).__name__, error=str(e))
                    except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                        pass
                raise

    def reset(self, correlation_id: str = None, **_kwargs) -> bool:
        """Reset configuration state."""
        if correlation_id is None:
            # SUGA-ISP compliant correlation ID generation
            correlation_id = _generate_correlation_id("cfg") if _generate_correlation_id else f"cfg_{int(time.time() * 1000)}"

        # SUGA-ISP compliant debug logging
        try:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="CONFIG",
                           message="reset called")
        except ImportError:
            # Optional dependency - continue if unavailable
            pass

        # SUGA-ISP compliant timing
        try:
            _GatewayInterface, _execute_operation = _get_gateway()
            timing_ctx = _execute_operation(_GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="CONFIG",
                                         operation="reset")
        except (ImportError, Exception):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                # FIXED: Add rate limit validation to prevent resource exhaustion (CVE-CONFIG-2025-001)
                if self._check_rate_limit(correlation_id=correlation_id):
                    try:
                        _execute_operation(_GatewayInterface.LOGGING, "log_error",
                                       message="Configuration reset rate limited",
                                       rate_limited_count=self._rate_limited_count)
                    except (ImportError, Exception):
                        if _is_debug_mode() and _execute_operation:
                            try:
                                _execute_operation(_GatewayInterface.DEBUG, "log",
                                               message="Configuration reset rate limited",
                                               scope="CONFIG")
                            except (ImportError, AttributeError, RuntimeError):
                                pass
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="CONFIG",
                                       message="reset completed", success=False, reason="Rate limited")
                    except ImportError:
                        # Optional dependency - continue if unavailable
                        pass
                    return False

                self._config.clear()
                self._state = ConfigurationState()
                self._initialized = False
                self._rate_limiter.clear()
                self._rate_limited_count = 0

                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="reset completed", success=True)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                return True

            except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError) as e:
                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.LOGGING, "log_error",
                                   message=f"Config reset failed: {e}",
                                   error_type=type(e).__name__)
                except (ImportError, AttributeError, KeyError, TypeError):
                    if _is_debug_mode() and _execute_operation:
                        try:
                            _execute_operation(_GatewayInterface.DEBUG, "log",
                                           message=f"Config reset failed: {e}",
                                           scope="CONFIG")
                        except (ImportError, AttributeError, RuntimeError):
                            pass
                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="reset failed",
                                   error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                raise

    def get_stats(self, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
        """Get configuration statistics."""
        if correlation_id is None:
            # SUGA-ISP compliant correlation ID generation
            correlation_id = _generate_correlation_id("cfg") if _generate_correlation_id else f"cfg_{int(time.time() * 1000)}"

        # SUGA-ISP compliant debug logging
        try:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="CONFIG",
                           message="get_stats called")
        except ImportError:
            # Optional dependency - continue if unavailable
            pass

        # SUGA-ISP compliant timing
        try:
            _GatewayInterface, _execute_operation = _get_gateway()
            timing_ctx = _execute_operation(_GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="CONFIG",
                                         operation="get_stats")
        except (ImportError, Exception):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                stats = {
                    "initialized": self._initialized,
                    "parameter_count": len(self._config),
                    "use_parameter_store": self._use_parameter_store,
                    "rate_limited_count": self._rate_limited_count,
                    "rate_limiter_size": len(self._rate_limiter),
                }

                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="get_stats completed",
                                   success=True, parameter_count=stats["parameter_count"],
                                   initialized=stats["initialized"])
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                return stats
            except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="get_stats failed",
                                   error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                raise


def get_config_manager(correlation_id: str = None, **_kwargs) -> ConfigurationCore:
    """Get configuration manager singleton.

    Uses SINGLETON pattern for lifecycle management.
    Attempts gateway registration, falls back to module-level singleton.
    """
    if correlation_id is None:
        # SUGA-ISP compliant correlation ID generation
        correlation_id = _generate_correlation_id("cfg") if _generate_correlation_id else f"cfg_{int(time.time() * 1000)}"

    # SUGA-ISP compliant debug logging
    try:
        _GatewayInterface, _execute_operation = _get_gateway()
        _execute_operation(_GatewayInterface.DEBUG, "log",
                       corr_id=correlation_id, scope="CONFIG",
                       message="get_config_manager called")
    except ImportError:
        # Optional dependency - continue if unavailable
        pass

    # SUGA-ISP compliant timing
    try:
        _GatewayInterface, _execute_operation = _get_gateway()
        timing_ctx = _execute_operation(_GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id, scope="CONFIG",
                                     operation="get_config_manager")
    except (ImportError, Exception):
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            global _config_core

            try:
                _GatewayInterface, _execute_operation = _get_gateway()
                manager = _execute_operation(_GatewayInterface.SINGLETON, "get", name="config_manager")
                if manager is None:
                    if _config_core is None:
                        _config_core = ConfigurationCore(correlation_id=correlation_id)
                    _execute_operation(_GatewayInterface.SINGLETON, "set", name="config_manager", instance=_config_core)
                    manager = _config_core

                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="get_config_manager completed",
                                   success=True, using_gateway=True)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                return manager
            except (ImportError, Exception):
                if _config_core is None:
                    _config_core = ConfigurationCore(correlation_id=correlation_id)

                try:
                    _GatewayInterface, _execute_operation = _get_gateway()
                    _execute_operation(_GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="CONFIG",
                                   message="get_config_manager completed",
                                   success=True, using_gateway=False, using_fallback=True)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    pass
                return _config_core
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ImportError) as e:
            try:
                _execute_operation(_GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="CONFIG",
                               message="get_config_manager failed",
                               error_type=type(e).__name__, error=str(e))
            except ImportError:
                # Optional dependency - continue if unavailable
                pass
            raise


__all__ = [
    "ConfigurationCore",
    "get_config_manager",
]
