#!/usr/bin/env python3
"""Anomaly severity enumeration for performance system."""

from enum import Enum


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies.

    Levels:
        LOW: Low severity anomaly
        MEDIUM: Medium severity anomaly
        HIGH: High severity anomaly
        CRITICAL: Critical anomaly requiring immediate attention
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
