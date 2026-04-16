# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_security.py
Version: 2026-04-11_2
Purpose: Security interface router with import protection
License: Apache 2.0
"""

from typing import Any

from lee.utils.graceful_import import graceful_import


@graceful_import(['lee.lee_security', 'lee.lee_utility'])
def _import_security():
    from lee.lee_security import (
        compare_tokens,
        generate_token,
        get_security_manager,
        hash_implementation,
        sanitize_input_implementation,
        security_reset_implementation,
        validate_cache_key_implementation,
        validate_email_implementation,
        validate_module_name_implementation,
        validate_number_range_implementation,
        validate_request_implementation,
        validate_string_implementation,
        validate_token_implementation,
        validate_ttl_implementation,
        validate_url_implementation,
        verify_hash_implementation,
    )
    from lee.lee_utility import generate_correlation_id_implementation
    return {
        'compare_tokens': compare_tokens,
        'generate_token': generate_token,
        'get_security_manager': get_security_manager,
        'hash': hash_implementation,
        'sanitize_input': sanitize_input_implementation,
        'security_reset': security_reset_implementation,
        'validate_cache_key': validate_cache_key_implementation,
        'validate_email': validate_email_implementation,
        'validate_module_name': validate_module_name_implementation,
        'validate_number_range': validate_number_range_implementation,
        'validate_request': validate_request_implementation,
        'validate_string': validate_string_implementation,
        'validate_token': validate_token_implementation,
        'validate_ttl': validate_ttl_implementation,
        'validate_url': validate_url_implementation,
        'verify_hash': verify_hash_implementation,
        'generate_correlation_id': generate_correlation_id_implementation,
    }


_security_funcs = _import_security()
_SECURITY_AVAILABLE = _import_security.__dict__.get('_SECURITY_AVAILABLE', False)
_SECURITY_IMPORT_ERROR = _import_security.__dict__.get('_SECURITY_IMPORT_ERROR', None)

if _SECURITY_AVAILABLE:
    compare_tokens = _security_funcs['compare_tokens']
    generate_token = _security_funcs['generate_token']
    get_security_manager = _security_funcs['get_security_manager']
    hash_implementation = _security_funcs['hash']
    sanitize_input_implementation = _security_funcs['sanitize_input']
    security_reset_implementation = _security_funcs['security_reset']
    validate_cache_key_implementation = _security_funcs['validate_cache_key']
    validate_email_implementation = _security_funcs['validate_email']
    validate_module_name_implementation = _security_funcs['validate_module_name']
    validate_number_range_implementation = _security_funcs['validate_number_range']
    validate_request_implementation = _security_funcs['validate_request']
    validate_string_implementation = _security_funcs['validate_string']
    validate_token_implementation = _security_funcs['validate_token']
    validate_ttl_implementation = _security_funcs['validate_ttl']
    validate_url_implementation = _security_funcs['validate_url']
    verify_hash_implementation = _security_funcs['verify_hash']
    generate_correlation_id_implementation = _security_funcs['generate_correlation_id']
else:
    def _create_stub(**_kwargs):
        return {"success": False, "error": "Security module unavailable"}

    compare_tokens = _create_stub
    generate_token = _create_stub
    get_security_manager = _create_stub
    hash_implementation = _create_stub
    sanitize_input_implementation = _create_stub
    security_reset_implementation = _create_stub
    validate_cache_key_implementation = _create_stub
    validate_email_implementation = _create_stub
    validate_module_name_implementation = _create_stub
    validate_number_range_implementation = _create_stub
    validate_request_implementation = _create_stub
    validate_string_implementation = _create_stub
    validate_token_implementation = _create_stub
    validate_ttl_implementation = _create_stub
    validate_url_implementation = _create_stub
    verify_hash_implementation = _create_stub
    generate_correlation_id_implementation = _create_stub


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for security operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category
    - description: Human-readable description
    """
    return {
        "generate_token": {
            "func": generate_token,
            "category": "write",
            "description": "Generate cryptographically secure token",
        },
        "hash_string": {
            "func": hash_implementation,
            "category": "write",
            "description": "Generate cryptographic hash of string",
        },
        "validate_request": {
            "func": validate_request_implementation,
            "category": "read",
            "description": "Validate incoming request for threats",
        },
        "validate_token": {
            "func": validate_token_implementation,
            "category": "read",
            "description": "Validate authentication token",
        },
        "hash": {
            "func": hash_implementation,
            "category": "write",
            "description": "Generate cryptographic hash of data",
        },
        "verify_hash": {
            "func": verify_hash_implementation,
            "category": "read",
            "description": "Verify data against cryptographic hash",
        },
        "sanitize": {
            "func": sanitize_input_implementation,
            "category": "read",
            "description": "Sanitize data by removing control chars",
        },
        "sanitize_data": {
            "func": sanitize_input_implementation,
            "category": "read",
            "description": "Sanitize data (alias for sanitize)",
        },
        "generate_correlation_id": {
            "func": generate_correlation_id_implementation,
            "category": "write",
            "description": "Generate unique correlation ID",
        },
        "validate_string": {
            "func": validate_string_implementation,
            "category": "read",
            "description": "Validate string input",
        },
        "validate_email": {
            "func": validate_email_implementation,
            "category": "read",
            "description": "Validate email address format",
        },
        "validate_url": {
            "func": validate_url_implementation,
            "category": "read",
            "description": "Validate URL format",
        },
        "get_stats": {
            "func": lambda **kw: get_security_manager().get_stats(),
            "category": "read",
            "description": "Get security validation statistics",
        },
        "validate_cache_key": {
            "func": validate_cache_key_implementation,
            "category": "read",
            "description": "Validate cache key format and length",
        },
        "validate_ttl": {
            "func": validate_ttl_implementation,
            "category": "read",
            "description": "Validate TTL value",
        },
        "validate_module_name": {
            "func": validate_module_name_implementation,
            "category": "read",
            "description": "Validate module name format",
        },
        "validate_number_range": {
            "func": validate_number_range_implementation,
            "category": "read",
            "description": "Validate numeric value within range",
        },
        "compare_tokens": {
            "func": compare_tokens,
            "category": "read",
            "description": "Compare two tokens (timing-attack safe)",
        },
        "reset": {
            "func": security_reset_implementation,
            "category": "delete",
            "description": "Reset security statistics",
        },
        "reset_security": {
            "func": security_reset_implementation,
            "category": "delete",
            "description": "Reset security statistics (alias)",
        },
    }


_OPERATION_DISPATCH = (
    _build_dispatch_dict() if _SECURITY_AVAILABLE else {}
)


def execute_security_operation(operation: str, **kwargs) -> Any:
    """Route security operation requests using dispatch dictionary.

    Args:
        operation: Security operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If Security interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    if not _SECURITY_AVAILABLE:
        raise RuntimeError(
            f"Security interface unavailable: {_SECURITY_IMPORT_ERROR}",
        )

    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid: {', '.join(_OPERATION_DISPATCH.keys())}",
        )

    entry = _OPERATION_DISPATCH[operation]
    func = entry["func"]
    return func(**kwargs)


__all__ = ["execute_security_operation"]
