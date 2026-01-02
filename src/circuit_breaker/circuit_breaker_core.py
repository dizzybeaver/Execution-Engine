"""
circuit_breaker/circuit_breaker_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for circuit breaker interface
License: Apache 2.0
"""

from typing import Callable, Dict, Any

from circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager


def get_breaker_implementation(name: str, failure_threshold: int = 5, 
                               timeout: int = 60, correlation_id: str = None,
                               **kwargs) -> Dict[str, Any]:
    """
    Get circuit breaker state using SINGLETON manager.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Seconds before attempting recovery
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Circuit breaker state dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "get_breaker_implementation called",
             breaker=name, threshold=failure_threshold, timeout=timeout)
    
    manager = get_circuit_breaker_manager()
    breaker = manager.get(name, failure_threshold, timeout, correlation_id)
    return breaker.get_state()


def execute_with_breaker_implementation(name: str, func: Callable, 
                                       args: tuple = (), 
                                       correlation_id: str = None,
                                       **kwargs) -> Any:
    """
    Execute call with circuit breaker protection using SINGLETON manager.
    
    Args:
        name: Circuit breaker name
        func: Function to execute
        args: Arguments for func
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Function result
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "execute_with_breaker_implementation called",
             breaker=name, func=func.__name__ if hasattr(func, '__name__') else str(func))
    
    manager = get_circuit_breaker_manager()
    return manager.call(name, func, correlation_id, *args, **kwargs)


def get_all_states_implementation(correlation_id: str = None,
                                  **kwargs) -> Dict[str, Dict[str, Any]]:
    """
    Get all circuit breaker states using SINGLETON manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Dict mapping breaker names to their states
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "get_all_states_implementation called")
    
    manager = get_circuit_breaker_manager()
    return manager.get_all_states(correlation_id)


def reset_all_implementation(correlation_id: str = None, **kwargs):
    """
    Reset all circuit breakers using SINGLETON manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "reset_all_implementation called")
    
    manager = get_circuit_breaker_manager()
    manager.reset_all(correlation_id)


def get_stats_implementation(correlation_id: str = None,
                             **kwargs) -> Dict[str, Any]:
    """
    Get circuit breaker statistics using SINGLETON manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Statistics dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "get_stats_implementation called")
    
    manager = get_circuit_breaker_manager()
    return manager.get_stats(correlation_id)


def reset_implementation(correlation_id: str = None,
                        **kwargs) -> Dict[str, Any]:
    """
    Reset circuit breaker manager state using SINGLETON manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success/error response dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id, create_success_response, create_error_response
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "CIRCUIT_BREAKER",
             "reset_implementation called")
    
    manager = get_circuit_breaker_manager()
    success = manager.reset(correlation_id)
    
    if success:
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 "Manager reset successful")
        return create_success_response("Circuit breaker manager reset", {
            'reset': True
        })
    else:
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 "Manager reset failed - rate limited")
        return create_error_response('Reset rate limited', 'RATE_LIMIT_EXCEEDED')


__all__ = [
    'get_breaker_implementation',
    'execute_with_breaker_implementation',
    'get_all_states_implementation',
    'reset_all_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
