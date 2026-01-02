"""
gateway_wrappers_circuit_breaker.py - CIRCUIT_BREAKER Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for CIRCUIT_BREAKER interface operations

CHANGELOG:
- 2025.10.22.02: Added get_stats and reset wrapper functions

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


def is_circuit_breaker_open(name: str) -> bool:
    """Check if circuit breaker is open."""
    state = execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)
    return state.get('state') == 'open'


def get_circuit_breaker_state(name: str) -> Dict[str, Any]:
    """Get circuit breaker state."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)


def get_circuit_breaker(name: str, failure_threshold: int = 5, timeout: float = 60.0) -> Any:
    """Get circuit breaker."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name, failure_threshold=failure_threshold, timeout=timeout)


def execute_with_circuit_breaker(name: str, func: Any, args: tuple = (), **kwargs) -> Any:
    """Execute function with circuit breaker protection."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', name=name, func=func, args=args, **kwargs)


def get_all_circuit_breaker_states() -> Dict[str, Dict[str, Any]]:
    """Get all circuit breaker states."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_all_states')


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers."""
    execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset_all')


def get_circuit_breaker_stats() -> Dict[str, Any]:
    """Get circuit breaker manager statistics."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_stats')


def reset_circuit_breaker_manager() -> Dict[str, Any]:
    """Reset circuit breaker manager state."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset')


__all__ = [
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    'get_circuit_breaker_stats',
    'reset_circuit_breaker_manager',
]
