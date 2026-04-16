# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-23 - Created Circuit Breaker wrapper module (6 operations)

"""Circuit Breaker Wrapper Functions

Direct access to circuit breaker operations through gateway.
All functions execute via execute_operation(
    GatewayInterface.CIRCUIT_BREAKER, ...
) internally.

Usage:
    from lee.gateway.wrappers import circuit_breaker

    # Get circuit breaker instance
    breaker = circuit_breaker.get(name='api_service')

    # Execute function with circuit breaker protection
    result = circuit_breaker.call(
        name='api_service', func=my_function
    )

    # Get all breaker states
    states = circuit_breaker.get_all_states()
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


# Circuit Breaker Instance Management
def get(**kwargs: Any) -> dict[str, Any]:
    """Get circuit breaker instance by name.

    Args:
        **kwargs: Parameters including name (str) - circuit breaker name

    Returns:
        Circuit breaker instance or state information
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', **kwargs)


def call(**kwargs: Any) -> dict[str, Any]:
    """Execute function with circuit breaker protection.

    Args:
        **kwargs: Parameters including:
            - name (str): Circuit breaker name
            - func (callable): Function to execute
            - fallback (callable, optional): Fallback function
            - **kwargs: Additional parameters for the function

    Returns:
        Function execution result or fallback result
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', **kwargs)


# State Management
def get_all_states(**kwargs: Any) -> dict[str, Any]:
    """Get states of all circuit breakers.

    Args:
        **kwargs: Optional filter parameters

    Returns:
        Dictionary of all circuit breaker states
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_all_states', **kwargs)


def reset(**kwargs: Any) -> dict[str, Any]:
    """Reset specific circuit breaker to closed state.

    Args:
        **kwargs: Parameters including name (str) - circuit breaker name

    Returns:
        Reset operation result
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset', **kwargs)


def reset_all(**kwargs: Any) -> dict[str, Any]:
    """Reset all circuit breakers to closed state.

    Args:
        **kwargs: Optional reset parameters

    Returns:
        Reset all operation result
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset_all', **kwargs)


# Statistics and Monitoring
def get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get circuit breaker statistics.

    Args:
        **kwargs: Optional filter parameters (name, etc.)

    Returns:
        Circuit breaker statistics including failure counts, success rates, etc.
    """
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_stats', **kwargs)


__all__ = [
    # Circuit Breaker Instance Management
    'get',
    'call',

    # State Management
    'get_all_states',
    'reset',
    'reset_all',

    # Statistics and Monitoring
    'get_stats',
]
