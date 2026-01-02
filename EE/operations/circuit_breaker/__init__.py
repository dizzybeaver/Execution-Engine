"""
Circuit Breaker Interface - Operations Domain

Fault tolerance and circuit breaker pattern.
"""

from EE.operations.circuit_breaker.circuit_breaker_interface import execute_circuit_breaker_operation
from EE.operations.circuit_breaker.circuit_breaker_factory import CircuitBreakerFactory, CircuitState

__all__ = [
    'execute_circuit_breaker_operation',
    'CircuitBreakerFactory',
    'CircuitState',
]
