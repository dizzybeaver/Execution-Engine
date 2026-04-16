"""Cold start tracking for Lambda container lifecycle phases.

This module tracks container state (INIT, FIRST_REQUEST, WARM) and
collects timing metrics for module imports during cold start.

Thread-safe singleton pattern ensures metrics are consistently
tracked across the container lifecycle.
"""

import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# Check if debug mode is enabled
_LEE_DEBUG = os.environ.get("LEE_DEBUG", "false").lower() == "true"


# Gateway debug system (initialized when LEE_DEBUG=true)
_execute_operation = None
_GatewayInterface = None


def _init_debug_system() -> None:
    """Initialize gateway debug system if available."""
    global _execute_operation, _GatewayInterface

    if not _LEE_DEBUG:
        return

    try:
        from lee.gateway import execute_operation, GatewayInterface
        _execute_operation = execute_operation
        _GatewayInterface = GatewayInterface
    except (ImportError, AttributeError):
        pass


# Initialize debug system on module load
_init_debug_system()


class ContainerPhase(Enum):
    """Lambda container lifecycle phases."""

    INIT = "init"
    FIRST_REQUEST = "first_request"
    WARM = "warm"


@dataclass
class ImportTiming:
    """Timing data for a single module import."""

    module_name: str
    duration_ms: float
    timestamp: float
    import_order: int

    # pylint: disable=too-many-instance-attributes


@dataclass
class ColdStartMetrics:
    """Comprehensive cold start metrics."""

    container_phase: ContainerPhase
    import_count: int
    total_import_time_ms: float
    average_import_time_ms: float
    slowest_import_ms: float
    slowest_import_module: str
    cold_start_complete_time: Optional[float] = None
    first_request_time: Optional[float] = None
    invocation_count: int = 0

    # pylint: disable=too-many-instance-attributes


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
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Creating ColdStartTracker instance",
                                 scope="COLD_START", current_instance=str(cls._instance))
            except (AttributeError, TypeError, RuntimeError):
                pass

        if cls._instance is None:
            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message="Instance is None, acquiring lock",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass

            with cls._lock:
                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message="Lock acquired, checking instance again",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

                if cls._instance is None:
                    if _execute_operation and _GatewayInterface:
                        try:
                            _execute_operation(_GatewayInterface.DEBUG, 'log',
                                             message="Creating new instance via super().__new__()",
                                             scope="COLD_START")
                        except (AttributeError, TypeError, RuntimeError):
                            pass

                    cls._instance = super().__new__(cls)

                    if _execute_operation and _GatewayInterface:
                        try:
                            _execute_operation(_GatewayInterface.DEBUG, 'log',
                                             message=f"New instance created: {cls._instance}",
                                             scope="COLD_START")
                        except (AttributeError, TypeError, RuntimeError):
                            pass
                else:
                    if _execute_operation and _GatewayInterface:
                        try:
                            _execute_operation(_GatewayInterface.DEBUG, 'log',
                                             message="Instance already exists (double-check)",
                                             scope="COLD_START")
                        except (AttributeError, TypeError, RuntimeError):
                            pass

            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message="Lock released",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass
        else:
            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message="Instance already exists",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass

        return cls._instance

    def __init__(self):
        """Initialize tracker (only once)."""
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="ColdStartTracker.__init__ called",
                                 scope="COLD_START",
                                 is_initialized=getattr(self, '_initialized', False))
            except (AttributeError, TypeError, RuntimeError):
                pass

        if getattr(self, '_initialized', False):
            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message="Already initialized, returning early",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass
            return

        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="First time initialization starting",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._phase: ContainerPhase = ContainerPhase.INIT
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message=f"Phase set to: {self._phase}",
                                 scope="COLD_START", phase=str(self._phase))
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._import_timings: dict[str, ImportTiming] = {}
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Import timings dict created",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._import_counter: int = 0
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Import counter set to 0",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._init_start_time: float = time.time()
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message=f"Init start time: {self._init_start_time}",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._cold_start_complete_time: Optional[float] = None
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Cold start complete time set to None",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._first_request_time: Optional[float] = None
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="First request time set to None",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._invocation_count: int = 0
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Invocation count set to 0",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._lock = threading.RLock()
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="RLock created",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        self._initialized = True  # noqa: E0203
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Initialization complete",
                                 scope="COLD_START", success=True)
            except (AttributeError, TypeError, RuntimeError):
                pass

    def record_import(self, module_name: str, duration_ms: float) -> None:
        """Record timing for a module import during INIT phase.

        Args:
            module_name: Name of the module being imported
            duration_ms: Time taken to import in milliseconds

        """
        with self._lock:
            if self._phase != ContainerPhase.INIT:
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
        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="finalize_cold_start ENTRY",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message=f"Current phase: {self._phase}",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Attempting to acquire self._lock",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        with self._lock:
            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message="Lock ACQUIRED successfully",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass

            if _execute_operation and _GatewayInterface:
                try:
                    _execute_operation(_GatewayInterface.DEBUG, 'log',
                                     message=f"Checking if phase == INIT: {self._phase == ContainerPhase.INIT}",
                                     scope="COLD_START")
                except (AttributeError, TypeError, RuntimeError):
                    pass

            if self._phase == ContainerPhase.INIT:
                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message="Phase is INIT, setting cold_start_complete_time",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

                self._cold_start_complete_time = time.time()

                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message=f"cold_start_complete_time set: {self._cold_start_complete_time}",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message="Transitioning phase to FIRST_REQUEST",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

                self._phase = ContainerPhase.FIRST_REQUEST

                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message=f"Phase transition complete: {self._phase}",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message="Finalization complete, releasing lock",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass
            else:
                if _execute_operation and _GatewayInterface:
                    try:
                        _execute_operation(_GatewayInterface.DEBUG, 'log',
                                         message=f"Phase is not INIT (current: {self._phase}), skipping",
                                         scope="COLD_START")
                    except (AttributeError, TypeError, RuntimeError):
                        pass

        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="Lock RELEASED",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

        if _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="finalize_cold_start EXIT",
                                 scope="COLD_START")
            except (AttributeError, TypeError, RuntimeError):
                pass

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
            if not timings:
                return ColdStartMetrics(
                    container_phase=self._phase,
                    import_count=0,
                    total_import_time_ms=0,
                    average_import_time_ms=0,
                    slowest_import_ms=0,
                    slowest_import_module=None,
                    invocation_count=self._invocation_count,
                )
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
