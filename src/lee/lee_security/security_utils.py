"""security_utils.py - Standalone Security Utility Functions

Lightweight security utilities ported from Home Assistant patterns.
These functions provide direct access (no gateway required) to common
security operations for LEE (Lambda Entry Environment).

Version: 2026.03.18
License: Apache 2.0

Functions:
- generate_token(): CSPRNG token generation (url_safe, hex, base64)
- validate_string(): String parameter validation
- hash_string(): Secure string hashing (sha256, sha384, sha512)

Usage:
    >>> from lee.lee_security.security_utils import generate_token, validate_string, hash_string
    >>>
    >>> # Generate secure tokens
    >>> token = generate_token(32, encoding='url_safe')
    >>>
    >>> # Validate string parameters
    >>> is_valid = validate_string("input", min_length=1, max_length=100)
    >>>
    >>> # Hash strings securely
    >>> hashed = hash_string("sensitive data", algorithm='sha256')

"""

import hashlib
import logging
import secrets
from typing import Literal

# Import maximum token length from configuration
try:
    from lee.lee_config.variables import (
        SECURITY_MAX_TOKEN_LENGTH,
        get_config_value,
    )
    # Validate token length bounds
    MAX_TOKEN_LENGTH = get_config_value(
        SECURITY_MAX_TOKEN_LENGTH,
        min_value=256,
        max_value=8192,
    )
except (ImportError, ValueError):
    # Fallback for standalone usage or if validation fails
    MAX_TOKEN_LENGTH = 4096

# Security logger
_logger = logging.getLogger(__name__)


def generate_token(
    length: int = 32,
    encoding: Literal["url_safe", "hex", "base64"] = "url_safe"
) -> str:
    """Generate a cryptographically secure random token.

    Ported from Home Assistant core-dev/homeassistant/helpers/template/extensions/crypto.py
    and core-dev/homeassistant/auth/models.py patterns.

    Uses Python secrets module for CSPRNG (Cryptographically Secure Pseudo-Random
    Number Generator) suitable for OAuth tokens, API keys, CSRF tokens, and
    session identifiers.

    Args:
        length: Token length in bytes (default: 32)
        encoding: Encoding format - 'url_safe', 'hex', or 'base64' (default: 'url_safe')

    Returns:
        Cryptographically secure random token string

    Raises:
        ValueError: If encoding is invalid or length too small (< 8) or too large (> 4096)

    Examples:
        >>> # URL-safe token (default, 32 bytes)
        >>> token = generate_token()
        >>> print(len(token))  # ~43 characters
        >>>
        >>> # Hex-encoded token (16 bytes)
        >>> token_hex = generate_token(16, encoding='hex')
        >>> print(len(token_hex))  # 32 characters
        >>>
        >>> # Base64-encoded token (24 bytes)
        >>> token_b64 = generate_token(24, encoding='base64')

    Home Assistant Pattern References:
        - secrets.token_hex(64) in auth/models.py (line 122)
        - secrets.token_urlsafe() in helpers/config_entry_oauth2_flow.py (line 382)

    """
    if length < 8:
        raise ValueError(f"Token length must be at least 8 bytes, got {length}")
    if length > MAX_TOKEN_LENGTH:
        raise ValueError(
            f"Token length must not exceed {MAX_TOKEN_LENGTH} bytes, got {length}"
        )

    try:
        if encoding == "url_safe":
            return secrets.token_urlsafe(length)
        if encoding == "hex":
            return secrets.token_hex(length)
        if encoding == "base64":
            token_bytes = secrets.token_bytes(length)
            # pylint: disable=import-outside-toplevel
            import base64
            return base64.b64encode(token_bytes).decode("ascii")

        raise ValueError(
            f"Invalid encoding: {encoding}. Use 'url_safe', 'hex', or 'base64'"
        )
    except (ValueError, TypeError) as e:
        _logger.error(
            "Token generation failed: %s",
            e.__class__.__name__,
            extra={"security_event": True, "operation": "generate_token"}
        )
        raise


def validate_string(
    value: str,
    min_length: int = 0,
    max_length: int = 1000,
    allow_empty: bool = False
) -> bool:
    """Validate string parameters with length and type checking.

    Ported from Home Assistant validation patterns found in:
    - helpers/template/extensions/crypto.py (line 59)
    - components/miele/diagnostics.py (line 21)
    - components/nightscout/utils.py (line 10)

    Provides defensive validation for user input, configuration values,
    and API parameters to prevent injection attacks and buffer overflows.

    Args:
        value: String value to validate
        min_length: Minimum allowed length (default: 0)
        max_length: Maximum allowed length (default: 1000)
        allow_empty: Allow empty strings (default: False)

    Returns:
        True if string passes validation, False otherwise

    Examples:
        >>> # Validate username
        >>> is_valid = validate_string("user123", min_length=3, max_length=50)
        >>>
        >>> # Validate optional field
        >>> is_valid = validate_string("", allow_empty=True)
        >>>
        >>> # Validate API key
        >>> is_valid = validate_string(api_key, min_length=32, max_length=64)

    Security Considerations:
        - Prevents buffer overflow attacks via length limits
        - Prevents injection attacks via type checking
        - Supports both required and optional fields
        - Fast-fail validation (checks type before length)

    """
    try:
        # Type check
        if not isinstance(value, str):
            return False

        # Empty string check
        if not value and not allow_empty:
            return False

        # Length validation
        if len(value) < min_length:
            return False
        if len(value) > max_length:
            return False

        return True
    except (AttributeError, TypeError) as e:
        _logger.warning(
            "String validation failed: %s",
            e.__class__.__name__,
            extra={"security_event": True, "operation": "validate_string"}
        )
        return False


def hash_string(
    data: str,
    algorithm: Literal["sha256", "sha384", "sha512"] = "sha256"
) -> str:
    """Hash a string using secure cryptographic algorithms.

    Ported from Home Assistant core-dev/homeassistant/helpers/template/extensions/crypto.py
    (lines 57-64) and used throughout the codebase:
    - components/androidtv/media_player.py (line 176)
    - components/esphome/assist_satellite.py (line 847)
    - components/lastfm/sensor.py (line 59)
    - components/nightscout/utils.py (line 10)

    Uses SHA-2 family algorithms (SHA-256, SHA-384, SHA-512) for secure
    one-way hashing suitable for:
    - Data deduplication
    - Identifier hashing (PII redaction)
    - Cache key generation
    - Data integrity verification

    **SECURITY WARNING:** Do NOT use for password storage. Use bcrypt/scrypt/argon2 instead.

    Args:
        data: String data to hash
        algorithm: Hash algorithm - 'sha256', 'sha384', or 'sha512' (default: 'sha256')

    Returns:
        Hexadecimal hash string

    Raises:
        ValueError: If algorithm is invalid
        TypeError: If data is not a string

    Examples:
        >>> # Hash URL for cache key
        >>> cache_key = hash_string("https://example.com/api/data")
        >>>
        >>> # Hash identifier for PII redaction
        >>> hashed_id = hash_string(user_email, algorithm='sha256')[:16]
        >>>
        >>> # Hash file data for integrity check
        >>> file_hash = hash_string(file_content, algorithm='sha512')

    Home Assistant Pattern References:
        - hashlib.sha256(value.encode()).hexdigest() (crypto.py:59)
        - hashlib.sha512(value.encode()).hexdigest() (crypto.py:64)

    Security Properties:
        - SHA-256: 256-bit output, 64 hex characters
        - SHA-384: 384-bit output, 96 hex characters
        - SHA-512: 512-bit output, 128 hex characters
        - Pre-image resistance: Cannot reverse hash to find original data
        - Collision resistance: Computationally infeasible to find two inputs with same hash
        - Avalanche effect: Small input changes cause large output changes

    """
    try:
        # Type check
        if not isinstance(data, str):
            raise TypeError(f"data must be str, got {type(data).__name__}")

        # Validate algorithm
        valid_algorithms = ["sha256", "sha384", "sha512"]
        if algorithm not in valid_algorithms:
            raise ValueError(
                f"Invalid algorithm: {algorithm}. Use {', '.join(valid_algorithms)}"
            )

        # Encode and hash
        encoded_data = data.encode("utf-8")
        hash_func = getattr(hashlib, algorithm)
        hash_value = hash_func(encoded_data)

        return hash_value.hexdigest()
    except (ValueError, TypeError, AttributeError, UnicodeEncodeError) as e:
        _logger.error(
            "String hashing failed: %s",
            e.__class__.__name__,
            extra={"security_event": True, "operation": "hash_string"}
        )
        raise


__all__ = [
    "generate_token",
    "validate_string",
    "hash_string",
]
