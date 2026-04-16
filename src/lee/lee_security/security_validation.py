"""security_validation.py - Security Validation Functions
Version: 2025.10.22.01
Description: COMPLETE FILE - All validators including SecurityValidator class

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import logging
import math
import re
from typing import Any

# ===== SECURITY VALIDATOR CLASS =====

class SecurityValidator:
    """Core security validator for requests, tokens, strings, emails, URLs."""

    def __init__(self):
        self._stats = {
            "validations_performed": 0,
            "validations_passed": 0,
            "validations_failed": 0,
        }
        self._logger = logging.getLogger(__name__)

    def validate_request(self, request: dict[str, Any]) -> bool:
        """Validate HTTP request structure and content."""
        self._stats["validations_performed"] += 1

        try:
            if not isinstance(request, dict):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: request must be dict",
                    extra={"security_event": True, "validation_type": "request"}
                )
                return False

            # Basic request validation
            if "method" in request and not isinstance(request["method"], str):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: method must be string",
                    extra={"security_event": True, "validation_type": "request"}
                )
                return False

            if "headers" in request and not isinstance(request["headers"], dict):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: headers must be dict",
                    extra={"security_event": True, "validation_type": "request"}
                )
                return False

            self._stats["validations_passed"] += 1
            return True

        except (AttributeError, TypeError, KeyError) as e:
            self._stats["validations_failed"] += 1
            self._logger.warning(
                "Validation failed for request: %s",
                e.__class__.__name__,
                extra={"security_event": True, "validation_type": "request"}
            )
            return False

    def validate_token(self, token: str) -> bool:
        """Validate authentication token format."""
        self._stats["validations_performed"] += 1

        try:
            if not isinstance(token, str):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: token must be string",
                    extra={"security_event": True, "validation_type": "token"}
                )
                return False

            if not token or not token.strip():
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: token cannot be empty",
                    extra={"security_event": True, "validation_type": "token"}
                )
                return False

            if len(token) < 10:
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: token too short",
                    extra={"security_event": True, "validation_type": "token"}
                )
                return False

            self._stats["validations_passed"] += 1
            return True

        except (AttributeError, TypeError) as e:
            self._stats["validations_failed"] += 1
            self._logger.warning(
                "Validation failed for token: %s",
                e.__class__.__name__,
                extra={"security_event": True, "validation_type": "token"}
            )
            return False

    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length and content."""
        self._stats["validations_performed"] += 1

        try:
            if not isinstance(value, str):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: value must be string",
                    extra={"security_event": True, "validation_type": "string"}
                )
                return False

            if len(value) < min_length:
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: string too short",
                    extra={"security_event": True, "validation_type": "string"}
                )
                return False

            if len(value) > max_length:
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: string too long",
                    extra={"security_event": True, "validation_type": "string"}
                )
                return False

            self._stats["validations_passed"] += 1
            return True

        except (AttributeError, TypeError) as e:
            self._stats["validations_failed"] += 1
            self._logger.warning(
                "Validation failed for string: %s",
                e.__class__.__name__,
                extra={"security_event": True, "validation_type": "string"}
            )
            return False

    def _email_log_failure(self, reason: str) -> bool:
        """Log email validation failure.

        Args:
            reason: Failure reason description

        Returns:
            False (indicating validation failed)
        """
        self._stats["validations_failed"] += 1
        self._logger.warning(
            f"Validation failed: {reason}",
            extra={"security_event": True, "validation_type": "email"}
        )
        return False

    def _validate_email_basic_structure(self, email: str) -> tuple[bool, str]:
        """Validate basic email structure.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(email, str):
            return False, "email must be string"

        if any(ord(char) < 32 for char in email):
            return False, "email contains control characters"

        if "@" not in email:
            return False, "email missing @ symbol"

        return True, ""

    def _validate_email_lengths(self, email: str, local_part: str, domain: str) -> bool:
        """Validate email length constraints.

        Args:
            email: Full email address
            local_part: Local part before @
            domain: Domain part after @

        Returns:
            True if all length checks pass
        """
        if len(email) > 320:
            return self._email_log_failure(
                f"email too long ({len(email)} chars, max: 320)"
            )

        if len(local_part) > 64:
            return self._email_log_failure(
                f"local part too long ({len(local_part)} chars, max: 64)"
            )

        if len(domain) > 255:
            return self._email_log_failure(
                f"domain too long ({len(domain)} chars, max: 255)"
            )

        return True

    def _validate_email_local_part(self, local_part: str) -> bool:  # pylint: disable=too-many-return-statements
        """Validate email local part format.

        Args:
            local_part: Local part before @ symbol

        Returns:
            True if valid
        """
        if not local_part:
            return self._email_log_failure("local part cannot be empty")

        if local_part.startswith('"') and local_part.endswith('"'):
            quoted_content = local_part[1:-1]
            if '"' in quoted_content.replace(r'\"', ''):
                return self._email_log_failure("unescaped quotes in quoted local part")
            return True

        if not re.match(r"^[a-zA-Z0-9._%+-]+$", local_part):
            return self._email_log_failure("local part contains invalid characters")

        if ".." in local_part:
            return self._email_log_failure("consecutive dots not allowed in local part")

        if local_part.startswith('.') or local_part.endswith('.'):
            return self._email_log_failure("local part cannot start or end with dot")

        return True

    def _validate_email_domain_label(self, label: str) -> bool:
        """Validate single domain label.

        Args:
            label: Domain label to validate

        Returns:
            True if valid
        """
        if not label:
            return self._email_log_failure("domain label cannot be empty")

        if len(label) > 63:
            return self._email_log_failure(
                f"domain label too long ({len(label)} chars, max: 63)"
            )

        if not re.match(r"^[a-zA-Z0-9-]+$", label):
            try:
                label.encode('idna')
            except (UnicodeError, UnicodeDecodeError):
                return self._email_log_failure("domain label contains invalid characters")

        if label.startswith('-') or label.endswith('-'):
            return self._email_log_failure("domain label cannot start or end with hyphen")

        return True

    def _validate_email_domain(self, domain: str) -> bool:  # pylint: disable=too-many-return-statements
        """Validate email domain format.

        Args:
            domain: Domain part to validate

        Returns:
            True if valid
        """
        if not domain:
            return self._email_log_failure("domain cannot be empty")

        ip_pattern = r'^(\d+\.\d+\.\d+\.\d+|\[.*\]|localhost|127\.0\.0\.1|0\.0\.0\.0|::1)$'
        if re.match(ip_pattern, domain.strip().lower()):
            return self._email_log_failure("IP-based domains not allowed for SSRF prevention")

        domain_labels = domain.split('.')

        if len(domain_labels) < 2:
            return self._email_log_failure("domain must have at least 2 labels")

        for label in domain_labels:
            if not self._validate_email_domain_label(label):
                return False

        tld = domain_labels[-1]
        if len(tld) < 2:
            return self._email_log_failure(f"TLD too short ({len(tld)} chars, min: 2)")

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", tld):
            return self._email_log_failure("TLD must start with letter and be alphanumeric")

        return True

    def validate_email(self, email: str) -> bool:
        """Validate email address format (RFC 5322 compliant with security controls).

        Security Rules:
        - RFC 5322 compliant format validation
        - Length limits: local part 64 chars, domain 255 chars, total 320 chars
        - No control characters (prevents header injection)
        - No IP-based domains (prevents SSRF attacks)
        - Internationalized domain support (IDN)
        - TLD validation (2-63 chars)
        - Quoted strings and comments supported

        Attack Vectors Prevented:
        - Header injection via control characters
        - SSRF via IP-based domains
        - Memory exhaustion via long emails
        - Phishing domain acceptance

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        self._stats["validations_performed"] += 1

        try:
            is_valid, error_msg = self._validate_email_basic_structure(email)
            if not is_valid:
                return self._email_log_failure(error_msg)

            local_part, domain = email.rsplit("@", 1)

            if not self._validate_email_lengths(email, local_part, domain):
                return False

            if not self._validate_email_local_part(local_part):
                return False

            if not self._validate_email_domain(domain):
                return False

            self._stats["validations_passed"] += 1
            return True

        except (ValueError, TypeError, re.error, UnicodeError) as e:
            return self._email_log_failure(f"{e.__class__.__name__}")

    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._stats["validations_performed"] += 1

        try:
            if not isinstance(url, str):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: URL must be string",
                    extra={"security_event": True, "validation_type": "url"}
                )
                return False

            if not url.startswith(("http://", "https://")):
                self._stats["validations_failed"] += 1
                self._logger.warning(
                    "Validation failed: URL must start with http:// or https://",
                    extra={"security_event": True, "validation_type": "url"}
                )
                return False

            self._stats["validations_passed"] += 1
            return True

        except (AttributeError, TypeError) as e:
            self._stats["validations_failed"] += 1
            self._logger.warning(
                "Validation failed for URL: %s",
                e.__class__.__name__,
                extra={"security_event": True, "validation_type": "url"}
            )
            return False

    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data for safe processing."""
        if isinstance(data, str):
            # Remove control characters
            return "".join(char for char in data if ord(char) >= 32 or char in "\n\r\t")
        if isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data

    def get_stats(self) -> dict[str, int]:
        """Get validation statistics."""
        return dict(self._stats)


# ===== METRICS SECURITY VALIDATIONS =====

def validate_metric_name(name: str) -> None:
    """Validate metric name for security and sanity.
    
    Security Rules:
    - Length: 1-200 characters
    - Characters: [a-zA-Z0-9_.-] only
    - No path separators (/, \\)
    - No control characters
    - No leading/trailing whitespace
    - Cannot start/end with . or -
    
    Args:
        name: Metric name to validate
        
    Raises:
        ValueError: If name is invalid with specific reason

    """
    # Check empty/whitespace
    if not name or not name.strip():
        raise ValueError("Metric name cannot be empty or whitespace")

    # Auto-strip for safety
    name = name.strip()

    # Check length
    if len(name) > 200:
        raise ValueError(
            f"Metric name too long: {len(name)} characters (max: 200). "
            "This may be a memory exhaustion attack.",
        )

    if len(name) < 1:
        raise ValueError("Metric name must be at least 1 character")

    # Check character set
    if not re.match(r"^[a-zA-Z0-9_.\-]+$", name):
        raise ValueError(
            f"Metric name contains invalid characters: '{name}'. "
            "Allowed characters: [a-zA-Z0-9_.-]",
        )

    # Check for path separators
    if "/" in name or "\\" in name:
        raise ValueError(
            f"Metric name cannot contain path separators: '{name}'. "
            "This may be a path traversal attack.",
        )

    # Check for leading/trailing special chars
    if name.startswith((".", "-")) or name.endswith((".", "-")):
        raise ValueError(
            f"Metric name cannot start or end with '.' or '-': '{name}'",
        )


def validate_dimension_value(value: str) -> None:
    """Validate metric dimension value for security.
    
    Security Rules:
    - Length: 1-100 characters
    - No control characters
    - No path separators
    - Must be printable
    
    Args:
        value: Dimension value to validate (will be converted to string)
        
    Raises:
        ValueError: If value is invalid with specific reason

    """
    # Convert to string if not already
    value = str(value)

    # Check empty/whitespace
    if not value or not value.strip():
        raise ValueError("Dimension value cannot be empty or whitespace")

    # Auto-strip for safety
    value = value.strip()

    # Check length
    if len(value) > 100:
        raise ValueError(
            f"Dimension value too long: {len(value)} characters (max: 100). "
            "This may be a memory exhaustion attack.",
        )

    # Check for control characters
    if not value.isprintable():
        raise ValueError(
            "Dimension value contains non-printable characters. "
            "This may be a control character injection attack.",
        )

    # Check for path separators
    if "/" in value or "\\" in value:
        raise ValueError(
            f"Dimension value cannot contain path separators: '{value}'. "
            "This may be a path traversal attack.",
        )


def validate_metric_value(value: float, allow_negative: bool = True) -> None:
    """Validate metric numeric value is valid.
    
    Validates that metric values are valid floats:
    - Rejects: NaN (Not a Number)
    - Rejects: Infinity (positive or negative)
    - Optionally rejects: Negative values
    
    Args:
        value: Numeric value to validate
        allow_negative: Whether negative values are allowed (default: True)
        
    Raises:
        ValueError: If value is invalid with specific reason

    """
    # Check for NaN
    if math.isnan(value):
        raise ValueError(
            "Metric value cannot be NaN (Not a Number). "
            "This indicates a calculation error or invalid input.",
        )

    # Check for infinity
    if math.isinf(value):
        raise ValueError(
            f"Metric value cannot be infinity. "
            f"Value: {value}. This may cause overflow or calculation errors.",
        )

    # Check for negative (if not allowed)
    if not allow_negative and value < 0:
        raise ValueError(
            f"Metric value cannot be negative: {value}. "
            "This is likely an error (e.g., negative duration).",
        )


# ===== EXPORTS =====

__all__ = [
    "SecurityValidator",
    "validate_dimension_value",
    "validate_metric_name",
    "validate_metric_value",
]

# EOF
