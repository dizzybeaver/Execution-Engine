# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-03 - Security audit logging for forensic and compliance

"""
Security Audit Logger Module

Provides comprehensive security event logging for forensic analysis
and compliance requirements (SOC 2, GDPR, PCI-DSS).

Events Logged:
- Authentication attempts (success/failure)
- Authorization failures
- Token validation failures
- Cryptographic operations
- Configuration changes
- Security policy violations
"""

import json
import os
import threading
import time
from collections import deque
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Optional

from lee.lee_logging.bootstrap_logging import get_bootstrap_logger
from lee.lee_security.sanitize import DataSanitizer
from lee.singleton import ThreadSafeSingleton


class SecurityEventType(Enum):
    """Security event types for audit logging"""

    # Authentication events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_TOKEN_INVALID = "auth_token_invalid"
    AUTH_TOKEN_EXPIRED = "auth_token_expired"
    AUTH_TOKEN_FORGED = "auth_token_forged"

    # Authorization events
    AUTHZ_GRANTED = "authz_granted"
    AUTHZ_DENIED = "authz_denied"

    # Token events
    TOKEN_ISSUED = "token_issued"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    TOKEN_ROTATED = "token_rotated"

    # Cryptographic events
    CRYPTO_KEY_ROTATED = "crypto_key_rotated"
    CRYPTO_KEY_GENERATED = "crypto_key_generated"
    CRYPTO_OPERATION_FAILED = "crypto_operation_failed"

    # Configuration events
    CONFIG_CHANGED = "config_changed"
    CONFIG_RELOADED = "config_reloaded"

    # Security policy events
    POLICY_VIOLATION = "policy_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

    # Data events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    PII_ACCESS = "pii_access"


class SecurityEventSeverity(Enum):
    """Security event severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAuditLogger(ThreadSafeSingleton):
    """
    Thread-safe security audit logger with batching and rotation.

    Features:
    - Thread-safe logging with RLock
    - In-memory buffer with max size (1000 events)
    - Automatic rotation to prevent memory overflow
    - Structured logging with JSON output
    - Correlation ID tracking
    - PII redaction (via LogSanitizer)
    - CloudWatch Logs integration
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self._initialized = False
        if self._initialized:
            return

        self._initialized = True
        self._lock = threading.RLock()
        self._logger = get_bootstrap_logger()
        self._buffer = deque(maxlen=1000)  # Rotate after 1000 events
        self._flush_interval = 60  # Flush every 60 seconds
        self._last_flush = time.time()
        self._event_count = 0
        self._enable_cloudwatch = (
            os.getenv("LEE_AUDIT_CLOUDWATCH", "true").lower() == "true"
        )

        # Security event counters for metrics
        self._counters = {
            SecurityEventType.AUTH_SUCCESS: 0,
            SecurityEventType.AUTH_FAILURE: 0,
            SecurityEventType.AUTH_TOKEN_INVALID: 0,
            SecurityEventType.AUTH_TOKEN_FORGED: 0,
            SecurityEventType.POLICY_VIOLATION: 0,
        }

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_security_event(
        self,
        event_type: SecurityEventType,
        severity: SecurityEventSeverity = SecurityEventSeverity.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None,
        event_data: Optional[dict[str, Any]] = None,
        outcome: str = "success",
        reason: Optional[str] = None,
    ) -> None:
        """
        Log a security event with full context.

        Args:
            event_type: Type of security event
            severity: Event severity level
            user_id: User identifier (if available)
            ip_address: Client IP address
            correlation_id: Request correlation ID
            event_data: Additional event context
            outcome: Event outcome (success/failure/pending)
            reason: Reason for failure or additional context
        """
        try:
            # Build event object
            event = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type.value,
                "severity": severity.value,
                "user_id": self._redact_pii(user_id) if user_id else None,
                "ip_address": self._redact_ip(ip_address) if ip_address else None,
                "correlation_id": correlation_id,
                "outcome": outcome,
                "reason": reason,
                "event_data": event_data or {},
                "source": "LEE_Gateway",
                "environment": os.getenv("AWS_LAMBDA_FUNCTION_NAME", "development"),
            }

            # Add to buffer (auto-rotates via deque maxlen)
            with self._lock:
                self._buffer.append(event)
                self._event_count += 1

                # Update counters
                if event_type in self._counters:
                    self._counters[event_type] += 1

                # Flush if needed
                current_time = time.time()
                if current_time - self._last_flush >= self._flush_interval:
                    self._flush_events()

            # Log to CloudWatch (if enabled)
            if self._enable_cloudwatch:
                self._log_to_cloudwatch(event, severity)

        except (ValueError, TypeError, KeyError, AttributeError, OSError, RuntimeError) as e:
            # Never fail the application for audit logging errors
            self._logger.error(f"Failed to log security event: {e}", exc_info=True)

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_auth_event(
        self,
        success: bool,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None,
        token_type: str = "bearer",
        reason: Optional[str] = None,
    ) -> None:
        """
        Log authentication event (helper method).

        Args:
            success: Whether authentication succeeded
            user_id: User identifier
            ip_address: Client IP address
            correlation_id: Request correlation ID
            token_type: Type of token (bearer, api_key, etc.)
            reason: Failure reason (if applicable)
        """
        if success:
            event_type = SecurityEventType.AUTH_SUCCESS
            severity = SecurityEventSeverity.INFO
        else:
            event_type = SecurityEventType.AUTH_FAILURE
            severity = SecurityEventSeverity.MEDIUM

        self.log_security_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            correlation_id=correlation_id,
            event_data={"token_type": token_type},
            outcome="success" if success else "failure",
            reason=reason,
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_token_validation(
        self,
        valid: bool,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None,
        token_issuer: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Log token validation event (helper method).

        Args:
            valid: Whether token is valid
            user_id: User identifier
            ip_address: Client IP address
            correlation_id: Request correlation ID
            token_issuer: Token issuer (e.g., "amazon.com")
            error_type: Type of validation error (if invalid)
        """
        if valid:
            event_type = SecurityEventType.AUTH_SUCCESS
            severity = SecurityEventSeverity.INFO
        else:
            # Determine event type based on error
            if error_type == "expired":
                event_type = SecurityEventType.AUTH_TOKEN_EXPIRED
                severity = SecurityEventSeverity.MEDIUM
            elif error_type == "signature":
                event_type = SecurityEventType.AUTH_TOKEN_FORGED
                severity = SecurityEventSeverity.HIGH  # Signature forgery is CRITICAL
            else:
                event_type = SecurityEventType.AUTH_TOKEN_INVALID
                severity = SecurityEventSeverity.MEDIUM

        self.log_security_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            correlation_id=correlation_id,
            event_data={"token_issuer": token_issuer, "error_type": error_type},
            outcome="valid" if valid else "invalid",
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_authorization(
        self,
        granted: bool,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        correlation_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log authorization decision (helper method).

        Args:
            granted: Whether access was granted
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            correlation_id: Request correlation ID
            reason: Denial reason (if not granted)
        """
        if granted:
            event_type = SecurityEventType.AUTHZ_GRANTED
            severity = SecurityEventSeverity.INFO
        else:
            event_type = SecurityEventType.AUTHZ_DENIED
            severity = SecurityEventSeverity.MEDIUM

        self.log_security_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            correlation_id=correlation_id,
            event_data={"resource": resource, "action": action},
            outcome="granted" if granted else "denied",
            reason=reason,
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_key_rotation(
        self,
        key_type: str,
        old_key_hash: Optional[str] = None,
        new_key_hash: Optional[str] = None,
        correlation_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log cryptographic key rotation event (helper method).

        Args:
            key_type: Type of key (e.g., "hmac_signing_key")
            old_key_hash: Hash of old key (for verification)
            new_key_hash: Hash of new key (for verification)
            correlation_id: Request correlation ID
            reason: Reason for rotation
        """
        self.log_security_event(
            event_type=SecurityEventType.CRYPTO_KEY_ROTATED,
            severity=SecurityEventSeverity.INFO,
            correlation_id=correlation_id,
            event_data={
                "key_type": key_type,
                "old_key_hash": old_key_hash,
                "new_key_hash": new_key_hash,
            },
            outcome="success",
            reason=reason,
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def log_policy_violation(
        self,
        policy_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None,
        violation_details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log security policy violation (helper method).

        Args:
            policy_type: Type of policy violated
            user_id: User identifier
            ip_address: Client IP address
            correlation_id: Request correlation ID
            violation_details: Additional violation context
        """
        self.log_security_event(
            event_type=SecurityEventType.POLICY_VIOLATION,
            severity=SecurityEventSeverity.HIGH,
            user_id=user_id,
            ip_address=ip_address,
            correlation_id=correlation_id,
            event_data=violation_details or {},
            outcome="violation",
            reason=f"Security policy violation: {policy_type}",
        )

    def get_event_count(self) -> int:
        """Get total number of events logged since startup."""
        with self._lock:
            return self._event_count

    def get_counters(self) -> dict[str, int]:
        """Get security event counters."""
        with self._lock:
            return {k.value: v for k, v in self._counters.items()}

    def get_recent_events(self, count: int = 100) -> list:
        """
        Get recent security events from buffer.

        Args:
            count: Maximum number of events to return

        Returns:
            List of recent security events
        """
        with self._lock:
            events = list(self._buffer)
            return events[-count:] if count < len(events) else events

    def _flush_events(self) -> None:
        """Flush events to persistent storage (if configured)."""
        # In Lambda, events are automatically flushed via CloudWatch Logs
        # For other environments, you might want to write to S3, DynamoDB, etc.
        self._last_flush = time.time()

    def _log_to_cloudwatch(
        self,
        event: dict[str, Any],
        severity: SecurityEventSeverity,
    ) -> None:
        """Log event to CloudWatch Logs with appropriate level."""
        message = f"[SECURITY_AUDIT] {json.dumps(event)}"

        if severity == SecurityEventSeverity.CRITICAL:
            # BootstrapLogger doesn't have critical method, use error instead
            self._logger.error(message)
        elif severity == SecurityEventSeverity.HIGH:
            self._logger.error(message)
        elif severity == SecurityEventSeverity.MEDIUM:
            self._logger.warning(message)
        else:
            self._logger.info(message)

    def _redact_pii(self, value: Optional[str]) -> Optional[str]:
        """
        Redact PII from logs.

        Args:
            value: Value to redact

        Returns:
            Redacted value
        """
        return DataSanitizer.redact_pii(value)

    def _redact_ip(self, value: Optional[str]) -> Optional[str]:
        """
        Redact IP address for privacy (preserve first 2 octets).

        Args:
            value: IP address to redact

        Returns:
            Redacted IP address
        """
        return DataSanitizer.redact_ip(value)


def get_audit_logger() -> SecurityAuditLogger:
    """Get the singleton SecurityAuditLogger instance."""
    return SecurityAuditLogger.get_instance()
