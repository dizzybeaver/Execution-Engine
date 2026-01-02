"""
security/security_manager.py
Version: 2025-12-13_1
Purpose: Security core manager with validators and rate limiting
License: Apache 2.0
"""

import time
import re
import math
from typing import Dict, Any
from collections import deque

from security.security_types import SecurityOperation
from security.security_validation import SecurityValidator
from security.security_crypto import SecurityCrypto


class CacheKeyValidator:
    """Comprehensive cache key validation (fixes CVE-SUGA-2025-001)."""
    
    SAFE_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_\-:.]+$')
    PATH_TRAVERSAL_PATTERNS = ['../', './', '..\\', '.\\', '/../', '/..']
    CONTROL_CHARS = set(chr(i) for i in range(0x00, 0x20)) | {chr(0x7F)}
    MIN_LENGTH = 1
    MAX_LENGTH = 255
    
    @classmethod
    def validate(cls, key: str) -> tuple:
        """Validate cache key for security. Returns (is_valid, error_message)."""
        if not isinstance(key, str):
            return False, f"Cache key must be string, got {type(key).__name__}"
        if len(key) < cls.MIN_LENGTH:
            return False, "Cache key cannot be empty"
        if len(key) > cls.MAX_LENGTH:
            return False, f"Cache key too long (max {cls.MAX_LENGTH} chars)"
        for char in key:
            if char in cls.CONTROL_CHARS:
                return False, f"Cache key contains control character: {repr(char)}"
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if pattern in key:
                return False, f"Cache key contains path traversal pattern: {pattern}"
        if not cls.SAFE_KEY_PATTERN.match(key):
            return False, "Cache key contains invalid characters (allowed: a-zA-Z0-9_-:.)"
        return True, None


class TTLValidator:
    """TTL validation with boundary protection (fixes CVE-SUGA-2025-002)."""
    
    MIN_TTL = 1
    MAX_TTL = 86400
    
    @classmethod
    def validate(cls, ttl: float) -> tuple:
        """Validate TTL value with boundary protection. Returns (is_valid, error_message)."""
        if not isinstance(ttl, (int, float)):
            return False, f"TTL must be numeric, got {type(ttl).__name__}"
        if math.isnan(ttl):
            return False, "TTL cannot be NaN"
        if math.isinf(ttl):
            return False, "TTL cannot be infinity"
        if ttl < cls.MIN_TTL:
            return False, f"TTL too small (min {cls.MIN_TTL} seconds)"
        if ttl > cls.MAX_TTL:
            return False, f"TTL too large (max {cls.MAX_TTL} seconds / 24 hours)"
        return True, None


class ModuleNameValidator:
    """Module name validation for LUGS (fixes CVE-SUGA-2025-004)."""
    
    MODULE_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$')
    MAX_LENGTH = 100
    
    @classmethod
    def validate(cls, module_name: str) -> tuple:
        """Validate module name for LUGS tracking. Returns (is_valid, error_message)."""
        if not isinstance(module_name, str):
            return False, f"Module name must be string, got {type(module_name).__name__}"
        if not module_name:
            return False, "Module name cannot be empty"
        if len(module_name) > cls.MAX_LENGTH:
            return False, f"Module name too long (max {cls.MAX_LENGTH} chars)"
        if '/' in module_name or '\\' in module_name:
            return False, "Module name cannot contain path separators"
        for char in module_name:
            if char in CacheKeyValidator.CONTROL_CHARS:
                return False, f"Module name contains control character: {repr(char)}"
        if not cls.MODULE_PATTERN.match(module_name):
            return False, "Module name must be valid Python identifier (letters, digits, underscores, dots)"
        return True, None


class NumberRangeValidator:
    """Generic number range validation."""
    
    @classmethod
    def validate(cls, value: float, min_val: float, max_val: float, name: str = 'value') -> tuple:
        """Validate number is within specified range. Returns (is_valid, error_message)."""
        if not isinstance(value, (int, float)):
            return False, f"{name} must be numeric, got {type(value).__name__}"
        if math.isnan(value):
            return False, f"{name} cannot be NaN"
        if math.isinf(value):
            return False, f"{name} cannot be infinity"
        if value < min_val:
            return False, f"{name} below minimum (min: {min_val}, got: {value})"
        if value > max_val:
            return False, f"{name} above maximum (max: {max_val}, got: {value})"
        return True, None


class SecurityCore:
    """
    Core security manager orchestrating validation and crypto operations.
    
    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_security_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """
    
    def __init__(self):
        self._validator = SecurityValidator()
        self._crypto = SecurityCrypto()
        
        # Rate limiting (1000 ops/sec)
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
    
    def reset(self, correlation_id: str = None) -> bool:
        """
        Reset security core state.
        
        Args:
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            bool: True on success
        """
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        debug_log(correlation_id, "SECURITY", "Resetting security core state")
        
        self._rate_limiter.clear()
        self._rate_limited_count = 0
        
        debug_log(correlation_id, "SECURITY", "Security core reset complete")
        
        return True
    
    def execute_security_operation(self, operation: SecurityOperation, correlation_id: str = None,
                                   *args, **kwargs) -> Any:
        """
        Generic security operation executor with rate limiting.
        
        Args:
            operation: Security operation to execute
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Operation result
            
        Raises:
            RuntimeError: If rate limited
            ValueError: If operation unknown or parameters invalid
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "SECURITY", "Rate limit exceeded",
                     rate_limited_count=self._rate_limited_count)
            raise RuntimeError(
                f"Rate limit exceeded: 1000 operations per second. "
                f"Total rate limited: {self._rate_limited_count}"
            )
        
        debug_log(correlation_id, "SECURITY", "Executing security operation",
                 operation=operation.value)
        
        with debug_timing(correlation_id, "SECURITY", f"op:{operation.value}"):
            result = self._execute_operation_logic(operation, correlation_id, *args, **kwargs)
            
            # Record metrics
            try:
                from gateway import execute_operation, GatewayInterface
                execute_operation(
                    GatewayInterface.METRICS,
                    'record_dispatcher_timing',
                    interface_name='SecurityCore',
                    operation_name=operation.value,
                    correlation_id=correlation_id
                )
            except Exception:
                pass
            
            return result
    
    def _execute_operation_logic(self, operation: SecurityOperation, correlation_id: str,
                                *args, **kwargs) -> Any:
        """Execute the actual operation logic."""
        # VALIDATE_REQUEST
        if operation == SecurityOperation.VALIDATE_REQUEST:
            request = args[0] if args else kwargs.get('request')
            if request is None:
                raise ValueError("validate_request requires 'request' parameter")
            return self._validator.validate_request(request)
        
        # VALIDATE_TOKEN
        elif operation == SecurityOperation.VALIDATE_TOKEN:
            token = args[0] if args else kwargs.get('token')
            if token is None:
                raise ValueError("validate_token requires 'token' parameter")
            return self._validator.validate_token(token)
        
        # VALIDATE_STRING
        elif operation == SecurityOperation.VALIDATE_STRING:
            value = args[0] if args else kwargs.get('value')
            if value is None:
                raise ValueError("validate_string requires 'value' parameter")
            min_length = args[1] if len(args) > 1 else kwargs.get('min_length', 0)
            max_length = args[2] if len(args) > 2 else kwargs.get('max_length', 1000)
            return self._validator.validate_string(value, min_length, max_length)
        
        # VALIDATE_EMAIL
        elif operation == SecurityOperation.VALIDATE_EMAIL:
            email = args[0] if args else kwargs.get('email')
            if email is None:
                raise ValueError("validate_email requires 'email' parameter")
            return self._validator.validate_email(email)
        
        # VALIDATE_URL
        elif operation == SecurityOperation.VALIDATE_URL:
            url = args[0] if args else kwargs.get('url')
            if url is None:
                raise ValueError("validate_url requires 'url' parameter")
            return self._validator.validate_url(url)
        
        # ENCRYPT
        elif operation == SecurityOperation.ENCRYPT:
            data = args[0] if args else kwargs.get('data')
            if data is None:
                raise ValueError("encrypt requires 'data' parameter")
            if not isinstance(data, str):
                raise TypeError(f"encrypt requires string data, got {type(data).__name__}")
            key = args[1] if len(args) > 1 else kwargs.get('key')
            if key is None:
                key = self._crypto.get_default_key()
            return self._crypto.encrypt_data(data, key)
        
        # DECRYPT
        elif operation == SecurityOperation.DECRYPT:
            data = args[0] if args else kwargs.get('data')
            if data is None:
                raise ValueError("decrypt requires 'data' parameter")
            if not isinstance(data, str):
                raise TypeError(f"decrypt requires string data, got {type(data).__name__}")
            key = args[1] if len(args) > 1 else kwargs.get('key')
            if key is None:
                key = self._crypto.get_default_key()
            return self._crypto.decrypt_data(data, key)
        
        # HASH
        elif operation == SecurityOperation.HASH:
            data = args[0] if args else kwargs.get('data')
            if data is None:
                raise ValueError("hash requires 'data' parameter")
            if not isinstance(data, str):
                raise TypeError(f"hash requires string data, got {type(data).__name__}")
            return self._crypto.hash_data(data)
        
        # VERIFY_HASH
        elif operation == SecurityOperation.VERIFY_HASH:
            data = args[0] if args else kwargs.get('data')
            hash_value = args[1] if len(args) > 1 else kwargs.get('hash_value')
            if data is None:
                raise ValueError("verify_hash requires 'data' parameter")
            if hash_value is None:
                raise ValueError("verify_hash requires 'hash_value' parameter")
            if not isinstance(data, str):
                raise TypeError(f"verify_hash requires string data, got {type(data).__name__}")
            return self._crypto.verify_hash(data, hash_value)
        
        # SANITIZE
        elif operation == SecurityOperation.SANITIZE:
            data = args[0] if args else kwargs.get('data')
            if data is None:
                return ""
            return self._validator.sanitize_input(data)
        
        # GENERATE_CORRELATION_ID
        elif operation == SecurityOperation.GENERATE_CORRELATION_ID:
            return self._crypto.generate_correlation_id()
        
        # VALIDATE_CACHE_KEY
        elif operation == SecurityOperation.VALIDATE_CACHE_KEY:
            key = args[0] if args else kwargs.get('key')
            if key is None:
                raise ValueError("validate_cache_key requires 'key' parameter")
            is_valid, error = CacheKeyValidator.validate(key)
            if not is_valid:
                raise ValueError(f"Invalid cache key: {error}")
            return True
        
        # VALIDATE_TTL
        elif operation == SecurityOperation.VALIDATE_TTL:
            ttl = args[0] if args else kwargs.get('ttl')
            if ttl is None:
                raise ValueError("validate_ttl requires 'ttl' parameter")
            is_valid, error = TTLValidator.validate(ttl)
            if not is_valid:
                raise ValueError(f"Invalid TTL: {error}")
            return True
        
        # VALIDATE_MODULE_NAME
        elif operation == SecurityOperation.VALIDATE_MODULE_NAME:
            module_name = args[0] if args else kwargs.get('module_name')
            if module_name is None:
                raise ValueError("validate_module_name requires 'module_name' parameter")
            is_valid, error = ModuleNameValidator.validate(module_name)
            if not is_valid:
                raise ValueError(f"Invalid module name: {error}")
            return True
        
        # VALIDATE_NUMBER_RANGE
        elif operation == SecurityOperation.VALIDATE_NUMBER_RANGE:
            value = args[0] if args else kwargs.get('value')
            min_val = args[1] if len(args) > 1 else kwargs.get('min_val')
            max_val = args[2] if len(args) > 2 else kwargs.get('max_val')
            name = kwargs.get('name', 'value')
            if value is None:
                raise ValueError("validate_number_range requires 'value' parameter")
            if min_val is None:
                raise ValueError("validate_number_range requires 'min_val' parameter")
            if max_val is None:
                raise ValueError("validate_number_range requires 'max_val' parameter")
            is_valid, error = NumberRangeValidator.validate(value, min_val, max_val, name)
            if not is_valid:
                raise ValueError(f"Invalid {name}: {error}")
            return True
        
        # UNKNOWN OPERATION
        else:
            raise ValueError(f"Unknown security operation: {operation}")
    
    def get_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get combined security statistics with rate limiting metrics."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        debug_log(correlation_id, "SECURITY", "Getting statistics")
        
        validator_stats = self._validator.get_stats()
        crypto_stats = self._crypto.get_stats()
        
        rate_limit_stats = {
            'current_operations': len(self._rate_limiter),
            'rate_limit': 1000,
            'rate_limited_count': self._rate_limited_count,
            'window_ms': self._rate_limit_window_ms
        }
        
        prefixed_stats = {}
        for key, value in validator_stats.items():
            prefixed_stats[f'validator_{key}'] = value
        for key, value in crypto_stats.items():
            prefixed_stats[f'crypto_{key}'] = value
        prefixed_stats['rate_limit'] = rate_limit_stats
        
        return prefixed_stats
    
    def get_validator(self) -> SecurityValidator:
        """Public accessor for validator."""
        return self._validator
    
    def get_crypto(self) -> SecurityCrypto:
        """Public accessor for crypto."""
        return self._crypto


# SINGLETON pattern (LESS-18)
_MANAGER = None


def get_security_manager() -> SecurityCore:
    """
    Get security manager singleton.
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        SecurityCore instance
    """
    global _MANAGER
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('security_manager')
        if manager is None:
            if _MANAGER is None:
                _MANAGER = SecurityCore()
            singleton_register('security_manager', _MANAGER)
            manager = _MANAGER
        
        return manager
        
    except (ImportError, Exception):
        if _MANAGER is None:
            _MANAGER = SecurityCore()
        return _MANAGER


__all__ = [
    'CacheKeyValidator',
    'TTLValidator',
    'ModuleNameValidator',
    'NumberRangeValidator',
    'SecurityCore',
    'get_security_manager',
]
