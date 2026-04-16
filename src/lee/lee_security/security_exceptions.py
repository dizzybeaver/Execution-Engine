"""security_exceptions.py - Security Exception Hierarchy

Version: 2026.03.29
Purpose: Security-specific exception types for proper error handling

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


class SecurityError(Exception):
    """Base security exception for LEE security module."""

    def __init__(self, message: str, operation: str = None, details: dict = None):
        """Initialize security error with context.

        Args:
            message: Error message (sanitized for logging)
            operation: Operation that failed (for security logging)
            details: Additional context (will be sanitized)
        """
        super().__init__(message)
        self.operation = operation
        self.details = details or {}


class ValidationError(SecurityError):
    """Raised when security validation fails."""


class TokenError(SecurityError):
    """Raised when token operation fails."""


class CryptoError(SecurityError):
    """Raised when cryptographic operation fails."""


class CacheSecurityError(SecurityError):
    """Raised when cache security operation fails."""


class RateLimitError(SecurityError):
    """Raised when rate limit is exceeded."""


__all__ = [
    "CacheSecurityError",
    "CryptoError",
    "RateLimitError",
    "SecurityError",
    "TokenError",
    "ValidationError",
]
