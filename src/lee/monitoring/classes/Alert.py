#!/usr/bin/env python3
"""Alert data model for monitoring system."""

from dataclasses import dataclass, field
from typing import Optional

from lee.monitoring.enums.AlertSeverity import AlertSeverity
from lee.monitoring.enums.AlertStatus import AlertStatus


@dataclass
class Alert:
    """Alert record with metadata and status tracking.

from typing import Optional
    Attributes:
        alert_id: Unique identifier for the alert
        title: Brief alert title
        description: Detailed alert description
        severity: Alert severity level (INFO, WARNING, ERROR, CRITICAL)
        status: Alert status (ACTIVE, ACKNOWLEDGED, RESOLVED, SUPPRESSED)
        source: Source module or system that generated the alert
        created_at: Timestamp when alert was created
        updated_at: Timestamp when alert was last updated
        correlation_id: Optional request correlation ID
        context: Additional context dictionary
        occurrences: Number of times this alert has occurred
        first_occurrence: Timestamp of first occurrence
        last_occurrence: Timestamp of most recent occurrence
    """

    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    created_at: float
    updated_at: float
    correlation_id: Optional[str] = None
    context: dict = field(default_factory=dict)
    occurrences: int = 1
    first_occurrence: Optional[float] = None
    last_occurrence: Optional[float] = None

    def __post_init__(self):
        """Initialize occurrence timestamps if not provided."""
        if self.first_occurrence is None:
            self.first_occurrence = self.created_at
        if self.last_occurrence is None:
            self.last_occurrence = self.created_at
