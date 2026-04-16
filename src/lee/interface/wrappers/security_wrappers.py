"""security_wrappers.py - SECURITY Interface Wrappers.

Version: 2026-04-11_1 (Consolidated with base_wrapper)
Description: SUGA-ISP compliant wrappers for SECURITY interface operations.

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0.

CONSOLIDATION:
- Removed duplicate correlation ID generation
- Uses base_wrapper.generate_correlation_id
- Reduced code by ~10 lines
"""

from typing import Any, Optional

from lee.gateway.gateway_core import generate_correlation_id as gateway_generate_correlation_id
from lee.lee_security.log_sanitizer import sanitize as sanitize_for_log
from lee.lee_security.security_crypto import (
    hash_data as hash_data_impl,
)
from lee.lee_security.security_crypto import (
    verify_hash as verify_hash_impl,
)
from lee.lee_security.security_sanitizer import sanitize_input as sanitize_input_impl
from lee.lee_security.security_validation_impl import (
    validate_cache_key_implementation,
    validate_email_implementation,
    validate_module_name_implementation,
    validate_number_range_implementation,
    validate_request_implementation,
    validate_string_implementation,
    validate_token_implementation,
    validate_ttl_implementation,
    validate_url_implementation,
)


def validate_request(request: dict[str, Any], _correlation_id: Optional[str] = None) -> dict[str, Any]:
    """Validate HTTP request.

    Args:
        request: HTTP request to validate
        correlation_id: Optional correlation ID for tracking
    """
    return validate_request_implementation(request=request)


def validate_token(token: str, _correlation_id: Optional[str] = None) -> bool:
    """Validate authentication token.

    Args:
        token: Token to validate
        correlation_id: Optional correlation ID for tracking
    """
    return validate_token_implementation(token=token)


def generate_correlation_id_with_prefix(prefix: Optional[str] = None, _correlation_id: Optional[str] = None) -> str:
    """Generate correlation ID with optional prefix.

    Args:
        prefix: Optional prefix for correlation ID
        correlation_id: Optional correlation ID for tracking
    """
    if prefix:
        return gateway_generate_correlation_id(prefix)
    return gateway_generate_correlation_id("cid")


def validate_string(value: str, _correlation_id: Optional[str] = None, **kwargs) -> bool:
    """Validate string.

    Args:
        value: String to validate
        correlation_id: Optional correlation ID for tracking
        **kwargs: Additional validation parameters
    """
    return validate_string_implementation(value=value, **kwargs)


def validate_email(email: str, _correlation_id: Optional[str] = None) -> bool:
    """Validate email address.

    Args:
        email: Email address to validate
        correlation_id: Optional correlation ID for tracking
    """
    return validate_email_implementation(email=email)


def validate_url(url: str, _correlation_id: Optional[str] = None) -> bool:
    """Validate URL.

    Args:
        url: URL to validate
        correlation_id: Optional correlation ID for tracking
    """
    return validate_url_implementation(url=url)


def hash_data(data: str, algorithm: str = "sha256", _correlation_id: Optional[str] = None) -> str:
    """Hash data.

    Args:
        data: Data to hash
        algorithm: Hash algorithm to use
        correlation_id: Optional correlation ID for tracking
    """
    return hash_data_impl(data=data, algorithm=algorithm)


def verify_hash(data: str, hash_value: str, algorithm: str = "sha256", _correlation_id: Optional[str] = None) -> bool:
    """Verify hash.

    Args:
        data: Data to verify
        hash_value: Hash value to compare against
        algorithm: Hash algorithm used
        correlation_id: Optional correlation ID for tracking
    """
    return verify_hash_impl(data=data, expected_hash=hash_value, algorithm=algorithm)


def sanitize_input(data: str, _correlation_id: Optional[str] = None) -> str:
    """Sanitize input data.

    Args:
        data: Data to sanitize
        correlation_id: Optional correlation ID for tracking
    """
    result = sanitize_input_impl(input_data=data)
    return result.sanitized if result.sanitized else data


def sanitize_for_log_wrapper(data: Any, _correlation_id: Optional[str] = None) -> Any:
    """Sanitize data for safe logging - removes PII and sensitive fields.

    Args:
        data: Data to sanitize
        correlation_id: Optional correlation ID for tracking

    Related CVE: CVE-LOG-001 (Sensitive Data Exposure in Logs)
    """
    return sanitize_for_log(message=data)


# ===== CACHE SECURITY VALIDATORS =====

def validate_cache_key(key: str, _correlation_id: Optional[str] = None) -> None:
    """Validate cache key format and safety.

    Validates cache keys against security rules:
    - Length: 1-255 characters
    - Characters: [a-zA-Z0-9_:-.]
    - Rejects: control characters, path traversal, special characters

    Args:
        key: Cache key to validate
        correlation_id: Optional correlation ID for tracking

    Raises:
        ValueError: If key is invalid with specific reason

    Related CVE: CVE-SUGA-2025-001 (Cache Key Injection)
    """
    validate_cache_key_implementation(key=key)


def validate_ttl(ttl: float, _correlation_id: Optional[str] = None) -> None:
    """Validate TTL (time-to-live) value is within acceptable range.

    Validates TTL boundaries:
    - Minimum: 1 second (prevents rapid churn)
    - Maximum: 86400 seconds / 24 hours (prevents resource exhaustion)
    - Rejects: NaN, infinity, negative values

    Args:
        ttl: Time-to-live in seconds
        correlation_id: Optional correlation ID for tracking

    Raises:
        ValueError: If TTL is out of bounds with specific reason

    Related CVE: CVE-SUGA-2025-002 (TTL Boundary Exploitation)
    """
    validate_ttl_implementation(ttl=ttl)


def validate_module_name(module_name: str, _correlation_id: Optional[str] = None) -> None:
    """Validate module name for LUGS (Lazy Unload with Graceful State) dependency tracking.

    Validates module names against security rules:
    - Pattern: Valid Python identifier (letters, digits, underscores)
    - Length: 1-100 characters
    - Rejects: path separators, control characters, special characters

    Args:
        module_name: Python module name to validate
        correlation_id: Optional correlation ID for tracking

    Raises:
        ValueError: If module name is invalid with specific reason

    Related CVE: CVE-SUGA-2025-004 (LUGS Dependency Poisoning)
    """
    validate_module_name_implementation(module_name=module_name)


def validate_number_range(
    value: float,
    min_value: float,
    max_value: float,
    name: str = "value",
    _correlation_id: Optional[str] = None
) -> None:
    """Generic numeric validation with bounds checking.

    Validates numeric values are within specified range and not special values:
    - Range: min_value <= value <= max_value
    - Rejects: NaN, infinity (positive or negative)

    Args:
        value: Numeric value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)
        name: Name of value for error messages (default: "value")
        correlation_id: Optional correlation ID for tracking

    Raises:
        ValueError: If value is out of range or special value with specific reason
    """
    validate_number_range_implementation(
        value=value,
        min_val=min_value,
        max_val=max_value,
        name=name
    )


def compare_tokens(token1: str, token2: str, _correlation_id: Optional[str] = None) -> bool:
    """Compare two tokens in constant time to prevent timing attacks.

    **CRITICAL SECURITY FUNCTION:** This function MUST be used for comparing
    security-sensitive tokens (OAuth tokens, API keys, session IDs, etc.).
    NEVER use simple string equality (== or !=) for token comparison.

    **Timing Attack Prevention:**
    Simple string comparison (==) in Python is vulnerable to timing attacks
    because it short-circuits on the first mismatching character. An attacker
    can measure response times to progressively guess correct token values.

    This function uses hmac.compare_digest() which compares ALL characters
    regardless of mismatches, making timing analysis impossible.

    **CVE Mitigation:**
    - CVE-TIMING-001 (OAuth Token Timing Attack) - CVSS 7.5 HIGH
    - Prevents token leakage via timing analysis
    - Required for OAuth token comparison in Lambda handlers

    Args:
        token1: First token to compare
        token2: Second token to compare
        correlation_id: Optional correlation ID for logging

    Returns:
        True if tokens are identical, False otherwise

    Example:
        >>> from lee.interface.wrappers.security_wrappers import compare_tokens
        >>>
        >>> # CORRECT: Constant-time comparison
        >>> if compare_tokens(oauth_token, stored_token):
        ...     authorize_user()
        >>>
        >>> # INCORRECT: Vulnerable to timing attacks
        >>> if oauth_token == stored_token:  # DON'T DO THIS!
        ...     authorize_user()

    **Use Cases:**
    - OAuth token comparison (Alexa Smart Home directives)
    - API key validation
    - Session token verification
    - CSRF token validation

    **Related Functions:**
    - hmac_verify(): For HMAC signature verification
    - verify_hash(): For hash value verification

    **Security Impact:**
    - CVSS 7.5 HIGH -> <2.0 (informational)
    - Prevents token guessing via timing analysis
    - Required for Alexa Smart Home SLA compliance
    """
    from lee.lee_security import compare_tokens as _compare_tokens  # pylint: disable=import-outside-toplevel
    return _compare_tokens(token1, token2)


__all__ = [
    "compare_tokens",
    "generate_correlation_id_with_prefix",
    "hash_data",
    "sanitize_for_log",
    "sanitize_input",
    "validate_cache_key",
    "validate_email",
    "validate_module_name",
    "validate_number_range",
    "validate_request",
    "validate_string",
    "validate_token",
    "validate_ttl",
    "validate_url",
    "verify_hash",
]
