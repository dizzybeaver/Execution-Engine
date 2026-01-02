"""
singleton/singleton_manager.py
Version: 2025-12-13_1
Purpose: Singleton instance manager with rate limiting
License: Apache 2.0
"""

import sys
import time
from typing import Any, Dict, Callable, Optional
from collections import deque
from enum import Enum


class SingletonOperation(Enum):
    """Enumeration of all singleton operations."""
    GET = "get"
    SET = "set"
    HAS = "has"
    DELETE = "delete"
    CLEAR = "clear"
    GET_STATS = "get_stats"
    RESET = "reset"
    # Legacy operations
    RESET_ALL = "reset_all"
    EXISTS = "exists"


class SingletonCore:
    """
    Manages singleton instances across the application.
    
    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_singleton_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    
    DISTINCTION FROM CACHE:
    - SINGLETON: Manages object instances (classes, managers, services)
    - CACHE: Manages data values with TTL and LRU eviction
    """
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._creation_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        
        # Rate limiting (1000 ops/sec for infrastructure)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check rate limit (1000 ops/sec)."""
        now = time.time() * 1000
        
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        
        self._rate_limiter.append(now)
        return True
    
    def get(self, name: str, factory_func: Optional[Callable] = None,
            correlation_id: str = None, **kwargs) -> Any:
        """
        Get or create singleton instance.
        
        Args:
            name: Singleton name (must be non-empty string)
            factory_func: Optional factory function to create instance
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Singleton instance or None if not exists and no factory provided
            
        Raises:
            ValueError: If name is empty or rate limited
            Exception: If factory function raises exception
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in get()")
            raise ValueError("Rate limit exceeded (1000 ops/sec)")
        
        if not name or not isinstance(name, str):
            debug_log(correlation_id, "SINGLETON", "Invalid name",
                     name=name, name_type=type(name).__name__)
            raise ValueError("Singleton name must be a non-empty string")
        
        # Check if exists
        if name not in self._instances:
            if factory_func is None:
                debug_log(correlation_id, "SINGLETON", "Instance not found, no factory",
                         name=name)
                return None
            
            # Create instance
            debug_log(correlation_id, "SINGLETON", "Creating new instance",
                     name=name, has_factory=True)
            
            with debug_timing(correlation_id, "SINGLETON", f"factory:{name}"):
                try:
                    instance = factory_func()
                    self._instances[name] = instance
                    self._creation_times[name] = time.time()
                    self._access_counts[name] = 0
                    
                    debug_log(correlation_id, "SINGLETON", "Instance created",
                             name=name, instance_type=type(instance).__name__)
                except Exception as e:
                    debug_log(correlation_id, "SINGLETON", "Factory failed",
                             name=name, error=str(e))
                    raise Exception(f"Failed to create singleton '{name}': {e}") from e
        
        # Update access count and return
        if name in self._instances:
            self._access_counts[name] = self._access_counts.get(name, 0) + 1
            
            debug_log(correlation_id, "SINGLETON", "Instance retrieved",
                     name=name, access_count=self._access_counts[name])
            
            return self._instances[name]
        return None
    
    def set(self, name: str, instance: Any, correlation_id: str = None, **kwargs):
        """
        Set singleton instance.
        
        Args:
            name: Singleton name (must be non-empty string)
            instance: Instance to store
            correlation_id: Optional correlation ID for debug tracking
            
        Raises:
            ValueError: If name is empty or rate limited
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in set()")
            raise ValueError("Rate limit exceeded (1000 ops/sec)")
        
        if not name or not isinstance(name, str):
            debug_log(correlation_id, "SINGLETON", "Invalid name in set()",
                     name=name)
            raise ValueError("Singleton name must be a non-empty string")
        
        debug_log(correlation_id, "SINGLETON", "Setting instance",
                 name=name, instance_type=type(instance).__name__)
        
        self._instances[name] = instance
        self._creation_times[name] = time.time()
        self._access_counts[name] = 0
        
        debug_log(correlation_id, "SINGLETON", "Instance set successfully", name=name)
    
    def has(self, name: str, correlation_id: str = None, **kwargs) -> bool:
        """
        Check if singleton exists.
        
        Args:
            name: Singleton name
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            True if singleton exists, False otherwise
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in has()")
            return False
        
        exists = name in self._instances
        
        debug_log(correlation_id, "SINGLETON", "Existence check",
                 name=name, exists=exists)
        
        return exists
    
    def delete(self, name: str, correlation_id: str = None, **kwargs) -> bool:
        """
        Delete singleton instance.
        
        Args:
            name: Singleton name
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            True if deleted, False if didn't exist or rate limited
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in delete()")
            return False
        
        if name in self._instances:
            debug_log(correlation_id, "SINGLETON", "Deleting instance", name=name)
            
            del self._instances[name]
            self._creation_times.pop(name, None)
            self._access_counts.pop(name, None)
            
            debug_log(correlation_id, "SINGLETON", "Instance deleted", name=name)
            return True
        
        debug_log(correlation_id, "SINGLETON", "Instance not found for deletion", name=name)
        return False
    
    def clear(self, correlation_id: str = None, **kwargs) -> int:
        """
        Clear all singleton instances.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Count of singletons cleared
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in clear()")
            return 0
        
        count = len(self._instances)
        
        debug_log(correlation_id, "SINGLETON", "Clearing all instances", count=count)
        
        self._instances.clear()
        self._creation_times.clear()
        self._access_counts.clear()
        
        debug_log(correlation_id, "SINGLETON", "All instances cleared")
        
        return count
    
    def get_stats(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get statistics about managed singletons.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Dictionary containing singleton statistics
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in get_stats()")
            return {'error': 'Rate limit exceeded'}
        
        total_memory = sum(
            sys.getsizeof(instance) 
            for instance in self._instances.values()
        )
        
        debug_log(correlation_id, "SINGLETON", "Getting statistics",
                 total_singletons=len(self._instances),
                 total_memory_kb=total_memory / 1024)
        
        return {
            'total_singletons': len(self._instances),
            'singleton_names': list(self._instances.keys()),
            'singleton_types': {
                name: type(instance).__name__ 
                for name, instance in self._instances.items()
            },
            'creation_times': dict(self._creation_times),
            'access_counts': dict(self._access_counts),
            'estimated_memory_bytes': total_memory,
            'estimated_memory_kb': total_memory / 1024,
            'estimated_memory_mb': total_memory / (1024 * 1024),
            'memory_note': 'Estimates are shallow size only (sys.getsizeof)',
            'rate_limited_count': self._rate_limited_count,
            'timestamp': time.time()
        }
    
    def reset(self, correlation_id: str = None, **kwargs) -> bool:
        """
        Reset SINGLETON manager state (lifecycle management).
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            True if reset successful, False if rate limited
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SINGLETON", "Rate limit exceeded in reset()")
            return False
        
        try:
            debug_log(correlation_id, "SINGLETON", "Resetting manager state")
            
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            debug_log(correlation_id, "SINGLETON", "Manager reset complete")
            return True
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "Manager reset failed", error=str(e))
            return False
    
    # Legacy methods (backward compatibility)
    
    def reset_all(self, **kwargs) -> int:
        """Legacy name for clear."""
        return self.clear(**kwargs)
    
    def exists(self, name: str, **kwargs) -> bool:
        """Legacy name for has."""
        return self.has(name, **kwargs)


# SINGLETON pattern (LESS-18)
_manager_core = None


def get_singleton_manager() -> SingletonCore:
    """
    Get the singleton manager instance (SINGLETON pattern).
    
    Ironic: SINGLETON interface using SINGLETON pattern for itself!
    
    Returns:
        SingletonCore instance
    """
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('singleton_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = SingletonCore()
            singleton_register('singleton_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        if _manager_core is None:
            _manager_core = SingletonCore()
        return _manager_core


__all__ = [
    'SingletonOperation',
    'SingletonCore',
    'get_singleton_manager',
]
