"""Cold start tracking for Lambda container lifecycle phases.

This module tracks container state (INIT, FIRST_REQUEST, WARM) and
collects timing metrics for module imports during cold start.

Thread-safe singleton pattern ensures metrics are consistently
tracked across the container lifecycle.
"""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ContainerPhase(Enum):
    """Lambda container lifecycle phases."""

    INIT = "init"  # Module import/initialization phase
    FIRST_REQUEST = "first_request"  # First Lambda invocation
    WARM = "warm"  # Subsequent invocations (warm container)


@dataclass
class ImportTiming:
    """Timing data for a single module import."""

    module_name: str
    duration_ms: float
    timestamp: float
    import_order: int


@dataclass
class ColdStartMetrics:
    """Comprehensive cold start metrics."""

    container_phase: ContainerPhase
    import_count: int
    total_import_time_ms: float
    average_import_time_ms: float
    slowest_import_ms: float
    slowest_import_module: str
    cold_start_complete_time: float | None = None
    first_request_time: float | None = None
    invocation_count: int = 0


class ColdStartTracker:
    """Tracks Lambda container lifecycle and import timing.

    Singleton pattern ensures only one tracker instance exists
    per container. Thread-safe for concurrent access.

    Usage:
        tracker = get_cold_start_tracker()
        tracker.record_import('urllib3', duration_ms=150.5)
        tracker.finalize_cold_start()
        is_cold = tracker.is_cold_start()
    """

    _instance: Optional["ColdStartTracker"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ColdStartTracker":
        """Enforce singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize tracker (only once)."""
        if self._initialized:
            return

        self._phase: ContainerPhase = ContainerPhase.INIT
        self._import_timings: dict[str, ImportTiming] = {}
        self._import_counter: int = 0
        self._init_start_time: float = time.time()
        self._cold_start_complete_time: float | None = None
        self._first_request_time: float | None = None
        self._invocation_count: int = 0
        self._lock = threading.RLock()
        self._initialized = True

    def record_import(self, module_name: str, duration_ms: float) -> None:
        """Record timing for a module import during INIT phase.

        Args:
            module_name: Name of the module being imported
            duration_ms: Time taken to import in milliseconds

        """
        with self._lock:
            if self._phase != ContainerPhase.INIT:
                # Only record imports during INIT phase
                return

            self._import_counter += 1
            self._import_timings[module_name] = ImportTiming(
                module_name=module_name,
                duration_ms=duration_ms,
                timestamp=time.time(),
                import_order=self._import_counter,
            )

    def finalize_cold_start(self) -> None:
        """Mark the end of INIT phase and transition to FIRST_REQUEST.

        Should be called after all module imports are complete.
        """
        with self._lock:
            if self._phase == ContainerPhase.INIT:
                self._cold_start_complete_time = time.time()
                self._phase = ContainerPhase.FIRST_REQUEST

    def record_invocation(self) -> None:
        """Record a Lambda invocation and update container phase.

        Transitions from FIRST_REQUEST to WARM after first invocation.
        """
        with self._lock:
            self._invocation_count += 1

            if self._phase == ContainerPhase.FIRST_REQUEST:
                self._first_request_time = time.time()
                self._phase = ContainerPhase.WARM

    def is_cold_start(self) -> bool:
        """Check if current invocation is a cold start.

        Returns:
            True if container is in INIT or FIRST_REQUEST phase

        """
        with self._lock:
            return self._phase in (ContainerPhase.INIT, ContainerPhase.FIRST_REQUEST)

    def get_metrics(self) -> ColdStartMetrics:
        """Get comprehensive cold start metrics.

        Returns:
            ColdStartMetrics with current container state

        """
        with self._lock:
            if not self._import_timings:
                return ColdStartMetrics(
                    container_phase=self._phase,
                    import_count=0,
                    total_import_time_ms=0.0,
                    average_import_time_ms=0.0,
                    slowest_import_ms=0.0,
                    slowest_import_module="",
                    cold_start_complete_time=self._cold_start_complete_time,
                    first_request_time=self._first_request_time,
                    invocation_count=self._invocation_count,
                )

            timings = list(self._import_timings.values())
            total_time = sum(t.duration_ms for t in timings)
            avg_time = total_time / len(timings)
            slowest = max(timings, key=lambda t: t.duration_ms)

            return ColdStartMetrics(
                container_phase=self._phase,
                import_count=len(timings),
                total_import_time_ms=total_time,
                average_import_time_ms=avg_time,
                slowest_import_ms=slowest.duration_ms,
                slowest_import_module=slowest.module_name,
                cold_start_complete_time=self._cold_start_complete_time,
                first_request_time=self._first_request_time,
                invocation_count=self._invocation_count,
            )

    def get_import_summary(self) -> dict[str, float]:
        """Get summary of all recorded import timings.

        Returns:
            Dict mapping module names to import duration in milliseconds

        """
        with self._lock:
            return {
                timing.module_name: timing.duration_ms
                for timing in self._import_timings.values()
            }

    def get_phase(self) -> ContainerPhase:
        """Get current container phase."""
        with self._lock:
            return self._phase

    def reset(self) -> None:
        """Reset tracker to initial state.

        Primarily used for testing. In production, tracker state
        persists for the lifetime of the container.
        """
        with self._lock:
            self._phase = ContainerPhase.INIT
            self._import_timings.clear()
            self._import_counter = 0
            self._init_start_time = time.time()
            self._cold_start_complete_time = None
            self._first_request_time = None
            self._invocation_count = 0


def get_cold_start_tracker() -> ColdStartTracker:
    """Get the singleton ColdStartTracker instance.

    Returns:
        The singleton ColdStartTracker instance

    """
    return ColdStartTracker()
