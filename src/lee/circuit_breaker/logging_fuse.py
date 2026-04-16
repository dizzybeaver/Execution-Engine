"""logging_fuse.py
Version: 2026-03-28_1
Purpose: Simple fuse for tracking logging failures without circuit breaker behavior

This module provides a lightweight fuse mechanism for tracking when logging
operations fail. Unlike CircuitBreaker, LoggingFuse does NOT disable operations
or implement thresholds - it simply records that a failure occurred.

Key Difference from CircuitBreaker:
- CircuitBreaker: Has threshold, disables after trips, needs recovery
- LoggingFuse: NO threshold, NEVER disables, just tracks failure history

Use Case:
Track logging degradation for health monitoring without stopping operations.
When logging fails, we want to know it's degraded but keep trying to log.

License: Apache 2.0
"""

from __future__ import annotations

from typing import Any, Optional

# Global registry for all LoggingFuse instances
_logging_fuse_registry: dict[str, LoggingFuse] = {}


def register_logging_fuse(name: str, fuse: LoggingFuse) -> None:
    """Register a LoggingFuse instance.

    Args:
        name: Unique identifier for the fuse
        fuse: LoggingFuse instance to register

    """
    _logging_fuse_registry[name] = fuse


def get_logging_fuse_registry() -> dict[str, LoggingFuse]:
    """Get all registered LoggingFuse instances.

    Returns:
        Copy of the registry dictionary

    """
    return dict(_logging_fuse_registry)


def clear_logging_fuse_registry() -> None:
    """Clear all registered fuses (mainly for testing)."""
    _logging_fuse_registry.clear()


class LoggingFuse:
    """Simple fuse for tracking logging failures.

    LoggingFuse is a lightweight alternative to CircuitBreaker for tracking
    when logging operations fail. It does NOT implement circuit breaker behavior
    (no thresholds, no disabling, no recovery) - it simply records that a
    failure occurred at some point.

    Key Characteristics:
        - fuse attribute (boolean): Starts False, becomes True on first failure
        - NO threshold: Any failure blows the fuse
        - NEVER disables: Operations continue regardless of fuse state
        - Manual reset: fuse stays True until manually reset
        - Pure tracking: Health monitoring can see logging degradation

    Use Case:
        Track logging degradation for health monitoring. When logging fails,
        we want to know it's degraded but keep trying to log. The fuse indicates
        "logging has failed at some point" for health reports.

    Example:
        >>> # Initialize fuse
        >>> fuse = LoggingFuse()
        >>> fuse.fuse  # False - never failed
        >>> fuse.is_blown()  # False

        >>> # Log failure
        >>> try:
        ...     execute_operation(GatewayInterface.LOGGING, "log_info", message="...")
        ... except (RuntimeError, ValueError, TypeError, ConnectionError, IOError) as e:
        ...     fuse.record_failure(e)  # Sets fuse=True

        >>> fuse.fuse  # True - failed at some point
        >>> fuse.is_blown()  # True

        >>> # Keep trying to log (no circuit breaker)
        >>> try:
        ...     execute_operation(GatewayInterface.LOGGING, "log_info", message="...")
        ... except (RuntimeError, ValueError, TypeError, ConnectionError, IOError) as e:
        ...     fuse.record_failure(e)  # Still True

        >>> # Health check can see degradation
        >>> if fuse.is_blown():
        ...     print("Logging has failed at some point - check health")

        >>> # Manual reset after fixing root cause
        >>> fuse.reset()
        >>> fuse.fuse  # False - clean history

    COMPLIANCE:
        - AP-08: No threading locks (Lambda single-threaded)
        - DEC-04: Lambda single-threaded model
    """

    def __init__(self, name: Optional[str] = None):
        """Initialize logging fuse.

        Args:
            name: Optional identifier for this fuse. If provided, auto-registers
                  the fuse in the global registry. If None, generates unique ID.

        """
        self.fuse = False  # ONLY set to False here

        # Auto-register if name provided
        if name:
            self._name = self._ensure_unique_name(name)
            register_logging_fuse(self._name, self)
        else:
            self._name = f"fuse_{id(self)}"

    def _ensure_unique_name(self, name: str) -> str:
        """Ensure name is unique in registry by appending suffix if needed.

        Args:
            name: Desired name for the fuse

        Returns:
            Unique name (may have _2, _3, etc. appended)

        """
        if name not in _logging_fuse_registry:
            return name

        # Find next available suffix
        counter = 2
        while True:
            candidate = f"{name}_{counter}"
            if candidate not in _logging_fuse_registry:
                return candidate
            counter += 1

    @property
    def name(self) -> str:
        """Get the fuse name.

        Returns:
            Fuse identifier

        """
        return self._name

    def record_failure(self, _error: Optional[Exception] = None) -> None:
        """Record a logging failure.

        Sets fuse to True if not already blown. Does nothing if fuse is
        already True (idempotent). Can optionally capture the error that
        caused the failure.

        Args:
            error: Optional exception that caused the failure

        Example:
            >>> fuse = LoggingFuse()
            >>> try:
            ...     log_message("test")
            ... except (RuntimeError, ValueError, TypeError, ConnectionError, IOError) as e:
            ...     fuse.record_failure(e)

        """
        if not self.fuse:
            self.fuse = True

    def is_blown(self) -> bool:
        """Check if fuse is blown.

        Returns True if logging has failed at some point, False otherwise.

        Returns:
            bool: True if fuse is blown (logging failed), False if not

        Example:
            >>> fuse = LoggingFuse()
            >>> fuse.is_blown()  # False
            >>> fuse.record_failure()
            >>> fuse.is_blown()  # True

        """
        return self.fuse

    def reset(self) -> None:
        """Manually reset the fuse.

        Sets fuse back to False. Should only be called after investigating
        and fixing the root cause of logging failures.

        Example:
            >>> fuse = LoggingFuse()
            >>> fuse.record_failure()
            >>> fuse.fuse  # True
            >>> # ... fix root cause ...
            >>> fuse.reset()
            >>> fuse.fuse  # False

        """
        self.fuse = False

    def reset_fuse(self) -> None:
        """Alias for reset().

        Provides alternative method name for clarity. Both reset() and
        reset_fuse() do the same thing.

        Example:
            >>> fuse = LoggingFuse()
            >>> fuse.record_failure()
            >>> fuse.reset_fuse()  # Same as fuse.reset()
            >>> fuse.fuse  # False

        """
        self.reset()

    def get_status(self) -> dict[str, Any]:
        """Get fuse status.

        Returns a dictionary with fuse state and interpretation.

        Returns:
            Dict containing:
                - name: Fuse identifier
                - fuse: Current fuse state (True if blown)
                - blown: Whether fuse is blown (same as fuse)
                - interpretation: Human-readable fuse status

        Example:
            >>> fuse = LoggingFuse("my_logger")
            >>> status = fuse.get_status()
            >>> print(status['interpretation'])
            'Never failed (clean history)'
            >>> fuse.record_failure()
            >>> status = fuse.get_status()
            >>> print(status['interpretation'])
            'FAILED at some point - logging degraded'

        """
        return {
            "name": self._name,
            "fuse": self.fuse,
            "blown": self.fuse,
            "interpretation": self._interpret_status(),
        }

    def _interpret_status(self) -> str:
        """Interpret fuse status for health reports.

        Returns:
            Human-readable interpretation of fuse state

        Example:
            >>> fuse = LoggingFuse()
            >>> fuse._interpret_status()
            'Never failed (clean history)'
            >>> fuse.record_failure()
            >>> fuse._interpret_status()
            'FAILED at some point - logging degraded'

        """
        if not self.fuse:
            return "Never failed (clean history)"
        return "FAILED at some point - logging degraded"


__all__ = [
    "LoggingFuse",
    "register_logging_fuse",
    "get_logging_fuse_registry",
    "clear_logging_fuse_registry",
]
