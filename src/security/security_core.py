"""
security/security_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for security interface
License: Apache 2.0
"""

from typing import Any, Dict, Optional

from security.security_types import SecurityOperation
from security.security_manager import get_security_manager


def validate_request_implementation(request: Dict[str, Any], 
                                    correlation_id: str = None, **kwargs) -> bool:
    """
    Execute validate request operation.
    
    Args:
        request: HTTP request dict
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        True if valid, False otherwise
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_request_implementation called",
             has_request=request is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_REQUEST, correlation_id, request, **kwargs
    )


def validate_token_implementation(token: str, correlation_id: str = None, **kwargs) -> bool:
    """Execute validate token operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_token_implementation called",
             has_token=token is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_TOKEN, correlation_id, token, **kwargs
    )


def validate_string_implementation(value: str, min_length: int = 0, 
                                   max_length: int = 1000, 
                                   correlation_id: str = None, **kwargs) -> bool:
    """Execute validate string operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_string_implementation called",
             value_length=len(value) if value else 0, min_length=min_length, max_length=max_length)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_STRING, correlation_id, value, min_length, max_length, **kwargs
    )


def validate_email_implementation(email: str, correlation_id: str = None, **kwargs) -> bool:
    """Execute validate email operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_email_implementation called",
             has_email=email is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_EMAIL, correlation_id, email, **kwargs
    )


def validate_url_implementation(url: str, correlation_id: str = None, **kwargs) -> bool:
    """Execute validate URL operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_url_implementation called",
             has_url=url is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_URL, correlation_id, url, **kwargs
    )


def encrypt_implementation(data: str, key: Optional[str] = None, 
                          correlation_id: str = None, **kwargs) -> str:
    """Execute encrypt operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "encrypt_implementation called",
             data_length=len(data) if data else 0, has_key=key is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.ENCRYPT, correlation_id, data, key, **kwargs
    )


def decrypt_implementation(data: str, key: Optional[str] = None,
                          correlation_id: str = None, **kwargs) -> str:
    """Execute decrypt operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "decrypt_implementation called",
             data_length=len(data) if data else 0, has_key=key is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.DECRYPT, correlation_id, data, key, **kwargs
    )


def hash_implementation(data: str, correlation_id: str = None, **kwargs) -> str:
    """Execute hash operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "hash_implementation called",
             data_length=len(data) if data else 0)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.HASH, correlation_id, data, **kwargs
    )


def verify_hash_implementation(data: str, hash_value: str, 
                               correlation_id: str = None, **kwargs) -> bool:
    """Execute verify hash operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "verify_hash_implementation called",
             data_length=len(data) if data else 0, has_hash=hash_value is not None)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VERIFY_HASH, correlation_id, data, hash_value, **kwargs
    )


def sanitize_implementation(data: Any, correlation_id: str = None, **kwargs) -> Any:
    """Execute sanitize operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "sanitize_implementation called",
             data_type=type(data).__name__)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.SANITIZE, correlation_id, data, **kwargs
    )


def generate_correlation_id_implementation(correlation_id: str = None, **kwargs) -> str:
    """Execute generate correlation ID operation."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "generate_correlation_id_implementation called")
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.GENERATE_CORRELATION_ID, correlation_id, **kwargs
    )


def validate_cache_key_implementation(key: str, correlation_id: str = None, **kwargs) -> bool:
    """Execute validate cache key operation (CVE-SUGA-2025-001 fix)."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_cache_key_implementation called",
             key_length=len(key) if key else 0)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_CACHE_KEY, correlation_id, key, **kwargs
    )


def validate_ttl_implementation(ttl: float, correlation_id: str = None, **kwargs) -> bool:
    """Execute validate TTL operation (CVE-SUGA-2025-002 fix)."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_ttl_implementation called",
             ttl=ttl)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_TTL, correlation_id, ttl, **kwargs
    )


def validate_module_name_implementation(module_name: str, correlation_id: str = None, 
                                       **kwargs) -> bool:
    """Execute validate module name operation (CVE-SUGA-2025-004 fix)."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_module_name_implementation called",
             module_name=module_name)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_MODULE_NAME, correlation_id, module_name, **kwargs
    )


def validate_number_range_implementation(value: float, min_val: float, max_val: float, 
                                        name: str = 'value', correlation_id: str = None,
                                        **kwargs) -> bool:
    """Execute validate number range operation (generic)."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "validate_number_range_implementation called",
             value=value, min_val=min_val, max_val=max_val, name=name)
    
    return get_security_manager().execute_security_operation(
        SecurityOperation.VALIDATE_NUMBER_RANGE, correlation_id, value, min_val, max_val, name=name, **kwargs
    )


def security_reset_implementation(correlation_id: str = None, **kwargs) -> bool:
    """
    Execute reset operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        bool: True on success
    """
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "security_reset_implementation called")
    
    return get_security_manager().reset(correlation_id)


def get_security_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Get security statistics."""
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SECURITY", "get_security_stats_implementation called")
    
    return get_security_manager().get_stats(correlation_id)


__all__ = [
    'validate_request_implementation',
    'validate_token_implementation',
    'validate_string_implementation',
    'validate_email_implementation',
    'validate_url_implementation',
    'encrypt_implementation',
    'decrypt_implementation',
    'hash_implementation',
    'verify_hash_implementation',
    'sanitize_implementation',
    'generate_correlation_id_implementation',
    'validate_cache_key_implementation',
    'validate_ttl_implementation',
    'validate_module_name_implementation',
    'validate_number_range_implementation',
    'security_reset_implementation',
    'get_security_stats_implementation',
]
