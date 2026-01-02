"""
utility/utility_data.py
Version: 2025-12-13_1
Purpose: Data operations for utility interface
License: Apache 2.0
"""

import json
from typing import Dict, Any, Optional, List
import logging as stdlib_logging

from utility.utility_types import DEFAULT_MAX_JSON_CACHE_SIZE

logger = stdlib_logging.getLogger(__name__)


class UtilityDataOperations:
    """Data operations for parsing, merging, and formatting."""
    
    def __init__(self, manager):
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager
    
    def parse_json(self, data: str, correlation_id: str = None) -> Dict:
        """Parse JSON string."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            result = json.loads(data)
            debug_log(correlation_id, "UTILITY", "JSON parsed successfully",
                     result_keys=len(result) if isinstance(result, dict) else 0)
            return result
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "JSON parse failed", error=str(e))
            logger.error(f"JSON parse error: {str(e)}")
            return {}
    
    def parse_json_safely(self, json_str: str, use_cache: bool = True,
                         correlation_id: str = None) -> Optional[Dict[str, Any]]:
        """Parse JSON safely with optional caching."""
        from gateway import debug_log, debug_timing, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._manager._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in parse_json_safely()")
            return None
        
        cache_key = hash(json_str)
        
        if use_cache and cache_key in self._manager._json_cache:
            debug_log(correlation_id, "UTILITY", "JSON parse cache hit")
            return self._manager._json_cache[cache_key]
        
        with debug_timing(correlation_id, "UTILITY", "parse_json"):
            try:
                parsed = json.loads(json_str)
                
                if use_cache:
                    if len(self._manager._json_cache) >= DEFAULT_MAX_JSON_CACHE_SIZE:
                        if self._manager._json_cache_order:
                            oldest_key = self._manager._json_cache_order.pop(0)
                            self._manager._json_cache.pop(oldest_key, None)
                    
                    self._manager._json_cache[cache_key] = parsed
                    self._manager._json_cache_order.append(cache_key)
                    debug_log(correlation_id, "UTILITY", "JSON parsed and cached")
                
                return parsed
                
            except json.JSONDecodeError as e:
                debug_log(correlation_id, "UTILITY", "JSON decode error", error=str(e))
                logger.error(f"JSON parse error: {str(e)}")
                return None
            except Exception as e:
                debug_log(correlation_id, "UTILITY", "Unexpected parse error", error=str(e))
                logger.error(f"Unexpected parse error: {str(e)}")
                return None
    
    def deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any],
                   correlation_id: str = None) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value, correlation_id)
            else:
                result[key] = value
        
        debug_log(correlation_id, "UTILITY", "Dictionaries merged",
                 dict1_keys=len(dict1), dict2_keys=len(dict2), result_keys=len(result))
        
        return result
    
    def safe_get(self, dictionary: Dict, key_path: str, default: Any = None,
                correlation_id: str = None) -> Any:
        """Safely get nested dictionary value using dot notation."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            keys = key_path.split('.')
            value = dictionary
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                    if value is None:
                        debug_log(correlation_id, "UTILITY", "Key path not found, using default",
                                 key_path=key_path)
                        return default
                else:
                    debug_log(correlation_id, "UTILITY", "Invalid path, using default",
                             key_path=key_path)
                    return default
            
            debug_log(correlation_id, "UTILITY", "Value retrieved via safe_get",
                     key_path=key_path, has_value=value is not None)
            return value
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "safe_get failed, using default",
                     key_path=key_path, error=str(e))
            return default
    
    def format_bytes(self, size: int, correlation_id: str = None) -> str:
        """Format bytes to human-readable string."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                result = f"{size:.2f} {unit}"
                debug_log(correlation_id, "UTILITY", "Bytes formatted",
                         size=size, result=result)
                return result
            size /= 1024.0
        
        result = f"{size:.2f} PB"
        debug_log(correlation_id, "UTILITY", "Bytes formatted (PB)", result=result)
        return result
    
    def merge_dictionaries(self, *dicts: Dict[str, Any], 
                          correlation_id: str = None) -> Dict[str, Any]:
        """Merge multiple dictionaries safely."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            result = {}
            for d in dicts:
                if isinstance(d, dict):
                    result.update(d)
            
            debug_log(correlation_id, "UTILITY", "Multiple dictionaries merged",
                     dict_count=len(dicts), result_keys=len(result))
            return result
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "Dictionary merge failed", error=str(e))
            logger.error(f"Dictionary merge error: {str(e)}")
            return {}
    
    def format_data_for_response(self, data: Any, format_type: str = "json",
                                include_metadata: bool = True,
                                correlation_id: str = None) -> Dict[str, Any]:
        """Format data for response."""
        from gateway import debug_log, generate_correlation_id
        import time
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        formatted = {
            "data": data,
            "format": format_type
        }
        
        if include_metadata:
            formatted["metadata"] = {
                "timestamp": int(time.time()),
                "type": type(data).__name__
            }
        
        debug_log(correlation_id, "UTILITY", "Data formatted for response",
                 format_type=format_type, include_metadata=include_metadata)
        
        return formatted
    
    def cleanup_cache(self, max_age_seconds: int = 3600,
                     correlation_id: str = None) -> int:
        """Clean up old cached utility data."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._manager._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in cleanup_cache()")
            return 0
        
        try:
            cleared = len(self._manager._json_cache)
            self._manager._json_cache.clear()
            self._manager._json_cache_order.clear()
            self._manager._stats['lugs_integrations'] += 1
            
            debug_log(correlation_id, "UTILITY", "Cache cleaned up", cleared_count=cleared)
            return cleared
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "Cache cleanup failed", error=str(e))
            logger.error(f"Cache cleanup error: {str(e)}")
            return 0
    
    def optimize_performance(self, correlation_id: str = None) -> Dict[str, Any]:
        """Optimize utility performance based on usage patterns."""
        from gateway import debug_log, generate_correlation_id
        import time
        import uuid
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._manager._check_rate_limit():
            debug_log(correlation_id, "UTILITY", "Rate limit exceeded in optimize_performance()")
            return {'error': 'Rate limit exceeded'}
        
        optimizations = []
        
        for op_type, metrics in self._manager._metrics.items():
            if metrics.avg_duration_ms > 100:
                optimizations.append(f"High latency detected for {op_type}")
            
            cache_hit_rate = 0.0
            if metrics.cache_hits + metrics.cache_misses > 0:
                cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
            
            if cache_hit_rate < 50 and metrics.cache_misses > 10:
                optimizations.append(f"Low cache hit rate for {op_type}")
        
        if not self._manager._id_pool or len(self._manager._id_pool) < 10:
            for _ in range(20):
                self._manager._id_pool.append(str(uuid.uuid4()))
            optimizations.append("Replenished ID pool")
        
        if len(self._manager._json_cache) > (DEFAULT_MAX_JSON_CACHE_SIZE * 0.9):
            optimizations.append("JSON cache approaching limit")
        
        debug_log(correlation_id, "UTILITY", "Performance optimization complete",
                 optimizations_count=len(optimizations))
        
        return {
            "optimizations_applied": optimizations,
            "timestamp": int(time.time())
        }
    
    def configure_caching(self, enabled: bool, ttl: int = 300,
                         correlation_id: str = None) -> bool:
        """Configure utility caching settings."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            self._manager._cache_enabled = enabled
            self._manager._cache_ttl = ttl
            
            debug_log(correlation_id, "UTILITY", "Caching configured",
                     enabled=enabled, ttl=ttl)
            return True
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "Caching configuration failed", error=str(e))
            return False


__all__ = [
    'UtilityDataOperations',
]
