# interface_test.py

**Version:** 2025-12-13_1  
**Module:** TEST  
**Layer:** Interface  
**Interface:** INT-15  
**Lines:** ~75

---

## Purpose

TEST interface router for comprehensive testing functionality.

---

## Main Function

### execute_test_operation()

**Signature:**
```python
def execute_test_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route test operations to implementations

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Test result (dict or bool)

**Operations:**
- `run_test_suite` - Run complete test suite
- `run_single_test` - Run single test
- `run_component_tests` - Test specific component
- `test_component_operation` - Test single operation
- `test_invalid_operation` - Test invalid operation handling
- `test_missing_parameters` - Test missing parameter handling
- `test_graceful_degradation` - Test degradation scenarios
- `run_error_scenario_tests` - Run error scenario suite
- `test_operation_performance` - Test operation performance
- `test_component_performance` - Test component performance
- `benchmark_operation` - Benchmark specific operation
- `run_performance_tests` - Run performance test suite
- `test_lambda_mode` - Test Lambda mode
- `test_emergency_mode` - Test emergency mode
- `test_failsafe_mode` - Test failsafe mode
- `test_diagnostic_mode` - Test diagnostic mode

**Raises:**
- `RuntimeError` - If TEST unavailable
- `ValueError` - If operation unknown

---

## Core Test Operations

### run_test_suite

**Purpose:** Execute complete test suite

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID for tracking

**Returns:** Dict with test results:
- `total_tests` - Total number of tests
- `passed` - Number of tests passed
- `failed` - Number of tests failed
- `duration_ms` - Total duration
- `pass_rate` - Percentage of tests passed
- `results` - Individual test results

**Usage:**
```python
results = execute_test_operation('run_test_suite', correlation_id='test-123')
```

---

### run_single_test

**Purpose:** Run a single test by name

**Parameters:**
- `test_name` (str, required) - Test name
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with test result:
- `test_name` - Test name
- `passed` - Whether test passed
- `duration_ms` - Test duration
- `error` - Error message (if failed)

**Usage:**
```python
result = execute_test_operation(
    'run_single_test',
    test_name='cache_get_basic',
    correlation_id='test-123'
)
```

---

### run_component_tests

**Purpose:** Run all tests for specific component

**Parameters:**
- `component` (str, required) - Component name
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with component test results

**Usage:**
```python
results = execute_test_operation(
    'run_component_tests',
    component='cache',
    correlation_id='test-123'
)
```

---

### test_component_operation

**Purpose:** Test single operation of component

**Parameters:**
- `component` (str, required) - Component name
- `operation` (str, required) - Operation name
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with operation test result

**Usage:**
```python
result = execute_test_operation(
    'test_component_operation',
    component='cache',
    operation='get',
    correlation_id='test-123'
)
```

---

## Error Scenario Tests

### test_invalid_operation

**Purpose:** Test invalid operation handling

**Parameters:**
- `component` (str, required) - Component to test
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with test result

**Usage:**
```python
result = execute_test_operation(
    'test_invalid_operation',
    component='cache',
    correlation_id='test-123'
)
```

---

### test_missing_parameters

**Purpose:** Test missing parameter handling

**Parameters:**
- `component` (str, required) - Component to test
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with test result

**Usage:**
```python
result = execute_test_operation(
    'test_missing_parameters',
    component='cache',
    correlation_id='test-123'
)
```

---

### test_graceful_degradation

**Purpose:** Test graceful degradation scenarios

**Parameters:**
- `component` (str, required) - Component to test
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with test result

**Usage:**
```python
result = execute_test_operation(
    'test_graceful_degradation',
    component='cache',
    correlation_id='test-123'
)
```

---

### run_error_scenario_tests

**Purpose:** Run complete error scenario test suite

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with error scenario test results

**Usage:**
```python
results = execute_test_operation(
    'run_error_scenario_tests',
    correlation_id='test-123'
)
```

---

## Performance Tests

### test_operation_performance

**Purpose:** Test single operation performance

**Parameters:**
- `component` (str, required) - Component name
- `operation` (str, required) - Operation name
- `iterations` (int, optional) - Number of iterations (default: 100)
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with performance results:
- `operation` - Operation tested
- `iterations` - Number of iterations
- `total_duration_ms` - Total duration
- `average_duration_ms` - Average per operation
- `min_duration_ms` - Minimum duration
- `max_duration_ms` - Maximum duration

**Usage:**
```python
results = execute_test_operation(
    'test_operation_performance',
    component='cache',
    operation='get',
    iterations=1000,
    correlation_id='test-123'
)
```

---

### test_component_performance

**Purpose:** Test all operations of component for performance

**Parameters:**
- `component` (str, required) - Component name
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with component performance results

**Usage:**
```python
results = execute_test_operation(
    'test_component_performance',
    component='cache',
    correlation_id='test-123'
)
```

---

### benchmark_operation

**Purpose:** Detailed benchmark of operation

**Parameters:**
- `component` (str, required) - Component name
- `operation` (str, required) - Operation name
- `iterations` (int, optional) - Iterations (default: 1000)
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with detailed benchmark:
- `operation` - Operation benchmarked
- `iterations` - Number of iterations
- `statistics` - Detailed statistics
- `percentiles` - Performance percentiles (p50, p95, p99)

**Usage:**
```python
results = execute_test_operation(
    'benchmark_operation',
    component='cache',
    operation='set',
    iterations=10000,
    correlation_id='test-123'
)
```

---

### run_performance_tests

**Purpose:** Run complete performance test suite

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with performance test results

**Usage:**
```python
results = execute_test_operation(
    'run_performance_tests',
    correlation_id='test-123'
)
```

---

## Lambda Mode Tests

### test_lambda_mode

**Purpose:** Test normal Lambda mode

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with Lambda mode test result

**Usage:**
```python
result = execute_test_operation(
    'test_lambda_mode',
    correlation_id='test-123'
)
```

---

### test_emergency_mode

**Purpose:** Test emergency Lambda mode

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with emergency mode test result

**Usage:**
```python
result = execute_test_operation(
    'test_emergency_mode',
    correlation_id='test-123'
)
```

---

### test_failsafe_mode

**Purpose:** Test failsafe Lambda mode

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with failsafe mode test result

**Usage:**
```python
result = execute_test_operation(
    'test_failsafe_mode',
    correlation_id='test-123'
)
```

---

### test_diagnostic_mode

**Purpose:** Test diagnostic Lambda mode

**Parameters:**
- `correlation_id` (str, optional) - Correlation ID

**Returns:** Dict with diagnostic mode test result

**Usage:**
```python
result = execute_test_operation(
    'test_diagnostic_mode',
    correlation_id='test-123'
)
```

---

## Import Structure

```python
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
```

---

## Dispatch Dictionary

```python
_DISPATCH = {
    'run_test_suite': lambda **kw: run_test_suite(**kw),
    'run_single_test': lambda **kw: run_single_test(**kw),
    # ... all operations mapped
} if _TEST_AVAILABLE else {}
```

---

## Test Result Format

**Standard Test Result:**
```python
{
    'test_name': 'cache_get_basic',
    'component': 'cache',
    'operation': 'get',
    'passed': True,
    'duration_ms': 12.34,
    'error': None,
    'correlation_id': 'test-123'
}
```

**Test Suite Result:**
```python
{
    'total_tests': 50,
    'passed': 48,
    'failed': 2,
    'duration_ms': 1234.56,
    'pass_rate': 96.0,
    'results': [
        # Individual test results
    ],
    'correlation_id': 'test-123'
}
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Comprehensive Testing:** Unit, integration, performance  
✅ **Lambda Mode Testing:** All modes covered  
✅ **Error Scenarios:** Thorough error handling tests  
✅ **Performance Benchmarking:** Detailed metrics

---

## Related Files

- `/test/` - Test implementation
- `/gateway/wrappers/gateway_wrappers_test.py` - Gateway wrappers
- `/test/test_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
