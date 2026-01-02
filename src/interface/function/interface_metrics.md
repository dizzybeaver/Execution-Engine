# interface_metrics.py

**Version:** 2025-12-11_1  
**Module:** METRICS  
**Layer:** Interface  
**Interface:** INT-04  
**Lines:** ~75

---

## Purpose

Metrics interface router following SUGA pattern for performance and operational metrics.

---

## Main Function

### execute_metrics_operation()

**Signature:**
```python
def execute_metrics_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Execute metrics operation via SUGA pattern

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (varies by operation)

**Operations:**
- `record` / `record_metric` - Record generic metric
- `increment` / `increment_counter` - Increment counter
- `get_stats` - Get metrics statistics
- `record_operation` / `record_operation_metric` - Record operation metric
- `record_error` / `record_error_response` - Record error metric
- `record_cache` / `record_cache_metric` - Record cache metric
- `record_api` / `record_api_metric` - Record API metric
- `record_response` / `record_response_metric` - Record response metric
- `record_http` / `record_http_metric` - Record HTTP metric
- `record_circuit_breaker` / `record_circuit_breaker_metric` - Record circuit breaker event
- `get_response_metrics` - Get response metrics
- `get_http_metrics` - Get HTTP metrics
- `get_circuit_breaker_metrics` - Get circuit breaker metrics
- `record_dispatcher_timing` - Record dispatcher timing
- `get_dispatcher_stats` / `get_dispatcher_metrics` - Get dispatcher stats
- `get_operation_metrics` - Get operation metrics
- `get_performance_report` - Get performance report
- `reset` / `reset_metrics` - Reset metrics

**Raises:**
- `ValueError` - If operation unknown

---

## Operations

### record / record_metric

**Purpose:** Record a generic metric

**Parameters:**
- `name` (str) - Metric name
- `value` (float) - Metric value
- `unit` (str, optional) - Metric unit
- `tags` (dict, optional) - Metric tags

**Usage:**
```python
execute_metrics_operation(
    'record',
    name='request_duration',
    value=45.2,
    unit='milliseconds',
    tags={'endpoint': '/api/users'}
)
```

---

### increment / increment_counter

**Purpose:** Increment a counter metric

**Parameters:**
- `name` (str) - Counter name
- `amount` (int, optional) - Amount to increment (default: 1)
- `tags` (dict, optional) - Counter tags

**Usage:**
```python
execute_metrics_operation(
    'increment',
    name='api_requests',
    amount=1,
    tags={'method': 'GET'}
)
```

---

### get_stats

**Purpose:** Get metrics statistics

**Parameters:** None

**Returns:** Dict with metrics stats:
- `total_metrics` - Total metrics recorded
- `metric_types` - Count by type
- `recording_duration_ms` - Average recording duration

**Usage:**
```python
stats = execute_metrics_operation('get_stats')
```

---

### record_operation / record_operation_metric

**Purpose:** Record operation metric with timing

**Parameters:**
- `operation_name` (str) - Operation name
- `duration_ms` (float) - Duration in milliseconds
- `success` (bool, optional) - Whether operation succeeded
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_operation',
    operation_name='user_login',
    duration_ms=125.3,
    success=True,
    tags={'user_type': 'premium'}
)
```

---

### record_error / record_error_response

**Purpose:** Record error metric

**Parameters:**
- `error_type` (str) - Error type/code
- `error_message` (str, optional) - Error message
- `severity` (str, optional) - Error severity
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_error',
    error_type='ValidationError',
    error_message='Invalid input',
    severity='medium'
)
```

---

### record_cache / record_cache_metric

**Purpose:** Record cache operation metric

**Parameters:**
- `operation` (str) - Cache operation (get, set, delete)
- `hit` (bool, optional) - Cache hit/miss
- `duration_ms` (float, optional) - Operation duration
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_cache',
    operation='get',
    hit=True,
    duration_ms=0.5
)
```

---

### record_api / record_api_metric

**Purpose:** Record API call metric

**Parameters:**
- `endpoint` (str) - API endpoint
- `method` (str) - HTTP method
- `status_code` (int) - Response status code
- `duration_ms` (float) - Request duration
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_api',
    endpoint='/api/users',
    method='GET',
    status_code=200,
    duration_ms=45.2
)
```

---

### record_response / record_response_metric

**Purpose:** Record response metric

**Parameters:**
- `status_code` (int) - HTTP status code
- `duration_ms` (float) - Response duration
- `size_bytes` (int, optional) - Response size
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_response',
    status_code=200,
    duration_ms=125.3,
    size_bytes=1024
)
```

---

### record_http / record_http_metric

**Purpose:** Record HTTP request metric

**Parameters:**
- `url` (str) - Request URL
- `method` (str) - HTTP method
- `status_code` (int) - Response status
- `duration_ms` (float) - Request duration
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_http',
    url='https://api.example.com/data',
    method='POST',
    status_code=201,
    duration_ms=234.5
)
```

---

### record_circuit_breaker / record_circuit_breaker_metric

**Purpose:** Record circuit breaker event

**Parameters:**
- `breaker_name` (str) - Circuit breaker name
- `event` (str) - Event type (opened, closed, half_open)
- `tags` (dict, optional) - Additional tags

**Usage:**
```python
execute_metrics_operation(
    'record_circuit_breaker',
    breaker_name='external_api',
    event='opened'
)
```

---

### get_response_metrics

**Purpose:** Get response metrics

**Parameters:** None

**Returns:** Dict with response metrics by status code

**Usage:**
```python
metrics = execute_metrics_operation('get_response_metrics')
```

---

### get_http_metrics

**Purpose:** Get HTTP metrics

**Parameters:** None

**Returns:** Dict with HTTP metrics by endpoint/method

**Usage:**
```python
metrics = execute_metrics_operation('get_http_metrics')
```

---

### get_circuit_breaker_metrics

**Purpose:** Get circuit breaker metrics

**Parameters:** None

**Returns:** Dict with circuit breaker events by breaker

**Usage:**
```python
metrics = execute_metrics_operation('get_circuit_breaker_metrics')
```

---

### record_dispatcher_timing

**Purpose:** Record dispatcher timing

**Parameters:**
- `interface_name` (str) - Interface name
- `operation_name` (str) - Operation name
- `duration_ms` (float) - Duration in milliseconds

**Usage:**
```python
execute_metrics_operation(
    'record_dispatcher_timing',
    interface_name='CacheCore',
    operation_name='get',
    duration_ms=1.2
)
```

---

### get_dispatcher_stats / get_dispatcher_metrics

**Purpose:** Get dispatcher statistics

**Parameters:** None

**Returns:** Dict with dispatcher stats by interface

**Usage:**
```python
stats = execute_metrics_operation('get_dispatcher_stats')
```

---

### get_operation_metrics

**Purpose:** Get operation metrics

**Parameters:** None

**Returns:** Dict with operation metrics

**Usage:**
```python
metrics = execute_metrics_operation('get_operation_metrics')
```

---

### get_performance_report

**Purpose:** Get comprehensive performance report

**Parameters:** None

**Returns:** Dict with performance report:
- `operations` - Operation metrics
- `cache` - Cache metrics
- `http` - HTTP metrics
- `errors` - Error metrics
- `circuit_breakers` - Circuit breaker metrics

**Usage:**
```python
report = execute_metrics_operation('get_performance_report')
```

---

### reset / reset_metrics

**Purpose:** Reset all metrics

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_metrics_operation('reset')
```

---

## Dispatch Dictionary

**Pattern:**
```python
DISPATCH = {
    'record': metrics.record_metric,
    'record_metric': metrics.record_metric,
    'increment': metrics.increment_counter,
    # ... all operations mapped
}
```

**Benefits:**
- O(1) operation lookup
- Operation aliases supported
- Clean separation of concerns

---

## Import Structure

```python
import metrics

# Lazy import at execution time
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Lazy Loading:** Metrics imported at function level  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Operation Aliases:** Multiple names for same operation  
✅ **Comprehensive Metrics:** Operations, cache, HTTP, errors, circuit breakers

---

## Related Files

- `/metrics/` - Metrics implementation
- `/gateway/wrappers/gateway_wrappers_metrics.py` - Gateway wrappers
- `/metrics/metrics_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
