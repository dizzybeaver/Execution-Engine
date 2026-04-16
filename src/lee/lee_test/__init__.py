"""test/__init__.py - TEST Core Implementations Package
Version: 2025-12-08_1
Purpose: Test implementation modules in /src/test/ subdirectory
License: Apache 2.0
"""

# CRITICAL: No relative imports (AP-28) - Lambda fails with dots
# Import commonly used functions for convenience

from lee.lee_test.test_core import (
    run_component_tests,
    run_single_test,
    run_test_suite,
    test_component_operation,
)
from lee.lee_test.test_lambda_modes import (
    test_diagnostic_mode,
    test_emergency_mode,
    test_failsafe_mode,
    test_lambda_mode,
)
from lee.lee_test.test_performance import (
    benchmark_operation,
    run_performance_tests,
    test_component_performance,
    test_operation_performance,
)
from lee.lee_test.test_scenarios import (
    run_error_scenario_tests,
    test_graceful_degradation,
    test_invalid_operation,
    test_missing_parameters,
)

__version__ = "2025-12-08_1"
__interface__ = "INT-15"

__all__ = [
    "benchmark_operation",
    "run_component_tests",
    "run_error_scenario_tests",
    "run_performance_tests",
    "run_single_test",
    "run_test_suite",
    "test_component_operation",
    "test_component_performance",
    "test_diagnostic_mode",
    "test_emergency_mode",
    "test_failsafe_mode",
    "test_graceful_degradation",
    "test_invalid_operation",
    "test_lambda_mode",
    "test_missing_parameters",
    "test_operation_performance",
]
