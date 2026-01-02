"""
initialization/initialization_manager.py
Version: 2025-12-13_1
Purpose: Lambda initialization manager with singleton pattern
License: Apache 2.0
"""

import time
from typing import Dict, Any, Optional
from collections import deque
from enum import Enum


class InitializationOperation(Enum):
    """Enumeration of all initialization operations."""
    INITIALIZE = "initialize"
    GET_CONFIG = "get_config"
    IS_INITIALIZED = "is_initialized"
    RESET = "reset"
    GET_STATUS = "get_status"
    GET_STATS = "get_stats"
    SET_FLAG = "set_flag"
    GET_FLAG = "get_flag"


class InitializationCore:
    """
    Handles Lambda environment initialization with idempotency.
    
    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_initialization_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """
    
    def __init__(self):
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._flags: Dict[str, Any] = {}
        self._init_timestamp: Optional[float] = None
        self._init_duration_ms: Optional[float] = None
        
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
    
    def initialize(self, config: Optional[Dict[str, Any]] = None, 
                   correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Initialize Lambda environment with idempotency.
        
        Idempotency guarantee: Multiple calls are safe. If already initialized,
        returns cached result without re-initializing.
        
        Args:
            config: Optional configuration dictionary
            correlation_id: Optional correlation ID for debug tracking
            **kwargs: Additional configuration items
            
        Returns:
            Dictionary with initialization status
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in initialize()")
            return {'status': 'rate_limited', 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        # Check if already initialized (fast path)
        if self._initialized:
            debug_log(correlation_id, "INIT", 
                     "Already initialized - returning cached result",
                     uptime_seconds=time.time() - self._init_timestamp if self._init_timestamp else 0)
            return {
                'status': 'already_initialized',
                'cached': True,
                'timestamp': self._init_timestamp,
                'init_duration_ms': self._init_duration_ms,
                'uptime_seconds': time.time() - self._init_timestamp if self._init_timestamp else 0,
                'config_keys': list(self._config.keys())
            }
        
        debug_log(correlation_id, "INIT", "Initializing Lambda environment",
                 has_config=config is not None, kwargs_count=len(kwargs))
        
        with debug_timing(correlation_id, "INIT", "initialize"):
            start_time = time.time()
            
            # Merge config and kwargs
            if config is None:
                config = {}
            self._config = {**config, **kwargs}
            
            # Mark as initialized
            self._initialized = True
            self._init_timestamp = start_time
            self._init_duration_ms = (time.time() - start_time) * 1000
            
            debug_log(correlation_id, "INIT", "Initialization complete",
                     config_keys=list(self._config.keys()),
                     duration_ms=self._init_duration_ms)
            
            return {
                'status': 'initialized',
                'cached': False,
                'timestamp': self._init_timestamp,
                'duration_ms': self._init_duration_ms,
                'config_keys': list(self._config.keys())
            }
    
    def get_config(self, correlation_id: str = None) -> Dict[str, Any]:
        """
        Get initialization configuration.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Copy of configuration dictionary
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in get_config()")
            return {}
        
        debug_log(correlation_id, "INIT", "Getting configuration",
                 config_keys=list(self._config.keys()))
        
        return self._config.copy()
    
    def is_initialized(self, correlation_id: str = None) -> bool:
        """
        Check if Lambda environment is initialized.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            True if initialized, False otherwise
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in is_initialized()")
            return False
        
        debug_log(correlation_id, "INIT", "Checking initialization status",
                 initialized=self._initialized)
        
        return self._initialized
    
    def reset(self, correlation_id: str = None) -> Dict[str, Any]:
        """
        Reset initialization state (lifecycle management).
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Dictionary with reset status
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in reset()")
            return {'status': 'rate_limited', 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        was_initialized = self._initialized
        
        debug_log(correlation_id, "INIT", "Resetting initialization state",
                 was_initialized=was_initialized)
        
        self._initialized = False
        self._config.clear()
        self._flags.clear()
        self._init_timestamp = None
        self._init_duration_ms = None
        
        # Reset rate limiter
        self._rate_limiter.clear()
        self._rate_limited_count = 0
        
        debug_log(correlation_id, "INIT", "Reset complete")
        
        return {
            'status': 'reset',
            'was_initialized': was_initialized,
            'timestamp': time.time()
        }
    
    def get_status(self, correlation_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive initialization status.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Dictionary containing complete initialization state
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in get_status()")
            return {'error': 'Rate limit exceeded'}
        
        debug_log(correlation_id, "INIT", "Getting status",
                 initialized=self._initialized, flag_count=len(self._flags))
        
        return {
            'initialized': self._initialized,
            'config': self._config.copy() if self._initialized else {},
            'flags': self._flags.copy(),
            'init_timestamp': self._init_timestamp,
            'init_duration_ms': self._init_duration_ms,
            'uptime_seconds': (time.time() - self._init_timestamp) if self._init_timestamp else None,
            'flag_count': len(self._flags),
            'config_keys': list(self._config.keys()) if self._initialized else [],
            'rate_limited_count': self._rate_limited_count
        }
    
    def get_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get initialization statistics (alias for get_status)."""
        return self.get_status(correlation_id)
    
    def set_flag(self, flag_name: str, value: Any, correlation_id: str = None) -> Dict[str, Any]:
        """
        Set an initialization flag with validation.
        
        Args:
            flag_name: Name of the flag (must be non-empty string)
            value: Value to set
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Dictionary with operation result
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in set_flag()")
            return {'success': False, 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        if not flag_name or not isinstance(flag_name, str):
            debug_log(correlation_id, "INIT", "Invalid flag name",
                     flag_name=flag_name, flag_name_type=type(flag_name).__name__)
            return {
                'success': False,
                'error': 'Flag name must be a non-empty string',
                'flag_name': flag_name
            }
        
        old_value = self._flags.get(flag_name)
        was_new = flag_name not in self._flags
        self._flags[flag_name] = value
        
        debug_log(correlation_id, "INIT", "Flag set",
                 flag_name=flag_name, value=value, was_new=was_new)
        
        return {
            'success': True,
            'flag_name': flag_name,
            'value': value,
            'old_value': old_value,
            'was_new': was_new
        }
    
    def get_flag(self, flag_name: str, default: Any = None, 
                 correlation_id: str = None) -> Any:
        """
        Get an initialization flag value with validation.
        
        Args:
            flag_name: Name of the flag
            default: Default value if flag doesn't exist
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Flag value or default
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "INIT", "Rate limit exceeded in get_flag()")
            return default
        
        if not flag_name or not isinstance(flag_name, str):
            debug_log(correlation_id, "INIT", "Invalid flag name in get_flag()",
                     flag_name=flag_name)
            return default
        
        value = self._flags.get(flag_name, default)
        
        debug_log(correlation_id, "INIT", "Flag retrieved",
                 flag_name=flag_name, has_value=flag_name in self._flags)
        
        return value


# SINGLETON pattern (LESS-18)
_manager_core = None


def get_initialization_manager() -> InitializationCore:
    """
    Get the initialization manager instance (SINGLETON pattern).
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        InitializationCore instance
    """
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('initialization_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = InitializationCore()
            singleton_register('initialization_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        if _manager_core is None:
            _manager_core = InitializationCore()
        return _manager_core


__all__ = [
    'InitializationOperation',
    'InitializationCore',
    'get_initialization_manager',
]
