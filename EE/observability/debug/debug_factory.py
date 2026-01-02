"""
Debug Factory - Observability Domain

Debug logging, correlation tracking, and diagnostics implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside observability domain (except stdlib)
- All cross-domain calls via call_operation callback
- Module-level state for persistence across instances
"""

import threading
import time
import uuid
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# Module-level debug state (shared across all instances)
# =============================================================================

_DEBUG_LOCK = threading.RLock()
_DEBUG_ENABLED = False
_CORRELATION_ID: Optional[str] = None
_TRACE_STACK: Dict[str, Any] = {}


# =============================================================================
# Trace data classes
# =============================================================================

@dataclass
class TraceSpan:
    """Represents a trace span for distributed tracing."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    status: str = "ok"  # ok, error


# =============================================================================
# Debug Factory Class
# =============================================================================

class DebugFactory:
    """Debug tools and diagnostics factory.

    Provides comprehensive debugging capabilities:
    - Debug mode control
    - Correlation ID tracking for request tracing
    - Distributed tracing with spans
    - Thread context management

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
        """Initialize debug factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger
        self.metrics = metrics
        self.call_operation = call_operation

    def enable_debug(self, **kwargs) -> bool:
        """Enable debug mode.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _DEBUG_ENABLED

        with _DEBUG_LOCK:
            _DEBUG_ENABLED = True

        if self.logger:
            self.logger.info("Debug mode enabled")

        # Record metric (EE 2.1: call_operation signature)
        if self.metrics and self.call_operation:
            try:
                # EE 2.1: call_operation(domain, interface, operation, **kwargs)
                self.call_operation(
                    'observability',  # domain
                    'metrics',        # interface
                    'increment',      # operation
                    metric_name='debug.enabled',
                    value=1
                )
            except Exception:
                pass

        return True

    def disable_debug(self, **kwargs) -> bool:
        """Disable debug mode.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _DEBUG_ENABLED

        with _DEBUG_LOCK:
            _DEBUG_ENABLED = False

        if self.logger:
            self.logger.info("Debug mode disabled")

        return True

    def is_debug_enabled(self, **kwargs) -> bool:
        """Check if debug mode is enabled.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if debug mode is enabled
        """
        with _DEBUG_LOCK:
            return _DEBUG_ENABLED

    def set_correlation_id(
        self,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Set correlation ID for request tracing.

        Args:
            correlation_id: Correlation ID (generated if not provided)
            **kwargs: Additional parameters

        Returns:
            Correlation ID that was set
        """
        global _CORRELATION_ID

        with _DEBUG_LOCK:
            if correlation_id is None:
                correlation_id = str(uuid.uuid4())

            _CORRELATION_ID = correlation_id

        if self.logger:
            self.logger.debug(
                f"Correlation ID set: {_CORRELATION_ID}"
            )

        # Store in thread context for logging
        return _CORRELATION_ID

    def get_correlation_id(self, **kwargs) -> Optional[str]:
        """Get current correlation ID.

        Args:
            **kwargs: Additional parameters

        Returns:
            Current correlation ID or None
        """
        with _DEBUG_LOCK:
            return _CORRELATION_ID

    def clear_correlation_id(self, **kwargs) -> bool:
        """Clear correlation ID.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _CORRELATION_ID

        with _DEBUG_LOCK:
            _CORRELATION_ID = None

        if self.logger:
            self.logger.debug("Correlation ID cleared")

        return True

    def start_trace(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Start a trace span.

        Args:
            operation_name: Operation being traced
            parent_span_id: Optional parent span ID
            tags: Optional tags for the span
            **kwargs: Additional parameters

        Returns:
            Span ID
        """
        global _TRACE_STACK

        with _DEBUG_LOCK:
            trace_id = self._get_or_create_trace_id()
            span_id = str(uuid.uuid4())

            span = TraceSpan(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                start_time=time.time(),
                tags=tags or {}
            )

            # Store span
            _TRACE_STACK[span_id] = span

        if self.logger:
            self.logger.debug(
                f"Trace started: {operation_name} "
                f"(trace_id={trace_id}, span_id={span_id})"
            )

        return span_id

    def end_trace(
        self,
        span_id: str,
        status: str = "ok",
        error: Optional[Exception] = None,
        **kwargs
    ) -> bool:
        """End a trace span.

        Args:
            span_id: Span ID to end
            status: Span status (ok, error)
            error: Optional exception
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        global _TRACE_STACK

        with _DEBUG_LOCK:
            span = _TRACE_STACK.get(span_id)

            if not span:
                return False

            span.end_time = time.time()
            span.status = status

            if error:
                span.tags['error'] = str(error)
                span.tags['error_type'] = type(error).__name__

        if self.logger:
            duration = (span.end_time - span.start_time) * 1000
            self.logger.debug(
                f"Trace ended: {span.operation_name} "
                f"(span_id={span_id}, duration={duration:.2f}ms)"
            )

        # Record timing metric (EE 2.1: call_operation signature)
        if self.metrics and self.call_operation:
            try:
                duration_ms = (span.end_time - span.start_time) * 1000
                # EE 2.1: call_operation(domain, interface, operation, **kwargs)
                self.call_operation(
                    'observability',  # domain
                    'metrics',        # interface
                    'timing',         # operation
                    metric_name=f'trace.{span.operation_name}',
                    value_ms=duration_ms
                )
            except Exception:
                pass

        return True

    def get_trace_context(self, **kwargs) -> Dict[str, Any]:
        """Get current trace context.

        Args:
            **kwargs: Additional parameters

        Returns:
            Trace context dictionary
        """
        with _DEBUG_LOCK:
            return {
                'trace_id': self._get_or_create_trace_id(),
                'correlation_id': _CORRELATION_ID,
                'debug_enabled': _DEBUG_ENABLED,
                'active_spans': len(_TRACE_STACK),
            }

    # ========================================================================
    # Private helper methods
    # ========================================================================

    def _get_or_create_trace_id(self) -> str:
        """Get or create trace ID.

        Returns:
            Trace ID
        """
        # Use correlation ID as trace ID if available
        if _CORRELATION_ID:
            return _CORRELATION_ID

        # Otherwise generate a new trace ID
        # In production, this would be fetched from incoming request headers
        return str(uuid.uuid4())


__all__ = [
    "DebugFactory",
    "TraceSpan",
]
