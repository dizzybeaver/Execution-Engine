"""
zaph_core.py
Version: 2025-12-14_1
Purpose: ZAPH (Zero-Abstraction Path for Hot operations) core implementation
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class OperationHeatLevel(Enum):
    """Operation heat levels for LUGS protection."""
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    CRITICAL = "critical"


@dataclass
class OperationMetrics:
    """Metrics for operation heat detection."""
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    last_call_time: float = 0.0
    last_access_time: float = 0.0
    heat_level: OperationHeatLevel = OperationHeatLevel.COLD
    source_module: Optional[str] = None


class LUGSAwareFastPath:
    """Fast path system with LUGS protection, LRU eviction, and prewarming."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._operation_metrics: Dict[str, OperationMetrics] = {}
        self._hot_paths: Dict[str, Callable] = {}
        self._protected_modules: set = set()
        self._call_counts = defaultdict(int)
        
        # Configuration
        self._enabled = True
        self._cache_size_limit = 100
        self._heat_thresholds = {
            OperationHeatLevel.WARM: 5,
            OperationHeatLevel.HOT: 20,
            OperationHeatLevel.CRITICAL: 100
        }
        
        # Statistics
        self._stats = {
            'total_operations': 0,
            'fast_path_hits': 0,
            'fast_path_misses': 0,
            'cache_evictions': 0,
            'hot_modules_protected': 0,
            'heat_promotions': 0,
            'time_saved_ms': 0.0
        }
    
    def track_operation(
        self,
        operation_key: str,
        duration_ms: float,
        source_module: Optional[str] = None
    ) -> OperationHeatLevel:
        """Track operation and determine heat level."""
        current_time = time.time()
        
        with self._lock:
            self._stats['total_operations'] += 1
            self._call_counts[operation_key] += 1
            
            if operation_key not in self._operation_metrics:
                self._operation_metrics[operation_key] = OperationMetrics(
                    source_module=source_module
                )
            
            metrics = self._operation_metrics[operation_key]
            metrics.call_count += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
            metrics.last_call_time = current_time
            metrics.last_access_time = current_time
            
            old_heat = metrics.heat_level
            new_heat = self._calculate_heat_level(metrics.call_count)
            
            if new_heat != old_heat:
                metrics.heat_level = new_heat
                self._stats['heat_promotions'] += 1
                
                if new_heat in [OperationHeatLevel.HOT, OperationHeatLevel.CRITICAL]:
                    self._protect_module(source_module)
            
            return new_heat
    
    def execute_fast_path(
        self,
        operation_key: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with fast-path optimization and LRU."""
        if not self._enabled:
            return func(*args, **kwargs)
        
        current_time = time.time()
        
        with self._lock:
            self._stats['total_operations'] += 1
            self._call_counts[operation_key] += 1
            
            # Check if in hot paths (cached)
            if operation_key in self._hot_paths:
                self._stats['fast_path_hits'] += 1
                
                # Update LRU access time
                if operation_key in self._operation_metrics:
                    self._operation_metrics[operation_key].last_access_time = current_time
        
        # Execute outside lock for performance
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start_time) * 1000
        
        with self._lock:
            # Track for heat detection
            if operation_key not in self._operation_metrics:
                self._operation_metrics[operation_key] = OperationMetrics()
            
            metrics = self._operation_metrics[operation_key]
            metrics.call_count = self._call_counts[operation_key]
            metrics.last_call_time = current_time
            metrics.last_access_time = current_time
            
            # Auto-cache if hot enough
            if operation_key not in self._hot_paths:
                self._stats['fast_path_misses'] += 1
                
                if self._call_counts[operation_key] >= self._heat_thresholds[OperationHeatLevel.WARM]:
                    self._add_to_hot_paths(operation_key, func)
            else:
                # Estimate time saved
                self._stats['time_saved_ms'] += max(0, 2.0 - elapsed_ms)
        
        return result
    
    def _add_to_hot_paths(self, operation_key: str, func: Callable) -> None:
        """Add to hot paths with LRU eviction (called within lock)."""
        # LRU eviction if at capacity
        if len(self._hot_paths) >= self._cache_size_limit:
            # Find least recently accessed
            lru_key = min(
                self._operation_metrics,
                key=lambda k: self._operation_metrics[k].last_access_time
                if k in self._hot_paths else float('inf')
            )
            
            if lru_key in self._hot_paths:
                del self._hot_paths[lru_key]
                self._stats['cache_evictions'] += 1
        
        self._hot_paths[operation_key] = func
    
    def _calculate_heat_level(self, call_count: int) -> OperationHeatLevel:
        """Calculate heat level based on call count."""
        if call_count >= self._heat_thresholds[OperationHeatLevel.CRITICAL]:
            return OperationHeatLevel.CRITICAL
        elif call_count >= self._heat_thresholds[OperationHeatLevel.HOT]:
            return OperationHeatLevel.HOT
        elif call_count >= self._heat_thresholds[OperationHeatLevel.WARM]:
            return OperationHeatLevel.WARM
        else:
            return OperationHeatLevel.COLD
    
    def _protect_module(self, module_name: Optional[str]) -> None:
        """Protect hot module from LUGS unloading."""
        if not module_name or module_name in self._protected_modules:
            return
        
        self._protected_modules.add(module_name)
        self._stats['hot_modules_protected'] += 1
    
    def register_fast_path(
        self,
        operation_key: str,
        fast_func: Callable,
        source_module: Optional[str] = None
    ) -> None:
        """Register a fast path for hot operation."""
        with self._lock:
            self._hot_paths[operation_key] = fast_func
            
            if operation_key not in self._operation_metrics:
                self._operation_metrics[operation_key] = OperationMetrics(
                    heat_level=OperationHeatLevel.HOT,
                    source_module=source_module,
                    last_access_time=time.time()
                )
            
            if source_module:
                self._protect_module(source_module)
    
    def get_fast_path(self, operation_key: str) -> Optional[Callable]:
        """Get fast path if available."""
        with self._lock:
            if operation_key in self._hot_paths:
                self._stats['fast_path_hits'] += 1
                
                # Update LRU
                if operation_key in self._operation_metrics:
                    self._operation_metrics[operation_key].last_access_time = time.time()
                
                return self._hot_paths[operation_key]
            return None
    
    def is_hot_operation(self, operation_key: str) -> bool:
        """Check if operation is hot."""
        with self._lock:
            if operation_key not in self._operation_metrics:
                return False
            
            heat = self._operation_metrics[operation_key].heat_level
            return heat in [OperationHeatLevel.HOT, OperationHeatLevel.CRITICAL]
    
    def should_protect_module(self, module_name: str) -> bool:
        """Check if module should be protected from unloading."""
        with self._lock:
            return module_name in self._protected_modules
    
    def get_heat_level(self, operation_key: str) -> OperationHeatLevel:
        """Get operation heat level."""
        with self._lock:
            if operation_key not in self._operation_metrics:
                return OperationHeatLevel.COLD
            return self._operation_metrics[operation_key].heat_level
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive fast path statistics."""
        with self._lock:
            stats = self._stats.copy()
            
            heat_counts = {
                OperationHeatLevel.COLD: 0,
                OperationHeatLevel.WARM: 0,
                OperationHeatLevel.HOT: 0,
                OperationHeatLevel.CRITICAL: 0
            }
            
            for metrics in self._operation_metrics.values():
                heat_counts[metrics.heat_level] += 1
            
            total = self._stats['total_operations']
            hits = self._stats['fast_path_hits']
            hit_rate = (hits / total * 100) if total > 0 else 0.0
            avg_time_saved = (self._stats['time_saved_ms'] / hits) if hits > 0 else 0.0
            
            stats.update({
                'total_tracked_operations': len(self._operation_metrics),
                'registered_fast_paths': len(self._hot_paths),
                'protected_modules': len(self._protected_modules),
                'cold_operations': heat_counts[OperationHeatLevel.COLD],
                'warm_operations': heat_counts[OperationHeatLevel.WARM],
                'hot_operations': heat_counts[OperationHeatLevel.HOT],
                'critical_operations': heat_counts[OperationHeatLevel.CRITICAL],
                'hit_rate_percent': round(hit_rate, 2),
                'avg_time_saved_ms': round(avg_time_saved, 3),
                'cache_size_limit': self._cache_size_limit,
                'enabled': self._enabled
            })
        
        return stats
    
    def get_hot_operations(self, limit: int = 10) -> list:
        """Get most frequently called operations."""
        with self._lock:
            sorted_ops = sorted(
                self._call_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_ops[:limit]
    
    def get_cached_operations(self) -> list:
        """Get list of operations in hot path cache."""
        with self._lock:
            return list(self._hot_paths.keys())
    
    def configure(
        self,
        enabled: Optional[bool] = None,
        cache_size: Optional[int] = None,
        warm_threshold: Optional[int] = None,
        hot_threshold: Optional[int] = None,
        critical_threshold: Optional[int] = None
    ) -> Dict[str, Any]:
        """Configure fast path behavior."""
        with self._lock:
            if enabled is not None:
                self._enabled = enabled
                if not enabled:
                    self.clear_cache()
            
            if cache_size is not None and cache_size > 0:
                self._cache_size_limit = cache_size
                
                # Trim if needed
                while len(self._hot_paths) > self._cache_size_limit:
                    lru_key = min(
                        self._operation_metrics,
                        key=lambda k: self._operation_metrics[k].last_access_time
                        if k in self._hot_paths else float('inf')
                    )
                    if lru_key in self._hot_paths:
                        del self._hot_paths[lru_key]
                        self._stats['cache_evictions'] += 1
            
            if warm_threshold is not None and warm_threshold > 0:
                self._heat_thresholds[OperationHeatLevel.WARM] = warm_threshold
            
            if hot_threshold is not None and hot_threshold > 0:
                self._heat_thresholds[OperationHeatLevel.HOT] = hot_threshold
            
            if critical_threshold is not None and critical_threshold > 0:
                self._heat_thresholds[OperationHeatLevel.CRITICAL] = critical_threshold
            
            return self.get_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'cache_size_limit': self._cache_size_limit,
                'warm_threshold': self._heat_thresholds[OperationHeatLevel.WARM],
                'hot_threshold': self._heat_thresholds[OperationHeatLevel.HOT],
                'critical_threshold': self._heat_thresholds[OperationHeatLevel.CRITICAL]
            }
    
    def prewarm(self, operation_keys: list) -> int:
        """Prewarm cache with operations (for Lambda cold starts)."""
        count = 0
        with self._lock:
            for key in operation_keys:
                if key not in self._hot_paths and len(self._hot_paths) < self._cache_size_limit:
                    # Add placeholder - actual func registered on first call
                    if key not in self._operation_metrics:
                        self._operation_metrics[key] = OperationMetrics(
                            heat_level=OperationHeatLevel.WARM,
                            last_access_time=time.time()
                        )
                    count += 1
        return count
    
    def prewarm_common(self) -> int:
        """Prewarm with common operations."""
        common_ops = [
            'cache_get', 'cache_set',
            'logging_log_info', 'logging_log_error',
            'metrics_record_metric',
            'security_generate_correlation_id',
            'config_get_state'
        ]
        return self.prewarm(common_ops)
    
    def clear_cache(self) -> None:
        """Clear hot path cache."""
        with self._lock:
            self._hot_paths.clear()
    
    def reset_call_counts(self) -> None:
        """Reset operation call counts."""
        with self._lock:
            self._call_counts.clear()
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._stats = {
                'total_operations': 0,
                'fast_path_hits': 0,
                'fast_path_misses': 0,
                'cache_evictions': 0,
                'hot_modules_protected': 0,
                'heat_promotions': 0,
                'time_saved_ms': 0.0
            }
    
    def optimize(self) -> Dict[str, Any]:
        """Run optimization cycle - remove stale operations."""
        optimizations = 0
        current_time = time.time()
        
        with self._lock:
            stale_operations = [
                key for key, metrics in self._operation_metrics.items()
                if current_time - metrics.last_call_time > 300
                and metrics.heat_level == OperationHeatLevel.COLD
                and key not in self._hot_paths
            ]
            
            for key in stale_operations:
                del self._operation_metrics[key]
                if key in self._call_counts:
                    del self._call_counts[key]
                optimizations += 1
        
        return {
            'optimizations': optimizations,
            'stale_removed': len(stale_operations)
        }

# EOF
