"""
gateway_wrappers_test.py
Version: 2025-12-13_1
Purpose: Gateway wrappers for TEST interface (INT-15)
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import path from interface.interface_test
"""

from typing import Dict, Any, Callable

def run_test_suite(**kwargs) -> Dict[str, Any]:
    """Run complete test suite."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('run_test_suite', **kwargs)

def run_single_test(**kwargs) -> Dict[str, Any]:
    """Run single named test."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('run_single_test', **kwargs)

def run_component_tests(**kwargs) -> Dict[str, Any]:
    """Run all tests for component."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('run_component_tests', **kwargs)

def test_component_operation(**kwargs) -> Dict[str, Any]:
    """Test specific component operation with scenario."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_component_operation', **kwargs)

def test_invalid_operation(**kwargs) -> Dict[str, Any]:
    """Test that invalid operations return proper errors."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_invalid_operation', **kwargs)

def test_missing_parameters(**kwargs) -> Dict[str, Any]:
    """Test that missing required parameters are handled."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_missing_parameters', **kwargs)

def test_graceful_degradation(**kwargs) -> Dict[str, Any]:
    """Test that system degrades gracefully when dependencies fail."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_graceful_degradation', **kwargs)

def run_error_scenario_tests(**kwargs) -> Dict[str, Any]:
    """Run error scenario tests on specified interfaces."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('run_error_scenario_tests', **kwargs)

def test_operation_performance(**kwargs) -> Dict[str, Any]:
    """Test operation performance with specified iterations."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_operation_performance', **kwargs)

def test_component_performance(**kwargs) -> Dict[str, Any]:
    """Test component performance patterns."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_component_performance', **kwargs)

def benchmark_operation(**kwargs) -> Dict[str, Any]:
    """Benchmark single operation."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('benchmark_operation', **kwargs)

def run_performance_tests(**kwargs) -> Dict[str, Any]:
    """Run all performance tests."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('run_performance_tests', **kwargs)

def test_lambda_mode(**kwargs) -> Dict[str, Any]:
    """Test Lambda mode by routing to appropriate handler."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_lambda_mode', **kwargs)

def test_emergency_mode(**kwargs) -> Dict[str, Any]:
    """Test emergency mode handler."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_emergency_mode', **kwargs)

def test_failsafe_mode(**kwargs) -> Dict[str, Any]:
    """Test failsafe mode handler."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_failsafe_mode', **kwargs)

def test_diagnostic_mode(**kwargs) -> Dict[str, Any]:
    """Test diagnostic mode handler."""
    from interface.interface_test import execute_test_operation
    return execute_test_operation('test_diagnostic_mode', **kwargs)

__all__ = [
    'run_test_suite',
    'run_single_test',
    'run_component_tests',
    'test_component_operation',
    'test_invalid_operation',
    'test_missing_parameters',
    'test_graceful_degradation',
    'run_error_scenario_tests',
    'test_operation_performance',
    'test_component_performance',
    'benchmark_operation',
    'run_performance_tests',
    'test_lambda_mode',
    'test_emergency_mode',
    'test_failsafe_mode',
    'test_diagnostic_mode'
]
