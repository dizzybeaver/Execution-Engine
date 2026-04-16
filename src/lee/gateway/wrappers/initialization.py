"""Initialization Wrapper Functions

Direct access to initialization operations (5 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import initialization

    # Initialize system
    initialization.initialize_system()

    # Get initialization status
    status = initialization.get_status()

    # Get stats
    stats = initialization.get_stats()

    # Set flag
    initialization.set_flag(flag_name='HA_INITIALIZED', value=True)

    # Get flag
    is_set = initialization.get_flag(flag_name='HA_INITIALIZED')
"""

from typing import Any

from lee.gateway.gateway_core import execute_operation


def initialize_system(**kwargs: Any) -> bool:
    """Initialize system components.

    Args:
        **kwargs: Additional initialization options

    Returns:
        True if successful
    """
    return execute_operation('INITIALIZATION', 'initialize', **kwargs)


def get_initialization_status(**kwargs: Any) -> dict[str, Any]:
    """Get initialization status.

    Args:
        **kwargs: Additional options

    Returns:
        Status dictionary
    """
    return execute_operation('INITIALIZATION', 'get_status', **kwargs)


def initialization_get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get initialization statistics.

    Args:
        **kwargs: Additional options

    Returns:
        Statistics dictionary
    """
    return execute_operation('INITIALIZATION', 'get_stats', **kwargs)


def set_initialization_flag(flag_name: str, value: Any, **kwargs: Any) -> None:
    """Set initialization flag.

    Args:
        flag_name: Flag name
        value: Flag value
        **kwargs: Additional options
    """
    execute_operation('INITIALIZATION', 'set_flag', flag_name=flag_name, value=value, **kwargs)


def get_initialization_flag(flag_name: str, **kwargs: Any) -> Any:
    """Get initialization flag.

    Args:
        flag_name: Flag name
        **kwargs: Additional options

    Returns:
        Flag value or None if not set
    """
    return execute_operation('INITIALIZATION', 'get_flag', flag_name=flag_name, **kwargs)


__all__ = [
    'get_initialization_flag',
    'get_initialization_status',
    'initialization_get_stats',
    'initialize_system',
    'set_initialization_flag',
]
