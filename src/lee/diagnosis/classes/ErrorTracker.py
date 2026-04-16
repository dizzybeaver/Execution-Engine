#!/usr/bin/env python3
"""Error Pattern Recognition System for LEE

Tracks and classifies error patterns across Lambda invocations to identify:
- NEW errors: First occurrence within time window
- EMERGING errors: Increasing frequency over time
- CHRONIC errors: Persistent recurring issues

Zero external dependencies (Python stdlib only)
"""

import threading
import time
from collections import defaultdict, deque
from typing import Any, Optional

from lee.diagnosis.classes.ErrorOccurrence import ErrorOccurrence
from lee.diagnosis.classes.ErrorPatternStats import ErrorPatternStats
from lee.diagnosis.classes.ErrorSignature import ErrorSignature
from lee.diagnosis.enums import ErrorPattern, ErrorSeverity
from lee.gateway.gateway_core import generate_correlation_id


class ErrorTracker:
    """Track and classify error patterns across Lambda invocations.

    Thread-safe singleton pattern for use in AWS Lambda.
    Uses deque with maxlen for automatic memory management.
    """

    def __init__(
        self,
        max_occurrences: int = 500,
        frequency_window: int = 20,
        emerging_threshold: float = 0.3,
        chronic_threshold: int = 10,
    ):
        """Initialize ErrorTracker.

        Args:
            max_occurrences: Maximum error occurrences to track (auto-evicts oldest)
            frequency_window: Number of data points for frequency trend calculation
            emerging_threshold: Growth rate to classify as EMERGING (30% increase)
            chronic_threshold: Occurrence count to classify as CHRONIC

        """
        self._occurrences: deque[ErrorOccurrence] = deque(maxlen=max_occurrences)
        self._patterns: dict[ErrorSignature, ErrorPatternStats] = {}
        self._frequency_history: dict[ErrorSignature, list[int]] = defaultdict(list)

        self._lock = threading.Lock()
        self._max_occurrences = max_occurrences
        self._frequency_window = frequency_window
        self._emerging_threshold = emerging_threshold
        self._chronic_threshold = chronic_threshold

    def record_error(
        self,
        error_type: str,
        error_category: str,
        source_module: str,
        message: str,
        severity: str = "medium",
        correlation_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> ErrorPatternStats:
        """Record an error occurrence and classify its pattern.

        Args:
            error_type: Exception type name (e.g., "ConnectionError")
            error_category: Category of error (e.g., "database", "network", "validation")
            source_module: Module where error occurred
            message: Error message
            severity: Error severity ("low", "medium", "high", "critical")
            correlation_id: Request correlation ID
            context: Additional context dictionary

        Returns:
            ErrorPatternStats for this error signature

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("err")

        if context is None:
            context = {}

        # Validate and normalize severity
        valid_severities = {s.value for s in ErrorSeverity}
        if severity not in valid_severities:
            severity = "medium"

        signature = ErrorSignature(error_type, error_category, source_module)
        timestamp = time.time()

        occurrence = ErrorOccurrence(
            signature=signature,
            timestamp=timestamp,
            correlation_id=correlation_id,
            message=message,
            severity=severity,
            context=context,
        )

        with self._lock:
            # Record occurrence
            self._occurrences.append(occurrence)

            # Update or create pattern stats
            if signature not in self._patterns:
                self._patterns[signature] = ErrorPatternStats(
                    signature=signature,
                    pattern=ErrorPattern.NEW,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    occurrence_count=1,
                    frequency_trend=0.0,
                    severity_distribution={severity: 1},
                    recent_correlation_ids=[correlation_id],
                )
            else:
                stats = self._patterns[signature]
                stats.last_seen = timestamp
                stats.occurrence_count += 1
                stats.severity_distribution[severity] = stats.severity_distribution.get(severity, 0) + 1

                # Keep only recent correlation IDs (last 10)
                if len(stats.recent_correlation_ids) >= 10:
                    stats.recent_correlation_ids.pop(0)
                stats.recent_correlation_ids.append(correlation_id)

            # Update frequency history
            self._frequency_history[signature].append(1)
            if len(self._frequency_history[signature]) > self._frequency_window:
                self._frequency_history[signature].pop(0)

            # Reclassify pattern
            self._classify_pattern(signature)

            return self._patterns[signature]

    def _classify_pattern(self, signature: ErrorSignature) -> None:
        """Classify error pattern based on occurrence history.

        Classification rules:
        - NEW: First occurrence OR recent occurrence after being RESOLVED
        - CHRONIC: High occurrence count (>= chronic_threshold)
        - EMERGING: Frequency trend showing growth
        - RESOLVED: Not seen for 2x the frequency window
        """
        stats = self._patterns[signature]

        # Check for CHRONIC (high occurrence)
        if stats.occurrence_count >= self._chronic_threshold:
            stats.pattern = ErrorPattern.CHRONIC
            return

        # Check for EMERGING (increasing frequency)
        freq_history = self._frequency_history[signature]
        if len(freq_history) >= 5:
            # Calculate trend: recent frequency vs older frequency
            recent_count = sum(freq_history[-3:])
            older_count = sum(freq_history[-6:-3]) if len(freq_history) >= 6 else recent_count

            if older_count > 0:
                growth_rate = (recent_count - older_count) / older_count
                stats.frequency_trend = growth_rate

                if growth_rate > self._emerging_threshold:
                    stats.pattern = ErrorPattern.EMERGING
                    return

        # Default to NEW if not CHRONIC or EMERGING
        stats.pattern = ErrorPattern.NEW

    def get_error_patterns(
        self,
        pattern_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Get error patterns with optional filtering.

        Args:
            pattern_filter: Filter by pattern ("new", "emerging", "chronic", "resolved")
            severity_filter: Filter by severity level
            category_filter: Filter by error category

        Returns:
            List of error pattern dictionaries

        """
        # Copy data under lock to minimize lock scope
        with self._lock:
            patterns_copy = [
                (signature, stats)
                for signature, stats in self._patterns.items()
            ]

        # Process outside lock
        results = []
        for signature, stats in patterns_copy:
            # Apply filters
            if pattern_filter and stats.pattern.value != pattern_filter:
                continue
            if severity_filter:
                if severity_filter not in stats.severity_distribution:
                    continue
            if category_filter and signature.error_category != category_filter:
                continue

            results.append({
                "error_type": signature.error_type,
                "error_category": signature.error_category,
                "source_module": signature.source_module,
                "pattern": stats.pattern.value,
                "first_seen": stats.first_seen,
                "last_seen": stats.last_seen,
                "occurrence_count": stats.occurrence_count,
                "frequency_trend": stats.frequency_trend,
                "severity_distribution": dict(stats.severity_distribution),
                "recent_correlation_ids": list(stats.recent_correlation_ids),
            })

        # Sort by last seen (most recent first)
        results.sort(key=lambda x: x["last_seen"], reverse=True)
        return results

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary statistics of all error patterns.

        Returns:
            Dictionary with summary statistics

        """
        # Copy data under lock to minimize lock scope
        with self._lock:
            total_occurrences = len(self._occurrences)
            patterns_copy = list(self._patterns.items())
            occurrences_copy = list(self._occurrences)[-10:]

        # Process outside lock
        pattern_counts = defaultdict(int)
        for stats in self._patterns.values():
            pattern_counts[stats.pattern.value] += 1

        # Get most severe errors (by severity and occurrence)
        severe_errors = sorted(
            [
                {
                    "signature": sig,
                    "count": stats.occurrence_count,
                    "severity": self._calculate_severity_score(stats),
                }
                for sig, stats in patterns_copy
            ],
            key=lambda x: (x["severity"], x["count"]),
            reverse=True,
        )[:10]

        return {
            "total_occurrences": total_occurrences,
            "total_patterns": len(patterns_copy),
            "patterns_by_type": dict(pattern_counts),
            "most_severe_errors": severe_errors,
            "recent_errors": [
                {
                    "error_type": occ.signature.error_type,
                    "message": occ.message,
                    "timestamp": occ.timestamp,
                    "correlation_id": occ.correlation_id,
                }
                for occ in occurrences_copy
            ],
        }

    def _calculate_severity_score(self, stats: ErrorPatternStats) -> int:
        """Calculate severity score (higher = more severe)."""
        severity_weights = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }

        # Weighted average severity
        weighted_sum = sum(
            severity_weights.get(sev, 0) * count
            for sev, count in stats.severity_distribution.items()
        )
        total_count = sum(stats.severity_distribution.values())

        if total_count == 0:
            return 0

        return int(weighted_sum / total_count)

    def reset(self) -> None:
        """Reset all tracking state."""
        with self._lock:
            self._occurrences.clear()
            self._patterns.clear()
            self._frequency_history.clear()


# Singleton instance
_error_tracker_singleton: Optional[ErrorTracker] = None
_error_tracker_lock = threading.Lock()


def get_error_tracker(
    max_occurrences: int = 500,
    reset: bool = False,
) -> ErrorTracker:
    """Get or create singleton ErrorTracker instance.

    Args:
        max_occurrences: Maximum occurrences to track
        reset: If True, reset the singleton

    Returns:
        ErrorTracker singleton instance

    """
    global _error_tracker_singleton

    if _error_tracker_singleton is None or reset:
        with _error_tracker_lock:
            if _error_tracker_singleton is None or reset:
                if reset and _error_tracker_singleton is not None:
                    _error_tracker_singleton.reset()
                _error_tracker_singleton = ErrorTracker(max_occurrences=max_occurrences)

    return _error_tracker_singleton


# Gateway integration functions
def error_tracker_record_error(
    error_type: str,
    error_category: str,
    source_module: str,
    message: str,
    severity: str = "medium",
    correlation_id: Optional[str] = None,
    context: Optional[dict] = None,
) -> dict[str, Any]:
    """Record error occurrence (Gateway integration)."""
    tracker = get_error_tracker()
    stats = tracker.record_error(
        error_type=error_type,
        error_category=error_category,
        source_module=source_module,
        message=message,
        severity=severity,
        correlation_id=correlation_id,
        context=context,
    )

    return {
        "pattern": stats.pattern.value,
        "occurrence_count": stats.occurrence_count,
        "first_seen": stats.first_seen,
        "last_seen": stats.last_seen,
    }


def error_tracker_get_patterns(
    pattern_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get error patterns (Gateway integration)."""
    tracker = get_error_tracker()
    return tracker.get_error_patterns(
        pattern_filter=pattern_filter,
        severity_filter=severity_filter,
        category_filter=category_filter,
    )


def error_tracker_get_summary() -> dict[str, Any]:
    """Get error summary (Gateway integration)."""
    tracker = get_error_tracker()
    return tracker.get_error_summary()


def error_tracker_reset() -> None:
    """Reset error tracker (Gateway integration)."""
    tracker = get_error_tracker()
    tracker.reset()


__all__ = [
    "ErrorTracker",
    "error_tracker_get_patterns",
    "error_tracker_get_summary",
    "error_tracker_record_error",
    "error_tracker_reset",
    "get_error_tracker",
]
