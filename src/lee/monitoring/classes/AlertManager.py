#!/usr/bin/env python3
"""Local Alerting System for LEE

In-memory alert tracking with severity-based aggregation and automatic de-duplication.
Zero external dependencies (Python stdlib only).
"""

import random
import threading
import time
from collections import defaultdict, deque
from hashlib import sha256
from typing import Any, Optional

from lee.lee_security import InputSanitizer, LogSanitizer, SanitizeLevel
from lee.monitoring.classes.Alert import Alert
from lee.monitoring.classes.AlertSeverity import AlertSeverity
from lee.monitoring.classes.AlertStats import AlertStats
from lee.monitoring.classes.AlertStatus import AlertStatus

# Security constants
MAX_DESCRIPTION_LENGTH = 4096
MAX_TITLE_LENGTH = 512
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_ALERTS_PER_SOURCE = 10


class AlertManager:
    """In-memory alert tracking with de-duplication and severity aggregation.

    Features:
    - Automatic de-duplication based on source:title signature
    - Duplicate window: 300 seconds (configurable)
    - Auto-suppression after 5 duplicates (configurable)
    - Alert lifecycle: ACTIVE -> ACKNOWLEDGED -> RESOLVED or SUPPRESSED
    """

    def __init__(
        self,
        max_alerts: int = 200,
        duplicate_window_seconds: int = 300,
        suppression_threshold: int = 5,
    ):
        """Initialize AlertManager.

        Args:
            max_alerts: Maximum alerts to track (auto-evicts oldest)
            duplicate_window_seconds: Time window for considering duplicates
            suppression_threshold: Number of duplicates before auto-suppression

        """
        self._alerts: deque[Alert] = deque(maxlen=max_alerts)
        self._alert_index: dict[str, Alert] = {}
        self._rate_limit_tracker: dict[str, list[float]] = defaultdict(list)

        self._lock = threading.Lock()
        self._max_alerts = max_alerts
        self._duplicate_window = duplicate_window_seconds
        self._suppression_threshold = suppression_threshold
        self._input_sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        self._log_sanitizer = LogSanitizer()

    def create_alert(
        self,
        title: str,
        description: str,
        severity: str,
        source: str,
        correlation_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> Alert:
        """Create or update an alert (with de-duplication).

        If an alert with the same source:title exists within the duplicate window,
        the existing alert is updated (occurrence count incremented) instead of
        creating a new alert.

        Args:
            title: Alert title
            description: Alert description
            severity: Alert severity ("info", "warning", "error", "critical")
            source: Alert source (module or system name)
            correlation_id: Request correlation ID
            context: Additional context dictionary

        Returns:
            Alert object (created or updated)

        Raises:
            ValueError: If rate limit exceeded or payload too large

        """
        if context is None:
            context = {}

        timestamp = time.time()

        # Rate limiting check (MEDIUM Issue #4)
        with self._lock:
            source_alerts = self._rate_limit_tracker[source]
            # Remove alerts outside the time window
            source_alerts[:] = [t for t in source_alerts if timestamp - t < RATE_LIMIT_WINDOW_SECONDS]

            if len(source_alerts) >= RATE_LIMIT_MAX_ALERTS_PER_SOURCE:
                raise ValueError(
                    f"Rate limit exceeded for source '{source}': "
                    f"{RATE_LIMIT_MAX_ALERTS_PER_SOURCE} alerts per {RATE_LIMIT_WINDOW_SECONDS} seconds"
                )

            source_alerts.append(timestamp)

        # Input sanitization (HIGH Issue #1)
        title_result = self._input_sanitizer.sanitize(title, context="general")
        description_result = self._input_sanitizer.sanitize(description, context="general")
        source_result = self._input_sanitizer.sanitize(source, context="general")

        title = title_result.sanitized
        description = description_result.sanitized
        source = source_result.sanitized

        # Payload size limits (MEDIUM Issue #5)
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH]
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH]

        # Normalize severity string to enum with validation warning
        try:
            severity_enum = AlertSeverity(severity.lower())
        except ValueError:
            print(f"WARNING: Invalid severity '{severity}' provided, defaulting to INFO")
            severity_enum = AlertSeverity.INFO

        # Generate signature and alert_id outside lock
        signature = self._generate_signature(source, title)
        alert_id = self._generate_alert_id(title, timestamp)

        with self._lock:
            # Check for duplicate within window
            if signature in self._alert_index:
                existing = self._alert_index[signature]

                # Check if within duplicate window
                if timestamp - existing.last_occurrence <= self._duplicate_window:
                    # Update existing alert
                    existing.occurrences += 1
                    existing.last_occurrence = timestamp
                    existing.updated_at = timestamp
                    existing.status = AlertStatus.ACTIVE

                    # Check for auto-suppression
                    if existing.occurrences >= self._suppression_threshold:
                        existing.status = AlertStatus.SUPPRESSED

                    return existing

            # Create new alert (only object creation under lock)
            alert = Alert(
                alert_id=alert_id,
                title=title,
                description=description,
                severity=severity_enum,
                status=AlertStatus.ACTIVE,
                source=source,
                created_at=timestamp,
                updated_at=timestamp,
                correlation_id=correlation_id,
                context=context,
                occurrences=1,
                first_occurrence=timestamp,
                last_occurrence=timestamp,
            )

            self._alerts.append(alert)
            self._alert_index[signature] = alert

            return alert

    def acknowledge_alert(self, alert_id: str, caller_permissions: Optional[dict[str, bool]] = None) -> Optional[Alert]:
        """Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge
            caller_permissions: Optional dict with 'can_acknowledge_alerts' permission key
                              If None, operation is allowed (backward compatibility)

        Returns:
            Updated Alert if found, None otherwise

        Raises:
            PermissionError: If caller lacks acknowledge permissions

        """
        # Access control check (HIGH Issue #3)
        if caller_permissions is not None and not caller_permissions.get('can_acknowledge_alerts', False):
            raise PermissionError("Caller lacks permission to acknowledge alerts")

        with self._lock:
            alert = self._get_alert_by_id(alert_id)
            if alert and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.updated_at = time.time()
                return alert

        return None

    def resolve_alert(self, alert_id: str, caller_permissions: Optional[dict[str, bool]] = None) -> Optional[Alert]:
        """Resolve an alert.

        Args:
            alert_id: Alert ID to resolve
            caller_permissions: Optional dict with 'can_resolve_alerts' permission key
                              If None, operation is allowed (backward compatibility)

        Returns:
            Updated Alert if found, None otherwise

        Raises:
            PermissionError: If caller lacks resolve permissions

        """
        # Access control check (HIGH Issue #3)
        if caller_permissions is not None and not caller_permissions.get('can_resolve_alerts', False):
            raise PermissionError("Caller lacks permission to resolve alerts")

        with self._lock:
            alert = self._get_alert_by_id(alert_id)
            if alert and alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED, AlertStatus.SUPPRESSED]:
                alert.status = AlertStatus.RESOLVED
                alert.updated_at = time.time()
                return alert

        return None

    def get_alerts(
        self,
        severity_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
        limit: Optional[int] = None,
        redact_pii: bool = True,
    ) -> list[dict[str, Any]]:
        """Get alerts with optional filtering.

        Args:
            severity_filter: Filter by severity level
            status_filter: Filter by status ("active", "acknowledged", "resolved", "suppressed")
            source_filter: Filter by source
            limit: Maximum number of alerts to return
            redact_pii: Whether to redact PII from descriptions (default: True)

        Returns:
            List of alert dictionaries with PII redacted

        """
        # Copy data under lock to minimize lock scope
        with self._lock:
            alerts_copy = list(self._alerts)

        # Process outside lock
        results = []
        for alert in alerts_copy:
            # Apply filters
            if severity_filter and alert.severity.value != severity_filter:
                continue
            if status_filter and alert.status.value != status_filter:
                continue
            if source_filter and alert.source != source_filter:
                continue

            # PII redaction (HIGH Issue #2)
            description = alert.description
            if redact_pii:
                description = self._log_sanitizer.sanitize(description)

            # Redact context dictionary if present
            sanitized_context = alert.context.copy()
            if redact_pii and sanitized_context:
                sanitized_context = self._log_sanitizer.sanitize_dict(sanitized_context)

            results.append({
                "alert_id": alert.alert_id,
                "title": alert.title,
                "description": description,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "source": alert.source,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at,
                "correlation_id": alert.correlation_id,
                "occurrences": alert.occurrences,
                "first_occurrence": alert.first_occurrence,
                "last_occurrence": alert.last_occurrence,
                "context": sanitized_context,
            })

        # Sort by created_at (most recent first)
        results.sort(key=lambda x: x["created_at"], reverse=True)

        if limit:
            results = results[:limit]

        return results

    def get_alert_stats(self) -> AlertStats:
        """Get alert statistics.

        Returns:
            AlertStats object with statistics

        """
        # Copy data under lock to minimize lock scope
        with self._lock:
            alerts_copy = list(self._alerts)

        # Process outside lock
        total_alerts = len(alerts_copy)
        severity_counts = defaultdict(int)
        status_counts = defaultdict(int)
        source_counts = defaultdict(int)

        for alert in alerts_copy:
            severity_counts[alert.severity.value] += 1
            status_counts[alert.status.value] += 1
            source_counts[alert.source] += 1

        # Get most active alerts
        most_active = sorted(
            alerts_copy,
            key=lambda a: (a.occurrences, a.last_occurrence),
            reverse=True,
        )[:5]

        return AlertStats(
            total_alerts=total_alerts,
            by_severity=dict(severity_counts),
            by_status=dict(status_counts),
            by_source=dict(source_counts),
            most_active=[
                {
                    "alert_id": a.alert_id,
                    "title": a.title,
                    "occurrences": a.occurrences,
                    "severity": a.severity.value,
                    "status": a.status.value,
                }
                for a in most_active
            ],
            active_critical_count=sum(
                1 for a in alerts_copy
                if a.status == AlertStatus.ACTIVE and a.severity == AlertSeverity.CRITICAL
            ),
            unacknowledged_count=sum(
                1 for a in alerts_copy
                if a.status == AlertStatus.ACTIVE
            ),
        )

    def _get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Find alert by ID (internal)."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                return alert
        return None

    def _generate_signature(self, source: str, title: str) -> str:
        """Generate signature for de-duplication."""
        signature_string = f"{source}:{title}"
        return sha256(signature_string.encode()).hexdigest()[:16]

    def _generate_alert_id(self, title: str, timestamp: float) -> str:
        """Generate unique alert ID."""
        # Alert ID - non-security-critical, use fast random
        hash_input = f"{title}:{timestamp}:{random.randbytes(4).hex()}"
        return sha256(hash_input.encode()).hexdigest()[:12]

    def reset(self) -> None:
        """Reset all alert state."""
        with self._lock:
            self._alerts.clear()
            self._alert_index.clear()
            self._rate_limit_tracker.clear()


# Singleton instance
_alert_manager_singleton: Optional[AlertManager] = None
_alert_manager_lock = threading.Lock()


def get_alert_manager(
    max_alerts: int = 200,
    reset: bool = False,
) -> AlertManager:
    """Get or create singleton AlertManager instance.

    Args:
        max_alerts: Maximum alerts to track
        reset: If True, reset the singleton

    Returns:
        AlertManager singleton instance

    """
    global _alert_manager_singleton

    if _alert_manager_singleton is None or reset:
        with _alert_manager_lock:
            if _alert_manager_singleton is None or reset:
                if reset and _alert_manager_singleton is not None:
                    _alert_manager_singleton.reset()
                _alert_manager_singleton = AlertManager(max_alerts=max_alerts)

    return _alert_manager_singleton


# Gateway integration functions
def alert_manager_create(
    title: str,
    description: str,
    severity: str,
    source: str,
    correlation_id: Optional[str] = None,
    context: Optional[dict] = None,
) -> dict[str, Any]:
    """Create or update alert (Gateway integration)."""
    manager = get_alert_manager()
    alert = manager.create_alert(
        title=title,
        description=description,
        severity=severity,
        source=source,
        correlation_id=correlation_id,
        context=context,
    )

    return {
        "alert_id": alert.alert_id,
        "status": alert.status.value,
        "occurrences": alert.occurrences,
    }


def alert_manager_acknowledge(
    alert_id: str,
    caller_permissions: Optional[dict[str, bool]] = None,
) -> Optional[dict[str, Any]]:
    """Acknowledge an alert (Gateway integration)."""
    manager = get_alert_manager()
    alert = manager.acknowledge_alert(alert_id, caller_permissions=caller_permissions)

    if alert:
        return {
            "alert_id": alert.alert_id,
            "status": alert.status.value,
            "updated_at": alert.updated_at,
        }

    return None


def alert_manager_resolve(
    alert_id: str,
    caller_permissions: Optional[dict[str, bool]] = None,
) -> Optional[dict[str, Any]]:
    """Resolve an alert (Gateway integration)."""
    manager = get_alert_manager()
    alert = manager.resolve_alert(alert_id, caller_permissions=caller_permissions)

    if alert:
        return {
            "alert_id": alert.alert_id,
            "status": alert.status.value,
            "updated_at": alert.updated_at,
        }

    return None


def alert_manager_get(
    severity_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    source_filter: Optional[str] = None,
    limit: Optional[int] = None,
    redact_pii: bool = True,
) -> list[dict[str, Any]]:
    """Get filtered alerts (Gateway integration)."""
    manager = get_alert_manager()
    return manager.get_alerts(
        severity_filter=severity_filter,
        status_filter=status_filter,
        source_filter=source_filter,
        limit=limit,
        redact_pii=redact_pii,
    )


def alert_manager_get_stats() -> dict[str, Any]:
    """Get alert statistics (Gateway integration)."""
    manager = get_alert_manager()
    stats = manager.get_alert_stats()

    return {
        "total_alerts": stats.total_alerts,
        "by_severity": stats.by_severity,
        "by_status": stats.by_status,
        "by_source": stats.by_source,
        "most_active": stats.most_active,
        "active_critical_count": stats.active_critical_count,
        "unacknowledged_count": stats.unacknowledged_count,
    }


def alert_manager_reset() -> None:
    """Reset alert manager (Gateway integration)."""
    manager = get_alert_manager()
    manager.reset()


__all__ = [
    "AlertManager",
    "alert_manager_acknowledge",
    "alert_manager_create",
    "alert_manager_get",
    "alert_manager_get_stats",
    "alert_manager_reset",
    "alert_manager_resolve",
    "get_alert_manager",
]
