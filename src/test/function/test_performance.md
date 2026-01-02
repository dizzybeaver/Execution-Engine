# test_performance.py

**Version:** 2025-12-08_1  
**Module:** TEST Interface  
**Layer:** Core  
**Lines:** 130

---

## Purpose

Performance testing and benchmarking. Measures operation timing, component performance, and generates performance statistics.

---

## Functions

### test_operation_performance()

**Purpose:** Test operation performance with specified iterations

**Signature:**
```python
def test_operation_performance(
    operation: Callable,
    iterations: int = 100,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `operation` - Callable to test (function reference)
- `iterations` - Number of iterations to run (default: 100)
- `**kwargs` - Parameters to pass to operation

**Returns:**
```python
{
    'success': bool,        # True if test completed
    'iterations': int,      # Number of iterations run
    'avg_ms': float,        # Average time per operation
    'min_ms': float,        # Minimum time observed
    'max_ms': float,        # Maximum time observed
    'total_ms': float,      # Total time for all iterations
    'error': str            # Error message (if failed)
}
```

**Behavior:**
1. Initialize timing list
2. For each iteration:
   - Record start time
   - Execute operation with kwargs
   - Calculate elapsed time in milliseconds
   - Append to timing list
3. Calculate statistics (avg, min, max, total)
4. Return performance summary

**Performance:** Depends on operation and iteration count

**Usage:**
```python
from test import test_operation_performance
from gateway import cache_get

# Test cache_get performance
result = test_operation_performance(
    cache_get,
    iterations=100,
    key='test.key'
)

print(f"Average: {result['avg_ms']:.2f}ms")
print(f"Min: {result['min_ms']:.2f}ms")
print(f"Max: {result['max_ms']:.2f}ms")
```

**With Lambda Function:**
```python
# Test anonymous operation
result = test_operation_performance(
    lambda: gateway.log_info('test'),
    iterations=50
)
```

**Error Handling:**
Returns error dict if operation fails:
```python
{
    'success': False,
    'error': 'Operation failed: ValueError: invalid parameter'
}
```

**Statistics Calculation:**
```python
avg_time = sum(times) / len(times)
min_time = min(times)
max_time = max(times)
total_time = sum(times)
```

---

### test_component_performance()

**Purpose:** Test component performance patterns

**Signature:**
```python
def test_component_performance(component: str, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `component` - Interface component name (e.g., 'CONFIG', 'CACHE')
- `**kwargs` - Component-specific parameters

**Returns:**
```python
{
    'success': bool,        # True if test completed
    'component': str,       # Component tested
    'operations': Dict,     # Performance by operation
    'message': str          # Info message (if no tests)
}
```

**Operations Dict Structure:**
```python
{
    'operation_name': {
        'avg_ms': float,    # Average time
        'min_ms': float,    # Minimum time
        'max_ms': float     # Maximum time
    }
}
```

**Predefined Tests by Component:**
```python
operations = {
    'CONFIG': [
        ('get_parameter', {'key': 'test', 'default': 'value'})
    ],
    'CACHE': [
        ('cache_get', {'key': 'test'})
    ],
    'LOGGING': [
        ('log_info', {'message': 'test'})
    ]
}
```

**Behavior:**
1. Resolve interface from component name
2. Look up predefined operations for component
3. For each operation (50 iterations):
   - Execute via execute_operation()
   - Record timing
   - Calculate statistics
4. Return performance summary by operation

**Performance:** ~500ms per component (50 iterations × operations)

**Usage:**
```python
from test import test_component_performance

# Test CACHE performance
results = test_component_performance('CACHE')

if results['success']:
    print(f"Component: {results['component']}")
    for op, stats in results['operations'].items():
        print(f"  {op}:")
        print(f"    Avg: {stats['avg_ms']:.2f}ms")
        print(f"    Min: {stats['min_ms']:.2f}ms")
        print(f"    Max: {stats['max_ms']:.2f}ms")
```

**Error Handling:**
- Returns message if no tests defined for component
- Silently skips failed operations (doesn't stop suite)
- Returns `{'success': False, 'error': ...}` if interface not found

---

### benchmark_operation()

**Purpose:** Benchmark single operation execution

**Signature:**
```python
def benchmark_operation(func: Callable, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `func` - Function to benchmark
- `**kwargs` - Function parameters

**Returns:**
```python
{
    'success': bool,        # True if completed
    'duration_ms': float,   # Execution time
    'result': Any,          # Function result (if success)
    'error': str            # Error message (if failed)
}
```

**Behavior:**
1. Record start time
2. Execute function with kwargs
3. Calculate duration in milliseconds
4. Return timing and result

**Performance:** Single execution (typically 1-100ms)

**Usage:**
```python
from test import benchmark_operation
from gateway import cache_get

# Benchmark single operation
result = benchmark_operation(cache_get, key='test.key')

if result['success']:
    print(f"Duration: {result['duration_ms']:.2f}ms")
    print(f"Result: {result['result']}")
else:
    print(f"Failed: {result['error']}")
```

**With Complex Operations:**
```python
def complex_operation(entity_id):
    state = gateway.cache_get(f'ha_entity_{entity_id}')
    if not state:
        state = fetch_from_ha(entity_id)
        gateway.cache_set(f'ha_entity_{entity_id}', state, ttl=300)
    return state

result = benchmark_operation(complex_operation, entity_id='light.kitchen')
```

**Error Handling:**
Returns error dict with timing if function fails:
```python
{
    'success': False,
    'duration_ms': 5.23,
    'error': 'ValueError: invalid entity_id'
}
```

---

### run_performance_tests()

**Purpose:** Run all performance tests

**Signature:**
```python
def run_performance_tests(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Test-specific parameters

**Returns:**
```python
{
    'success': bool,        # True if suite completed
    'total_tests': int,     # Number of tests run
    'results': Dict,        # Test results
    'error': str            # Error message (if failed)
}
```

**Behavior:**
1. Lazy import test_config_performance
2. Call run_config_performance_tests()
3. Return comprehensive performance results

**Performance:** ~1-3 seconds (depends on test count)

**Usage:**
```python
from test import run_performance_tests

# Run all performance tests
results = run_performance_tests()

print(f"Total tests: {results['total_tests']}")
for test_name, result in results['results'].items():
    print(f"  {test_name}: {result['avg_ms']:.2f}ms avg")
```

**Error Handling:**
Returns error dict if test module not available:
```python
{
    'success': False,
    'error': 'test_config_performance not available'
}
```

---

## Performance Metrics

**Timing Precision:**
- Uses `time.time()` for millisecond precision
- Resolution: ~1ms on most platforms
- Overhead: <0.1ms per measurement

**Statistical Measures:**
```python
avg_ms = sum(times) / len(times)  # Mean
min_ms = min(times)                # Minimum
max_ms = max(times)                # Maximum
total_ms = sum(times)              # Total time
```

**Iteration Guidelines:**
- Quick operations (< 1ms): 100-1000 iterations
- Medium operations (1-10ms): 50-100 iterations
- Slow operations (> 10ms): 10-50 iterations

---

## Performance Testing Patterns

**Basic Performance Test:**
```python
from test import test_operation_performance

result = test_operation_performance(
    my_function,
    iterations=100,
    param1='value1'
)
```

**Component Benchmarking:**
```python
from test import test_component_performance

results = test_component_performance('CACHE')
cache_get_avg = results['operations']['cache_get']['avg_ms']
```

**Single Operation Benchmark:**
```python
from test import benchmark_operation

result = benchmark_operation(expensive_operation, data=large_dataset)
print(f"Operation took {result['duration_ms']:.2f}ms")
```

**Performance Regression Testing:**
```python
# Establish baseline
baseline = test_operation_performance(cache_get, iterations=100)

# ... make changes ...

# Test again
current = test_operation_performance(cache_get, iterations=100)

# Compare
speedup = baseline['avg_ms'] / current['avg_ms']
print(f"Performance change: {speedup:.2f}x")
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** TEST (INT-15)  
**Gateway Access:** Via gateway.execute_operation()

**Import Pattern:**
```python
# From test package
from test import (
    test_operation_performance,
    test_component_performance,
    benchmark_operation
)

# Direct import (for testing)
from test.test_performance import run_performance_tests
```

---

## Dependencies

**Internal:**
- gateway (execute_operation, GatewayInterface)
- test.test_config_performance (lazy import)

**External:**
- time (timing measurements)
- typing (type hints)

---

## Related Files

**Test Modules:**
- test_core.py - Test orchestration
- test_scenarios.py - Error scenario tests
- test_lambda_modes.py - Lambda mode tests

**Performance Testing:**
- test_config_performance.py - Config-specific performance tests

**Interface:**
- interface_test.py - TEST interface router

**Gateway:**
- gateway_wrappers_test.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version migrated from test_config_performance.py
- test_operation_performance() with iteration support
- test_component_performance() for interface benchmarking
- benchmark_operation() for single execution timing
- run_performance_tests() suite runner
- Statistical measures (avg, min, max, total)
- Error handling with timing preservation
