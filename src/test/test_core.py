"""
test/test_core.py
Version: 2025-12-08_1
Purpose: Core test execution logic
License: Apache 2.0
"""

from typing import Dict, Any, List, Callable, Optional
import time

def run_test_suite(suite_name: str, **kwargs) -> Dict[str, Any]:
    """Run complete test suite."""
    start_time = time.time()
    
    suite_map = {
        'config_unit': _run_config_unit_suite,
        'config_integration': _run_config_integration_suite,
        'config_performance': _run_config_performance_suite,
        'config_gateway': _run_config_gateway_suite,
        'error_scenarios': _run_error_scenario_suite,
        'debug_patterns': _run_debug_pattern_suite
    }
    
    runner = suite_map.get(suite_name)
    if not runner:
        return {
            'suite': suite_name,
            'success': False,
            'error': f'Unknown suite: {suite_name}'
        }
    
    results = runner(**kwargs)
    duration_ms = (time.time() - start_time) * 1000
    
    results['suite'] = suite_name
    results['duration_ms'] = duration_ms
    
    return results


def run_single_test(test_name: str, **kwargs) -> Dict[str, Any]:
    """Run single named test."""
    start_time = time.time()
    
    # Import test modules lazily
    test_modules = {
        'test_config_': 'test_config_unit',
        'test_gateway_': 'test_config_gateway',
        'test_invalid_': 'test_error_scenarios',
        'test_performance_': 'test_config_performance'
    }
    
    module_name = None
    for prefix, mod in test_modules.items():
        if test_name.startswith(prefix):
            module_name = mod
            break
    
    if not module_name:
        return {
            'test': test_name,
            'success': False,
            'error': f'Unknown test: {test_name}'
        }
    
    try:
        module = __import__(module_name)
        test_func = getattr(module, test_name)
        result = test_func(**kwargs)
        
        duration_ms = (time.time() - start_time) * 1000
        result['test'] = test_name
        result['duration_ms'] = duration_ms
        
        return result
        
    except Exception as e:
        return {
            'test': test_name,
            'success': False,
            'error': str(e),
            'duration_ms': (time.time() - start_time) * 1000
        }


def run_component_tests(component: str, **kwargs) -> Dict[str, Any]:
    """Run all tests for component."""
    results = {
        'component': component,
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # Run component-specific tests
    test_operations = ['invalid_operation', 'missing_parameters']
    
    for operation in test_operations:
        results['total_tests'] += 1
        
        try:
            from test import test_invalid_operation, test_missing_parameters
            
            if operation == 'invalid_operation':
                test_result = test_invalid_operation(component, **kwargs)
            else:
                test_result = test_missing_parameters(component, **kwargs)
            
            if test_result.get('success', False):
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            results['tests'].append({
                'operation': operation,
                'success': test_result.get('success', False),
                'message': test_result.get('message', test_result.get('error', ''))
            })
            
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({
                'operation': operation,
                'success': False,
                'message': f'Exception: {str(e)}'
            })
    
    return results


def test_component_operation(component: str, operation: str, 
                            scenario: str = 'valid', **params) -> Dict[str, Any]:
    """Test specific component operation with scenario."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        interface = getattr(GatewayInterface, component)
    except AttributeError:
        return {
            'test': f'{component}.{operation}',
            'component': component,
            'operation': operation,
            'scenario': scenario,
            'success': False,
            'error': f'Interface not found: {component}'
        }
    
    if scenario == 'valid':
        try:
            result = execute_operation(interface, operation, **params)
            return {
                'test': f'{component}.{operation}',
                'component': component,
                'operation': operation,
                'scenario': scenario,
                'success': True,
                'result': result
            }
        except Exception as e:
            return {
                'test': f'{component}.{operation}',
                'component': component,
                'operation': operation,
                'scenario': scenario,
                'success': False,
                'error': str(e)
            }
    
    elif scenario == 'invalid_op':
        from test import test_invalid_operation
        return test_invalid_operation(component)
    
    elif scenario == 'missing_params':
        from test import test_missing_parameters
        return test_missing_parameters(component)
    
    else:
        return {
            'test': f'{component}.{operation}',
            'component': component,
            'operation': operation,
            'scenario': scenario,
            'success': False,
            'error': f'Unknown scenario: {scenario}'
        }


def _run_config_unit_suite(**kwargs) -> Dict[str, Any]:
    """Run config unit test suite."""
    try:
        from test import run_config_unit_tests
        return run_config_unit_tests()
    except ImportError:
        return {'success': False, 'error': 'test_config_unit not available'}


def _run_config_integration_suite(**kwargs) -> Dict[str, Any]:
    """Run config integration test suite."""
    try:
        from test import run_config_integration_tests
        return run_config_integration_tests()
    except ImportError:
        return {'success': False, 'error': 'test_config_integration not available'}


def _run_config_performance_suite(**kwargs) -> Dict[str, Any]:
    """Run config performance test suite."""
    try:
        from test import run_config_performance_tests
        return run_config_performance_tests()
    except ImportError:
        return {'success': False, 'error': 'test_config_performance not available'}


def _run_config_gateway_suite(**kwargs) -> Dict[str, Any]:
    """Run config gateway test suite."""
    try:
        from test import run_config_gateway_tests
        return run_config_gateway_tests()
    except ImportError:
        return {'success': False, 'error': 'test_config_gateway not available'}


def _run_error_scenario_suite(**kwargs) -> Dict[str, Any]:
    """Run error scenario test suite."""
    try:
        from test import run_error_scenario_tests
        return run_error_scenario_tests(**kwargs)
    except ImportError:
        return {'success': False, 'error': 'test_error_scenarios not available'}


def _run_debug_pattern_suite(**kwargs) -> Dict[str, Any]:
    """Run debug pattern test suite."""
    try:
        from test import run_debug_pattern_tests
        return run_debug_pattern_tests(**kwargs)
    except ImportError:
        return {'success': False, 'error': 'test_debug_patterns not available'}


__all__ = [
    'run_test_suite',
    'run_single_test',
    'run_component_tests',
    'test_component_operation'
]
