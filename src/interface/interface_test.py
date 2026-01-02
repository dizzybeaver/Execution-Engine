"""
interface_test.py
Version: 2025-12-13_1
Purpose: TEST interface router (INT-15)
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import from test package instead of direct module imports
"""

from typing import Any

_TEST_AVAILABLE = True
_TEST_IMPORT_ERROR = None

try:
    from test import (
        run_test_suite,
        run_single_test,
        run_component_tests,
        test_component_operation,
        test_invalid_operation,
        test_missing_parameters,
        test_graceful_degradation,
        run_error_scenario_tests,
        test_operation_performance,
        test_component_performance,
        benchmark_operation,
        run_performance_tests,
        test_lambda_mode,
        test_emergency_mode,
        test_failsafe_mode,
        test_diagnostic_mode
    )
except ImportError as e:
    _TEST_AVAILABLE = False
    _TEST_IMPORT_ERROR = str(e)

_DISPATCH = {
    'run_test_suite': lambda **kw: run_test_suite(**kw),
    'run_single_test': lambda **kw: run_single_test(**kw),
    'run_component_tests': lambda **kw: run_component_tests(**kw),
    'test_component_operation': lambda **kw: test_component_operation(**kw),
    'test_invalid_operation': lambda **kw: test_invalid_operation(**kw),
    'test_missing_parameters': lambda **kw: test_missing_parameters(**kw),
    'test_graceful_degradation': lambda **kw: test_graceful_degradation(**kw),
    'run_error_scenario_tests': lambda **kw: run_error_scenario_tests(**kw),
    'test_operation_performance': lambda **kw: test_operation_performance(**kw),
    'test_component_performance': lambda **kw: test_component_performance(**kw),
    'benchmark_operation': lambda **kw: benchmark_operation(**kw),
    'run_performance_tests': lambda **kw: run_performance_tests(**kw),
    'test_lambda_mode': lambda **kw: test_lambda_mode(**kw),
    'test_emergency_mode': lambda **kw: test_emergency_mode(**kw),
    'test_failsafe_mode': lambda **kw: test_failsafe_mode(**kw),
    'test_diagnostic_mode': lambda **kw: test_diagnostic_mode(**kw)
} if _TEST_AVAILABLE else {}

def execute_test_operation(operation: str, **kwargs) -> Any:
    """Route test operations to implementations."""
    if not _TEST_AVAILABLE:
        raise RuntimeError(f"TEST unavailable: {_TEST_IMPORT_ERROR}")
    
    handler = _DISPATCH.get(operation)
    if not handler:
        raise ValueError(f"Unknown TEST operation: {operation}")
    
    return handler(**kwargs)

__all__ = ['execute_test_operation']
