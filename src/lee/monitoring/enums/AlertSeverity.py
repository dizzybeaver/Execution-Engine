#!/usr/bin/env python3
"""Alert severity enumeration for monitoring system."""

from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels.

    Levels:
        INFO: Informational alert
        WARNING: Warning alert
        ERROR: Error alert
        CRITICAL: Critical alert requiring immediate attention
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
