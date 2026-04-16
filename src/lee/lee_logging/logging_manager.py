"""logging/logging_manager.py
Version: 2025-12-08_1
Purpose: Core logging manager with rate limiting and singleton pattern (thread-safe)
License: Apache 2.0

CHANGES (2025-12-08_1):
- Moved to logging/ subdirectory
- Integrated hierarchical debug control via debug module
- Replaced _is_debug_mode()/_print_debug() with debug.debug_log()
- Added debug_timing context managers
- Updated imports for logging/ subdirectory

CHANGES (2025-10-22_01):
- Added reset() method for Phase 1 compliance
- SINGLETON pattern: Try gateway first, fallback to module-level
- Rate limiting: MAX_LOGS_PER_INVOCATION to prevent log flooding
- LOG_LEVEL validation: Prevents misconfiguration

CHANGES (2026-04-09):
- CRITICAL: Added thread safety with double-checked locking pattern
- Lambda CAN have concurrent executions - lock required
"""

import logging
import os
import threading
from collections import deque
from datetime import datetime
from typing import Any, Optional

from lee.lee_logging.logging_types import ErrorEntry, ErrorLogLevel, LogTemplate

# ===== CONFIGURATION =====

_USE_LOG_TEMPLATES = os.environ.get("USE_LOG_TEMPLATES", "false").lower() == "true"
MAX_LOGS_PER_INVOCATION = int(os.environ.get("MAX_LOGS_PER_INVOCATION", "500"))
LOG_RATE_LIMIT_ENABLED = os.environ.get("LOG_RATE_LIMIT_ENABLED", "true").lower() == "true"
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# ===== LOGGING CONFIGURATION =====

def _get_validated_log_level() -> int:
    """Get and validate LOG_LEVEL environment variable.

    For AWS Lambda: Read from environment variable set by Lambda configuration.
    For local testing: .env file should set this via environment variable.
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    if log_level_str not in VALID_LOG_LEVELS:
        print(f"[LOGGING_MANAGER_WARNING] Invalid LOG_LEVEL='{log_level_str}', "
              f"must be one of {VALID_LOG_LEVELS}. Defaulting to INFO.")
        log_level_str = "INFO"

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return level_map[log_level_str]

logging.basicConfig(
    level=_get_validated_log_level(),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ===== RATE LIMITING TRACKER =====

class RateLimitTracker:
    """Track log count per Lambda invocation for rate limiting."""

    def __init__(self):
        self.invocation_id = None
        self.log_count = 0
        self.limit_warning_shown = False

    def reset_for_invocation(self, invocation_id: str):
        """Reset counter for new Lambda invocation."""
        self.invocation_id = invocation_id
        self.log_count = 0
        self.limit_warning_shown = False

    def reset(self):
        """Reset all state (for testing/debugging)."""
        self.invocation_id = None
        self.log_count = 0
        self.limit_warning_shown = False

    def increment(self) -> bool:
        """Increment log count and check if limit exceeded."""
        self.log_count += 1

        if not LOG_RATE_LIMIT_ENABLED:
            return True

        if self.log_count > MAX_LOGS_PER_INVOCATION:
            if not self.limit_warning_shown:
                print(f"[LOGGING_MANAGER_RATE_LIMIT] Log limit of {MAX_LOGS_PER_INVOCATION} "
                      f"exceeded for invocation {self.invocation_id}. Suppressing further logs.")
                self.limit_warning_shown = True
            return False

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiting statistics."""
        return {
            "invocation_id": self.invocation_id,
            "log_count": self.log_count,
            "limit": MAX_LOGS_PER_INVOCATION,
            "limit_exceeded": self.log_count > MAX_LOGS_PER_INVOCATION if LOG_RATE_LIMIT_ENABLED else False,
            "rate_limiting_enabled": LOG_RATE_LIMIT_ENABLED,
        }

_RATE_LIMITER = RateLimitTracker()

# ===== LOGGING CORE =====

class LoggingCore:
    """Unified logging manager with template optimization and rate limiting."""

    def __init__(self):
        """Initialize logging core."""
        self.logger = logging.getLogger("SUGA-ISP")
        self._templates: dict[str, LogTemplate] = {}
        self._template_hits = 0
        self._template_misses = 0
        self._error_log: deque = deque(maxlen=100)
        self._error_count_by_type: dict[str, int] = {}

    def set_invocation_id(self, invocation_id: str):
        """Set Lambda invocation ID and reset rate limiter."""
        _RATE_LIMITER.reset_for_invocation(invocation_id)

    def reset(self) -> bool:
        """Reset logging core state (Phase 1 requirement).
        
        Clears:
        - Template cache and statistics
        - Error log and error counts
        - Rate limiter state
        
            bool: True on success

        """
        # Clear templates
        self._templates.clear()
        self._template_hits = 0
        self._template_misses = 0

        # Clear error tracking
        self._error_log.clear()
        self._error_count_by_type.clear()

        # Reset rate limiter
        _RATE_LIMITER.reset()

        return True

    def log(self, message: str, level: int = logging.INFO, **kwargs) -> None:
        """Core logging with rate limiting."""
        if not _RATE_LIMITER.increment():
            return

        if _USE_LOG_TEMPLATES:
            template_key = self._get_template_key(message)

            if template_key in self._templates:
                template = self._templates[template_key]
                self._template_hits += 1
                self.logger.log(level, "[T%s] %s", id(template), message, extra=kwargs)
            else:
                self._templates[template_key] = message
                self._template_misses += 1
                self.logger.log(level, message, extra=kwargs)
        else:
            self.logger.log(level, message, extra=kwargs)

    def log_error_with_tracking(self, message: str, error: Optional[str] = None,
                               level: ErrorLogLevel = ErrorLogLevel.MEDIUM, **kwargs) -> None:
        """Log error with tracking and rate limiting."""
        if not _RATE_LIMITER.increment():
            return

        entry = ErrorEntry(
            timestamp=datetime.now(),
            error_type=kwargs.get("error_type", "UnknownError"),
            message=message,
            level=level,
            details=error,
        )

        self._error_log.append(entry)

        error_type = entry.error_type
        self._error_count_by_type[error_type] = self._error_count_by_type.get(error_type, 0) + 1

        level_map = {
            ErrorLogLevel.LOW: logging.WARNING,
            ErrorLogLevel.MEDIUM: logging.ERROR,
            ErrorLogLevel.HIGH: logging.ERROR,
            ErrorLogLevel.CRITICAL: logging.CRITICAL,
        }

        log_level = level_map.get(level, logging.ERROR)
        self.logger.log(log_level, f"{message}: {error}" if error else message, extra=kwargs)

    def _get_template_key(self, message: str) -> str:
        """Generate template key from message."""
        return message[:100]

    def get_template_stats(self) -> dict[str, Any]:
        """Get template statistics."""
        return {
            "templates_cached": len(self._templates),
            "template_hits": self._template_hits,
            "template_misses": self._template_misses,
            "hit_rate": (self._template_hits / (self._template_hits + self._template_misses) * 100
                        if (self._template_hits + self._template_misses) > 0 else 0.0),
        }

    def get_error_stats(self) -> dict[str, Any]:
        """Get error tracking statistics."""
        return {
            "total_errors": len(self._error_log),
            "errors_by_type": self._error_count_by_type.copy(),
            "recent_errors": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "type": entry.error_type,
                    "message": entry.message,
                    "level": entry.level.value,
                }
                for entry in list(self._error_log)[-10:]
            ],
        }

    def get_rate_limit_stats(self) -> dict[str, Any]:
        """Get rate limiting statistics."""
        return _RATE_LIMITER.get_stats()

# ===== MODULE-LEVEL SINGLETON (Thread-Safe) =====

_LOGGING_CORE = None
_logging_core_lock = threading.Lock()


def get_logging_core() -> LoggingCore:
    """Get logging core singleton (SINGLETON pattern) with thread-safe lazy initialization.

    Tries gateway first, falls back to module-level instance.
    Thread-safe: Uses double-checked locking for Lambda concurrent execution.

    Returns:
        LoggingCore singleton instance
    """
    global _LOGGING_CORE  # pylint: disable=global-statement

    try:
        from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel

        manager = execute_operation(GatewayInterface.SINGLETON, "get", name="logging_manager")
        if manager is None:
            # Fast path: check without lock (read-only, safe in Python)
            if _LOGGING_CORE is not None:
                manager = _LOGGING_CORE
            else:
                # Slow path: acquire lock for initialization
                with _logging_core_lock:
                    # Double-check: another thread may have initialized while we waited
                    if _LOGGING_CORE is not None:
                        manager = _LOGGING_CORE
                    else:
                        _LOGGING_CORE = LoggingCore()
                        manager = _LOGGING_CORE

            execute_operation(GatewayInterface.SINGLETON, "set",
                            name="logging_manager", instance=_LOGGING_CORE)
            manager = _LOGGING_CORE

        return manager

    except (ImportError, RuntimeError, ValueError, TypeError, ConnectionError, TimeoutError, OSError):
        # Fast path: check without lock (read-only, safe in Python)
        if _LOGGING_CORE is not None:
            return _LOGGING_CORE

        # Slow path: acquire lock for initialization
        with _logging_core_lock:
            # Double-check: another thread may have initialized while we waited
            if _LOGGING_CORE is not None:
                return _LOGGING_CORE

            # Initialize singleton
            _LOGGING_CORE = LoggingCore()

        return _LOGGING_CORE

# ===== EXPORTS =====

__all__ = [
    "LoggingCore",
    "RateLimitTracker",
    "get_logging_core",
]
