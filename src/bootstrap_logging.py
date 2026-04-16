"""bootstrap_logging.py - Bootstrap-Resistant Logging for Lambda Cold Start
Version: 2025-03-03_2
Purpose: Two-tier logging system for handling Lambda initialization phases
License: Apache 2.0

CHANGES (2025-03-03_2):
- Security: Added message sanitization to prevent log injection
- Security: Added sensitive data redaction (passwords, tokens, API keys)
- Security: Added maximum message length limits
- Fix: Python 3.12+ compatibility (datetime.now(timezone.utc))
- Fix: Document singleton pattern behavior in get_bootstrap_logger()
- Fix: Added buffer overflow warnings for Lambda context
- Fix: Changed diagnostic print statements to stderr
- Fix: Context dictionary no longer mutated (uses copy)
- Enhancement: Added callback validation in transition_to_gateway()
- Enhancement: Made buffer size configurable via env var
- Enhancement: Added type hints for all callback functions
- Enhancement: Added overflow count warnings after gateway transition

CHANGES (2025-03-03_1):
- Initial implementation
- Bootstrap mode: Simple stdout logging with buffering
- Full mode: Gateway logging with buffered log replay
- Zero external dependencies (Python stdlib only)

Architecture:
    Phase 1 (Bootstrap): Lambda INIT → Gateway unavailable
                        → BootstrapLogger (stdout + buffer)

    Phase 2 (Full): Gateway initialized → transition_to_gateway()
                    → Replay buffered logs through gateway
                    → BootstrapLogger becomes gateway passthrough

Design Rationale:
- Cold start problem: Gateway imports take 100-200ms
- Bootstrap logs must work BEFORE gateway exists
- No circular imports: bootstrap_logging has NO LEE dependencies
- Replay ensures no logs are lost during transition

Usage:
    # In lambda_preload.py or early initialization
from lee.bootstrap_logging import BootstrapLogger, bootstrap_log

    bootstrap_log.info("Loading module...")
    bootstrap_log.warning("Configuration fallback")
    bootstrap_log.error("Initialization failed")

    # After gateway is ready
    BootstrapLogger.transition_to_gateway()
    # Buffered logs are automatically replayed

Performance:
- Bootstrap mode: ~0.1ms per log (simple print + list append)
- Replay: ~5-10ms total (typically 10-20 buffered logs)
- Memory: ~1KB for 20 buffered log entries

Security Features:
- Message sanitization: Newlines removed to prevent log injection
- Sensitive data redaction: Passwords, tokens, API keys automatically redacted
- Message length limits: Messages truncated at 10,000 characters
- Context sanitization: All context values sanitized

Configuration:
- BOOTSTRAP_LOG_MAX_BUFFER_SIZE: Environment variable to override default
  buffer size (default: 100)
"""

import os
import re
import sys
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# ===== LAZY IMPORT HELPER =====

def _import_gateway():
    """Lazy import gateway for logging operations (imported only when needed).

        Tuple of (execute_operation, GatewayInterface) or (None, None) if import fails

    """
    try:
        # pylint: disable=import-outside-toplevel
        from lee.gateway import GatewayInterface, execute_operation
        return execute_operation, GatewayInterface
    except ImportError:
        return None, None

# ===== CONSTANTS =====

# Security: Maximum message length to prevent log injection
_MAX_MESSAGE_LENGTH = 10000

# Security: Translation table for single-pass newline replacement (faster than chained replace)
_NEWLINE_TO_SPACE_TRANS = str.maketrans({'\n': ' ', '\r': ' '})

# Security: Pattern to detect potential sensitive data
_SENSITIVE_PATTERNS = [
    (re.compile(
        r'(password["\']?\s*[:=]\s*["\']?)([^"\',\s}]+)', re.IGNORECASE,
    ), r"\1***"),
    (re.compile(
        r'(token["\']?\s*[:=]\s*["\']?)([^"\',\s}]+)', re.IGNORECASE,
    ), r"\1***"),
    (re.compile(
        r'(api_key["\']?\s*[:=]\s*["\']?)([^"\',\s}]+)', re.IGNORECASE,
    ), r"\1***"),
    (re.compile(
        r'(secret["\']?\s*[:=]\s*["\']?)([^"\',\s}]+)', re.IGNORECASE,
    ), r"\1***"),
    (re.compile(
        r"(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE,
    ), r"\1***"),
]

# Security: Context keys that should always have their values redacted
_SENSITIVE_CONTEXT_KEYS = {
    "password", "passwd", "pwd",
    "token", "access_token", "refresh_token", "auth_token",
    "api_key", "apikey", "api-key",
    "secret", "secret_key", "secretkey",
    "credential", "credentials",
}

# Configurable buffer size (can be overridden via environment variable)
_DEFAULT_MAX_BUFFER_SIZE = 100


# ===== LOG LEVEL ENUMERATION =====

class BootstrapLogLevel(Enum):
    """Log levels for bootstrap logging."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


# ===== HELPER FUNCTIONS =====

def _sanitize_message(message: str) -> str:
    """Sanitize log message to prevent log injection and remove sensitive data.

        message: Raw message to sanitize

        Sanitized message with sensitive data redacted

    """
    # Truncate to maximum length
    if len(message) > _MAX_MESSAGE_LENGTH:
        message = message[:_MAX_MESSAGE_LENGTH] + "... (truncated)"

    # Remove newlines to prevent log injection (single-pass translation)
    message = message.translate(_NEWLINE_TO_SPACE_TRANS)

    # Redact sensitive data patterns
    for pattern, replacement in _SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)

    return message


def _sanitize_context(context: dict[str, Any]) -> dict[str, Any]:
    """Sanitize context dictionary to prevent log injection.

        context: Raw context dictionary

        Sanitized context dictionary

    """
    sanitized = {}
    for key, value in context.items():
        # Check if key is sensitive (redact entire value)
        if key.lower() in _SENSITIVE_CONTEXT_KEYS:
            sanitized[key] = "***"
            continue

        # Convert values to strings and sanitize
        str_value = str(value)

        # Truncate long values
        if len(str_value) > _MAX_MESSAGE_LENGTH:
            str_value = str_value[:_MAX_MESSAGE_LENGTH] + "... (truncated)"

        # Remove newlines (single-pass translation)
        str_value = str_value.translate(_NEWLINE_TO_SPACE_TRANS)

        # Redact sensitive data patterns
        for pattern, replacement in _SENSITIVE_PATTERNS:
            str_value = pattern.sub(replacement, str_value)

        sanitized[key] = str_value

    return sanitized


# ===== BUFFERED LOG ENTRY =====

class BufferedLog:
    """Single buffered log entry for replay."""

    def __init__(
        self,
        level: BootstrapLogLevel,
        message: str,
        timestamp: datetime,
        context: Optional[dict[str, Any]] = None,
    ):
        self.level = level
        self.message = _sanitize_message(message)
        self.timestamp = timestamp
        self.context = _sanitize_context(context or {})

    def format_stdout(self) -> str:
        """Format log entry for stdout output."""
        ts_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        context_str = ""
        if self.context:
            context_parts = [f"{k}={v}" for k, v in self.context.items()]
            context_str = f" [{', '.join(context_parts)}]"
        return (
            f"[{ts_str}] [BOOTSTRAP_{self.level.value}] "
            f"{self.message}{context_str}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for gateway replay."""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


# ===== BOOTSTRAP LOGGER CORE =====

class BootstrapLogger:
    """Two-tier logger for Lambda cold start initialization.

    Phase 1 (Bootstrap Mode):
    - Logs to stdout with [BOOTSTRAP_*] prefix
    - Buffers all logs for later replay
    - No gateway dependencies

    Phase 2 (Full Mode):
    - Transitioned via transition_to_gateway()
    - Routes to LEE gateway logging
    - Replays buffered logs
    - No longer buffers
    """

    # Class-level state (shared across all instances)
    _is_gateway_mode: bool = False
    _log_buffer: list[BufferedLog] = []
    _max_buffer_size: int = int(
        os.environ.get("BOOTSTRAP_LOG_MAX_BUFFER_SIZE", _DEFAULT_MAX_BUFFER_SIZE),
    )
    _buffer_overflow_count: int = 0
    _gateway_available_callback: Optional[Callable[[str, str], None]] = (
        None
    )

    @classmethod
    def is_bootstrap_mode(cls) -> bool:
        """Check if currently in bootstrap mode."""
        return not cls._is_gateway_mode

    @classmethod
    def is_gateway_mode(cls) -> bool:
        """Check if currently in gateway mode."""
        return cls._is_gateway_mode

    @classmethod
    def get_buffer_size(cls) -> int:
        """Get current buffer size."""
        return len(cls._log_buffer)

    @classmethod
    def get_buffer_stats(cls) -> dict[str, Any]:
        """Get buffer statistics."""
        return {
            "buffer_size": len(cls._log_buffer),
            "max_buffer_size": cls._max_buffer_size,
            "overflow_count": cls._buffer_overflow_count,
            "mode": "gateway" if cls._is_gateway_mode else "bootstrap",
        }

    @classmethod
    # pylint: disable=too-many-branches,too-many-statements
    def transition_to_gateway(
        cls,
        gateway_callback: Optional[Callable[[str, str], None]] = None,
    ) -> bool:
        """Transition from bootstrap mode to gateway mode.

        This method:
        1. Switches to gateway mode
        2. Replays all buffered logs through gateway
        3. Clears the buffer

            gateway_callback: Optional callback function for logging.
                Should accept (level, message, **context).
                If not provided, attempts to import gateway.

            bool: True if transition successful, False otherwise

        Raises:
            TypeError: If gateway_callback is not callable or None

        """
        if gateway_callback is not None and not callable(gateway_callback):
            raise TypeError(f"gateway_callback must be callable or None, got {type(gateway_callback)}")
        if cls._is_gateway_mode:
            # Already in gateway mode
            return True

        # Import gateway if no callback provided
        if gateway_callback is None:
            try:
                # Try to import LEE's logging core, fall back to stdlib logging
                # pylint: disable=import-outside-toplevel
                import logging as stdlib_logging

                # Configure basic logging if not already configured
                if not stdlib_logging.getLogger().handlers:
                    stdlib_logging.basicConfig(
                        level=stdlib_logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )

                # Map our levels to stdlib levels
                level_map = {
                    "info": stdlib_logging.INFO,
                    "warning": stdlib_logging.WARNING,
                    "error": stdlib_logging.ERROR,
                    "debug": stdlib_logging.DEBUG,
                }

                def _format_log_message(message: str, context: dict) -> str:
                    """Format log message with context.

                        message: Base log message
                        context: Context dictionary

                        Formatted message string
                    """
                    if not context:
                        return message

                    context_parts = [f"{k}={v}" for k, v in context.items()]
                    return f"{message} [{', '.join(context_parts)}]"

                def _gateway_logging_callback(
                    level: str, message: str, **context,
                ) -> None:
                    """Gateway logging callback using stdlib logging directly.

                        level: Log level string
                        message: Log message
                        **context: Additional context key-value pairs

                    """
                    log_level = level_map.get(level.lower(), stdlib_logging.INFO)
                    formatted_msg = _format_log_message(message, context)
                    stdlib_logging.log(log_level, formatted_msg)

                gateway_callback = _gateway_logging_callback
            except ImportError as e:
                # Gateway not available, remain in bootstrap mode
                print(
                    "[BOOTSTRAP_LOGGER] Gateway not available, "
                    "remaining in bootstrap mode",
                    file=sys.stderr,
                )
                print(
                    f"[BOOTSTRAP_LOGGER] ImportError: {e}",
                    file=sys.stderr,
                )
                return False

        # Store callback
        cls._gateway_available_callback = gateway_callback

        # Switch to gateway mode
        cls._is_gateway_mode = True

        # Replay buffered logs
        if cls._log_buffer:
            execute_operation, GatewayInterface = _import_gateway()
            if execute_operation and GatewayInterface:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_info',
                        message=f"Replaying {len(cls._log_buffer)} buffered logs",
                        corr_id='bootstrap_replay'
                    )
                # pylint: disable=broad-exception-caught
                except Exception:
                    # Fallback to print if gateway logging fails
                    print(
                        f"[BOOTSTRAP_LOGGER] Replaying {len(cls._log_buffer)} "
                        f"buffered logs...",
                        file=sys.stderr,
                    )
            else:
                # Gateway not available, use print
                print(
                    f"[BOOTSTRAP_LOGGER] Replaying {len(cls._log_buffer)} "
                    f"buffered logs...",
                    file=sys.stderr,
                )
            replay_count = 0
            failed_count = 0

            for log_entry in cls._log_buffer:
                # Early continuation if no callback
                if cls._gateway_available_callback is None:
                    print(log_entry.format_stdout(), file=sys.stderr)
                    continue

                try:
                    # Callback is guaranteed to be callable at this point (checked above)
                    # pylint: disable=not-callable
                    cls._gateway_available_callback(
                        log_entry.level.value,
                        log_entry.message,
                        **log_entry.context,
                    )
                    replay_count += 1
                except (OSError, IOError) as e:
                    cls._log_replay_error(e, log_entry)
                    failed_count += 1
                except (ValueError, TypeError) as e:
                    cls._log_replay_error(e, log_entry)
                    failed_count += 1
                except (AttributeError, KeyError, RuntimeError) as e:
                    cls._log_replay_error(e, log_entry)
                    failed_count += 1

            # Clear buffer
            cls._log_buffer.clear()

            execute_operation, GatewayInterface = _import_gateway()
            if execute_operation and GatewayInterface:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_info',
                        message=f"Replay complete: {replay_count} succeeded, {failed_count} failed",
                        corr_id='bootstrap_replay'
                    )
                # pylint: disable=broad-exception-caught
                except Exception:
                    # Fallback to print if gateway logging fails
                    print(
                        f"[BOOTSTRAP_LOGGER] Replay complete: {replay_count} "
                        f"succeeded, {failed_count} failed",
                        file=sys.stderr,
                    )
            else:
                # Gateway not available, use print
                print(
                    f"[BOOTSTRAP_LOGGER] Replay complete: {replay_count} "
                    f"succeeded, {failed_count} failed",
                    file=sys.stderr,
                )

            # Warn if there were buffer overflows
            if cls._buffer_overflow_count > 0:
                execute_operation, GatewayInterface = _import_gateway()
                if execute_operation and GatewayInterface:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_warning',
                            message=f"{cls._buffer_overflow_count} log(s) lost due to buffer overflow",
                            corr_id='bootstrap_replay'
                        )
                    # pylint: disable=broad-exception-caught
                    except Exception:
                        # Fallback to print if gateway logging fails
                        print(
                            f"[BOOTSTRAP_LOGGER] WARNING: "
                            f"{cls._buffer_overflow_count} log(s) lost due to "
                            f"buffer overflow",
                            file=sys.stderr,
                        )
                else:
                    # Gateway not available, use print
                    print(
                        f"[BOOTSTRAP_LOGGER] WARNING: "
                        f"{cls._buffer_overflow_count} log(s) lost due to "
                        f"buffer overflow",
                        file=sys.stderr,
                    )

        return True

    @classmethod
    def reset(cls):
        """Reset to bootstrap mode and clear buffer.

        Useful for testing or Lambda container reuse scenarios.
        """
        cls._is_gateway_mode = False
        cls._log_buffer.clear()
        cls._buffer_overflow_count = 0
        cls._gateway_available_callback = None

    @classmethod
    def cleanup(cls):
        """Cleanup singleton instance to prevent memory leaks.

        Call this before Lambda container reuse to release resources.
        """
        cls._is_gateway_mode = False
        cls._log_buffer.clear()
        cls._buffer_overflow_count = 0
        cls._gateway_available_callback = None

    def __init__(self, component: str = "BOOTSTRAP"):
        """Initialize bootstrap logger instance.

        NOTE: Due to singleton pattern in get_bootstrap_logger(), different
        component names will return the same instance. Only the first component
        name is preserved. For per-component logging in production, use
        gateway logging after transition.

            component: Component name for log context (only used on first call)

        """
        self.component = component

    def _log(
        self,
        level: BootstrapLogLevel,
        message: str,
        **context,
    ) -> None:
        """Internal logging method with mode-aware routing.

            level: Log level (BootstrapLogLevel enum)
            message: Log message
            **context: Additional context key-value pairs

        """
        # Add component to context (avoid mutating original context)
        context_with_component = dict(context)  # Create a copy
        if self.component:
            context_with_component["component"] = self.component

        # Create log entry
        log_entry = BufferedLog(
            level=level,
            message=message,
            timestamp=datetime.now(timezone.utc),
            context=context_with_component,
        )

        if BootstrapLogger._is_gateway_mode:
            # Gateway mode: Route through gateway
            if BootstrapLogger._gateway_available_callback:
                try:
                    BootstrapLogger._gateway_available_callback(
                        level.value,
                        log_entry.message,  # Use sanitized message
                        **context_with_component,  # Use sanitized context
                    )
                except (OSError, IOError) as e:
                    # Gateway logging failed due to I/O error, fallback to stdout
                    print(f"[GATEWAY_LOG_ERROR] {e}", file=sys.stderr)
                    print(log_entry.format_stdout(), file=sys.stderr)
                except (ValueError, TypeError) as e:
                    # Gateway logging failed due to data error, fallback to stdout
                    print(f"[GATEWAY_LOG_ERROR] {e}", file=sys.stderr)
                    print(log_entry.format_stdout(), file=sys.stderr)
                except (AttributeError, KeyError, RuntimeError) as e:
                    # Gateway logging failed due to unexpected error, fallback to stdout
                    print(f"[GATEWAY_LOG_ERROR] {e}", file=sys.stderr)
                    print(log_entry.format_stdout(), file=sys.stderr)
            else:
                # No callback, fallback to stdout
                print(log_entry.format_stdout(), file=sys.stderr)
        else:
            # Bootstrap mode: Buffer + stdout
            # Add to buffer (with overflow protection)
            if len(BootstrapLogger._log_buffer) < BootstrapLogger._max_buffer_size:
                BootstrapLogger._log_buffer.append(log_entry)
            else:
                BootstrapLogger._buffer_overflow_count += 1
                if BootstrapLogger._buffer_overflow_count == 1:
                    # Only warn once (use stderr for warnings in Lambda context)
                    print(
                        f"[BOOTSTRAP_LOGGER_WARNING] Buffer overflow "
                        f"({BootstrapLogger._max_buffer_size} max) - "
                        f"logs will be lost",
                        file=sys.stderr,
                    )

            # Always output to stdout
            print(log_entry.format_stdout())

    def info(self, message: str, **context) -> None:
        """Log INFO level message."""
        self._log(BootstrapLogLevel.INFO, message, **context)

    def warning(self, message: str, **context) -> None:
        """Log WARNING level message."""
        self._log(BootstrapLogLevel.WARNING, message, **context)

    @staticmethod
    def _log_replay_error(error: Exception, log_entry: 'BootstrapLogger._LogEntry') -> None:
        """Log replay error with consistent formatting.

            error: The exception that occurred
            log_entry: The log entry that failed to replay
        """
        print(
            f"[BOOTSTRAP_LOGGER_REPLAY_ERROR] {error}",
            file=sys.stderr,
        )
        print(f"  {log_entry.format_stdout()}", file=sys.stderr)

    def error(self, message: str, **context) -> None:
        """Log ERROR level message."""
        self._log(BootstrapLogLevel.ERROR, message, **context)

    def debug(self, message: str, **context) -> None:
        """Log DEBUG level message."""
        self._log(BootstrapLogLevel.DEBUG, message, **context)


# ===== MODULE-LEVEL SINGLETON =====

class BootstrapLoggerManager:
    """Thread-safe singleton manager for BootstrapLogger.

    Replaces module-level global variable to prevent memory leaks
    in Lambda container reuse scenarios.
    """
    _instance: Optional[BootstrapLogger] = None
    _lock = threading.Lock()

    @classmethod
    def get_logger(cls, component: str = "BOOTSTRAP") -> BootstrapLogger:
        """Get bootstrap logger singleton instance.

        WARNING: This implements a singleton pattern where the first call's
        component name is used for all subsequent calls. Different component names
        will return the same instance. This is by design for early Lambda
        initialization, but may cause confusion if used for per-component logging.

        For per-component logging in production, transition to gateway logging
        which supports proper per-component instances.

            component: Component name for log context (only used on first call)

            BootstrapLogger instance (singleton)

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = BootstrapLogger(component=component)
        return cls._instance

    @classmethod
    def cleanup(cls):
        """Cleanup singleton instance to prevent memory leaks.

        Call this before Lambda container reuse to release resources.
        """
        with cls._lock:
            if cls._instance is not None:
                BootstrapLogger.reset()
            cls._instance = None


def get_bootstrap_logger(component: str = "BOOTSTRAP") -> BootstrapLogger:
    """Get bootstrap logger singleton instance.

    WARNING: This implements a singleton pattern where the first call's
    component name is used for all subsequent calls. Different component names
    will return the same instance. This is by design for early Lambda
    initialization, but may cause confusion if used for per-component logging.

    For per-component logging in production, transition to gateway logging
    which supports proper per-component instances.

        component: Component name for log context (only used on first call)

        BootstrapLogger instance (singleton)

    """
    return BootstrapLoggerManager.get_logger(component)


# ===== CONVENIENCE FUNCTIONS =====

# Create default logger for direct access
bootstrap_log = get_bootstrap_logger()


def bootstrap_log_info(message: str, **context: Any) -> None:
    """Convenience function for INFO level logging.

        message: Log message
        **context: Additional context key-value pairs

    """
    bootstrap_log.info(message, **context)


def bootstrap_log_warning(message: str, **context: Any) -> None:
    """Convenience function for WARNING level logging.

        message: Log message
        **context: Additional context key-value pairs

    """
    bootstrap_log.warning(message, **context)


def bootstrap_log_error(message: str, **context: Any) -> None:
    """Convenience function for ERROR level logging.

        message: Log message
        **context: Additional context key-value pairs

    """
    bootstrap_log.error(message, **context)


def bootstrap_log_debug(message: str, **context: Any) -> None:
    """Convenience function for DEBUG level logging.

        message: Log message
        **context: Additional context key-value pairs

    """
    bootstrap_log.debug(message, **context)


def transition_to_gateway_logging() -> bool:
    """Transition from bootstrap logging to gateway logging.

    This is a convenience wrapper around
    BootstrapLogger.transition_to_gateway().
    Automatically imports gateway and handles the transition.

        bool: True if transition successful

    """
    return BootstrapLogger.transition_to_gateway()


def get_bootstrap_stats() -> dict[str, Any]:
    """Get bootstrap logger statistics.

        Dictionary with buffer stats and mode information

    """
    return BootstrapLogger.get_buffer_stats()


def reset_bootstrap_logging() -> None:
    """Reset bootstrap logging to initial state.

    Clears buffer and returns to bootstrap mode.
    Useful for testing or container reuse.
    """
    BootstrapLogger.reset()


def cleanup_bootstrap_logging() -> None:
    """Cleanup bootstrap logging singleton to prevent memory leaks.

    Call this before Lambda container reuse to release resources.
    """
    BootstrapLoggerManager.cleanup()


# ===== INTEGRATION HELPERS =====

def setup_lambda_bootstrap_logging(component: str = "LAMBDA_INIT") -> BootstrapLogger:
    """Setup bootstrap logging for Lambda initialization.

    This function should be called at the very start of Lambda initialization,
    before any gateway imports. It provides a configured logger instance.

    Usage in lambda_preload.py:
from lee.bootstrap_logging import setup_lambda_bootstrap_logging

        bootstrap_log = setup_lambda_bootstrap_logging("PRELOAD")
        bootstrap_log.info("Starting module preload...")
        # ... initialization code ...

    After gateway is ready (in lambda_function.py):
from lee.bootstrap_logging import transition_to_gateway_logging

        transition_to_gateway_logging()

        component: Component name for log context

        Configured BootstrapLogger instance

    """
    logger = get_bootstrap_logger(component=component)
    logger.info(
        f"Bootstrap logging initialized for {component}",
        phase="initialization",
    )
    return logger


# ===== EXPORTS =====

__all__ = [
    # Core classes
    "BootstrapLogger",
    "BootstrapLoggerManager",
    "BootstrapLogLevel",
    "BufferedLog",

    # Module functions
    "get_bootstrap_logger",
    "transition_to_gateway_logging",
    "get_bootstrap_stats",
    "reset_bootstrap_logging",
    "cleanup_bootstrap_logging",
    "setup_lambda_bootstrap_logging",

    # Convenience functions
    "bootstrap_log",
    "bootstrap_log_info",
    "bootstrap_log_warning",
    "bootstrap_log_error",
    "bootstrap_log_debug",
]


# EOF
