"""
Validation Factory - Security Domain

Input validation and sanitization implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside security domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

import re
import html
import logging
from typing import Any, Dict, Optional, Callable, List
from urllib.parse import urlparse


class ValidationFactory:
    """Validation factory.

    Provides input validation and sanitization operations:
    - Email, URL, UUID, IP, phone validation
    - String, HTML, SQL sanitization
    - Length and range checks
    - Regex matching

    UG-ISP Compliance:
    - ONLY standard library
    - Cross-domain calls via call_operation callback
    - Implements secure validation practices
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize validation factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def validate_email(self, email: str, **kwargs) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate
            **kwargs: Additional parameters

        Returns:
            True if email format is valid
        """
        if not email or not isinstance(email, str):
            return False

        # Basic email validation regex
        # RFC 5322 compliant pattern (simplified)
        email_pattern = re.compile(
            r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+'
            r'@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
            r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        )

        return bool(email_pattern.match(email))

    def validate_url(self, url: str, **kwargs) -> bool:
        """Validate URL format.

        Args:
            url: URL to validate
            **kwargs: Additional parameters
                - allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

        Returns:
            True if URL format is valid
        """
        if not url or not isinstance(url, str):
            return False

        try:
            result = urlparse(url)

            # Check scheme
            allowed_schemes = kwargs.get("allowed_schemes", ['http', 'https'])
            if result.scheme.lower() not in allowed_schemes:
                return False

            # Check netloc (domain)
            if not result.netloc:
                return False

            return True

        except Exception:
            return False

    def validate_uuid(self, uuid_str: str, **kwargs) -> bool:
        """Validate UUID format.

        Args:
            uuid_str: UUID string to validate
            **kwargs: Additional parameters
                - version: UUID version to validate (1, 4, None for any)

        Returns:
            True if UUID format is valid
        """
        if not uuid_str or not isinstance(uuid_str, str):
            return False

        # UUID regex pattern
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )

        if not uuid_pattern.match(uuid_str):
            return False

        # Check version if specified
        version = kwargs.get("version")
        if version is not None:
            # Version is in the 3rd group (characters 14-15)
            version_char = uuid_str[14:15]
            return version_char == str(version)

        return True

    def validate_ip(self, ip: str, **kwargs) -> bool:
        """Validate IP address format.

        Args:
            ip: IP address to validate
            **kwargs: Additional parameters
                - version: IP version (4, 6, None for any)

        Returns:
            True if IP address format is valid
        """
        if not ip or not isinstance(ip, str):
            return False

        version = kwargs.get("version")

        # IPv4 validation
        if version in [None, 4]:
            ipv4_pattern = re.compile(
                r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            )
            if ipv4_pattern.match(ip):
                return True

        # IPv6 validation
        if version in [None, 6]:
            ipv6_pattern = re.compile(
                r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::$|'
                r'^(?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}$'
            )
            if ipv6_pattern.match(ip):
                return True

        return False

    def validate_phone(self, phone: str, **kwargs) -> bool:
        """Validate phone number format.

        Args:
            phone: Phone number to validate
            **kwargs: Additional parameters
                - country_code: Country code for validation (default: international)

        Returns:
            True if phone number format is valid
        """
        if not phone or not isinstance(phone, str):
            return False

        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

        # International format (E.164): + followed by 10-15 digits
        international_pattern = re.compile(r'^\+[1-9]\d{9,14}$')
        if international_pattern.match(cleaned):
            return True

        # US/Canada format: 10 digits
        us_pattern = re.compile(r'^[1-9]\d{9}$')
        if us_pattern.match(cleaned):
            return True

        return False

    def sanitize_string(self, input_str: str, **kwargs) -> str:
        """Sanitize string input.

        Args:
            input_str: String to sanitize
            **kwargs: Additional parameters
                - remove_whitespace: Remove all whitespace (default: False)
                - remove_special_chars: Remove special characters (default: False)
                - max_length: Maximum length (default: None)

        Returns:
            Sanitized string
        """
        if not input_str or not isinstance(input_str, str):
            return ""

        result = input_str

        # Remove special characters if requested
        if kwargs.get("remove_special_chars", False):
            result = re.sub(r'[^\w\s]', '', result)

        # Remove whitespace if requested
        if kwargs.get("remove_whitespace", False):
            result = result.replace(' ', '').replace('\t', '').replace('\n', '')

        # Trim length
        max_length = kwargs.get("max_length")
        if max_length and len(result) > max_length:
            result = result[:max_length]

        # Strip leading/trailing whitespace
        result = result.strip()

        return result

    def sanitize_html(self, html_str: str, **kwargs) -> str:
        """Sanitize HTML input.

        Args:
            html_str: HTML string to sanitize
            **kwargs: Additional parameters
                - allowed_tags: List of allowed HTML tags (default: [])

        Returns:
            Sanitized string with HTML escaped
        """
        if not html_str or not isinstance(html_str, str):
            return ""

        # Escape HTML characters
        sanitized = html.escape(html_str)

        # If allowed tags specified, you could unescape them here
        # For now, we escape everything for security

        return sanitized

    def sanitize_sql(self, sql_input: str, **kwargs) -> str:
        """Escape SQL input to prevent injection.

        Args:
            sql_input: SQL input to escape
            **kwargs: Additional parameters

        Returns:
            Escaped SQL string

        WARNING: This is basic escaping. Use parameterized queries for real security.
        """
        if not sql_input or not isinstance(sql_input, str):
            return ""

        # Basic SQL escaping - escape single quotes
        escaped = sql_input.replace("'", "''")

        # Remove SQL comments
        escaped = re.sub(r'--.*', '', escaped)
        escaped = re.sub(r'/\*.*?\*/', '', escaped, flags=re.DOTALL)

        return escaped

    def check_length(self, value: str, min_length: int = 0, max_length: int = 255, **kwargs) -> bool:
        """Check string length constraints.

        Args:
            value: String to check
            min_length: Minimum length (default: 0)
            max_length: Maximum length (default: 255)
            **kwargs: Additional parameters

        Returns:
            True if length is within bounds
        """
        if not isinstance(value, str):
            return False

        length = len(value)
        return min_length <= length <= max_length

    def check_range(self, value: float, min_value: float, max_value: float, **kwargs) -> bool:
        """Check numeric range constraints.

        Args:
            value: Numeric value to check
            min_value: Minimum value
            max_value: Maximum value
            **kwargs: Additional parameters

        Returns:
            True if value is within range
        """
        try:
            num_value = float(value)
            return min_value <= num_value <= max_value
        except (ValueError, TypeError):
            return False

    def check_regex(self, value: str, pattern: str, **kwargs) -> bool:
        """Check if value matches regex pattern.

        Args:
            value: String to check
            pattern: Regex pattern to match
            **kwargs: Additional parameters
                - flags: Regex flags (default: 0)
                - full_match: Require full string match (default: True)

        Returns:
            True if value matches pattern
        """
        if not value or not pattern:
            return False

        try:
            flags = kwargs.get("flags", 0)
            full_match = kwargs.get("full_match", True)

            if full_match:
                regex_pattern = re.compile(f'^{pattern}$', flags)
            else:
                regex_pattern = re.compile(pattern, flags)

            return bool(regex_pattern.search(value))

        except re.error:
            self.logger.error(f"Invalid regex pattern: {pattern}")
            return False


__all__ = [
    "ValidationFactory",
]
