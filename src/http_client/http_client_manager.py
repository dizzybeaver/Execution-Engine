"""
http_client/http_client_manager.py
Version: 2025-12-10_1
Purpose: HTTP client core manager with singleton pattern
License: Apache 2.0
"""

import os
import json
import time
from typing import Dict, Any, Optional
from collections import deque

# Import preloaded urllib3 classes
from lambda_preload import PoolManager, Timeout

from http_client.http_client_utilities import get_standard_headers


class HTTPClientCore:
    """Core HTTP client with retry, circuit breaker, rate limiting."""
    
    def __init__(self):
        # Read SSL verification setting
        verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
        verify_ssl = verify_ssl_env != 'false'
        cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
        
        # Use preloaded classes
        self.http = PoolManager(
            cert_reqs=cert_reqs,
            timeout=Timeout(connect=10.0, read=30.0),
            maxsize=10,
            retries=False
        )
        
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        
        self._retry_config = {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2.0,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504}
        }
        
        # Rate limiting (500 ops/sec)
        self._rate_limiter = deque(maxlen=500)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if operation within rate limits."""
        now = time.time() * 1000
        
        # Remove old timestamps
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check limit
        if len(self._rate_limiter) >= 500:
            self._rate_limited_count += 1
            return False
        
        self._rate_limiter.append(now)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        stats = self._stats.copy()
        stats['rate_limited'] = self._rate_limited_count
        stats['rate_limiter_size'] = len(self._rate_limiter)
        return stats
    
    def reset(self) -> bool:
        """Reset HTTP client state."""
        if not self._check_rate_limit():
            return False
        
        try:
            # Close existing pool
            if hasattr(self, 'http') and self.http:
                self.http.clear()
            
            # Reset statistics
            self._stats = {
                'requests': 0,
                'successful': 0,
                'failed': 0,
                'retries': 0
            }
            
            # Reset rate limiter
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            # Recreate pool
            verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
            verify_ssl = verify_ssl_env != 'false'
            cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
            
            self.http = PoolManager(
                cert_reqs=cert_reqs,
                timeout=Timeout(connect=10.0, read=30.0),
                maxsize=10,
                retries=False
            )
            
            return True
            
        except Exception as e:
            from gateway import log_error
            log_error(f"HTTP client reset failed: {str(e)}", error=e)
            return False
    
    def _is_retriable_error(self, status_code: int) -> bool:
        """Check if error is retriable."""
        return status_code in self._retry_config['retriable_status_codes']
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_ms = self._retry_config['backoff_base_ms']
        multiplier = self._retry_config['backoff_multiplier']
        delay_ms = base_ms * (multiplier ** attempt)
        return delay_ms / 1000.0
    
    def _execute_request(self, method: str, url: str, correlation_id: str = None, 
                        **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request."""
        import gateway
        
        # Rate limit check
        if not self._check_rate_limit():
            gateway.debug_log(correlation_id or 'none', 'HTTP', 'Rate limit exceeded')
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'error_type': 'RateLimitError',
                'rate_limited': True
            }
        
        try:
            self._stats['requests'] += 1
            
            # Debug logging
            gateway.debug_log(correlation_id or 'none', 'HTTP', f'Request start',
                            method=method, url=url[:50])
            
            # Get headers
            headers = kwargs.get('headers', {})
            if not headers:
                headers = get_standard_headers()
            
            # Handle JSON body encoding
            body = None
            if kwargs.get('json'):
                json_data = kwargs.get('json')
                body = json.dumps(json_data).encode('utf-8')
                headers.setdefault('Content-Type', 'application/json')
            elif kwargs.get('body'):
                body = kwargs.get('body')
                if isinstance(body, str):
                    body = body.encode('utf-8')
            
            # Execute with timing
            with gateway.debug_timing(correlation_id or 'none', 'HTTP', f'{method} {url[:30]}'):
                response = self.http.request(
                    method,
                    url,
                    headers=headers,
                    body=body,
                    timeout=kwargs.get('timeout')
                )
            
            # Parse response
            status_code = response.status
            success = 200 <= status_code < 300
            
            response_data = None
            try:
                response_body = response.data.decode('utf-8')
                if response_body:
                    response_data = json.loads(response_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = response.data
            
            if success:
                self._stats['successful'] += 1
                gateway.debug_log(correlation_id or 'none', 'HTTP', 'Request success',
                                status=status_code)
            else:
                self._stats['failed'] += 1
                gateway.debug_log(correlation_id or 'none', 'HTTP', 'Request failed',
                                status=status_code)
            
            return {
                'success': success,
                'status_code': status_code,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            gateway.log_error(f"HTTP request failed: {str(e)}", error=e)
            gateway.debug_log(correlation_id or 'none', 'HTTP', 'Request exception',
                            error=str(e))
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def make_request(self, method: str, url: str, correlation_id: str = None,
                    **kwargs) -> Dict[str, Any]:
        """Execute HTTP request with retry logic."""
        max_attempts = self._retry_config['max_attempts']
        
        for attempt in range(max_attempts):
            result = self._execute_request(method, url, correlation_id, **kwargs)
            
            # Don't retry rate limit errors
            if result.get('rate_limited'):
                return result
            
            if result.get('success'):
                return result
            
            status_code = result.get('status_code', 0)
            if attempt < max_attempts - 1 and self._is_retriable_error(status_code):
                self._stats['retries'] += 1
                backoff = self._calculate_backoff(attempt)
                time.sleep(backoff)
                continue
            
            return result
        
        return {
            'success': False,
            'error': 'Max retry attempts exceeded',
            'attempts': max_attempts
        }


# SINGLETON pattern
_http_client_core = None


def get_http_client_manager() -> HTTPClientCore:
    """Get HTTP client manager singleton."""
    global _http_client_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('http_client_manager')
        if manager is None:
            if _http_client_core is None:
                _http_client_core = HTTPClientCore()
            singleton_register('http_client_manager', _http_client_core)
            manager = _http_client_core
        
        return manager
        
    except (ImportError, Exception):
        if _http_client_core is None:
            _http_client_core = HTTPClientCore()
        return _http_client_core


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client (legacy compatibility)."""
    return get_http_client_manager()


__all__ = [
    'HTTPClientCore',
    'get_http_client_manager',
    'get_http_client',
]
