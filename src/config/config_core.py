"""
config/config_core.py
Version: 2025-12-09_1
Purpose: Core configuration management with singleton pattern
License: Apache 2.0
"""

import time
from typing import Dict, Any
from collections import deque

from config.config_state import ConfigurationState
from config.config_validator import ConfigurationValidator

_config_core = None

class ConfigurationCore:
    """Configuration system core with rate limiting."""

    def __init__(self, correlation_id: str = None, **kwargs):
        # NEW: Add debug tracing for exact failure point identification
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CONFIG", "ConfigurationCore.__init__ called")

        with debug_timing(correlation_id, "CONFIG", "ConfigurationCore.__init__"):
            try:
                self._config: Dict[str, Any] = {}
                self._state = ConfigurationState()
                self._validator = ConfigurationValidator()
                self._cache_prefix = "config_"
                self._initialized = False
                self._use_parameter_store = False
                self._parameter_prefix = "/lambda-execution-engine"

                # Rate limiting (1000 ops/sec)
                self._rate_limiter = deque(maxlen=1000)
                self._rate_limit_window_ms = 1000
                self._rate_limited_count = 0

                debug_log(correlation_id, "CONFIG", "ConfigurationCore.__init__ completed", success=True)
            except Exception as e:
                debug_log(correlation_id, "CONFIG", "ConfigurationCore.__init__ failed",
                         error_type=type(e).__name__, error=str(e))
                raise
    
    def _check_rate_limit(self, correlation_id: str = None, **kwargs) -> bool:
        """Check if operation should be rate limited."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CONFIG", "_check_rate_limit called")

        with debug_timing(correlation_id, "CONFIG", "_check_rate_limit"):
            try:
                current_time_ms = int(time.time() * 1000)

                # Remove old entries
                while self._rate_limiter and \
                      (current_time_ms - self._rate_limiter[0]) > self._rate_limit_window_ms:
                    self._rate_limiter.popleft()

                # Check limit
                if len(self._rate_limiter) >= 1000:
                    self._rate_limited_count += 1
                    debug_log(correlation_id, "CONFIG", "_check_rate_limit completed",
                             success=False, reason="Rate limit exceeded",
                             rate_limited_count=self._rate_limited_count)
                    return True

                self._rate_limiter.append(current_time_ms)
                debug_log(correlation_id, "CONFIG", "_check_rate_limit completed",
                         success=True, rate_limited=False)
                return False
            except Exception as e:
                debug_log(correlation_id, "CONFIG", "_check_rate_limit failed",
                         error_type=type(e).__name__, error=str(e))
                raise
    
    def reset(self, correlation_id: str = None, **kwargs) -> bool:
        """Reset configuration state."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CONFIG", "reset called")

        with debug_timing(correlation_id, "CONFIG", "reset"):
            try:
                # FIXED: Add rate limit validation to prevent resource exhaustion (CVE-CONFIG-2025-001)
                if self._check_rate_limit(correlation_id=correlation_id):
                    try:
                        import gateway
                        gateway.log_error("Configuration reset rate limited",
                                        extra={"rate_limited_count": self._rate_limited_count})
                    except (ImportError, Exception):
                        pass
                    debug_log(correlation_id, "CONFIG", "reset completed",
                             success=False, reason="Rate limited")
                    return False

                self._config.clear()
                self._state = ConfigurationState()
                self._initialized = False
                self._rate_limiter.clear()
                self._rate_limited_count = 0

                debug_log(correlation_id, "CONFIG", "reset completed", success=True)
                return True

            except Exception as e:
                try:
                    import gateway
                    gateway.log_error(f"Config reset failed: {e}")
                except (ImportError, Exception):
                    pass
                debug_log(correlation_id, "CONFIG", "reset failed",
                         error_type=type(e).__name__, error=str(e))
                raise
    
    def get_stats(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get configuration statistics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CONFIG", "get_stats called")

        with debug_timing(correlation_id, "CONFIG", "get_stats"):
            try:
                stats = {
                    'initialized': self._initialized,
                    'parameter_count': len(self._config),
                    'use_parameter_store': self._use_parameter_store,
                    'rate_limited_count': self._rate_limited_count,
                    'rate_limiter_size': len(self._rate_limiter)
                }

                debug_log(correlation_id, "CONFIG", "get_stats completed",
                         success=True, parameter_count=stats['parameter_count'],
                         initialized=stats['initialized'])
                return stats
            except Exception as e:
                debug_log(correlation_id, "CONFIG", "get_stats failed",
                         error_type=type(e).__name__, error=str(e))
                raise


def get_config_manager(correlation_id: str = None, **kwargs) -> ConfigurationCore:
    """
    Get configuration manager singleton.

    Uses SINGLETON pattern for lifecycle management.
    Attempts gateway registration, falls back to module-level singleton.
    """
    if correlation_id is None:
        from debug import generate_correlation_id
        correlation_id = generate_correlation_id()

    from debug import debug_log, debug_timing

    debug_log(correlation_id, "CONFIG", "get_config_manager called")

    with debug_timing(correlation_id, "CONFIG", "get_config_manager"):
        try:
            global _config_core

            try:
                import gateway
                manager = gateway.singleton_get('config_manager')
                if manager is None:
                    if _config_core is None:
                        _config_core = ConfigurationCore(correlation_id=correlation_id)
                    gateway.singleton_register('config_manager', _config_core)
                    manager = _config_core

                debug_log(correlation_id, "CONFIG", "get_config_manager completed",
                         success=True, using_gateway=True)
                return manager
            except (ImportError, Exception):
                if _config_core is None:
                    _config_core = ConfigurationCore(correlation_id=correlation_id)

                debug_log(correlation_id, "CONFIG", "get_config_manager completed",
                         success=True, using_gateway=False, using_fallback=True)
                return _config_core
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "get_config_manager failed",
                     error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'ConfigurationCore',
    'get_config_manager'
]
