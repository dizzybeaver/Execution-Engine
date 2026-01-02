# test_scenarios.py

**Version:** 2025-12-08_1  
**Module:** TEST Interface  
**Layer:** Core  
**Lines:** 200

---

## Purpose

Error scenario testing. Validates error handling, parameter validation, and graceful degradation across all interfaces.

---

## Functions

### test_invalid_operation()

**Purpose:** Test that invalid operations return proper errors

**Signature:**
```python
def test_invalid_operation(interface_name: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `interface_name` - Interface to test (e.g., 'CACHE', 'CONFIG')
- `**kwargs` - Additional test parameters (optional)

**Returns:**
```python
{
    'success': bool,        # True if error handled correctly
    'message': str,         # Success message (if passed)
    'error': str            # Error details (if failed)
}
```

**Behavior:**
1. Resolve interface from name via GatewayInterface
2. Execute non-existent operation via execute_operation()
3. Expect ValueError with informative message
4. Validate error message contains 'unknown', 'invalid', or 'operation'
5. Return success if error handled correctly

**Expected Error Patterns:**
- "Unknown operation: invalid_operation_that_does_not_exist"
- "Invalid operation for CACHE interface"
- "Operation not found: invalid_operation_that_does_not_exist"

**Performance:** ~10-20ms

**Usage:**
```python
from test import test_invalid_operation

# Test CACHE interface error handling
result = test_invalid_operation('CACHE')

if result['success']:
    print(f"✓ Invalid operation handled: {result['message']}")
else:
    print(f"✗ Error handling failed: {result['error']}")
```

**Error Handling:**
- Returns `{'success': False, 'error': ...}` if interface not found
- Returns `{'success': False, 'error': ...}` if error message not informative
- Returns `{'success': False, 'error': ...}` if exception type unexpected

**Test Expectations:**
```python
# Expected behavior
try:
    execute_operation(GatewayInterface.CACHE, 'invalid_op')
except ValueError as e:
    # Should contain: 'unknown' or 'invalid' or 'operation'
    assert 'unknown' in str(e).lower() or 'invalid' in str(e).lower()
```

---

### test_missing_parameters()

**Purpose:** Test that missing required parameters are handled

**Signature:**
```python
def test_missing_parameters(interface_name: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `interface_name` - Interface to test
- `**kwargs` - Additional test parameters (optional)

**Returns:**
```python
{
    'success': bool,        # True if validation works
    'message': str,         # Success message (if passed)
    'error': str            # Error details (if failed)
}
```

**Behavior:**
1. Resolve interface from name
2. Look up known operation with required parameters
3. Call operation with `None` or missing parameters
4. Expect ValueError, TypeError, or KeyError
5. Return success if validation catches missing parameters

**Parameter Tests by Interface:**
```python
operations_with_params = {
    'CONFIG': ('get_parameter', {'key': None}),
    'CACHE': ('cache_get', {'key': None}),
    'LOGGING': ('log_info', {'message': None}),
    'METRICS': ('track_time', {'metric_name': None}),
    'SECURITY': ('encrypt', {'data': None}),
}
```

**Performance:** ~10-20ms

**Usage:**
```python
from test import test_missing_parameters

# Test CONFIG parameter validation
result = test_missing_parameters('CONFIG')

if result['success']:
    print(f"✓ Parameter validation works: {result['message']}")
else:
    print(f"✗ Validation failed: {result['error']}")
```

**Error Handling:**
- Returns `{'success': True, 'message': ...}` if no params to test
- Returns `{'success': True, 'message': ...}` if error dict returned
- Returns `{'success': True, 'message': ...}` if exception raised
- Returns `{'success': False, 'error': ...}` if validation missing

**Test Expectations:**
```python
# Expected behavior
try:
    execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=None)
except (ValueError, TypeError, KeyError) as e:
    # Should catch missing/invalid parameter
    assert 'parameter' in str(e).lower() or 'required' in str(e).lower()
```

---

### test_graceful_degradation()

**Purpose:** Test that system degrades gracefully when dependencies fail

**Signature:**
```python
def test_graceful_degradation(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Test-specific parameters (optional)

**Returns:**
```python
{
    'success': bool,        # True if degradation works
    'message': str,         # Success message (if passed)
    'error': str            # Error details (if failed)
}
```

**Behavior:**
1. Test CONFIG interface with fallback parameter
2. Call get_parameter() with default value
3. Verify result is not None (fallback worked)
4. Return success if system continues with fallback

**Test Scenario:**
Tests that when cache or parameter store unavailable, system falls back to provided default value instead of failing.

**Performance:** ~10-20ms

**Usage:**
```python
from test import test_graceful_degradation

# Test fallback behavior
result = test_graceful_degradation()

if result['success']:
    print(f"✓ Graceful degradation working")
else:
    print(f"✗ System not degrading gracefully: {result['error']}")
```

**Error Handling:**
- Returns `{'success': True, 'message': ...}` if fallback works
- Returns `{'success': False, 'error': ...}` if no fallback
- Returns `{'success': False, 'error': ...}` if exception raised

**Test Expectations:**
```python
# Expected behavior
result = execute_operation(
    GatewayInterface.CONFIG,
    'get_parameter',
    key='test.parameter',
    default='fallback_value'
)
assert result is not None  # Should get fallback, not None
```

---

### run_error_scenario_tests()

**Purpose:** Run error scenario tests on specified interfaces

**Signature:**
```python
def run_error_scenario_tests(
    interfaces: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `interfaces` - List of interface names to test (default: all)
- `**kwargs` - Additional test parameters

**Returns:**
```python
{
    'total_tests': int,     # Number of tests run
    'passed': int,          # Tests passed
    'failed': int,          # Tests failed
    'tests': List[Dict]     # Individual test results
}
```

**Default Interfaces:**
```python
interfaces = [
    'CONFIG',
    'CACHE',
    'LOGGING',
    'METRICS',
    'SECURITY',
    'HTTP',
    'WEBSOCKET'
]
```

**Behavior:**
1. Use default interfaces if not specified
2. For each interface:
   - Run test_invalid_operation()
   - Run test_missing_parameters()
   - Record results
3. Aggregate pass/fail counts
4. Return test suite summary

**Performance:** ~100-300ms (depends on interface count)

**Usage:**
```python
from test import run_error_scenario_tests

# Test all interfaces
results = run_error_scenario_tests()
print(f"Passed: {results['passed']}/{results['total_tests']}")

# Test specific interfaces
results = run_error_scenario_tests(interfaces=['CACHE', 'CONFIG'])

for test in results['tests']:
    status = "✓" if test['success'] else "✗"
    print(f"{status} {test['interface']}.{test['test']}: {test['message']}")
```

**Error Handling:**
Individual test failures are recorded in results, not raised:
```python
{
    'interface': 'CACHE',
    'test': 'invalid_operation',
    'success': False,
    'message': 'Exception: ...'
}
```

---

## Test Result Structure

**Success Result:**
```python
{
    'success': True,
    'message': 'Invalid operation error handled correctly: Unknown operation'
}
```

**Failure Result:**
```python
{
    'success': False,
    'error': 'Error message not informative: Some error'
}
```

**Suite Result:**
```python
{
    'total_tests': 14,
    'passed': 12,
    'failed': 2,
    'tests': [
        {
            'interface': 'CACHE',
            'test': 'invalid_operation',
            'success': True,
            'message': 'Invalid operation error handled correctly'
        },
        {
            'interface': 'CACHE',
            'test': 'missing_parameters',
            'success': True,
            'message': 'Missing parameter caught by validation'
        }
    ]
}
```

---

## Error Validation Patterns

**Invalid Operation Validation:**
```python
try:
    execute_operation(interface, 'invalid_op')
except ValueError as e:
    error_message = str(e).lower()
    if 'unknown' in error_message or 'invalid' in error_message:
        return {'success': True, 'message': f'Handled: {str(e)}'}
```

**Missing Parameter Validation:**
```python
try:
    execute_operation(interface, operation, **invalid_params)
except (ValueError, TypeError, KeyError) as e:
    return {'success': True, 'message': f'Validation caught: {str(e)}'}
```

**Graceful Degradation Pattern:**
```python
result = execute_operation(
    interface,
    'get_parameter',
    key='test.parameter',
    default='fallback_value'
)
if result is not None:
    return {'success': True, 'message': 'Fallback working'}
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** TEST (INT-15)  
**Gateway Access:** Via gateway.execute_operation()

**Import Pattern:**
```python
# From test package
from test import test_invalid_operation, test_missing_parameters

# Direct import (for testing)
from test.test_scenarios import run_error_scenario_tests
```

---

## Dependencies

**Internal:**
- gateway (execute_operation, GatewayInterface)

**External:**
- typing (type hints)

---

## Related Files

**Test Modules:**
- test_core.py - Test orchestration
- test_performance.py - Performance tests
- test_lambda_modes.py - Lambda mode tests

**Interface:**
- interface_test.py - TEST interface router

**Gateway:**
- gateway_wrappers_test.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version migrated from test_error_scenarios.py
- test_invalid_operation() for error handling validation
- test_missing_parameters() for parameter validation
- test_graceful_degradation() for fallback behavior
- run_error_scenario_tests() for suite execution
- Error pattern validation
- Comprehensive error message checking
