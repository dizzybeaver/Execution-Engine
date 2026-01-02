"""
test/__init__.py - TEST Core Implementations Package
Version: 2025-12-08_1
Purpose: Test implementation modules in /src/test/ subdirectory
License: Apache 2.0
"""

# CRITICAL: No relative imports (AP-28) - Lambda fails with dots
# Import commonly used functions for convenience

from test.test_core import (
    run_test_suite,
    run_single_test,
    run_component_tests,
    test_component_operation
)
from test.test_scenarios import (
    test_invalid_operation,
    test_missing_parameters,
    test_graceful_degradation,
    run_error_scenario_tests
)
from test.test_performance import (
    test_operation_performance,
    test_component_performance,
    benchmark_operation,
    run_performance_tests
)
from test.test_lambda_modes import (
    test_lambda_mode,
    test_emergency_mode,
    test_failsafe_mode,
    test_diagnostic_mode
)

__version__ = '2025-12-08_1'
__interface__ = 'INT-15'

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
