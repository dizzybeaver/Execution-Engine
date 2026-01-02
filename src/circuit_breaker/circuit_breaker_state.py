"""
circuit_breaker/circuit_breaker_state.py
Version: 2025-12-13_1
Purpose: Circuit breaker state and individual breaker implementation
License: Apache 2.0
"""

import time
from typing import Callable, Dict, Any
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Single circuit breaker instance.
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-21: Rate limiting for DoS protection
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        
        # Statistics
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._rejected_calls = 0
    
    def call(self, func: Callable, rate_limit_check: Callable, 
             correlation_id: str, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            rate_limit_check: Callable that returns True if within rate limit
            correlation_id: Correlation ID for debug tracking
            *args, **kwargs: Arguments for func
        
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing
        
        # Rate limit check
        if not rate_limit_check():
            debug_log(correlation_id, "CIRCUIT_BREAKER", 
                     f"Rate limit exceeded", breaker=self.name)
            raise Exception(f"Circuit breaker '{self.name}': Rate limit exceeded")
        
        self._total_calls += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                debug_log(correlation_id, "CIRCUIT_BREAKER",
                         f"Transitioning to HALF_OPEN", breaker=self.name)
                self.state = CircuitState.HALF_OPEN
            else:
                self._rejected_calls += 1
                debug_log(correlation_id, "CIRCUIT_BREAKER",
                         f"Circuit OPEN - rejecting call", 
                         breaker=self.name, failures=self.failures)
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Executing protected call",
                 breaker=self.name, state=self.state.value)
        
        # Execute with timing
        with debug_timing(correlation_id, "CIRCUIT_BREAKER", f"call:{self.name}"):
            try:
                # Import from gateway for cross-interface utilities
                from gateway import execute_operation, GatewayInterface
                
                result = func(*args, **kwargs)
                
                # Record success metrics
                try:
                    execute_operation(
                        GatewayInterface.METRICS,
                        'record_metric',
                        name='circuit_breaker_call_success',
                        value=1,
                        tags={
                            'breaker': self.name,
                            'correlation_id': correlation_id
                        }
                    )
                except Exception:
                    pass
                
                self._on_success(correlation_id)
                return result
                
            except ImportError:
                # Fallback without gateway
                try:
                    result = func(*args, **kwargs)
                    self._on_success(correlation_id)
                    return result
                except Exception as e:
                    self._on_failure(correlation_id, e)
                    raise
            
            except Exception as e:
                # Record failure metrics
                try:
                    from gateway import execute_operation, GatewayInterface, log_error
                    
                    execute_operation(
                        GatewayInterface.METRICS,
                        'record_metric',
                        name='circuit_breaker_call_failure',
                        value=1,
                        tags={
                            'breaker': self.name,
                            'correlation_id': correlation_id
                        }
                    )
                    
                    log_error(f"Circuit breaker call failed: {str(e)}",
                             extra={'correlation_id': correlation_id, 'breaker': self.name})
                except Exception:
                    pass
                
                self._on_failure(correlation_id, e)
                raise
    
    def _on_success(self, correlation_id: str):
        """Handle successful call."""
        from gateway import debug_log
        
        self._successful_calls += 1
        self.failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     f"Success in HALF_OPEN - closing circuit", breaker=self.name)
            self.state = CircuitState.CLOSED
    
    def _on_failure(self, correlation_id: str, error: Exception):
        """Handle failed call."""
        from gateway import debug_log
        
        self._failed_calls += 1
        self.failures += 1
        self.last_failure_time = time.time()
        
        debug_log(correlation_id, "CIRCUIT_BREAKER",
                 f"Call failed - failures: {self.failures}/{self.failure_threshold}",
                 breaker=self.name, error=str(error))
        
        if self.failures >= self.failure_threshold:
            debug_log(correlation_id, "CIRCUIT_BREAKER",
                     f"Threshold exceeded - opening circuit", breaker=self.name)
            self.state = CircuitState.OPEN
    
    def reset(self):
        """Reset circuit breaker state."""
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failures': self.failures,
            'threshold': self.failure_threshold,
            'timeout': self.timeout,
            'last_failure': self.last_failure_time,
            'statistics': {
                'total_calls': self._total_calls,
                'successful_calls': self._successful_calls,
                'failed_calls': self._failed_calls,
                'rejected_calls': self._rejected_calls
            }
        }


__all__ = ['CircuitState', 'CircuitBreaker']
