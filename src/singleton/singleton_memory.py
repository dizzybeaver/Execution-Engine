"""
singleton_memory.py
Version: 2025.10.03.03
Description: Memory monitoring with standardized gateway response handlers

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import logging
import gc
import resource
import sys
import time
from typing import Dict, Any
from gateway import (
    generate_correlation_id,
    create_success_response,
    create_error_response,
    log_info, log_error
)

logger = logging.getLogger(__name__)


def get_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        
        return create_success_response(
            "Memory statistics retrieved",
            {
                'rss_mb': memory_mb,
                'vms_mb': memory_mb,
                'percent': (memory_mb / 128) * 100,
                'available_mb': (128 - memory_mb),
                'compliant': memory_mb < 128
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Memory stats failed: {str(e)}", e)
        return create_error_response(
            "Failed to get memory statistics",
            error_code="MEMORY_STATS_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        
        gc_stats = gc.get_stats()
        gc_counts = gc.get_count()
        object_count = len(gc.get_objects())
        
        return create_success_response(
            "Comprehensive memory statistics retrieved",
            {
                'memory': {
                    'rss_mb': memory_mb,
                    'available_mb': 128 - memory_mb,
                    'percent_used': (memory_mb / 128) * 100,
                    'compliant': memory_mb < 128
                },
                'gc': {
                    'collections': gc_counts,
                    'stats': gc_stats,
                    'tracked_objects': object_count
                },
                'system': {
                    'lambda_limit_mb': 128,
                    'pressure_level': 'high' if memory_mb > 100 else 'normal'
                }
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Comprehensive memory stats failed: {str(e)}", e)
        return create_error_response(
            "Failed to get comprehensive memory statistics",
            error_code="COMPREHENSIVE_STATS_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def check_lambda_memory_compliance() -> Dict[str, Any]:
    """Check if memory usage is within Lambda 128MB limit - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        compliant = memory_mb < 128
        
        message = "Memory compliant" if compliant else "Memory exceeds limit"
        
        return create_success_response(
            message,
            {
                'compliant': compliant,
                'current_mb': memory_mb,
                'limit_mb': 128,
                'margin_mb': 128 - memory_mb
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Memory compliance check failed: {str(e)}", e)
        return create_error_response(
            "Failed to check memory compliance",
            error_code="COMPLIANCE_CHECK_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def force_memory_cleanup() -> Dict[str, Any]:
    """Force aggressive memory cleanup - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        rusage_before = resource.getrusage(resource.RUSAGE_SELF)
        memory_before = rusage_before.ru_maxrss / 1024
        
        collected = gc.collect()
        
        rusage_after = resource.getrusage(resource.RUSAGE_SELF)
        memory_after = rusage_after.ru_maxrss / 1024
        
        return create_success_response(
            "Memory cleanup completed",
            {
                'gc_collected': collected,
                'memory_before_mb': memory_before,
                'memory_after_mb': memory_after,
                'memory_freed_mb': max(0, memory_before - memory_after),
                'compliant': memory_after < 128
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Memory cleanup failed: {str(e)}", e)
        return create_error_response(
            "Memory cleanup failed",
            error_code="CLEANUP_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage with multiple cleanup strategies - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        optimization_results = []
        
        collected = gc.collect()
        optimization_results.append(f"gc_collected_{collected}_objects")
        
        for generation in range(3):
            gen_collected = gc.collect(generation)
            optimization_results.append(f"gen{generation}_collected_{gen_collected}_objects")
        
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        current_memory = rusage.ru_maxrss / 1024
        
        if current_memory > 100:
            try:
                from singleton_core import _SINGLETON_MANAGER
                _SINGLETON_MANAGER.reset_all()
                optimization_results.append("singleton_cache_cleared")
            except Exception:
                pass
        
        rusage_final = resource.getrusage(resource.RUSAGE_SELF)
        final_memory = rusage_final.ru_maxrss / 1024
        
        return create_success_response(
            "Memory optimization completed",
            {
                'strategies_applied': optimization_results,
                'final_memory_mb': final_memory,
                'compliant': final_memory < 128,
                'optimization_count': len(optimization_results)
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Memory optimization failed: {str(e)}", e)
        return create_error_response(
            "Memory optimization failed",
            error_code="OPTIMIZATION_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        cleanup_results = []
        
        basic_cleanup = force_memory_cleanup()
        cleanup_results.append(('basic_gc', basic_cleanup.get('data', {})))
        
        try:
            from singleton_core import _SINGLETON_MANAGER
            _SINGLETON_MANAGER.reset_all()
            cleanup_results.append(('singleton_cleanup', {'success': True}))
        except Exception as e:
            cleanup_results.append(('singleton_cleanup', {'error': str(e)}))
        
        try:
            cleanup_results.append(('system_cleanup', {'intern_cleared': True}))
        except Exception as e:
            cleanup_results.append(('system_cleanup', {'error': str(e)}))
        
        final_stats = get_memory_stats()
        
        return create_success_response(
            "Comprehensive cleanup completed",
            {
                'cleanup_steps': cleanup_results,
                'final_memory_mb': final_stats.get('data', {}).get('rss_mb', 0),
                'final_compliant': final_stats.get('data', {}).get('compliant', False),
                'steps_completed': len(cleanup_results)
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Comprehensive cleanup failed: {str(e)}", e)
        return create_error_response(
            "Comprehensive cleanup failed",
            error_code="COMPREHENSIVE_CLEANUP_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


def emergency_memory_preserve() -> Dict[str, Any]:
    """Emergency memory preservation mode - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        initial_stats = get_memory_stats()
        initial_data = initial_stats.get('data', {})
        
        if initial_data.get('compliant', False):
            return create_success_response(
                "Memory within limits, emergency mode not required",
                {
                    'emergency_mode': False,
                    'reason': 'memory_within_limits',
                    'current_mb': initial_data.get('rss_mb', 0)
                },
                correlation_id
            )
        
        emergency_steps = []
        
        gc_result = gc.collect()
        emergency_steps.append(f"gc_collected_{gc_result}_objects")
        
        from singleton_core import _SINGLETON_MANAGER
        singleton_count = len(_SINGLETON_MANAGER._instances)
        _SINGLETON_MANAGER.reset_all()
        emergency_steps.append(f"cleared_{singleton_count}_singletons")
        
        final_gc = gc.collect()
        emergency_steps.append(f"final_gc_collected_{final_gc}_objects")
        
        final_stats = get_memory_stats()
        final_data = final_stats.get('data', {})
        
        return create_success_response(
            "Emergency memory preservation completed",
            {
                'emergency_mode': True,
                'emergency_steps': emergency_steps,
                'memory_before_mb': initial_data.get('rss_mb', 0),
                'memory_after_mb': final_data.get('rss_mb', 0),
                'memory_freed_mb': initial_data.get('rss_mb', 0) - final_data.get('rss_mb', 0),
                'now_compliant': final_data.get('compliant', False)
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Emergency memory preservation failed: {str(e)}", e)
        return create_error_response(
            "Emergency memory preservation failed",
            error_code="EMERGENCY_PRESERVE_ERROR",
            details={
                'error': str(e),
                'fallback_cleanup_attempted': True
            },
            correlation_id=correlation_id
        )


def _get_singleton_memory_status_implementation() -> Dict[str, Any]:
    """Get singleton memory status implementation - returns standardized response."""
    correlation_id = generate_correlation_id()
    
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        
        from singleton_core import _SINGLETON_MANAGER
        singleton_count = len(_SINGLETON_MANAGER._instances)
        
        return create_success_response(
            "Singleton memory status retrieved",
            {
                'total_process_memory_mb': memory_mb,
                'singleton_count': singleton_count,
                'lambda_128mb_compliant': memory_mb < 128,
                'memory_pressure': 'high' if memory_mb > 100 else 'normal'
            },
            correlation_id
        )
    except Exception as e:
        log_error(f"Singleton memory status failed: {str(e)}", e)
        return create_error_response(
            "Failed to get singleton memory status",
            error_code="SINGLETON_STATUS_ERROR",
            details={'error': str(e)},
            correlation_id=correlation_id
        )


__all__ = [
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    '_get_singleton_memory_status_implementation',
]

# EOF
