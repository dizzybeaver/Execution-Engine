#!/usr/bin/env python3
"""Alert statistics data model for monitoring system."""

from dataclasses import dataclass
from typing import Any


@dataclass
class AlertStats:
    """Alert statistics summary.

    Attributes:
        total_alerts: Total number of alerts
        by_severity: Dictionary of alert counts by severity level
        by_status: Dictionary of alert counts by status
        by_source: Dictionary of alert counts by source
        most_active: List of most active alerts (by occurrence count)
        active_critical_count: Number of active critical alerts
        unacknowledged_count: Number of unacknowledged active alerts
    """

    total_alerts: int
    by_severity: dict[str, int]
    by_status: dict[str, int]
    by_source: dict[str, int]
    most_active: list[dict[str, Any]]
    active_critical_count: int
    unacknowledged_count: int
