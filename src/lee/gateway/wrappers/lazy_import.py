# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-23 - Created Lazy Import wrapper module (9 operations)

"""Lazy Import Wrapper Functions

Direct access to Lazy Import Gateway System (LIGS) through gateway.
All functions execute via execute_operation(GatewayInterface.LAZY_IMPORT, ...) internally.

LIGS provides lazy module loading for 40-60% cold start reduction.

Usage:
    from lee.gateway.wrappers import lazy_import

    # Register lazy module
    lazy_import.register(name='ha_devices', factory=lambda: __import__('home_assistant'))

    # Get module (loads on first access)
    ha = lazy_import.get(name='ha_devices')

    # Check load status
    if lazy_import.is_loaded(name='ha_devices'):
        print('HA devices loaded')
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


# Module Registration and Retrieval
def register(**kwargs: Any) -> dict[str, Any]:
    """Register a lazy module.

    Args:
        **kwargs: Parameters including:
            - name (str): Module name
            - factory (callable): Factory function to load module
            - correlation_id (str, optional): Correlation ID

    Returns:
        Registration result
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'register', **kwargs)


def get(**kwargs: Any) -> dict[str, Any]:
    """Get lazy module (loads if needed).

    Args:
        **kwargs: Parameters including name (str) - module name

    Returns:
        Module object or load result
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'get', **kwargs)


def preload(**kwargs: Any) -> dict[str, Any]:
    """Preload specific modules.

    Args:
        **kwargs: Parameters including:
            - names (list): List of module names to preload
            - correlation_id (str, optional): Correlation ID

    Returns:
        Preload result
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'preload', **kwargs)


# Status Queries
def is_loaded(**kwargs: Any) -> dict[str, Any]:
    """Check if module loaded.

    Args:
        **kwargs: Parameters including name (str) - module name

    Returns:
        True if loaded, False otherwise
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'is_loaded', **kwargs)


def get_all_loaded(**kwargs: Any) -> dict[str, Any]:
    """Get all loaded module names.

    Args:
        **kwargs: Optional filter parameters

    Returns:
        List of loaded module names
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'get_all_loaded', **kwargs)


def get_all_registered(**kwargs: Any) -> dict[str, Any]:
    """Get all registered module names.

    Args:
        **kwargs: Optional filter parameters

    Returns:
        List of all registered module names
    """
    return execute_operation(
        GatewayInterface.LAZY_IMPORT, 'get_all_registered', **kwargs
    )


# Performance Monitoring
def get_load_time(**kwargs: Any) -> dict[str, Any]:
    """Get load time for specific module.

    Args:
        **kwargs: Parameters including name (str) - module name

    Returns:
        Load time in milliseconds
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'get_load_time', **kwargs)


def get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get registry statistics.

    Args:
        **kwargs: Optional filter parameters

    Returns:
        Registry statistics including counts, load times, etc.
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'get_stats', **kwargs)


# Management
def clear(**kwargs: Any) -> dict[str, Any]:
    """Clear all registered modules.

    Args:
        **kwargs: Optional clear parameters

    Returns:
        Clear operation result
    """
    return execute_operation(GatewayInterface.LAZY_IMPORT, 'clear', **kwargs)


__all__ = [
    # Module Registration and Retrieval
    'register',
    'get',
    'preload',

    # Status Queries
    'is_loaded',
    'get_all_loaded',
    'get_all_registered',

    # Performance Monitoring
    'get_load_time',
    'get_stats',

    # Management
    'clear',
]
