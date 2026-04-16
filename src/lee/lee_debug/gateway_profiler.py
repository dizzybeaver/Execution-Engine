"""lee_debug/gateway_profiler.py
Version: 2025-03-03_1
Purpose: Gateway profiler for timing statistics collection
License: Apache 2.0

Collects and aggregates timing statistics from all DEBUG timing calls.
Provides p50, p95, p99 percentiles for operation performance analysis.

Memory-efficient design using bounded samples (100 max per operation).
Thread-safe singleton implementation following LEE patterns.
"""

from __future__ import annotations

import statistics
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class OperationStatistics:
    """Statistics for a single operation name.

    Memory-efficient design:
    - Keeps last 100 samples only (bounded deque)
    - Computes percentiles on-demand
    - Tracks aggregates (count, min, max, total) incrementally

    Attributes:
        operation_name: Operation identifier
        scope: Debug scope (GATEWAY, CACHE, HA, etc.)
        call_count: Total number of calls
        min_duration_ms: Minimum duration observed
        max_duration_ms: Maximum duration observed
        total_duration_ms: Sum of all durations (for average calculation)
        avg_duration_ms: Average duration
        p50_duration_ms: 50th percentile (median)
        p95_duration_ms: 95th percentile
        p99_duration_ms: 99th percentile
        last_call: Most recent call timestamp
        created_at: When this operation was first tracked
        samples: Bounded deque of last 100 samples

    """

    operation_name: str
    scope: str
    call_count: int = 0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    last_call: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    samples: deque[float] = field(default_factory=lambda: deque(maxlen=100))

    def record_timing(self, duration_ms: float) -> None:
        """Record a timing sample.

        Args:
            duration_ms: Duration in milliseconds

        """
        self.call_count += 1
        self.last_call = datetime.now()

        # Update aggregates
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
        self.total_duration_ms += duration_ms
        self.avg_duration_ms = self.total_duration_ms / self.call_count

        # Keep last 100 samples for percentiles (deque auto-bounds)
        self.samples.append(duration_ms)

        # Update percentile statistics
        self._update_percentiles()

    def _update_percentiles(self) -> None:
        """Update percentile statistics from current samples."""
        if not self.samples:
            return

        # P50: Use statistics.median()
        self.p50_duration_ms = statistics.median(self.samples)

        # P95/P99: Index-based (cache_observability.py pattern)
        sorted_samples = sorted(self.samples)
        n = len(sorted_samples)

        # P95 requires at least 20 samples
        if n >= 20:
            self.p95_duration_ms = sorted_samples[int(n * 0.95)]
        else:
            self.p95_duration_ms = 0.0

        # P99 requires at least 100 samples
        if n >= 100:
            self.p99_duration_ms = sorted_samples[int(n * 0.99)]
        else:
            self.p99_duration_ms = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dict representation of statistics

        """
        return {
            "operation_name": self.operation_name,
            "scope": self.scope,
            "call_count": self.call_count,
            "min_duration_ms": (
                round(self.min_duration_ms, 2)
                if self.min_duration_ms != float("inf")
                else 0.0
            ),
            "max_duration_ms": round(self.max_duration_ms, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "p50_duration_ms": round(self.p50_duration_ms, 2),
            "p95_duration_ms": round(self.p95_duration_ms, 2),
            "p99_duration_ms": round(self.p99_duration_ms, 2),
            "last_call": self.last_call.isoformat() if self.last_call else None,
            "created_at": self.created_at.isoformat(),
            "sample_count": len(self.samples),
        }


class GatewayProfiler:  # pylint: disable=too-many-instance-attributes
    """Gateway profiler for timing statistics collection.

    Thread-safe singleton implementation following CacheObservability pattern.

    Features:
    - Automatic collection from existing timing calls
    - Per-operation statistics with percentiles
    - Memory-efficient (~1.6MB for all operations)
    - Thread-safe with RLock

    Memory estimation:
    - 100 operations × 100 samples × 8 bytes (float) = 80KB samples
    - 100 operations × ~500 bytes metadata = 50KB metadata
    - Overhead: ~1.5MB for data structures
    """

    _instance: Optional[GatewayProfiler] = None
    _lock = threading.RLock()

    def __new__(cls) -> GatewayProfiler:
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize gateway profiler (only once)."""
        if getattr(self, "_initialized", False):
            return

        self._operation_stats: dict[str, OperationStatistics] = {}
        self._enabled: bool = True
        self._initialized = True

    def enable(self) -> None:
        """Enable profiler collection."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable profiler collection."""
        with self._lock:
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if profiler is enabled.

        Returns:
            True if enabled, False otherwise

        """
        return self._enabled

    def record_timing(self, operation_name: str, duration_ms: float,
                     scope: str = "GATEWAY") -> None:
        """Record a timing sample for an operation.

        Thread-safe with RLock.

        Args:
            operation_name: Operation identifier
            duration_ms: Duration in milliseconds
            scope: Debug scope (default: GATEWAY)

        """
        if not self._enabled:
            return

        with self._lock:
            stats = self._operation_stats.get(operation_name)
            if stats is None:
                stats = OperationStatistics(
                    operation_name=operation_name,
                    scope=scope,
                )
                self._operation_stats[operation_name] = stats

            stats.record_timing(duration_ms)

    def get_operation_stats(self, operation_name: str) -> Optional[dict[str, Any]]:
        """Get statistics for a specific operation.

        Args:
            operation_name: Operation identifier

        Returns:
            Statistics dict or None if operation not found

        """
        with self._lock:
            stats = self._operation_stats.get(operation_name)
            return stats.to_dict() if stats else None

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all tracked operations.

        Returns:
            Dict mapping operation_name → statistics dict

        """
        with self._lock:
            return {
                op_name: stats.to_dict()
                for op_name, stats in self._operation_stats.items()
            }

    def get_stats_by_scope(self, scope: str) -> dict[str, dict[str, Any]]:
        """Get statistics for all operations in a specific scope.

        Args:
            scope: Debug scope (e.g., "CACHE", "HA", "GATEWAY")

        Returns:
            Dict mapping operation_name → statistics dict

        """
        with self._lock:
            return {
                op_name: stats.to_dict()
                for op_name, stats in self._operation_stats.items()
                if stats.scope == scope
            }

    def reset_operation(self, operation_name: str) -> bool:
        """Reset statistics for a specific operation.

        Args:
            operation_name: Operation identifier

        Returns:
            True if reset, False if operation not found

        """
        with self._lock:
            if operation_name in self._operation_stats:
                del self._operation_stats[operation_name]
                return True
            return False

    def reset_all(self) -> int:
        """Reset all operation statistics.

        Returns:
            Count of operations reset

        """
        with self._lock:
            count = len(self._operation_stats)
            self._operation_stats.clear()
            return count

    def get_summary(self) -> dict[str, Any]:
        """Get profiler summary statistics.

        Returns:
            Summary dict with totals and memory estimate

        """
        with self._lock:
            total_calls = sum(stats.call_count for stats in self._operation_stats.values())
            total_operations = len(self._operation_stats)

            # Memory estimation (rough)
            sample_bytes = sum(
                len(stats.samples) * 8
                for stats in self._operation_stats.values()
            )
            metadata_bytes = total_operations * 500
            overhead_bytes = 1500000  # Fixed overhead
            memory_bytes = sample_bytes + metadata_bytes + overhead_bytes

            return {
                "total_operations": total_operations,
                "total_calls": total_calls,
                "enabled": self._enabled,
                "estimated_memory_bytes": memory_bytes,
                "estimated_memory_kb": memory_bytes / 1024,
                "estimated_memory_mb": memory_bytes / (1024 * 1024),
                "scopes": list(
                    set(stats.scope for stats in self._operation_stats.values()),
                ),
            }


def get_gateway_profiler() -> GatewayProfiler:
    """Get singleton GatewayProfiler instance.

    Returns:
        GatewayProfiler singleton instance

    """
    return GatewayProfiler()


__all__ = [
    "GatewayProfiler",
    "OperationStatistics",
    "get_gateway_profiler",
]
