"""
gateway_wrappers_security.py - SECURITY Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for SECURITY interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation
# NEW: Add debug system for exact failure point identification
from debug import debug_log, debug_timing, generate_correlation_id


def validate_request(request: Dict[str, Any], correlation_id: str = None) -> Dict[str, Any]:
    """Validate HTTP request."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_request called")

    with debug_timing(correlation_id, "SECURITY", "validate_request"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_request', request=request)
            debug_log(correlation_id, "SECURITY", "validate_request completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_request failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_token(token: str, correlation_id: str = None) -> bool:
    """Validate authentication token."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_token called")

    with debug_timing(correlation_id, "SECURITY", "validate_token"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)
            debug_log(correlation_id, "SECURITY", "validate_token completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_token failed", error_type=type(e).__name__, error=str(e))
            raise


def encrypt_data(data: str, correlation_id: str = None) -> str:
    """Encrypt data."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "encrypt_data called")

    with debug_timing(correlation_id, "SECURITY", "encrypt_data"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)
            debug_log(correlation_id, "SECURITY", "encrypt_data completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "encrypt_data failed", error_type=type(e).__name__, error=str(e))
            raise


def decrypt_data(data: str, correlation_id: str = None) -> str:
    """Decrypt data."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "decrypt_data called")

    with debug_timing(correlation_id, "SECURITY", "decrypt_data"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'decrypt', data=data)
            debug_log(correlation_id, "SECURITY", "decrypt_data completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "decrypt_data failed", error_type=type(e).__name__, error=str(e))
            raise


def generate_correlation_id(prefix: Optional[str] = None, correlation_id: str = None) -> str:
    """Generate correlation ID."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = "cid-generate"  # Use fixed ID for correlation ID generation

    debug_log(correlation_id, "SECURITY", "generate_correlation_id called", prefix=prefix)

    with debug_timing(correlation_id, "SECURITY", "generate_correlation_id", prefix=prefix):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id', prefix=prefix)
            debug_log(correlation_id, "SECURITY", "generate_correlation_id completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "generate_correlation_id failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_string(value: str, correlation_id: str = None, **kwargs) -> bool:
    """Validate string."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_string called", value_length=len(value))

    with debug_timing(correlation_id, "SECURITY", "validate_string"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_string', value=value, **kwargs)
            debug_log(correlation_id, "SECURITY", "validate_string completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_string failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_email(email: str, correlation_id: str = None) -> bool:
    """Validate email address."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_email called", email_length=len(email))

    with debug_timing(correlation_id, "SECURITY", "validate_email"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_email', email=email)
            debug_log(correlation_id, "SECURITY", "validate_email completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_email failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_url(url: str, correlation_id: str = None) -> bool:
    """Validate URL."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_url called", url_length=len(url))

    with debug_timing(correlation_id, "SECURITY", "validate_url"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_url', url=url)
            debug_log(correlation_id, "SECURITY", "validate_url completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_url failed", error_type=type(e).__name__, error=str(e))
            raise


def hash_data(data: str, algorithm: str = 'sha256', correlation_id: str = None) -> str:
    """Hash data."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "hash_data called", algorithm=algorithm, data_length=len(data))

    with debug_timing(correlation_id, "SECURITY", "hash_data", algorithm=algorithm):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'hash', data=data, algorithm=algorithm)
            debug_log(correlation_id, "SECURITY", "hash_data completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "hash_data failed", error_type=type(e).__name__, error=str(e))
            raise


def verify_hash(data: str, hash_value: str, algorithm: str = 'sha256', correlation_id: str = None) -> bool:
    """Verify hash."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "verify_hash called", algorithm=algorithm)

    with debug_timing(correlation_id, "SECURITY", "verify_hash", algorithm=algorithm):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'verify_hash', data=data, hash_value=hash_value, algorithm=algorithm)
            debug_log(correlation_id, "SECURITY", "verify_hash completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "verify_hash failed", error_type=type(e).__name__, error=str(e))
            raise


def sanitize_input(data: str, correlation_id: str = None) -> str:
    """Sanitize input data."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "sanitize_input called", data_length=len(data))

    with debug_timing(correlation_id, "SECURITY", "sanitize_input"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)
            debug_log(correlation_id, "SECURITY", "sanitize_input completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "sanitize_input failed", error_type=type(e).__name__, error=str(e))
            raise


def sanitize_for_log(data: Any, correlation_id: str = None) -> Any:
    """
    Sanitize data for safe logging - removes PII and sensitive fields.

    Related CVE: CVE-LOG-001 (Sensitive Data Exposure in Logs)
    """
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "sanitize_for_log called", data_type=type(data).__name__)

    with debug_timing(correlation_id, "SECURITY", "sanitize_for_log"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)
            debug_log(correlation_id, "SECURITY", "sanitize_for_log completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "sanitize_for_log failed", error_type=type(e).__name__, error=str(e))
            raise


# ===== CACHE SECURITY VALIDATORS (2025.10.20) =====

def validate_cache_key(key: str, correlation_id: str = None) -> None:
    """
    Validate cache key format and safety.

    Validates cache keys against security rules:
    - Length: 1-255 characters
    - Characters: [a-zA-Z0-9_\\-:.]
    - Rejects: control characters, path traversal, special characters

    Args:
        key: Cache key to validate

    Raises:
        ValueError: If key is invalid with specific reason

    Related CVE: CVE-SUGA-2025-001 (Cache Key Injection)
    """
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_cache_key called", key_length=len(key))

    with debug_timing(correlation_id, "SECURITY", "validate_cache_key"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_cache_key', key=key)
            debug_log(correlation_id, "SECURITY", "validate_cache_key completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_cache_key failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_ttl(ttl: float, correlation_id: str = None) -> None:
    """
    Validate TTL (time-to-live) value is within acceptable range.

    Validates TTL boundaries:
    - Minimum: 1 second (prevents rapid churn)
    - Maximum: 86400 seconds / 24 hours (prevents resource exhaustion)
    - Rejects: NaN, infinity, negative values

    Args:
        ttl: Time-to-live in seconds

    Raises:
        ValueError: If TTL is out of bounds with specific reason

    Related CVE: CVE-SUGA-2025-002 (TTL Boundary Exploitation)
    """
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_ttl called", ttl=ttl)

    with debug_timing(correlation_id, "SECURITY", "validate_ttl"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_ttl', ttl=ttl)
            debug_log(correlation_id, "SECURITY", "validate_ttl completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_ttl failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_module_name(module_name: str, correlation_id: str = None) -> None:
    """
    Validate module name for LUGS (Lazy Unload with Graceful State) dependency tracking.

    Validates module names against security rules:
    - Pattern: Valid Python identifier (letters, digits, underscores)
    - Length: 1-100 characters
    - Rejects: path separators, control characters, special characters

    Args:
        module_name: Python module name to validate

    Raises:
        ValueError: If module name is invalid with specific reason

    Related CVE: CVE-SUGA-2025-004 (LUGS Dependency Poisoning)
    """
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_module_name called", module_name_length=len(module_name))

    with debug_timing(correlation_id, "SECURITY", "validate_module_name"):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_module_name', module_name=module_name)
            debug_log(correlation_id, "SECURITY", "validate_module_name completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_module_name failed", error_type=type(e).__name__, error=str(e))
            raise


def validate_number_range(value: float, min_value: float, max_value: float, name: str = "value", correlation_id: str = None) -> None:
    """
    Generic numeric validation with bounds checking.

    Validates numeric values are within specified range and not special values:
    - Range: min_value <= value <= max_value
    - Rejects: NaN, infinity (positive or negative)

    Args:
        value: Numeric value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)
        name: Name of value for error messages (default: "value")

    Raises:
        ValueError: If value is out of range or special value with specific reason
    """
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "SECURITY", "validate_number_range called", name=name, value=value, min_value=min_value, max_value=max_value)

    with debug_timing(correlation_id, "SECURITY", "validate_number_range", name=name):
        try:
            result = execute_operation(GatewayInterface.SECURITY, 'validate_number_range',
                                     value=value, min_value=min_value, max_value=max_value, name=name)
            debug_log(correlation_id, "SECURITY", "validate_number_range completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "SECURITY", "validate_number_range failed", error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'generate_correlation_id',
    'validate_string',
    'validate_email',
    'validate_url',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    'sanitize_for_log',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
]
