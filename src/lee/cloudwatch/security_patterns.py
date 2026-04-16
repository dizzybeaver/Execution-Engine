"""cloudwatch/security_patterns.py - Shared Security Pattern Detection
Version: 2026-04-03_2
Purpose: Centralized credential pattern detection for CloudWatch security
License: Apache 2.0

This module provides shared security pattern detection functions to prevent
credential exfiltration through CloudWatch metrics and error messages.

CHANGES (2026-04-03_2):
- Refactored to use unified DataSanitizer from lee_security.sanitize
- Eliminated code duplication (70% reduction)
- Maintained all security properties
- Added backward compatibility imports

Security measures:
- Detects sensitive patterns (tokens, api keys, passwords, secrets)
- Removes control characters
- Truncates long values
- Returns placeholders for sensitive data
"""

# Import unified sanitizer
from lee.lee_security.sanitize import (
    DataSanitizer,
    contains_sensitive_data,
    sanitize_cloudwatch_error,
    sanitize_dimension_value,
)

# Re-export CREDENTIAL_PATTERNS for backward compatibility
CREDENTIAL_PATTERNS = DataSanitizer.CREDENTIAL_PATTERNS

__all__ = [
    "CREDENTIAL_PATTERNS",
    "contains_sensitive_data",
    "sanitize_cloudwatch_error",
    "sanitize_dimension_value",
]
