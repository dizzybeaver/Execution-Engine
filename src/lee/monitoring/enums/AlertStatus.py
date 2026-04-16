#!/usr/bin/env python3
"""Alert status enumeration for monitoring system."""

from enum import Enum


class AlertStatus(Enum):
    """Alert status tracking.

    States:
        ACTIVE: Alert is active and requires attention
        ACKNOWLEDGED: Alert has been acknowledged but not resolved
        RESOLVED: Alert has been resolved
        SUPPRESSED: Alert has been auto-suppressed due to duplicate threshold
    """

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
