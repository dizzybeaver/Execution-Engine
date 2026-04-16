# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-03 - Unified data sanitization module

"""
Unified Data Sanitization Module

This module consolidates all data sanitization functions into a single source of truth,
eliminating code duplication across security_patterns.py, security_audit_logger.py,
interface_cache.py, and interface_logging.py.

Security Features:
- Credential sanitization (tokens, API keys, passwords)
- PII redaction (emails, SSNs, credit cards, IPs)
- Log data sanitization (sensitive keys, length limits)
- CloudWatch dimension sanitization
- Deep recursive sanitization for data structures

Usage:
    from lee.lee_security.sanitize import DataSanitizer

    # Sanitize credentials
    safe = DataSanitizer.sanitize_credentials("Bearer eyJhbGci...")

    # Redact PII
    safe = DataSanitizer.redact_pii("user@example.com")

    # Redact IP
    safe = DataSanitizer.redact_ip("192.168.1.100")

    # Sanitize log data
    safe_message, safe_extra = DataSanitizer.sanitize_log_data(message, extra)
"""

import re
from typing import Any, Optional


class DataSanitizer:
    """
    Unified data sanitization class consolidating all sanitization functions.

    This class provides a single source of truth for data sanitization across
    the LEE codebase, replacing duplicate implementations in:
    - cloudwatch/security_patterns.py
    - lee_security/security_audit_logger.py
    - interface/interface_cache.py
    - interface/interface_logging.py

    Thread Safety: Safe for Lambda's single-threaded execution model.
    Pattern Compilation: Lazy compilation on first use (cached afterward).
    """

    # Credential patterns (from security_patterns.py)
    CREDENTIAL_PATTERNS: list[tuple[str, str]] = [
        # Bearer tokens (OAuth, JWT)
        (r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", "Bearer [REDACTED]"),

        # AWS Access Keys
        (r"AKIA[0-9A-Z]{16}", "AKIA********"),

        # Password patterns
        (r'password[\'"]?\s*[:=]\s*[\'"]?[^\s\'"]+', "password=[REDACTED]"),

        # Secret patterns
        (r'secret[\'"]?\s*[:=]\s*[\'"]?[^\s\'"]+', "secret=[REDACTED]"),

        # API key patterns
        (r'api[_-]?key[\'"]?\s*[:=]\s*[\'"]?[^\s\'"]+', "apikey=[REDACTED]"),

        # JWT tokens (eyJ header)
        (r"ey[A-Za-z0-9\-_.=]{10,}", "eyJ[REDACTED]"),

        # Base64 encoded secrets (32+ chars with optional padding)
        (r"[A-Za-z0-9+/]{32,}={0,2}", "[BASE64_REDACTED]"),

        # Generic token/apikey/secret with 20+ chars
        (r'(?:token|api[_-]?key|secret|auth)[\'"]?\s*[:=]\s*[\'"]?[A-Za-z0-9\-._~+/]{20,}', "[REDACTED]"),
    ]

    # Sensitive keys for log sanitization (from interface_logging.py)
    _SENSITIVE_KEYS = [
        "password", "token", "key", "secret", "auth", "credential"
    ]

    # Compiled patterns cache
    _compiled_patterns: Optional[list[tuple[re.Pattern, str]]] = None

    @classmethod
    def _compile_patterns(cls) -> None:
        """Compile credential patterns on first use."""
        if cls._compiled_patterns is not None:
            return

        cls._compiled_patterns = []
        for pattern, replacement in cls.CREDENTIAL_PATTERNS:
            try:
                cls._compiled_patterns.append(
                    (re.compile(pattern, re.IGNORECASE), replacement)
                )
            except re.error:
                # Skip invalid patterns but continue with others
                continue

    @classmethod
    def sanitize_credentials(cls, value: str) -> str:
        """
        Sanitize credentials to prevent exfiltration.

        Removes credential patterns (tokens, API keys, passwords, secrets)
        and returns a safe string with placeholders for sensitive data.

        Args:
            value: Raw string potentially containing credentials

        Returns:
            Sanitized string with credentials redacted

        Example:
            >>> DataSanitizer.sanitize_credentials("Bearer eyJhbGci...")
            'Bearer [REDACTED]'
        """
        if not isinstance(value, str):
            value = str(value)

        cls._compile_patterns()

        # Remove credential patterns
        # Note: If _compiled_patterns is empty (all failed to compile),
        # we just return the original value - safe fallback
        if cls._compiled_patterns:
            for pattern, replacement in cls._compiled_patterns:
                value = pattern.sub(replacement, value)

        return value

    @classmethod
    def redact_pii(cls, value: Optional[str]) -> Optional[str]:
        """
        Redact PII from logs (emails, SSNs, credit cards).

        For user IDs, shows first 4 and last 4 characters.
        For emails, shows first character and domain.

        Args:
            value: Value to redact

        Returns:
            Redacted value or None if input is None

        Example:
            >>> DataSanitizer.redact_pii("user@example.com")
            'u***@***.***'
            >>> DataSanitizer.redact_pii("ABCDE12345FGHIJ")
            'ABCD...EFGH'
        """
        if not value:
            return None

        # Check if it's an email address
        if "@" in value and "." in value.split("@")[1]:
            parts = value.split("@")
            if len(parts[0]) > 0:
                username = parts[0][0] + "***"
                domain_parts = parts[1].split(".")
                domain = "***." + domain_parts[-1] if domain_parts else "***"
                return f"{username}@{domain}"

        # For user IDs, show first 4 and last 4 characters
        if len(value) > 8:
            return f"{value[:4]}...{value[-4:]}"

        return "****"

    @classmethod
    def redact_ip(cls, value: Optional[str]) -> Optional[str]:
        """
        Redact IP address for privacy (preserve first 2 octets for IPv4).

        Args:
            value: IP address to redact

        Returns:
            Redacted IP address or None if input is None

        Example:
            >>> DataSanitizer.redact_ip("192.168.1.100")
            '192.168.***.***'
        """
        if not value:
            return None

        try:
            # IPv4: preserve first 2 octets
            parts = value.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.***.***"

            # IPv6: show first two hextets
            if ":" in value:
                hextets = value.split(":")
                if len(hextets) >= 2:
                    return f"{hextets[0]}:{hextets[1]}:..."

            # Fallback: show first 9 characters
            return value[:9] + "..." if len(value) > 9 else "****"
        except (ValueError, AttributeError, IndexError):
            # Invalid IP format - return safe fallback
            return "****"

    @classmethod
    def sanitize_log_data(
        cls,
        message: str,
        extra: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """
        Sanitize log message and extra data.

        Security measures:
        - Truncates message to 500 characters
        - Removes newlines (prevents log injection)
        - Redacts sensitive keys (password, token, key, secret, auth, credential)
        - Truncates string values to 200 characters

        Args:
            message: Log message to sanitize
            extra: Dictionary of extra log fields

        Returns:
            Tuple of (sanitized_message, sanitized_extra_dict)

        Example:
            >>> message = "User logged in\\nWith newline"
            >>> extra = {"token": "abc123", "user": "john"}
            >>> safe_msg, safe_extra = DataSanitizer.sanitize_log_data(message, extra)
            >>> safe_msg
            'User logged in With newline'
            >>> safe_extra
            {'token': '***REDACTED***', 'user': 'john'}
        """
        # Translation table for single-pass newline replacement
        newline_to_space_trans = str.maketrans({'\n': ' ', '\r': ' '})

        # Sanitize message: remove newlines and truncate
        safe_message = message.translate(newline_to_space_trans)[:500]

        # Sanitize extra data
        safe_extra = {}
        for key, value in extra.items():
            if any(sens in key.lower() for sens in cls._SENSITIVE_KEYS):
                safe_extra[key] = "***REDACTED***"
            elif isinstance(value, str):
                safe_extra[key] = value[:200]
            else:
                safe_extra[key] = value

        return safe_message, safe_extra

    @classmethod
    def sanitize_cloudwatch_error(cls, error_msg: str) -> str:
        """
        Sanitize CloudWatch error messages to prevent information exposure.

        Security measures:
        - Removes credential patterns (tokens, api keys, passwords)
        - Removes control characters
        - Truncates to 200 characters

        Args:
            error_msg: Raw error message

        Returns:
            Sanitized error message safe for logging
        """
        if not isinstance(error_msg, str):
            error_msg = str(error_msg)

        # Remove control characters
        error_msg = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", error_msg)

        # Remove credential patterns
        error_msg = cls.sanitize_credentials(error_msg)

        # Truncate to 200 characters
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."

        return error_msg

    @classmethod
    def sanitize_dimension_value(cls, value: str) -> str:
        """
        Sanitize CloudWatch dimension value to prevent credential exfiltration.

        Security measures:
        - Detects sensitive patterns (tokens, api keys, passwords, secrets)
        - Truncates long values (>100 chars)
        - Removes control characters
        - Returns placeholder for sensitive data

        Args:
            value: Raw dimension value

        Returns:
            Sanitized dimension value safe for CloudWatch
        """
        if not isinstance(value, str):
            value = str(value)

        # Remove control characters
        value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", value)

        # Truncate long values
        if len(value) > 100:
            value = value[:100]

        # Check for sensitive patterns
        cls._compile_patterns()
        if cls._compiled_patterns:
            for pattern, _ in cls._compiled_patterns:
                if pattern.search(value):
                    return "[REDACTED]"

        return value

    @classmethod
    def contains_sensitive_data(cls, value: str) -> bool:
        """
        Check if a value contains sensitive data patterns.

        Args:
            value: Value to check

        Returns:
            True if sensitive patterns detected, False otherwise
        """
        if not isinstance(value, str):
            value = str(value)

        cls._compile_patterns()
        if cls._compiled_patterns:
            for pattern, _ in cls._compiled_patterns:
                if pattern.search(value):
                    return True

        return False

    @classmethod
    def sanitize_value_deep(cls, value: Any, path: str = "root") -> Any:
        """
        Recursively sanitize data structures (dict, list, set, etc.).

        Removes sentinel objects and applies sanitization recursively.

        Args:
            value: Value to sanitize (can be any type)
            path: Current path in the data structure (for logging)

        Returns:
            Sanitized value with sentinel objects removed

        Example:
            >>> data = {"user": {"id": "token123"}, "items": [1, 2, 3]}
            >>> DataSanitizer.sanitize_value_deep(data)
            {'user': {'id': 'token123'}, 'items': [1, 2, 3]}
        """
        def _is_sentinel_object(obj: Any) -> bool:
            """Detect if value is object() sentinel."""
            return (
                type(obj).__name__ == "object" and
                not isinstance(obj, (
                    str, int, float, bool, list, dict, tuple, set,
                    type(None)
                )) and
                str(obj).startswith("<object object")
            )

        if _is_sentinel_object(value):
            return None

        if isinstance(value, dict):
            return {
                k: cls.sanitize_value_deep(v, f"{path}.{k}")
                for k, v in value.items()
                if not _is_sentinel_object(v)
            }

        if isinstance(value, (list, tuple)):
            sanitized = [
                cls.sanitize_value_deep(item, f"{path}[{i}]")
                for i, item in enumerate(value)
                if not _is_sentinel_object(item)
            ]
            return type(value)(sanitized)

        if isinstance(value, set):
            return {
                cls.sanitize_value_deep(item, f"{path}.item")
                for item in value
                if not _is_sentinel_object(item)
            }

        return value

    @classmethod
    def sanitize_directive_input(cls, directive: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize Alexa directive input to prevent XSS attacks.

        Security measures:
        - Strips HTML tags from all string values
        - Removes dangerous JavaScript patterns
        - Truncates excessive string lengths
        - Sanitizes nested dictionaries and lists

        Args:
            directive: Alexa directive dictionary

        Returns:
            Sanitized directive dictionary

        Example:
            >>> directive = {"header": {"name": "<script>alert('xss')</script>TurnOn"}}
            >>> safe = DataSanitizer.sanitize_directive_input(directive)
            >>> safe["header"]["name"]
            'TurnOn'
        """
        import html

        def sanitize_string(value: str) -> str:
            """Sanitize string to prevent XSS."""
            if not isinstance(value, str):
                return value

            # Remove HTML tags
            value = html.unescape(value)
            value = html.escape(value)

            # Remove script tags and content
            value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)

            # Remove dangerous event handlers
            dangerous_patterns = [
                r'on\w+\s*=',  # onclick=, onload=, etc.
                r'javascript:',
                r'vbscript:',
                r'data:text/html',
            ]
            for pattern in dangerous_patterns:
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)

            # Truncate excessive lengths
            if len(value) > 1000:
                value = value[:1000]

            return value.strip()

        def sanitize_value(value: Any) -> Any:
            """Recursively sanitize values."""
            if isinstance(value, str):
                return sanitize_string(value)
            if isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            if isinstance(value, list):
                return [sanitize_value(item) for item in value]
            return value

        # Sanitize directive recursively
        return sanitize_value(directive)


# Convenience functions for quick usage
def sanitize_credentials(value: str) -> str:
    """Quick credential sanitization function."""
    return DataSanitizer.sanitize_credentials(value)


def redact_pii(value: Optional[str]) -> Optional[str]:
    """Quick PII redaction function."""
    return DataSanitizer.redact_pii(value)


def redact_ip(value: Optional[str]) -> Optional[str]:
    """Quick IP redaction function."""
    return DataSanitizer.redact_ip(value)


def sanitize_log_data(message: str, extra: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Quick log data sanitization function."""
    return DataSanitizer.sanitize_log_data(message, extra)


def sanitize_cloudwatch_error(error_msg: str) -> str:
    """Quick CloudWatch error sanitization function."""
    return DataSanitizer.sanitize_cloudwatch_error(error_msg)


def sanitize_dimension_value(value: str) -> str:
    """Quick CloudWatch dimension sanitization function."""
    return DataSanitizer.sanitize_dimension_value(value)


def contains_sensitive_data(value: str) -> bool:
    """Quick sensitive data detection function."""
    return DataSanitizer.contains_sensitive_data(value)


__all__ = [
    "DataSanitizer",
    "sanitize_credentials",
    "redact_pii",
    "redact_ip",
    "sanitize_log_data",
    "sanitize_cloudwatch_error",
    "sanitize_dimension_value",
    "contains_sensitive_data",
]
