#!/usr/bin/env python3
"""Error severity enumeration for diagnosis system."""

from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels.

    Levels:
        LOW: Low severity error
        MEDIUM: Medium severity error
        HIGH: High severity error
        CRITICAL: Critical error requiring immediate attention
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
