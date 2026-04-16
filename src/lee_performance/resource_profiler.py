"""Resource profiling for operation performance analysis.

Uses Python's tracemalloc to track memory allocation during operations.
Provides decorator and context manager interfaces for profiling.

Thread-safe singleton pattern with minimal overhead when disabled.
"""

import os
import threading
import time
import tracemalloc
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import ContextManager, Optional

from lee.gateway import GatewayInterface, execute_operation


                # Operation already started - log error and return
@dataclass
class OperationProfile:
    """Profile data for a single operation execution."""

    operation_name: str
    duration_ms: float
    memory_allocated_bytes: int
    memory_peak_bytes: int
    timestamp: float
    success: bool


@dataclass
class AggregatedProfileStats:
    """Aggregated statistics for an operation."""

    operation_name: str
    execution_count: int
    success_count: int
    failure_count: int
    total_duration_ms: float
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    total_memory_allocated_bytes: int
    avg_memory_allocated_bytes: int
    peak_memory_bytes: int
    last_execution_time: float


class ResourceProfiler:
    """Profiles operation performance and memory usage.

    Singleton pattern with enable/disable control. When disabled,
    profiling overhead is minimal (single boolean check).

    Usage:
        profiler = get_resource_profiler()
        profiler.enable()

        # Decorator usage
        @profiler.profile_operation
        def my_function():
            pass

        # Context manager usage
        with profiler.profile_operation("custom_name"):
            expensive_operation()

        # Manual usage
        profiler.start_operation("operation")
        try:
            result = do_work()
            profiler.end_operation("operation", success=True)
        except Exception:
            profiler.end_operation("operation", success=False)
            raise

        stats = profiler.get_stats("operation")
    """

    _instance: Optional["ResourceProfiler"] = None
    _initialized: bool = False
    _lock = threading.Lock()

    def __new__(cls) -> "ResourceProfiler":
        """Enforce singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize profiler (only once)."""
        if ResourceProfiler._initialized:
            return

        self._enabled: bool = False
        self._profiles: dict[str, list[OperationProfile]] = defaultdict(list)
        self._active_operations: dict[str, float] = {}
        self._operation_memory: dict[str, int] = {}
        self._lock = threading.RLock()

        # Memory leak prevention: limit profiles per operation
        self._max_profiles_per_operation = 1000
        self._profile_ttl_hours = 24  # Remove profiles older than 24 hours

        ResourceProfiler._initialized = True

    def enable(self) -> None:
        """Enable profiling and start tracemalloc.

        Only starts tracemalloc if not already tracking.
        Checks ENABLE_PERFORMANCE_TRACKING environment variable.
        """
        # Check if performance tracking is enabled via environment variable
        if not os.environ.get("ENABLE_PERFORMANCE_TRACKING", "true").lower() == "true":
            return

        with self._lock:
            if not self._enabled:
                tracemalloc.start()
                self._enabled = True

    def disable(self) -> None:
        """Disable profiling and stop tracemalloc.

        Clears active operation tracking but retains historical data.
        """
        with self._lock:
            if self._enabled:
                tracemalloc.stop()
                self._enabled = False
                self._active_operations.clear()
                self._operation_memory.clear()

    def is_enabled(self) -> bool:
        """Check if profiler is enabled."""
        with self._lock:
            return self._enabled

    def profile_operation(self, operation_name: str | None = None) -> Callable:
        """Decorator to profile a function.

            operation_name: Custom name for the operation.
                          Defaults to function name if not provided.

            Decorated function with profiling

        Example:
            @profiler.profile_operation("my_operation")
            def my_function():
                pass

        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                name = operation_name or func.__name__
                self.start_operation(name)
                try:
                    result = func(*args, **kwargs)
                    self.end_operation(name, success=True)
                    return result
                except (TypeError, ValueError, KeyError, AttributeError, RuntimeError):
                    self.end_operation(name, success=False)
                    raise
            return wrapper
        return decorator

    @contextmanager
    def profile_operation_ctx(self, operation_name: str) -> ContextManager[None]:
        """Context manager to profile a block of code.

            operation_name: Name for the operation being profiled

        Example:
            with profiler.profile_operation_ctx("database_query"):
                results = db.query("SELECT * FROM users")

        """
        self.start_operation(operation_name)
        try:
            yield
            self.end_operation(operation_name, success=True)
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError):
            self.end_operation(operation_name, success=False)
            raise

    def start_operation(self, operation_name: str) -> None:
        """Start profiling an operation.

            operation_name: Name of the operation to profile

        """
        with self._lock:
            if not self._enabled:
                return

            if operation_name in self._active_operations:
                # This prevents silent failures when start_operation is called twice
                # Use gateway logging if available, otherwise silent fail
                try:
                    from lee.gateway import GatewayInterface, execute_operation
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_error",
                        message=f"[ResourceProfiler] start_operation called twice for '{operation_name}' without end_operation",
                        corr_id="resource_profiler",
                    )
                except (ImportError, AttributeError):
                    # Gateway not available, silent fail
                    pass
                return

            self._active_operations[operation_name] = time.time()
            current, peak = tracemalloc.get_traced_memory()
            self._operation_memory[operation_name] = current

    def end_operation(self, operation_name: str, success: bool = True) -> None:
        """End profiling an operation and record metrics.

            operation_name: Name of the operation to end
            success: Whether the operation completed successfully

        """
        with self._lock:
            if not self._enabled:
                return

            if operation_name not in self._active_operations:
                # Operation not started - ignore
                return

            end_time = time.time()
            start_time = self._active_operations.pop(operation_name)
            duration_ms = (end_time - start_time) * 1000

            current, peak = tracemalloc.get_traced_memory()
            start_memory = self._operation_memory.pop(operation_name, 0)
            memory_allocated = current - start_memory

            profile = OperationProfile(
                operation_name=operation_name,
                duration_ms=duration_ms,
                memory_allocated_bytes=memory_allocated,
                memory_peak_bytes=peak,
                timestamp=end_time,
                success=success,
            )

            self._profiles[operation_name].append(profile)
            self._enforce_profile_limits(operation_name)

    def _enforce_profile_limits(self, operation_name: str) -> None:
        """Enforce memory limits on profiles to prevent unbounded growth.

            operation_name: Name of the operation to clean up

        """
        try:
            profiles = self._profiles.get(operation_name, [])
            if not profiles:
                return

            current_time = time.time()
            ttl_seconds = self._profile_ttl_hours * 3600

            # Remove profiles older than TTL
            self._profiles[operation_name] = [
                p for p in profiles
                if current_time - p.timestamp < ttl_seconds
            ]

            # If still too many profiles, remove oldest (FIFO)
            if len(self._profiles[operation_name]) > self._max_profiles_per_operation:
                self._profiles[operation_name] = self._profiles[operation_name][-self._max_profiles_per_operation:]
        except (KeyError, ValueError, AttributeError) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(KeyError, ValueError, AttributeError) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

    def get_stats(self, operation_name: str) -> AggregatedProfileStats | None:
        """Get aggregated statistics for a specific operation.

            operation_name: Name of the operation

            AggregatedProfileStats or None if operation not found

        """
        with self._lock:
            profiles = self._profiles.get(operation_name, [])
            if not profiles:
                return None

            success_profiles = [p for p in profiles if p.success]
            failure_profiles = [p for p in profiles if not p.success]

            durations = [p.duration_ms for p in profiles]
            memory_allocated = [p.memory_allocated_bytes for p in profiles]
            peak_memory = max((p.memory_peak_bytes for p in profiles), default=0)

            return AggregatedProfileStats(
                operation_name=operation_name,
                execution_count=len(profiles),
                success_count=len(success_profiles),
                failure_count=len(failure_profiles),
                total_duration_ms=sum(durations),
                avg_duration_ms=sum(durations) / len(durations),
                min_duration_ms=min(durations),
                max_duration_ms=max(durations),
                total_memory_allocated_bytes=sum(memory_allocated),
                avg_memory_allocated_bytes=sum(memory_allocated) / len(memory_allocated),
                peak_memory_bytes=peak_memory,
                last_execution_time=profiles[-1].timestamp,
            )

    def get_all_stats(self) -> dict[str, AggregatedProfileStats]:
        """Get aggregated statistics for all profiled operations.

            Dict mapping operation names to their stats

        """
        with self._lock:
            result = {}
            for operation_name in self._profiles.keys():
                stats = self.get_stats(operation_name)
                if stats:
                    result[operation_name] = stats
            return result

    def reset(self) -> None:
        """Reset profiler state.

        Clears all profile history. Useful for testing or
        starting fresh profiling session.
        """
        with self._lock:
            self._profiles.clear()
            self._active_operations.clear()
            self._operation_memory.clear()


def get_resource_profiler() -> ResourceProfiler:
    """Get the singleton ResourceProfiler instance.

        The singleton ResourceProfiler instance

    """
    return ResourceProfiler()
