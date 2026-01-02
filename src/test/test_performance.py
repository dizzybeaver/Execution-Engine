"""
test/test_performance.py
Version: 2025-12-08_1
Purpose: Performance testing (migrated from test_config_performance.py)
License: Apache 2.0
"""

import time
from typing import Dict, Any, Callable

def test_operation_performance(operation: Callable, iterations: int = 100, **kwargs) -> Dict[str, Any]:
    """Test operation performance with specified iterations."""
    times = []
    
    for i in range(iterations):
        start_time = time.time()
        try:
            result = operation(**kwargs)
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
        except Exception as e:
            return {
                'success': False,
                'error': f'Operation failed: {str(e)}'
            }
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    return {
        'success': True,
        'iterations': iterations,
        'avg_ms': avg_time,
        'min_ms': min_time,
        'max_ms': max_time,
        'total_ms': sum(times)
    }


def test_component_performance(component: str, **kwargs) -> Dict[str, Any]:
    """Test component performance patterns."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        interface = getattr(GatewayInterface, component)
    except AttributeError:
        return {
            'success': False,
            'error': f'Interface not found: {component}'
        }
    
    # Common operations to test
    operations = {
        'CONFIG': [('get_parameter', {'key': 'test', 'default': 'value'})],
        'CACHE': [('cache_get', {'key': 'test'})],
        'LOGGING': [('log_info', {'message': 'test'})],
    }
    
    op_list = operations.get(component, [])
    if not op_list:
        return {
            'success': True,
            'message': f'No performance tests defined for {component}'
        }
    
    results = {}
    for op_name, params in op_list:
        times = []
        for i in range(50):
            start_time = time.time()
            try:
                execute_operation(interface, op_name, **params)
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)
            except:
                pass
        
        if times:
            results[op_name] = {
                'avg_ms': sum(times) / len(times),
                'min_ms': min(times),
                'max_ms': max(times)
            }
    
    return {
        'success': True,
        'component': component,
        'operations': results
    }


def benchmark_operation(func: Callable, **kwargs) -> Dict[str, Any]:
    """Benchmark single operation."""
    start_time = time.time()
    
    try:
        result = func(**kwargs)
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            'success': True,
            'duration_ms': duration_ms,
            'result': result
        }
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return {
            'success': False,
            'duration_ms': duration_ms,
            'error': str(e)
        }


def run_performance_tests(**kwargs) -> Dict[str, Any]:
    """Run all performance tests."""
    from test import run_config_performance_tests
    
    try:
        return run_config_performance_tests()
    except ImportError:
        return {
            'success': False,
            'error': 'test_config_performance not available'
        }


__all__ = [
    'test_operation_performance',
    'test_component_performance',
    'benchmark_operation',
    'run_performance_tests'
]
