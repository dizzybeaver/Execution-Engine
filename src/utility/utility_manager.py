"""
utility/utility_manager.py
Version: 2025-12-13_1
Purpose: Core utility manager with rate limiting and metrics
License: Apache 2.0
"""

import json
import time
import uuid
import traceback
import os
from typing import Dict, Any, Optional, List
from collections import deque
import logging as stdlib_logging

from utility.utility_types import UtilityMetrics, DEFAULT_MAX_JSON_CACHE_SIZE

logger = stdlib_logging.getLogger(__name__)


class SharedUtilityCore:
    """
    Core utility manager with data operations, validation, and performance tracking.
    
    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_utility_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """
    
    def __init__(self):
        self._metrics = {}
        self._cache_enabled = True
        self._cache_ttl = 300
        self._id_pool = []
        self._json_cache = {}
        self._json_cache_order = []
        self._stats = {
            'template_hits': 0,
            'template_fallbacks': 0,
            'cache_optimizations': 0,
            'id_pool_reuse': 0,
            'lugs_integrations': 0,
            'templates_rendered': 0,
            'configs_retrieved': 0
        }
        
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
    
    # === TRACKING ===
    
    def _start_operation_tracking(self, operation_type: str):
        """Start tracking an operation."""
        if not self._check_rate_limit():
            return
        
        if operation_type not in self._metrics:
            self._metrics[operation_type] = UtilityMetrics(operation_type=operation_type)
    
    def _complete_operation_tracking(self, operation_type: str, 
                                    duration_ms: float, success: bool = True,
                                    cache_hit: bool = False, used_template: bool = False):
        """Complete tracking for an operation."""
        if not self._check_rate_limit():
            return
        
        metrics = self._metrics.get(operation_type)
        if not metrics:
            return
        
        metrics.call_count += 1
        
        if success:
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
        else:
            metrics.error_count += 1
        
        if cache_hit:
            metrics.cache_hits += 1
        elif operation_type in ['parse_json', 'parse_json_safely']:
            metrics.cache_misses += 1
        
        if used_template:
            metrics.template_usage += 1
            self._stats['template_hits'] += 1
    
    # === UUID AND TIMESTAMP ===
    
    def generate_uuid(self, correlation_id: str = None) -> str:
        """Generate UUID with pool optimization."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in generate_uuid()")
            return str(uuid.uuid4())
        
        if self._id_pool:
            self._stats['id_pool_reuse'] += 1
            uuid_val = self._id_pool.pop()
            debug_log(correlation_id, "UTILITY", "UUID from pool", pool_size=len(self._id_pool))
            return uuid_val
        
        uuid_val = str(uuid.uuid4())
        debug_log(correlation_id, "UTILITY", "UUID generated", new_uuid=True)
        return uuid_val
    
    def get_timestamp(self, correlation_id: str = None) -> str:
        """Get current timestamp as ISO string."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        debug_log(correlation_id, "UTILITY", "Timestamp generated", timestamp=timestamp)
        return timestamp
    
    def generate_correlation_id_impl(self, prefix: Optional[str] = None, 
                                     correlation_id: str = None) -> str:
        """Generate correlation ID with optional prefix."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        base_id = self.generate_uuid(correlation_id)
        if prefix:
            result = f"{prefix}_{base_id}"
            debug_log(correlation_id, "UTILITY", "Correlation ID with prefix", 
                     prefix=prefix, result_length=len(result))
            return result
        
        debug_log(correlation_id, "UTILITY", "Correlation ID generated", 
                 result_length=len(base_id))
        return base_id
    
    # === TEMPLATE RENDERING ===
    
    def render_template_impl(self, template: dict, data: dict, 
                            correlation_id: str = None, **kwargs) -> dict:
        """Render template with {placeholder} substitution."""
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in render_template_impl()")
            return template
        
        debug_log(correlation_id, "UTILITY", "Rendering template",
                 placeholder_count=len(data))
        
        with debug_timing(correlation_id, "UTILITY", "render_template"):
            try:
                if 'message_id' not in data:
                    data['message_id'] = self.generate_correlation_id_impl(correlation_id=correlation_id)
                
                template_str = json.dumps(template)
                
                for key, value in data.items():
                    placeholder = f'{{{key}}}'
                    
                    if isinstance(value, (list, dict)):
                        value_str = json.dumps(value)
                    elif value is None:
                        value_str = ''
                    else:
                        value_str = str(value)
                    
                    template_str = template_str.replace(placeholder, value_str)
                
                result = json.loads(template_str)
                
                self._stats['templates_rendered'] += 1
                debug_log(correlation_id, "UTILITY", "Template rendered successfully")
                
                return result
                
            except Exception as e:
                debug_log(correlation_id, "UTILITY", "Template rendering failed",
                         error=str(e))
                logger.error(f"Template rendering failed: {e}")
                return template
    
    # === CONFIG RETRIEVAL ===
    
    def config_get_impl(self, key: str, default=None, 
                       correlation_id: str = None, **kwargs) -> Any:
        """Get typed configuration value from environment."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in config_get_impl()")
            return default
        
        value = os.getenv(key)
        
        if value is None:
            debug_log(correlation_id, "UTILITY", "Config not found, using default",
                     key=key, has_default=default is not None)
            return default
        
        if default is None:
            self._stats['configs_retrieved'] += 1
            debug_log(correlation_id, "UTILITY", "Config retrieved as string", key=key)
            return value
        
        try:
            if isinstance(default, bool):
                result = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                result = int(value)
            elif isinstance(default, float):
                result = float(value)
            else:
                result = value
            
            self._stats['configs_retrieved'] += 1
            debug_log(correlation_id, "UTILITY", "Config retrieved and converted",
                     key=key, result_type=type(result).__name__)
            return result
                
        except (ValueError, AttributeError) as e:
            debug_log(correlation_id, "UTILITY", "Config conversion failed, using default",
                     key=key, error=str(e))
            logger.debug(f"Config conversion failed for {key}={value}, using default={default}")
            return default
    
    # === PERFORMANCE AND STATS ===
    
    def get_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get utility statistics."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in get_stats()")
            return {'error': 'Rate limit exceeded'}
        
        debug_log(correlation_id, "UTILITY", "Getting statistics")
        return self.get_performance_stats(correlation_id)
    
    def get_performance_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get utility performance statistics."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded'}
        
        operation_stats = {}
        
        for op_type, metrics in self._metrics.items():
            cache_hit_rate = 0.0
            if metrics.cache_hits + metrics.cache_misses > 0:
                cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
            
            error_rate = 0.0
            if metrics.call_count > 0:
                error_rate = metrics.error_count / metrics.call_count * 100
            
            template_usage_rate = 0.0
            if metrics.call_count > 0:
                template_usage_rate = metrics.template_usage / metrics.call_count * 100
            
            operation_stats[op_type] = {
                "call_count": metrics.call_count,
                "avg_duration_ms": round(metrics.avg_duration_ms, 2),
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "error_rate_percent": round(error_rate, 2),
                "template_usage_percent": round(template_usage_rate, 2),
                "cache_hits": metrics.cache_hits,
                "cache_misses": metrics.cache_misses,
                "error_count": metrics.error_count,
                "template_usage": metrics.template_usage
            }
        
        debug_log(correlation_id, "UTILITY", "Performance statistics retrieved",
                 operation_count=len(operation_stats))
        
        return {
            "overall_stats": self._stats,
            "operation_stats": operation_stats,
            "id_pool_size": len(self._id_pool),
            "json_cache_size": len(self._json_cache),
            "json_cache_limit": DEFAULT_MAX_JSON_CACHE_SIZE,
            "cache_enabled": self._cache_enabled,
            "rate_limited_count": self._rate_limited_count
        }
    
    def reset(self, correlation_id: str = None) -> bool:
        """Reset UTILITY manager state."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in reset()")
            return False
        
        debug_log(correlation_id, "UTILITY", "Resetting utility manager state")
        
        try:
            self._metrics.clear()
            self._stats = {
                'template_hits': 0,
                'template_fallbacks': 0,
                'cache_optimizations': 0,
                'id_pool_reuse': 0,
                'lugs_integrations': 0,
                'templates_rendered': 0,
                'configs_retrieved': 0
            }
            self._json_cache.clear()
            self._json_cache_order.clear()
            self._id_pool.clear()
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            debug_log(correlation_id, "UTILITY", "Utility manager reset complete")
            return True
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "Reset failed", error=str(e))
            return False


# SINGLETON pattern (LESS-18)
_manager_core = None


def get_utility_manager() -> SharedUtilityCore:
    """
    Get the utility manager instance (SINGLETON pattern).
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        SharedUtilityCore instance
    """
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('utility_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = SharedUtilityCore()
            singleton_register('utility_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        if _manager_core is None:
            _manager_core = SharedUtilityCore()
        return _manager_core


__all__ = [
    'SharedUtilityCore',
    'get_utility_manager',
]
