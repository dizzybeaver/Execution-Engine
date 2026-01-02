# test_core.py

**Version:** 2025-12-08_1  
**Module:** TEST Interface  
**Layer:** Core  
**Lines:** 250

---

## Purpose

Core test execution logic. Orchestrates test suite execution, component testing, and individual test runs. Routes test requests to appropriate handlers.

---

## Functions

### run_test_suite()

**Purpose:** Execute complete test suite by name

**Signature:**
```python
def run_test_suite(suite_name: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `suite_name` - Test suite identifier (e.g., 'config_unit', 'config_integration')
- `**kwargs` - Suite-specific parameters

**Returns:**
```python
{
    'suite': str,           # Suite name
    'success': bool,        # True if all tests passed
    'duration_ms': float,   # Total execution time
    'total_tests': int,     # Number of tests run
    'passed': int,          # Tests passed
    'failed': int,          # Tests failed
    'tests': List[Dict]     # Individual test results
}
```

**Behavior:**
1. Start timing measurement
2. Map suite name to runner function
3. Execute suite runner with kwargs
4. Calculate total duration
5. Return results with suite metadata

**Available Suites:**
- `config_unit` - Configuration unit tests
- `config_integration` - Configuration integration tests
- `config_performance` - Configuration performance tests
- `config_gateway` - Configuration gateway tests
- `error_scenarios` - Error scenario tests
- `debug_patterns` - Debug pattern tests

**Performance:** Variable (depends on suite size, typically 50-500ms)

**Usage:**
```python
from test import run_test_suite

# Run config unit tests
results = run_test_suite('config_unit')
print(f"Passed: {results['passed']}/{results['total_tests']}")

# Run error scenario tests with specific interfaces
results = run_test_suite('error_scenarios', interfaces=['CACHE', 'CONFIG'])
```

**Error Handling:**
Returns error dict if suite not found:
```python
{
    'suite': 'unknown_suite',
    'success': False,
    'error': 'Unknown suite: unknown_suite'
}
```

---

### run_single_test()

**Purpose:** Execute single named test

**Signature:**
```python
def run_single_test(test_name: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `test_name` - Test function name (e.g., 'test_config_get_parameter')
- `**kwargs` - Test-specific parameters

**Returns:**
```python
{
    'test': str,            # Test name
    'success': bool,        # True if test passed
    'duration_ms': float,   # Execution time
    'result': Any,          # Test result (if success)
    'error': str            # Error message (if failed)
}
```

**Behavior:**
1. Start timing measurement
2. Determine module from test name prefix
3. Lazy import test module
4. Get test function by name
5. Execute test with kwargs
6. Calculate duration and return results

**Test Name Patterns:**
- `test_config_*` → test_config_unit module
- `test_gateway_*` → test_config_gateway module
- `test_invalid_*` → test_error_scenarios module
- `test_performance_*` → test_config_performance module

**Performance:** Variable (depends on test, typically 10-100ms)

**Usage:**
```python
from test import run_single_test

# Run specific config test
result = run_single_test('test_config_get_parameter', key='test.key')

if result['success']:
    print(f"✓ Test passed in {result['duration_ms']:.2f}ms")
else:
    print(f"✗ Test failed: {result['error']}")
```

**Error Handling:**
Returns error dict if test not found or fails:
```python
{
    'test': 'unknown_test',
    'success': False,
    'error': 'Unknown test: unknown_test',
    'duration_ms': 0.5
}
```

---

### run_component_tests()

**Purpose:** Run all tests for a specific component

**Signature:**
```python
def run_component_tests(component: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `component` - Interface component name (e.g., 'CONFIG', 'CACHE')
- `**kwargs` - Component-specific parameters

**Returns:**
```python
{
    'component': str,       # Component tested
    'total_tests': int,     # Number of tests run
    'passed': int,          # Tests passed
    'failed': int,          # Tests failed
    'tests': List[Dict]     # Individual test results
}
```

**Behavior:**
1. Initialize results structure
2. Define test operations for component
3. For each operation:
   - Run invalid_operation test
   - Run missing_parameters test
   - Record results
4. Aggregate pass/fail counts
5. Return component test summary

**Test Operations:**
- `invalid_operation` - Tests error handling for unknown operations
- `missing_parameters` - Tests validation of required parameters

**Performance:** ~50-100ms per component (2 tests)

**Usage:**
```python
from test import run_component_tests

# Test CACHE component
results = run_component_tests('CACHE')

print(f"Component: {results['component']}")
print(f"Passed: {results['passed']}/{results['total_tests']}")

for test in results['tests']:
    status = "✓" if test['success'] else "✗"
    print(f"{status} {test['operation']}: {test['message']}")
```

**Error Handling:**
Individual test failures are recorded in results, not raised.

---

### test_component_operation()

**Purpose:** Test specific component operation with scenario

**Signature:**
```python
def test_component_operation(
    component: str,
    operation: str,
    scenario: str = 'valid',
    **params
) -> Dict[str, Any]
```

**Parameters:**
- `component` - Interface component (e.g., 'CACHE')
- `operation` - Operation name (e.g., 'cache_get')
- `scenario` - Test scenario: 'valid', 'invalid_op', 'missing_params'
- `**params` - Operation parameters

**Returns:**
```python
{
    'test': str,            # Test identifier
    'component': str,       # Component name
    'operation': str,       # Operation name
    'scenario': str,        # Test scenario
    'success': bool,        # Test result
    'result': Any,          # Operation result (if success)
    'error': str            # Error message (if failed)
}
```

**Scenarios:**
- `valid` - Normal operation execution
- `invalid_op` - Test invalid operation handling
- `missing_params` - Test missing parameter validation

**Behavior:**
1. Resolve interface from component name
2. Route to scenario handler:
   - `valid`: Execute operation via gateway
   - `invalid_op`: Call test_invalid_operation()
   - `missing_params`: Call test_missing_parameters()
3. Catch and report any errors
4. Return test results

**Performance:** 10-50ms (depends on operation)

**Usage:**
```python
from test import test_component_operation

# Test valid operation
result = test_component_operation(
    'CACHE',
    'cache_get',
    scenario='valid',
    key='test.key'
)

# Test invalid operation
result = test_component_operation(
    'CACHE',
    'invalid_op',
    scenario='invalid_op'
)

# Test missing parameters
result = test_component_operation(
    'CONFIG',
    'get_parameter',
    scenario='missing_params'
)
```

**Error Handling:**
Returns structured error dict if interface not found or operation fails.

---

## Internal Functions

### _run_config_unit_suite()

**Purpose:** Execute config unit test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_config_unit
2. Call run_config_unit_tests()
3. Return results or error dict

---

### _run_config_integration_suite()

**Purpose:** Execute config integration test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_config_integration
2. Call run_config_integration_tests()
3. Return results or error dict

---

### _run_config_performance_suite()

**Purpose:** Execute config performance test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_config_performance
2. Call run_config_performance_tests()
3. Return results or error dict

---

### _run_config_gateway_suite()

**Purpose:** Execute config gateway test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_config_gateway
2. Call run_config_gateway_tests()
3. Return results or error dict

---

### _run_error_scenario_suite()

**Purpose:** Execute error scenario test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_error_scenarios
2. Call run_error_scenario_tests() with kwargs
3. Return results or error dict

---

### _run_debug_pattern_suite()

**Purpose:** Execute debug pattern test suite

**Returns:** Test suite results

**Behavior:**
1. Lazy import test_debug_patterns
2. Call run_debug_pattern_tests() with kwargs
3. Return results or error dict

---

## Patterns

**Suite Execution Pattern:**
```python
# Define suite map
suite_map = {
    'config_unit': _run_config_unit_suite,
    'config_integration': _run_config_integration_suite
}

# Get runner
runner = suite_map.get(suite_name)
if not runner:
    return {'success': False, 'error': f'Unknown suite: {suite_name}'}

# Execute
results = runner(**kwargs)
```

**Test Module Mapping:**
```python
# Map test name prefix to module
test_modules = {
    'test_config_': 'test_config_unit',
    'test_gateway_': 'test_config_gateway'
}

# Find module
for prefix, mod in test_modules.items():
    if test_name.startswith(prefix):
        module_name = mod
        break
```

**Lazy Import Pattern:**
```python
# Import only when needed
try:
    from test import run_config_unit_tests
    return run_config_unit_tests()
except ImportError:
    return {'success': False, 'error': 'test_config_unit not available'}
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** TEST (INT-15)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From test package (preferred)
from test import run_test_suite, run_single_test, run_component_tests

# From test_core directly (for testing)
from test.test_core import run_test_suite
```

---

## Dependencies

**Internal:**
- test.test_scenarios (lazy import)
- test.test_performance (lazy import)
- gateway (execute_operation, GatewayInterface)

**External:**
- time (timing measurements)
- typing (type hints)

---

## Related Files

**Test Modules:**
- test_scenarios.py - Error scenario tests
- test_performance.py - Performance tests
- test_lambda_modes.py - Lambda mode tests

**Interface:**
- interface_test.py - TEST interface router

**Gateway:**
- gateway_wrappers_test.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version migrated from test framework
- run_test_suite() with 6 suite types
- run_single_test() with module mapping
- run_component_tests() for interface testing
- test_component_operation() with scenarios
- Lazy imports for test modules
- Suite timing measurements
