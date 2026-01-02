"""
Logging Factory - Observability Domain

Structured logging and CloudWatch integration implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside observability domain (except stdlib)
- All cross-domain calls via call_operation callback
- Module-level state for persistence across instances
"""

import logging
import sys
import json
import threading
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
from contextlib import contextmanager


# =============================================================================
# Module-level logging state (shared across all instances)
# =============================================================================

_LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

_LOG_LOCK = threading.RLock()
_LOGGER_CACHE: Dict[str, logging.Logger] = {}
_ROOT_CONFIGURED = False
_HANDLERS: List[logging.Handler] = []


# =============================================================================
# Structured formatter for CloudWatch
# =============================================================================

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for CloudWatch integration."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'exc_info', 'exc_text', 'stack_info'
            }:
                log_data[key] = value

        return json.dumps(log_data)


# =============================================================================
# Logging Factory Class
# =============================================================================

class LoggingFactory:
    """Structured logging factory.

    Provides comprehensive logging capabilities with CloudWatch integration:
    - Structured JSON logging for CloudWatch
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Configurable handlers (console, file, CloudWatch)
    - Correlation ID tracking
    - Thread-safe operations

    UG-ISP Compliance:
    - Cross-domain calls via call_operation callback
    - Uses module-level state for persistence
    - No direct imports outside observability domain
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize logging factory.

        Args:
            logger: Logger instance (for internal use)
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Configure root logger if not already configured
        self._configure_root_logger()

    def _configure_root_logger(self) -> None:
        """Configure root logger with structured formatter."""
        global _ROOT_CONFIGURED, _HANDLERS

        with _LOG_LOCK:
            if _ROOT_CONFIGURED:
                return

            # Get root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            # Add console handler with structured formatter
            if not _HANDLERS:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(StructuredFormatter())
                _HANDLERS.append(console_handler)
                root_logger.addHandler(console_handler)

            _ROOT_CONFIGURED = True

    def _get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get or create logger instance.

        Args:
            name: Logger name (defaults to calling module)

        Returns:
            Logger instance
        """
        with _LOG_LOCK:
            logger_name = name or 'ee.observability'

            if logger_name not in _LOGGER_CACHE:
                _LOGGER_CACHE[logger_name] = logging.getLogger(logger_name)

            return _LOGGER_CACHE[logger_name]

    def log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """Log message at specified level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Additional context data
            **kwargs: Additional parameters (correlation_id, user_id, etc.)

        Returns:
            True if logged successfully
        """
        logger = self._get_logger(kwargs.get('logger_name'))

        # Normalize log level
        level_upper = level.upper()
        if level_upper not in _LOG_LEVELS:
            self.logger.warning(f"Invalid log level: {level}, using INFO")
            level_upper = 'INFO'

        log_level = _LOG_LEVELS[level_upper]

        # Create extra dict for structured fields
        extra = {}
        if 'correlation_id' in kwargs:
            extra['correlation_id'] = kwargs['correlation_id']
        if 'user_id' in kwargs:
            extra['user_id'] = kwargs['user_id']
        if 'request_id' in kwargs:
            extra['request_id'] = kwargs['request_id']
        if context:
            extra.update(context)

        # Log the message
        logger.log(log_level, message, extra=extra)

        # Record metric if available (EE 2.1: call_operation signature)
        if self.metrics and self.call_operation:
            try:
                # EE 2.1: call_operation(domain, interface, operation, **kwargs)
                self.call_operation(
                    'observability',  # domain
                    'metrics',        # interface
                    'increment',      # operation
                    metric_name=f'logging.{level.lower()}',
                    value=1
                )
            except Exception:
                pass  # Ignore metric errors

        return True

    def debug(self, message: str, **kwargs) -> bool:
        """Log debug message.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        return self.log('DEBUG', message, **kwargs)

    def info(self, message: str, **kwargs) -> bool:
        """Log info message.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        return self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs) -> bool:
        """Log warning message.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        return self.log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs) -> bool:
        """Log error message.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        return self.log('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs) -> bool:
        """Log critical message.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        return self.log('CRITICAL', message, **kwargs)

    def exception(self, message: str, **kwargs) -> bool:
        """Log exception with traceback.

        Args:
            message: Log message
            **kwargs: Additional parameters

        Returns:
            True if logged successfully
        """
        logger = self._get_logger(kwargs.get('logger_name'))
        extra = {}
        if 'correlation_id' in kwargs:
            extra['correlation_id'] = kwargs['correlation_id']
        if context := kwargs.get('context'):
            extra.update(context)

        logger.exception(message, extra=extra)
        return True

    def set_level(self, level: str, **kwargs) -> bool:
        """Set logging level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        level_upper = level.upper()
        if level_upper not in _LOG_LEVELS:
            raise ValueError(f"Invalid log level: {level}")

        log_level = _LOG_LEVELS[level_upper]

        with _LOG_LOCK:
            for logger in _LOGGER_CACHE.values():
                logger.setLevel(log_level)

            logging.getLogger().setLevel(log_level)

        return True

    def get_level(self, **kwargs) -> str:
        """Get current logging level.

        Args:
            **kwargs: Additional parameters

        Returns:
            Current log level name
        """
        root_logger = logging.getLogger()
        level_num = root_logger.level

        for name, num in _LOG_LEVELS.items():
            if num == level_num:
                return name

        return 'INFO'

    def add_handler(
        self,
        handler_type: str,
        **kwargs
    ) -> bool:
        """Add log handler.

        Args:
            handler_type: Handler type (console, file, cloudwatch)
            **kwargs: Handler configuration

        Returns:
            True if successful
        """
        global _HANDLERS

        with _LOG_LOCK:
            if handler_type == 'console':
                handler = logging.StreamHandler(sys.stdout)
            elif handler_type == 'file':
                filename = kwargs.get('filename', 'ee.log')
                handler = logging.FileHandler(filename)
            else:
                raise ValueError(f"Unknown handler type: {handler_type}")

            handler.setFormatter(StructuredFormatter())
            logging.getLogger().addHandler(handler)
            _HANDLERS.append(handler)

        return True

    def remove_handler(self, handler_type: str, **kwargs) -> bool:
        """Remove log handler by type.

        Args:
            handler_type: Handler type to remove
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _HANDLERS

        with _LOG_LOCK:
            root_logger = logging.getLogger()
            handlers_to_remove = [
                h for h in _HANDLERS
                if isinstance(h, logging.StreamHandler) and handler_type == 'console'
                or isinstance(h, logging.FileHandler) and handler_type == 'file'
            ]

            for handler in handlers_to_remove:
                root_logger.removeHandler(handler)
                _HANDLERS.remove(handler)

        return True

    def flush(self, **kwargs) -> bool:
        """Flush all log handlers.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with _LOG_LOCK:
            for handler in _HANDLERS:
                if hasattr(handler, 'flush'):
                    handler.flush()

        return True


__all__ = [
    "LoggingFactory",
]
