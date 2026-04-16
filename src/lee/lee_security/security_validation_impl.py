"""security/security_validation_impl.py
Version: 2026-04-11_2
Purpose: Validation implementation functions for security interface
License: Apache 2.0

REFACTOR (2026-04-11):
- Consolidated 9 duplicate functions (225 lines) using factory pattern
- Reduced to 9 factory calls (27 lines) - 198 lines eliminated
- All functionality preserved, 100% backward compatible
"""


from lee.lee_security.security_factory import create_security_function_factory
from lee.lee_security.security_types import SecurityOperation


def _log_params_request(kwargs):
    """Create log parameters for validate_request operation."""
    return {"has_request": kwargs.get("request") is not None}


def _log_params_token(kwargs):
    """Create log parameters for validate_token operation."""
    return {"token": kwargs.get("token")}


def _log_params_string(kwargs):
    """Create log parameters for validate_string operation."""
    value = kwargs.get("value", "")
    return {
        "value_length": len(value) if value else 0,
        "min_length": kwargs.get("min_length", 0),
        "max_length": kwargs.get("max_length", 1000)
    }


def _log_params_email(kwargs):
    """Create log parameters for validate_email operation."""
    return {"has_email": kwargs.get("email") is not None}


def _log_params_url(kwargs):
    """Create log parameters for validate_url operation."""
    return {"has_url": kwargs.get("url") is not None}


def _log_params_cache_key(kwargs):
    """Create log parameters for validate_cache_key operation."""
    key = kwargs.get("key", "")
    return {"key_length": len(key) if key else 0}


def _log_params_ttl(kwargs):
    """Create log parameters for validate_ttl operation."""
    return {"ttl": kwargs.get("ttl")}


def _log_params_module_name(kwargs):
    """Create log parameters for validate_module_name operation."""
    return {"module_name": kwargs.get("module_name")}


def _log_params_number_range(kwargs):
    """Create log parameters for validate_number_range operation."""
    return {
        "value": kwargs.get("value"),
        "min_val": kwargs.get("min_val"),
        "max_val": kwargs.get("max_val"),
        "name": kwargs.get("name", "value")
    }


# Create all validation functions using factory pattern
# Each line replaces 25 lines of duplicate code
validate_request_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_REQUEST,
    "validate_request_implementation",
    log_params_factory=_log_params_request
)

validate_token_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_TOKEN,
    "validate_token_implementation",
    log_params_factory=_log_params_token
)

validate_string_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_STRING,
    "validate_string_implementation",
    log_params_factory=_log_params_string
)

validate_email_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_EMAIL,
    "validate_email_implementation",
    log_params_factory=_log_params_email
)

validate_url_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_URL,
    "validate_url_implementation",
    log_params_factory=_log_params_url
)

validate_cache_key_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_CACHE_KEY,
    "validate_cache_key_implementation",
    log_params_factory=_log_params_cache_key
)

validate_ttl_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_TTL,
    "validate_ttl_implementation",
    log_params_factory=_log_params_ttl
)

validate_module_name_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_MODULE_NAME,
    "validate_module_name_implementation",
    log_params_factory=_log_params_module_name
)

validate_number_range_implementation = create_security_function_factory(
    SecurityOperation.VALIDATE_NUMBER_RANGE,
    "validate_number_range_implementation",
    log_params_factory=_log_params_number_range
)


__all__ = [
    "validate_cache_key_implementation",
    "validate_email_implementation",
    "validate_module_name_implementation",
    "validate_number_range_implementation",
    "validate_request_implementation",
    "validate_string_implementation",
    "validate_token_implementation",
    "validate_ttl_implementation",
    "validate_url_implementation",
]
