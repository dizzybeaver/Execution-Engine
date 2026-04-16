"""Resource profiling for operation performance analysis.

Uses Python's tracemalloc to track memory allocation during operations.
Provides decorator and context manager interfaces for profiling.

Thread-safe singleton pattern with minimal overhead when disabled.
"""

import os
import sys
import threading
import time
import tracemalloc
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from contextlib import AbstractContextManager
from typing import Optional


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

    # pylint: disable=too-many-instance-attributes


class ResourceProfiler:
    """Profiles operation performance and memory usage.

    Singleton pattern with enable/disable control. When disabled,
    profiling overhead is minimal (single boolean check).

    Usage:
        profiler = get_resource_profiler()
        profiler.enable()

        @profiler.profile_operation
        def my_function():
            pass

        with profiler.profile_operation_ctx("custom_name"):
            expensive_operation()

        profiler.start_operation("operation")
        try:
            result = do_work()
            profiler.end_operation("operation", success=True)
        except (RuntimeError, ValueError, KeyError, AttributeError, TypeError):
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
        ResourceProfiler._initialized = True

    def enable(self) -> None:
        """Enable profiling and start tracemalloc.

        Only starts tracemalloc if not already tracking.
        Checks ENABLE_PERFORMANCE_TRACKING environment variable.
        """
        if os.environ.get("ENABLE_PERFORMANCE_TRACKING", "true").lower() != "true":
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

    def profile_operation(self, operation_name: Optional[str] = None) -> Callable:
        """Decorator to profile a function.

        Args:
            operation_name: Custom name for the operation.

        Returns:
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
                except (RuntimeError, ValueError, KeyError, AttributeError, TypeError):
                    self.end_operation(name, success=False)
                    raise
            return wrapper
        return decorator

    @contextmanager
    def profile_operation_ctx(self, operation_name: str) -> AbstractContextManager[None]:
        """Context manager to profile a block of code.

        Args:
            operation_name: Name for the operation being profiled

        Example:
            with profiler.profile_operation_ctx("database_query"):
                results = db.query("SELECT * FROM users")

        """
        self.start_operation(operation_name)
        try:
            yield
            self.end_operation(operation_name, success=True)
        except (RuntimeError, ValueError, KeyError, AttributeError, TypeError):
            self.end_operation(operation_name, success=False)
            raise

    def start_operation(self, operation_name: str) -> None:
        """Start profiling an operation.

        Args:
            operation_name: Name of the operation to profile

        """
        with self._lock:
            if not self._enabled:
                return

            if operation_name in self._active_operations:
                print(f"[ResourceProfiler] ERROR: start_operation called twice for '{operation_name}' without end_operation", file=sys.stderr)
                return

            self._active_operations[operation_name] = time.time()
            current, _peak = tracemalloc.get_traced_memory()
            self._operation_memory[operation_name] = current

    def end_operation(self, operation_name: str, success: bool = True) -> None:
        """End profiling an operation and record metrics.

        Args:
            operation_name: Name of the operation to end
            success: Whether the operation completed successfully

        """
        with self._lock:
            if not self._enabled:
                return

            if operation_name not in self._active_operations:
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

    def get_stats(self, operation_name: str) -> Optional[AggregatedProfileStats]:
        """Get aggregated statistics for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
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

        Returns:
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

    Returns:
        The singleton ResourceProfiler instance

    """
    return ResourceProfiler()
