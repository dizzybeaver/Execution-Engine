"""lee_debug/hot_path_detector.py
Version: 2025-03-03_1
Purpose: Hot path detection for gateway operations
License: Apache 2.0

Identifies which gateway operations handle the majority of traffic.
Enables Pareto analysis (top 20% of code handling 80% of requests).

Memory-efficient design with sampling support.
Thread-safe singleton implementation.
"""

from __future__ import annotations

import os
import random
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional


        # Sampling check
@dataclass
class HotPathStats:
    """Statistics for a single operation in hot path analysis.

    Attributes:
        operation_key: Combined "interface.operation" key
        interface: GatewayInterface value
        operation: Operation name
        call_count: Number of times called
        percentage: Percentage of total calls

    """

    operation_key: str
    interface: str
    operation: str
    call_count: int = 0
    percentage: float = 0.0


class HotPathDetector:
    """Detects and analyzes hot paths in gateway operation execution.

    Tracks which (interface, operation) pairs are called most frequently
    to identify optimization opportunities. Follows Lambda constraints:
    - Zero overhead when disabled
    - Minimal overhead when enabled (~1µs per call)
    - Memory efficient (~100KB for full operation tracking)
    - Thread-safe with RLock

    Features:
    - Operation frequency tracking
    - Top N operation identification
    - Percentage distribution calculation
    - Pareto analysis (20% of code → 80% of traffic)
    """

    _instance: Optional[HotPathDetector] = None
    _lock = threading.RLock()

    def __new__(cls) -> HotPathDetector:
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize hot path detector."""
        if getattr(self, "_initialized", False):
            return

        self._operation_counts: dict[str, int] = defaultdict(int)
        self._total_calls: int = 0
        self._enabled: bool = os.environ.get(
            "HOT_PATH_DETECTOR_ENABLED", "false",
        ).lower() == "true"
        try:
            self._sample_rate: float = float(
                os.environ.get("HOT_PATH_SAMPLE_RATE", "1.0"),
            )
            self._sample_rate = max(0.0, min(1.0, self._sample_rate))
        except (ValueError, TypeError):
            self._sample_rate = 1.0
        self._created_at: float = time.time()
        self._initialized = True

    def enable(self) -> None:
        """Enable hot path detection."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable hot path detection."""
        with self._lock:
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if detector is enabled.

            True if enabled, False otherwise

        """
        return self._enabled

    def set_sample_rate(self, sample_rate: float) -> float:
        """Set sampling rate for hot path detection.

            sample_rate: 0.0 to 1.0 (1.0 = track all calls, 0.1 = track 10%)

            Previous sample rate

        """
        with self._lock:
            previous = self._sample_rate
            self._sample_rate = max(0.0, min(1.0, sample_rate))
            return previous

    def record_operation(self, interface: str, operation: str) -> bool:
        """Record a gateway operation call.

        Thread-safe with optional sampling.

            interface: GatewayInterface value being called
            operation: Operation name being called

            True if recorded, False if not (disabled or sampled out)

        """
        if not self._enabled:
            return False

        if self._sample_rate < 1.0:
            if random.random() > self._sample_rate:
                return False

        with self._lock:
            key = f"{interface}.{operation}"
            self._operation_counts[key] += 1
            self._total_calls += 1
            return True

    def get_top_operations(self, n: int = 10) -> list[tuple[str, str, int]]:
        """Get top N most-called operations.

            n: Number of top operations to return

            List of tuples: [(interface, operation, count), ...]
            Sorted by count descending (hot path first)

        """
        with self._lock:
            # Sort by count descending
            sorted_ops = sorted(
                self._operation_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            # Convert to (interface, operation, count) tuples
            result = []
            for key, count in sorted_ops[:n]:
                parts = key.split(".", 1)
                if len(parts) == 2:
                    result.append((parts[0], parts[1], count))
                else:
                    result.append(("", key, count))

            return result

    def get_distribution(self) -> dict[str, Any]:
        """Get percentage distribution of operations.

            {
                'total_calls': int,
                'unique_operations': int,
                'by_interface': {'interface': percentage, ...},
                'by_operation': [('interface.operation', percentage), ...],
                'pareto_analysis': {
                    'top_20_percent_ops': [...],
                    'coverage_percent': float,
                    'is_pareto': bool
                }
            }

        """
        with self._lock:
            if self._total_calls == 0:
                return {
                    "total_calls": 0,
                    "unique_operations": 0,
                    "by_interface": {},
                    "by_operation": [],
                    "pareto_analysis": {
                        "top_20_percent_ops": [],
                        "coverage_percent": 0.0,
                        "is_pareto": False,
                    },
                }

            # Calculate operation percentages
            op_percentages = {
                op: (count / self._total_calls) * 100
                for op, count in self._operation_counts.items()
            }

            # Calculate interface percentages
            interface_counts: dict[str, int] = defaultdict(int)
            for key, count in self._operation_counts.items():
                parts = key.split(".", 1)
                interface = parts[0] if len(parts) == 2 else "unknown"
                interface_counts[interface] += count

            interface_percentages = {
                iface: (count / self._total_calls) * 100
                for iface, count in interface_counts.items()
            }

            # Pareto analysis: top 20% of operations
            sorted_ops = sorted(
                op_percentages.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            top_20_percent_count = max(1, len(sorted_ops) // 5)
            top_ops = sorted_ops[:top_20_percent_count]

            pareto_coverage = sum(percent for _, percent in top_ops)
            is_pareto = pareto_coverage >= 80.0

            return {
                "total_calls": self._total_calls,
                "unique_operations": len(self._operation_counts),
                "by_interface": interface_percentages,
                "by_operation": sorted_ops,
                "pareto_analysis": {
                    "top_20_percent_ops": [op for op, _ in top_ops],
                    "coverage_percent": round(pareto_coverage, 2),
                    "is_pareto": is_pareto,
                },
            }

    def get_stats(self) -> dict[str, Any]:
        """Get hot path detector statistics.

            {
                'enabled': bool,
                'sample_rate': float,
                'total_calls': int,
                'unique_operations': int,
                'estimated_memory_bytes': int,
                'uptime_seconds': float
            }

        """
        with self._lock:
            # Memory estimation: ~50 bytes per operation
            memory_bytes = len(self._operation_counts) * 50

            return {
                "enabled": self._enabled,
                "sample_rate": self._sample_rate,
                "total_calls": self._total_calls,
                "unique_operations": len(self._operation_counts),
                "estimated_memory_bytes": memory_bytes,
                "estimated_memory_kb": memory_bytes / 1024,
                "uptime_seconds": time.time() - self._created_at,
            }

    def reset(self) -> int:
        """Reset all tracking data.

            Previous total call count

        """
        with self._lock:
            previous_total = self._total_calls
            self._operation_counts.clear()
            self._total_calls = 0
            return previous_total


def get_hot_path_detector() -> HotPathDetector:
    """Get singleton HotPathDetector instance.

        HotPathDetector singleton instance

    """
    return HotPathDetector()


__all__ = [
    "HotPathDetector",
    "HotPathStats",
    "get_hot_path_detector",
]
