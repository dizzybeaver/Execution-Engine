"""Utility Wrapper Functions

Direct access to utility operations (6 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import utility

    # Generate correlation ID
    corr_id = utility.generate_correlation_id()

    # Get system info
    info = utility.get_system_info()
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def utility_get_system_info(**kwargs: Any) -> dict[str, Any]:
    """Get system information.

    Args:
        **kwargs: Additional options

    Returns:
        System information dictionary
    """
    return execute_operation(GatewayInterface.UTILITY, 'get_system_info', **kwargs)


def utility_get_timestamp(**kwargs: Any) -> int:
    """Get current timestamp.

    Args:
        **kwargs: Additional options

    Returns:
        Unix timestamp in milliseconds
    """
    return execute_operation(GatewayInterface.UTILITY, 'get_timestamp', **kwargs)


def utility_format_timestamp(timestamp_ms: int, **kwargs: Any) -> str:
    """Format timestamp to ISO string.

    Args:
        timestamp_ms: Unix timestamp in milliseconds
        **kwargs: Additional options

    Returns:
        ISO 8601 formatted timestamp string
    """
    return execute_operation(GatewayInterface.UTILITY, 'format_timestamp', timestamp_ms=timestamp_ms, **kwargs)


def utility_parse_timestamp(iso_string: str, **kwargs: Any) -> int:
    """Parse ISO timestamp to milliseconds.

    Args:
        iso_string: ISO 8601 formatted timestamp string
        **kwargs: Additional options

    Returns:
        Unix timestamp in milliseconds
    """
    return execute_operation(GatewayInterface.UTILITY, 'parse_timestamp', iso_string=iso_string, **kwargs)


def utility_validate_timestamp(timestamp_ms: int, **kwargs: Any) -> bool:
    """Validate timestamp is within acceptable range.

    Args:
        timestamp_ms: Unix timestamp in milliseconds
        **kwargs: Additional options (max_future_ms, max_past_ms)

    Returns:
        True if timestamp is valid
    """
    return execute_operation(GatewayInterface.UTILITY, 'validate_timestamp', timestamp_ms=timestamp_ms, **kwargs)


# Convenience aliases without utility_ prefix
get_system_info = utility_get_system_info
get_timestamp = utility_get_timestamp
format_timestamp = utility_format_timestamp
parse_timestamp = utility_parse_timestamp
validate_timestamp = utility_validate_timestamp


__all__ = [
    'utility_get_system_info',
    'utility_get_timestamp',
    'utility_format_timestamp',
    'utility_parse_timestamp',
    'utility_validate_timestamp',
    # Convenience aliases
    'get_system_info',
    'get_timestamp',
    'format_timestamp',
    'parse_timestamp',
    'validate_timestamp',
]
