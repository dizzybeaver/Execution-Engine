"""
circuit_breaker/circuit_breaker_manager.py
Version: 2025-12-13_1
Purpose: Circuit breaker manager with singleton pattern
License: Apache 2.0
"""

import time
from typing import Callable, Dict, Any
from collections import deque

from circuit_breaker.circuit_breaker_state import CircuitBreaker


class CircuitBreakerCore:
    """
    Manages circuit breakers with SINGLETON pattern and rate limiting.
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_circuit_breaker_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        
        # Rate limiting (1000 ops/sec - higher for infrastructure)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
        
        # Statistics
        self._total_operations = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check if operation is within rate limit.
        
        Returns:
            bool: True if allowed, False if rate limited
        """
        now = time.time() * 1000
        
        # Remove expired timestamps
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        
        self._rate_limiter.append(now)
        return True
    
    def get(self, name: str, failure_threshold: int = 5, 
            timeout: int = 60, correlation_id: str = None) -> CircuitBreaker:
        """Get or create circuit breaker."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in get()", operation="get", breaker=name)
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        
        if name not in self._breakers:
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     f"Creating new circuit breaker",
                     breaker=name, threshold=failure_threshold, timeout=timeout)
            self._breakers[name] = CircuitBreaker(name, failure_threshold, timeout)
        
        return self._breakers[name]
    
    def call(self, name: str, func: Callable, correlation_id: str = None,
             *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in call()", operation="call", breaker=name)
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Executing protected call", breaker=name)
        
        with debug_timing(correlation_id, "CIRCUIT_BREAKER", f"manager.call:{name}"):
            breaker = self.get(name, correlation_id=correlation_id)
            return breaker.call(func, self._check_rate_limit, correlation_id, *args, **kwargs)
    
    def get_all_states(self, correlation_id: str = None) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in get_all_states()")
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Getting all states", breaker_count=len(self._breakers))
        
        return {
            name: breaker.get_state()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self, correlation_id: str = None):
        """Reset all circuit breakers."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in reset_all()")
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Resetting all circuit breakers", count=len(self._breakers))
        
        for breaker in self._breakers.values():
            breaker.reset()
    
    def get_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get circuit breaker manager statistics."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id, create_success_response, create_error_response
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in get_stats()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Getting statistics",
                 operations=self._total_operations, breakers=len(self._breakers))
        
        return create_success_response("Circuit breaker statistics", {
            'total_operations': self._total_operations,
            'breakers_count': len(self._breakers),
            'rate_limited_count': self._rate_limited_count,
            'rate_limit_window_ms': self._rate_limit_window_ms,
            'current_rate_limit_size': len(self._rate_limiter),
            'max_rate_limit': self._rate_limiter.maxlen,
            'breakers': {
                name: breaker.get_state()
                for name, breaker in self._breakers.items()
            }
        })
    
    def reset(self, correlation_id: str = None) -> bool:
        """
        Reset circuit breaker manager state.
        
        Returns:
            bool: True if reset successful, False if rate limited
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Rate limit exceeded in reset()")
            return False
        
        try:
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     "Resetting manager state",
                     breakers=len(self._breakers), operations=self._total_operations)
            
            self._breakers.clear()
            self._total_operations = 0
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            debug_log(correlation_id, "CIRCUIT_BREAKER", "Manager reset complete")
            return True
        except Exception as e:
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     f"Manager reset failed", error=str(e))
            return False


# SINGLETON pattern (LESS-18)
_circuit_breaker_core = None


def get_circuit_breaker_manager() -> CircuitBreakerCore:
    """
    Get SINGLETON circuit breaker manager instance.
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        CircuitBreakerCore: The singleton manager instance
    """
    global _circuit_breaker_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('circuit_breaker_manager')
        if manager is None:
            if _circuit_breaker_core is None:
                _circuit_breaker_core = CircuitBreakerCore()
            singleton_register('circuit_breaker_manager', _circuit_breaker_core)
            manager = _circuit_breaker_core
        
        return manager
        
    except (ImportError, Exception):
        if _circuit_breaker_core is None:
            _circuit_breaker_core = CircuitBreakerCore()
        return _circuit_breaker_core


__all__ = ['CircuitBreakerCore', 'get_circuit_breaker_manager']
