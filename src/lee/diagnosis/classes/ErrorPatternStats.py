#!/usr/bin/env python3
"""Error pattern statistics data model for diagnosis system."""

from dataclasses import dataclass, field

from lee.diagnosis.classes.ErrorSignature import ErrorSignature
from lee.diagnosis.enums.ErrorPattern import ErrorPattern


@dataclass
class ErrorPatternStats:
    """Statistics for a specific error pattern.

    Attributes:
        signature: Error signature for this pattern
        pattern: Error classification pattern (NEW, EMERGING, CHRONIC, RESOLVED)
        first_seen: Unix timestamp of first occurrence
        last_seen: Unix timestamp of most recent occurrence
        occurrence_count: Total number of occurrences
        frequency_trend: Growth rate (positive = increasing, negative = decreasing)
        severity_distribution: Dictionary of severity level counts
        recent_correlation_ids: List of recent correlation IDs (last 10)
    """

    signature: ErrorSignature
    pattern: ErrorPattern
    first_seen: float
    last_seen: float
    occurrence_count: int
    frequency_trend: float
    severity_distribution: dict[str, int] = field(default_factory=dict)
    recent_correlation_ids: list[str] = field(default_factory=list)
