"""interface/interface_debug.py
Version: 2025-12-23_2
Purpose: DEBUG interface router (INT-14) - Runtime inspection with Static Dictionary Dispatch System (DDS-1)
License: Apache 2.0

CHANGES (2025-12-23_1):
- FIXED: Removed self-referential debug logging that caused infinite recursion
- execute_debug_operation no longer tries to route through gateway for logging

CHANGES (2026-03-03):
- ADDED: Phase 3 Analytics - Request tracing capabilities
- ADDED: RequestTrace and TraceStep classes for detailed execution tracking
- ADDED: Trace storage with deque-based memory management (max 100 traces)

CHANGES (2026-03-16):
- ADDED: CORRELATION_ID_LOGGING_ENABLED environment variable to control corr_id in logs

CHANGES (2026-03-22):
- Upgraded to Static DDS with metadata (func, category, description)
- Zero breaking changes - all existing operations preserved
"""

import os
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from lee.gateway.gateway_core import generate_correlation_id

try:
    from lee.lee_debug.debug_config import get_debug_config
    _DEBUG_CONFIG_AVAILABLE = True
except ImportError:
    _DEBUG_CONFIG_AVAILABLE = False

# ===== CONFIGURATION =====

# Import configuration values from centralized config
try:
    from lee.lee_config.variables import (
        DEBUG_DEFAULT_SLOWEST_STEPS_COUNT,
        DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS,
        DEBUG_DEFAULT_TOP_OPERATIONS_COUNT,
        DEBUG_MAX_STEP_NAME_LENGTH,
        DEBUG_MAX_TRACES,
    )
    _CONFIG_AVAILABLE = True
except ImportError:
    # Fallback to hardcoded defaults if config unavailable
    _CONFIG_AVAILABLE = False
    DEBUG_MAX_TRACES = 100
    DEBUG_MAX_STEP_NAME_LENGTH = 200
    DEBUG_DEFAULT_SLOWEST_STEPS_COUNT = 5
    DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS = 3
    DEBUG_DEFAULT_TOP_OPERATIONS_COUNT = 10

# Control whether correlation_id appears in debug logs
_CORRELATION_ID_LOGGING_ENABLED = os.getenv("CORRELATION_ID_LOGGING_ENABLED", "false").lower() == "true"

# ===== CONSTANTS =====

# Trace storage limits (now from config)
MAX_TRACES: int = DEBUG_MAX_TRACES
MAX_STEP_NAME_LENGTH: int = DEBUG_MAX_STEP_NAME_LENGTH

# Default analysis parameters (now from config)
DEFAULT_SLOWEST_STEPS_COUNT: int = DEBUG_DEFAULT_SLOWEST_STEPS_COUNT
DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS: int = DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS
DEFAULT_TOP_OPERATIONS_COUNT: int = DEBUG_DEFAULT_TOP_OPERATIONS_COUNT

# Percentage calculations
PERCENTAGE_MULTIPLIER: int = 100

# Valid scope prefixes for operation names
# Used to extract scope from operation name format: "scope:operation"
VALID_SCOPES = frozenset({
    "ALEXA", "HA", "DEVICES", "CACHE",
    "HTTP", "CONFIG", "SECURITY", "METRICS",
    "CIRCUIT_BREAKER", "SINGLETON", "GATEWAY",
    "INIT", "WEBSOCKET", "LOGGING",
})

# Simple in-memory trace context storage
_trace_context: dict[str, dict[str, Any]] = {}

# ===== PHASE 3 ANALYTICS: REQUEST TRACING =====

@dataclass
class TraceStep:
    """Represents a single step in a request trace.

    Tracks individual operations within a request, including timing
    and success/failure status for performance analysis.
    """

    step_name: str
    duration_ms: float
    success: bool
    timestamp: float
    extra_context: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert step to dictionary for serialization."""
        return {
            "step_name": self.step_name,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "timestamp": self.timestamp,
            "datetime": datetime.utcfromtimestamp(self.timestamp).isoformat(),
            "extra_context": self.extra_context,
        }


@dataclass
class RequestTrace:
    """Represents a complete request trace with multiple steps.

    Tracks the full execution path of a request from start to finish,
    enabling detailed performance analysis and bottleneck identification.

    Thread Safety:
        add_step() method is thread-safe using instance-level lock.
    """

    correlation_id: str
    start_perf: float  # perf_counter for duration measurements
    start_timestamp: float  # time.time() for datetime serialization
    end_perf: Optional[float] = None  # perf_counter for duration measurements
    end_timestamp: Optional[float] = None  # time.time() for datetime serialization
    steps: list[TraceStep] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_step(self, step_name: str, duration_ms: float, success: bool = True, **extra_context) -> None:
        """Add a step to the trace.

        Thread-safe: Uses lock to protect steps list.
        """
        # Validate step_name length to prevent memory issues
        if len(step_name) > MAX_STEP_NAME_LENGTH:
            step_name = step_name[:MAX_STEP_NAME_LENGTH]

        step = TraceStep(
            step_name=step_name,
            duration_ms=duration_ms,
            success=success,
            timestamp=time.time(),
            extra_context=extra_context,
        )

        with self._lock:
            self.steps.append(step)

    def complete(self) -> None:
        """Mark the trace as completed."""
        if self.end_perf is None:
            self.end_perf = time.perf_counter()
            self.end_timestamp = time.time()

    def get_duration_ms(self) -> float:
        """Get total duration of the trace in milliseconds."""
        if self.end_perf is None:
            return (time.perf_counter() - self.start_perf) * 1000
        return (self.end_perf - self.start_perf) * 1000

    def get_failed_steps(self) -> list[TraceStep]:
        """Get all steps that failed."""
        return [step for step in self.steps if not step.success]

    def get_slowest_steps(self, n: int = DEFAULT_SLOWEST_STEPS_COUNT) -> list[TraceStep]:
        """Get the N slowest steps."""
        return sorted(self.steps, key=lambda s: s.duration_ms, reverse=True)[:n]

    def to_dict(self) -> dict:
        """Convert trace to dictionary for serialization."""
        return {
            "correlation_id": self.correlation_id,
            "start_time": self.start_timestamp,
            "start_datetime": datetime.utcfromtimestamp(self.start_timestamp).isoformat(),
            "end_time": self.end_timestamp,
            "end_datetime": datetime.utcfromtimestamp(self.end_timestamp).isoformat() if self.end_timestamp else None,
            "duration_ms": self.get_duration_ms(),
            "step_count": len(self.steps),
            "failed_step_count": len(self.get_failed_steps()),
            "steps": [step.to_dict() for step in self.steps],
        }

    def analyze(self) -> dict:
        """Analyze trace and return performance insights."""
        if not self.steps:
            return {
                "status": "no_steps",
                "message": "Trace has no steps to analyze",
            }

        total_duration = self.get_duration_ms()
        step_durations = [step.duration_ms for step in self.steps]
        failed_steps = self.get_failed_steps()

        analysis = {
            "correlation_id": self.correlation_id,
            "total_duration_ms": total_duration,
            "step_count": len(self.steps),
            "successful_steps": len(self.steps) - len(failed_steps),
            "failed_steps": len(failed_steps),
            "avg_step_duration_ms": sum(step_durations) / len(step_durations),
            "min_step_duration_ms": min(step_durations),
            "max_step_duration_ms": max(step_durations),
            "slowest_steps": [
                {
                    "step_name": step.step_name,
                    "duration_ms": step.duration_ms,
                    "percentage": (step.duration_ms / total_duration * PERCENTAGE_MULTIPLIER) if total_duration > 0 else 0,
                }
                for step in self.get_slowest_steps(DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS)
            ],
        }

        if failed_steps:
            analysis["failures"] = [
                {
                    "step_name": step.step_name,
                    "duration_ms": step.duration_ms,
                    "timestamp": step.timestamp,
                }
                for step in failed_steps
            ]

        return analysis


# Trace storage: Dict for O(1) lookup, managed size via _clear_old_traces
_trace_storage: dict[str, RequestTrace] = {}
_trace_storage_lock = threading.Lock()
_max_trace_storage_size: int = MAX_TRACES


def _clear_old_traces() -> None:
    """Clear old traces when storage exceeds maximum size.

    Removes oldest traces (by start_time) to maintain MAX_TRACES limit.
    Uses FIFO eviction strategy - removes traces in order of creation.
    """
    with _trace_storage_lock:
        if len(_trace_storage) > _max_trace_storage_size:
            # Sort by start_time and remove oldest
            sorted_traces = sorted(
                _trace_storage.items(),
                key=lambda item: item[1].start_timestamp,
            )
            # Remove oldest traces to get back to limit
            num_to_remove = len(_trace_storage) - _max_trace_storage_size
            for correlation_id, _ in sorted_traces[:num_to_remove]:
                del _trace_storage[correlation_id]


# ===== INLINE DEBUG IMPLEMENTATIONS =====

def _debug_log_inline(corr_id: str, message: str, scope: Optional[str] = None, **context: Any) -> None:
    """Inline debug log implementation.

    Args:
        corr_id: Correlation ID for log tracking
        message: Log message
        scope: Optional scope/category for the log entry
        **context: Additional context parameters
    """
    # Check if debug is enabled for this scope before logging
    if _DEBUG_CONFIG_AVAILABLE:
        try:
            config = get_debug_config()
            # If no scope specified, use LOGGING as default
            debug_scope = scope if scope else "LOGGING"
            if not config.is_debug_enabled(debug_scope):
                # Debug mode is disabled for this scope, skip logging
                return
        except (AttributeError, KeyError):
            # If debug config check fails, skip logging to be safe
            return

    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        scope_prefix = f"[{scope}] " if scope else ""

        # Conditionally include correlation_id based on environment variable
        corr_id_prefix = f"[{corr_id}] " if _CORRELATION_ID_LOGGING_ENABLED else ""
        log_entry = f"[{timestamp}] {corr_id_prefix}{scope_prefix}{message}"

        if context:
            # Sanitize context to prevent PII leakage in logs
            try:
                # pylint: disable=import-outside-toplevel
                from lee.lee_security import LogSanitizer
                sanitized_context = LogSanitizer.sanitize_any(context)
                log_entry += f" | Context: {sanitized_context}"
            except (ImportError, ValueError, TypeError, AttributeError):
                # If sanitization fails, log without context
                log_entry += " | Context: <sanitization failed>"
        print(log_entry, file=sys.stderr, flush=True)
    except RuntimeError:
        # Fallback logging failed - continue
        pass

def _record_to_profiler_if_available(op_name: str, duration_ms: float) -> None:
    """Record timing to GatewayProfiler if available."""
    try:
        from lee.lee_debug.gateway_profiler import get_gateway_profiler
        profiler = get_gateway_profiler()
        if profiler.is_enabled():
            # Extract scope from operation name if available (format: "scope:operation")
            scope = "GATEWAY"
            if ":" in op_name:
                parts = op_name.split(":", 1)
                if len(parts) == 2 and parts[0] in VALID_SCOPES:
                    scope = parts[0]
            profiler.record_timing(op_name, duration_ms, scope)
    except (AttributeError, KeyError, TypeError):
        # FIXED: Removed logging call that caused infinite recursion
        # DEBUG interface calling LOGGING which calls DEBUG which calls LOGGING...
        pass  # Silent fail - profiler recording is optional


@contextmanager
def _debug_timing_inline(corr_id: str, op_name: str) -> Any:
    """Inline debug timing implementation."""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Check if timing is enabled for this operation before printing
        should_log = False
        if _DEBUG_CONFIG_AVAILABLE:
            try:
                config = get_debug_config()
                # Extract scope from operation name if available (format: "scope:operation")
                timing_scope = "GATEWAY"
                if ":" in op_name:
                    parts = op_name.split(":", 1)
                    if len(parts) == 2 and parts[0] in VALID_SCOPES:
                        timing_scope = parts[0]

                # Check if timing is enabled for this scope
                if config.is_timing_enabled(timing_scope):
                    should_log = True
            except (AttributeError, KeyError):
                # If debug config check fails, don't log to be safe
                should_log = False

        # EXISTING: Print to stderr (NO BREAKING CHANGES)
        if should_log:
            # Conditionally include correlation_id based on environment variable
            corr_id_prefix = f"[{corr_id}] " if _CORRELATION_ID_LOGGING_ENABLED else ""
            print(f"{corr_id_prefix}TIMING: {op_name} took {duration_ms:.2f}ms", file=sys.stderr, flush=True)

        # NEW: Auto-record to GatewayProfiler (always record, regardless of timing flag)
        _record_to_profiler_if_available(op_name, duration_ms)

def _set_trace_context_inline(trace_id: str, **context) -> None:
    """Inline trace context implementation."""
    _trace_context[trace_id] = {
        "trace_id": trace_id,
        "timestamp": time.time(),
        **context,
    }

def _clear_trace_context_inline(trace_id: str = None) -> None:
    """Inline trace context clearing."""
    if trace_id:
        _trace_context.pop(trace_id, None)
    else:
        _trace_context.clear()

def _fix_timing_params(kwargs) -> dict[str, Any]:
    """Fix timing operation parameters (map operation_name to operation, correlation_id to corr_id)."""
    kwargs = kwargs.copy()
    if "operation_name" in kwargs:
        kwargs["op_name"] = kwargs.pop("operation_name")
    if "correlation_id" in kwargs:
        kwargs["corr_id"] = kwargs.pop("correlation_id")
    # Only keep parameters that _debug_timing_inline accepts
    allowed_params = {"op_name", "corr_id"}
    return {k: v for k, v in kwargs.items() if k in allowed_params}


# ===== INLINE IMPLEMENTATIONS FOR NEW DEBUG OPERATIONS =====

def _profiler_get_stats_inline(operation_name: Optional[str] = None, **kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get profiler statistics for an operation."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.gateway_profiler import get_gateway_profiler
        profiler = get_gateway_profiler()
        if operation_name:
            return profiler.get_operation_stats(operation_name) or {}
        return profiler.get_all_stats()
    except (ImportError, AttributeError):
        return {}


def _profiler_reset_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Reset profiler data."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.gateway_profiler import get_gateway_profiler
        profiler = get_gateway_profiler()
        count = profiler.reset_all()
        return {"status": "reset", "reset_count": count}
    except (ImportError, AttributeError):
        return {"error": "Profiler reset failed"}


def _profiler_get_summary_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get profiler summary."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.gateway_profiler import get_gateway_profiler
        profiler = get_gateway_profiler()
        return profiler.get_summary()
    except (ImportError, AttributeError):
        return {"error": "Profiler summary failed"}


def _get_call_stack_inline(corr_id: str, **kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get call stack for a correlation ID."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.call_stack_tracker import get_call_stack_tracker
        tracker = get_call_stack_tracker()
        return tracker.get_call_stack_dict(corr_id) or {}
    except (ImportError, AttributeError):
        return {}


def _clear_call_stack_inline(corr_id: str, **kwargs) -> bool:  # pylint: disable=unused-argument
    """Clear call stack for a correlation ID."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.call_stack_tracker import get_call_stack_tracker
        tracker = get_call_stack_tracker()
        return tracker.clear_call_stack(corr_id)
    except (ImportError, AttributeError):
        return False


def _get_call_stack_stats_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get call stack tracker statistics."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.call_stack_tracker import get_call_stack_tracker
        tracker = get_call_stack_tracker()
        return tracker.get_stats()
    except (ImportError, AttributeError):
        return {"error": "Call stack stats failed"}


def _enable_call_tracking_inline(enabled: bool = True, **kwargs) -> bool:  # pylint: disable=unused-argument
    """Enable or disable call tracking."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.call_stack_tracker import get_call_stack_tracker
        tracker = get_call_stack_tracker()
        if enabled:
            tracker.enable()
        else:
            tracker.disable()
        return True
    except (ImportError, AttributeError):
        return False


def _hot_path_get_top_n_inline(n: int = DEFAULT_TOP_OPERATIONS_COUNT, **kwargs) -> list[dict[str, Any]]:  # pylint: disable=unused-argument
    """Get top N most-called operations."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.hot_path_detector import get_hot_path_detector
        detector = get_hot_path_detector()
        return detector.get_top_operations(n)
    except (ImportError, AttributeError):
        return []


def _hot_path_get_distribution_inline(**kwargs) -> dict[str, int]:  # pylint: disable=unused-argument
    """Get operation distribution."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.hot_path_detector import get_hot_path_detector
        detector = get_hot_path_detector()
        return detector.get_distribution()
    except (ImportError, AttributeError):
        return {}


def _hot_path_get_stats_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get hot path detector statistics."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.hot_path_detector import get_hot_path_detector
        detector = get_hot_path_detector()
        return detector.get_stats()
    except (ImportError, AttributeError):
        return {"error": "Hot path stats failed"}


def _hot_path_reset_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Reset hot path tracking."""
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_debug.hot_path_detector import get_hot_path_detector
        detector = get_hot_path_detector()
        previous_total = detector.reset()
        return {"status": "reset", "previous_total_calls": previous_total}
    except (ImportError, AttributeError):
        return {"error": "Hot path reset failed"}


# ===== PHASE 3 ANALYTICS: REQUEST TRACING OPERATIONS =====

def _start_trace_inline(correlation_id: str, **kwargs) -> RequestTrace:  # pylint: disable=unused-argument
    """Start a new request trace."""
    trace = RequestTrace(
        correlation_id=correlation_id,
        start_perf=time.perf_counter(),
        start_timestamp=time.time(),
        end_perf=None,
        end_timestamp=None,
        steps=[],
        _lock=threading.Lock(),
    )

    with _trace_storage_lock:
        _trace_storage[correlation_id] = trace
        _clear_old_traces()

    return trace


def _add_trace_step_inline(
    correlation_id: str,
    step_name: str,
    duration_ms: float,
    success: bool = True,
    **extra_context,
) -> bool:  # pylint: disable=unused-argument
    """Add a step to an existing trace."""
    with _trace_storage_lock:
        trace = _trace_storage.get(correlation_id)
        if trace and trace.end_time is None:
            trace.add_step(step_name, duration_ms, success, **extra_context)
            return True
    return False


def _end_trace_inline(correlation_id: str, **kwargs) -> bool:  # pylint: disable=unused-argument
    """End a request trace."""
    with _trace_storage_lock:
        trace = _trace_storage.get(correlation_id)
        if trace:
            trace.complete()
            return True
    return False


def _analyze_trace_inline(correlation_id: str, **kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Analyze a request trace and return performance insights."""
    with _trace_storage_lock:
        trace = _trace_storage.get(correlation_id)
        if trace:
            return trace.analyze()
    return {"error": f"Trace not found: {correlation_id}"}


def _get_trace_inline(correlation_id: str, **kwargs) -> Optional[dict[str, Any]]:  # pylint: disable=unused-argument
    """Get a request trace by correlation ID."""
    with _trace_storage_lock:
        trace = _trace_storage.get(correlation_id)
        if trace:
            return trace.to_dict()
    return None


def _get_all_traces_inline(**kwargs) -> list[dict[str, Any]]:  # pylint: disable=unused-argument
    """Get all traces."""
    with _trace_storage_lock:
        return [trace.to_dict() for trace in _trace_storage.values()]


def _clear_traces_inline(**kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Clear all traces from storage."""
    with _trace_storage_lock:
        count = len(_trace_storage)
        _trace_storage.clear()
    return {"status": "cleared", "count": count}


# ===== STATIC DISPATCH DICTIONARY FOR O(1) OPERATION ROUTING =====

def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for DEBUG operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category
    - description: Human-readable description
    """
    return {
        # Core Debug Operations
        "log": {
            "func": lambda corr_id=None, message=None, scope=None, **context: _debug_log_inline(
                corr_id or "unknown", message or "", scope, **context
            ),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Log debug message with correlation ID and optional scope",
        },
        "timing": {
            "func": lambda **kw: _debug_timing_inline(**_fix_timing_params(kw)),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Record operation timing with context manager",
        },
        "generate_correlation_id": {
            "func": lambda **kw: generate_correlation_id("dbg"),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Generate unique correlation ID for debugging",
        },
        "generate_trace_id": {
            "func": lambda **kw: generate_correlation_id("trace"),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Generate unique trace ID for request tracking",
        },
        "set_trace_context": {
            "func": lambda trace_id, **context: _set_trace_context_inline(trace_id, **context),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Set trace context for debugging",
        },
        "get_trace_context": {
            "func": lambda trace_id, **kw: _trace_context.get(trace_id, {}),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get trace context by trace ID",
        },
        "clear_trace_context": {
            "func": lambda trace_id=None, **kw: _clear_trace_context_inline(trace_id),  # pylint: disable=unnecessary-lambda
            "category": "delete",
            "description": "Clear trace context (specific or all)",
        },

        # Gateway Profiler Operations
        "profiler_get_stats": {
            "func": lambda operation_name=None, **kw: _profiler_get_stats_inline(operation_name, **kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get profiler statistics (p50/p95/p99 timing)",
        },
        "profiler_reset": {
            "func": lambda **kw: _profiler_reset_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "delete",
            "description": "Reset profiler data",
        },
        "profiler_get_summary": {
            "func": lambda **kw: _profiler_get_summary_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get profiler summary statistics",
        },

        # Call Stack Tracker Operations
        "get_call_stack": {
            "func": lambda corr_id, **kw: _get_call_stack_inline(corr_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get call stack for correlation ID",
        },
        "clear_call_stack": {
            "func": lambda corr_id, **kw: _clear_call_stack_inline(corr_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "delete",
            "description": "Clear call stack for correlation ID",
        },
        "get_call_stack_stats": {
            "func": lambda **kw: _get_call_stack_stats_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get call stack tracker statistics",
        },
        "enable_call_tracking": {
            "func": lambda enabled=True, **kw: _enable_call_tracking_inline(enabled, **kw),  # pylint: disable=unnecessary-lambda
            "category": "admin",
            "description": "Enable or disable call tracking",
        },

        # Hot Path Detector Operations
        "hot_path_get_top_n": {
            "func": lambda n=DEFAULT_TOP_OPERATIONS_COUNT, **kw: _hot_path_get_top_n_inline(n, **kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get top N most-called operations (Pareto analysis)",
        },
        "hot_path_get_distribution": {
            "func": lambda **kw: _hot_path_get_distribution_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get operation call distribution",
        },
        "hot_path_get_stats": {
            "func": lambda **kw: _hot_path_get_stats_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get hot path detector statistics",
        },
        "hot_path_reset": {
            "func": lambda **kw: _hot_path_reset_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "delete",
            "description": "Reset hot path tracking data",
        },

        # Phase 3.1: Time Operations (2026-03-09)
        "get_time": {
            "func": lambda **kw: time.time(),  # pylint: disable=unnecessary-lambda
            "category": "timing",
            "description": "Get current time for timing measurements (time.time equivalent)",
        },
        "get_perf_counter": {
            "func": lambda **kw: time.perf_counter(),  # pylint: disable=unnecessary-lambda
            "category": "timing",
            "description": "Get high-performance counter for precise timing",
        },
        "sleep": {
            "func": lambda seconds, **kw: time.sleep(seconds),  # pylint: disable=unnecessary-lambda
            "category": "timing",
            "description": "Sleep for specified seconds (use sparingly in Lambda)",
        },

        # Phase 3 Analytics: Request Tracing Operations
        "start_trace": {
            "func": lambda correlation_id, **kw: _start_trace_inline(correlation_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Start new request trace",
        },
        "add_trace_step": {
            "func": lambda correlation_id, step_name, duration_ms, success=True, **kw: _add_trace_step_inline(
                correlation_id, step_name, duration_ms, success, **kw,
            ),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "Add step to existing trace",
        },
        "end_trace": {
            "func": lambda correlation_id, **kw: _end_trace_inline(correlation_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "write",
            "description": "End request trace and mark complete",
        },
        "analyze_trace": {
            "func": lambda correlation_id, **kw: _analyze_trace_inline(correlation_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Analyze trace and return performance insights",
        },
        "get_trace": {
            "func": lambda correlation_id, **kw: _get_trace_inline(correlation_id, **kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get trace by correlation ID",
        },
        "get_all_traces": {
            "func": lambda **kw: _get_all_traces_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "read",
            "description": "Get all traces",
        },
        "clear_traces": {
            "func": lambda **kw: _clear_traces_inline(**kw),  # pylint: disable=unnecessary-lambda
            "category": "delete",
            "description": "Clear all traces from storage",
        },
    }

_DEBUG_DISPATCH = _build_dispatch_dict()


def execute_debug_operation(operation: str, **kwargs) -> Any:
    """Route debug operations using enhanced dispatch dictionary pattern.

    Args:
        operation: Debug operation name
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If unknown operation

    """
    # Generate correlation ID for debugging if not provided
    if "correlation_id" not in kwargs:
        kwargs["correlation_id"] = generate_correlation_id("dbg")

    # Validate operation using dispatch keys (O(1) lookup)
    if operation not in _DEBUG_DISPATCH:
        valid_ops = ", ".join(_DEBUG_DISPATCH.keys())
        raise ValueError(f"Unknown debug operation: '{operation}'. Valid operations: {valid_ops}")

    # Execute operation through dispatch handler (O(1) lookup)
    entry = _DEBUG_DISPATCH[operation]
    func = entry["func"]
    result = func(**kwargs)

    return result

__all__ = ["execute_debug_operation"]
