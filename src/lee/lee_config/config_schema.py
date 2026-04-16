# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-29 - Add safe configuration parameter utilities

"""
config_schema.py - Configuration Schema and Safe Type Conversion

This module provides safe type conversion utilities for configuration parameters
with validation, range checking, and proper error handling.

Version: 1.0.0 (2026-03-29)
License: Apache 2.0
"""

import os
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def _log_conversion_warning(key: str, value: str, default: Any, error: str) -> None:
    """Log configuration conversion warning.

    Args:
        key: Configuration parameter key
        value: String value that failed conversion
        default: Default value used as fallback
        error: Error message
    """
    try:
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"Config conversion failed for {key}, using default {default}",
            key=key,
            value=value[:50] if value else "None",
            error=error,
        )
    except (ImportError, AttributeError):
        # Optional dependency - continue if unavailable
        ...


def safe_int_parameter(
    key: str,
    default: int,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
) -> int:
    """Safely convert environment variable to integer with validation.

    Args:
        key: Environment variable name
        default: Default value if conversion fails or out of range
        min_val: Minimum allowed value (None for no minimum)
        max_val: Maximum allowed value (None for no maximum)

    Returns:
        int: Validated integer value or default

    Example:
        >>> timeout = safe_int_parameter("HTTP_TIMEOUT", 10, min_val=1, max_val=300)
        >>> assert 1 <= timeout <= 300
    """
    try:
        env_value = os.getenv(key)
        if env_value is None:
            return default

        value = int(env_value)

        if min_val is not None and value < min_val:
            _log_conversion_warning(
                key, env_value, default,
                f"Value {value} < minimum {min_val}"
            )
            return default

        if max_val is not None and value > max_val:
            _log_conversion_warning(
                key, env_value, default,
                f"Value {value} > maximum {max_val}"
            )
            return default

        return value

    except (ValueError, TypeError) as e:
        _log_conversion_warning(
            key, str(os.getenv(key, "")), default, str(e)
        )
        return default


def safe_float_parameter(
    key: str,
    default: float,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> float:
    """Safely convert environment variable to float with validation.

    Args:
        key: Environment variable name
        default: Default value if conversion fails or out of range
        min_val: Minimum allowed value (None for no minimum)
        max_val: Maximum allowed value (None for no maximum)

    Returns:
        float: Validated float value or default

    Example:
        >>> backoff = safe_float_parameter("HTTP_BACKOFF", 0.5, min_val=0.1, max_val=10.0)
        >>> assert 0.1 <= backoff <= 10.0
    """
    try:
        env_value = os.getenv(key)
        if env_value is None:
            return default

        value = float(env_value)

        if min_val is not None and value < min_val:
            _log_conversion_warning(
                key, env_value, default,
                f"Value {value} < minimum {min_val}"
            )
            return default

        if max_val is not None and value > max_val:
            _log_conversion_warning(
                key, env_value, default,
                f"Value {value} > maximum {max_val}"
            )
            return default

        return value

    except (ValueError, TypeError) as e:
        _log_conversion_warning(
            key, str(os.getenv(key, "")), default, str(e)
        )
        return default


def safe_bool_parameter(key: str, default: bool) -> bool:
    """Safely convert environment variable to boolean.

    Accepts: true, false, 1, 0, yes, no (case-insensitive)

    Args:
        key: Environment variable name
        default: Default value if conversion fails

    Returns:
        bool: Boolean value or default

    Example:
        >>> debug = safe_bool_parameter("DEBUG_MODE", False)
        >>> assert isinstance(debug, bool)
    """
    try:
        env_value = os.getenv(key)
        if env_value is None:
            return default

        normalized = env_value.strip().lower()
        boolean_map = {
            "true": True, "1": True, "yes": True, "on": True,
            "false": False, "0": False, "no": False, "off": False
        }
        result = boolean_map.get(normalized)
        if result is None:
            _log_conversion_warning(
                key, env_value, default,
                f"Invalid boolean value: {env_value}"
            )
            return default
        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        _log_conversion_warning(
            key, str(os.getenv(key, "")), default, str(e)
        )
        return default


def safe_str_parameter(
    key: str,
    default: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> str:
    """Safely get string parameter with length validation.

    Args:
        key: Environment variable name
        default: Default value if validation fails
        min_length: Minimum allowed length (None for no minimum)
        max_length: Maximum allowed length (None for no maximum)

    Returns:
        str: Validated string value or default

    Example:
        >>> url = safe_str_parameter("API_URL", "http://localhost", max_length=2000)
        >>> assert len(url) <= 2000
    """
    try:
        env_value = os.getenv(key)
        if env_value is None:
            return default

        value = str(env_value)

        if min_length is not None and len(value) < min_length:
            _log_conversion_warning(
                key, env_value, default,
                f"Length {len(value)} < minimum {min_length}"
            )
            return default

        if max_length is not None and len(value) > max_length:
            _log_conversion_warning(
                key, env_value, default,
                f"Length {len(value)} > maximum {max_length}"
            )
            return default

        return value

    except (ValueError, TypeError) as e:
        _log_conversion_warning(
            key, str(os.getenv(key, "")), default, str(e)
        )
        return default


__all__ = [
    "safe_bool_parameter",
    "safe_float_parameter",
    "safe_int_parameter",
    "safe_str_parameter",
]
