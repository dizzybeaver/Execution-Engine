#!/usr/bin/env python3
"""Error pattern enumeration for diagnosis system."""

from enum import Enum


class ErrorPattern(Enum):
    """Error classification pattern.

    Patterns:
        NEW: First occurrence within time window
        EMERGING: Increasing frequency over time
        CHRONIC: Persistent recurring issues
        RESOLVED: Error has been resolved
    """

    NEW = "new"
    EMERGING = "emerging"
    CHRONIC = "chronic"
    RESOLVED = "resolved"
