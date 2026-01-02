# metrics_core.py - Function Reference

**Version:** 2025-12-11_1  
**Module:** metrics/metrics_core.py  
**Purpose:** Core metrics implementation function reference  
**Lines:** 299

---

## Public API Functions

### record_metric()

**Purpose:** Record a metric value with optional dimensions

**Signature:**
```python
def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool
```

**Parameters:**
- `name` - Metric name (e.g., 'api.calls', 'cache.hits')
- `value` - Metric value (float)
- `dimensions` - Optional dimension tags (e.g., {'endpoint': '/users', 'method': 'GET'})
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_metric('api.calls', 1.0, {'endpoint': '/users'})
```

---

### increment_counter()

**Purpose:** Increment a counter by specified value

**Signature:**
```python
def increment_counter(name: str, value: int = 1, **kwargs) -> int
```

**Parameters:**
- `name` - Counter name
- `value` - Increment amount (default: 1)
- `**kwargs` - Additional parameters (reserved)

**Returns:** `int` - New counter value

**Usage:**
```python
import metrics
count = metrics.increment_counter('requests', 1)
```

---

### get_stats()

**Purpose:** Get all metrics statistics

**Signature:**
```python
def get_stats(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:** 
```python
{
    'metrics': Dict[str, float],      # All recorded metrics
    'counters': Dict[str, int],       # All counters
    'gauges': Dict[str, float],       # All gauges
    'histograms': Dict[str, List]     # All histograms
}
```

**Usage:**
```python
import metrics
stats = metrics.get_stats()
print(f"Total metrics: {len(stats['metrics'])}")
```

---

### record_operation_metric()

**Purpose:** Record operation execution metrics

**Signature:**
```python
def record_operation_metric(
    operation_name: str, 
    success: bool = True, 
    duration_ms: float = 0, 
    error_type: Optional[str] = None, 
    **kwargs
) -> bool
```

**Parameters:**
- `operation_name` - Operation identifier
- `success` - Whether operation succeeded (default: True)
- `duration_ms` - Operation duration in milliseconds (default: 0)
- `error_type` - Error type if failed (optional)
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_operation_metric(
    'process_data',
    success=True,
    duration_ms=45.2
)
```

---

### record_error_response()

**Purpose:** Record error response metrics

**Signature:**
```python
def record_error_response(
    error_type: str, 
    severity: str = 'medium', 
    category: str = 'internal', 
    **kwargs
) -> bool
```

**Parameters:**
- `error_type` - Type of error (e.g., 'ValidationError', 'NotFound')
- `severity` - Error severity ('low', 'medium', 'high', 'critical')
- `category` - Error category ('internal', 'external', 'user')
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_error_response('ValidationError', severity='low', category='user')
```

---

### record_cache_metric()

**Purpose:** Record cache operation metrics

**Signature:**
```python
def record_cache_metric(
    operation_name: str, 
    hit: bool = False, 
    miss: bool = False, 
    duration_ms: float = 0, 
    **kwargs
) -> bool
```

**Parameters:**
- `operation_name` - Cache operation name ('get', 'set', 'delete')
- `hit` - Whether cache hit occurred
- `miss` - Whether cache miss occurred
- `duration_ms` - Operation duration in milliseconds
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_cache_metric('get', hit=True, duration_ms=2.5)
```

---

### record_api_metric()

**Purpose:** Record API call metrics

**Signature:**
```python
def record_api_metric(
    api_name: str, 
    endpoint: str, 
    success: bool = True, 
    duration_ms: float = 0, 
    status_code: Optional[int] = None, 
    **kwargs
) -> bool
```

**Parameters:**
- `api_name` - API identifier (e.g., 'home_assistant', 'alexa')
- `endpoint` - API endpoint path
- `success` - Whether call succeeded
- `duration_ms` - Call duration in milliseconds
- `status_code` - HTTP status code (optional)
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_api_metric('home_assistant', '/api/states', success=True, duration_ms=125.3, status_code=200)
```

---

### record_response_metric()

**Purpose:** Record response type metrics

**Signature:**
```python
def record_response_metric(
    response_type: str, 
    success: bool = True, 
    error_type: Optional[str] = None, 
    **kwargs
) -> bool
```

**Parameters:**
- `response_type` - Type of response ('success', 'error', 'timeout', 'cached')
- `success` - Whether response successful
- `error_type` - Error type if failed (optional)
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_response_metric('success', success=True)
```

---

### record_http_metric()

**Purpose:** Record HTTP request metrics

**Signature:**
```python
def record_http_metric(
    method: str, 
    url: str, 
    status_code: int, 
    duration_ms: float, 
    response_size: int = 0, 
    **kwargs
) -> bool
```

**Parameters:**
- `method` - HTTP method ('GET', 'POST', 'PUT', 'DELETE')
- `url` - Request URL
- `status_code` - HTTP status code
- `duration_ms` - Request duration in milliseconds
- `response_size` - Response size in bytes (default: 0)
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_http_metric('GET', 'https://api.example.com/users', 200, 45.2, 1024)
```

---

### record_circuit_breaker_event()

**Purpose:** Record circuit breaker state change

**Signature:**
```python
def record_circuit_breaker_event(
    circuit_name: str, 
    event_type: str, 
    success: bool = True, 
    **kwargs
) -> bool
```

**Parameters:**
- `circuit_name` - Circuit breaker identifier
- `event_type` - Event type ('open', 'half_open', 'closed', 'call')
- `success` - Whether event was successful
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_circuit_breaker_event('ha_api', 'open', success=False)
```

---

### get_response_metrics()

**Purpose:** Get response metrics summary

**Signature:**
```python
def get_response_metrics(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
{
    'total_responses': int,
    'successful_responses': int,
    'error_responses': int,
    'success_rate': float  # Percentage
}
```

**Usage:**
```python
import metrics
response_metrics = metrics.get_response_metrics()
print(f"Success rate: {response_metrics['success_rate']:.2f}%")
```

---

### get_http_metrics()

**Purpose:** Get HTTP request metrics summary

**Signature:**
```python
def get_http_metrics(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
{
    'total_requests': int,
    'successful_requests': int,
    'failed_requests': int,
    'avg_response_time_ms': float,
    'requests_by_method': Dict[str, int],
    'requests_by_status': Dict[int, int]
}
```

**Usage:**
```python
import metrics
http_metrics = metrics.get_http_metrics()
print(f"Total requests: {http_metrics['total_requests']}")
```

---

### get_circuit_breaker_metrics()

**Purpose:** Get circuit breaker metrics

**Signature:**
```python
def get_circuit_breaker_metrics(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `circuit_name` - Specific circuit name (optional, None = all circuits)
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
# Single circuit:
{
    'circuit_name': str,
    'total_calls': int,
    'successful_calls': int,
    'failed_calls': int,
    'circuit_opens': int,
    'half_open_attempts': int
}
# All circuits (if circuit_name=None):
{
    'circuit1': {...},
    'circuit2': {...}
}
```

**Usage:**
```python
import metrics
cb_metrics = metrics.get_circuit_breaker_metrics('ha_api')
print(f"Failed calls: {cb_metrics['failed_calls']}")
```

---

### record_dispatcher_timing()

**Purpose:** Record dispatcher operation timing

**Signature:**
```python
def record_dispatcher_timing(
    interface_name: str, 
    operation_name: str, 
    duration_ms: float, 
    **kwargs
) -> bool
```

**Parameters:**
- `interface_name` - Interface identifier (e.g., 'CACHE', 'HTTP_CLIENT')
- `operation_name` - Operation name within interface
- `duration_ms` - Operation duration in milliseconds
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.record_dispatcher_timing('CACHE', 'get', 2.3)
```

---

### get_dispatcher_stats()

**Purpose:** Get dispatcher timing statistics

**Signature:**
```python
def get_dispatcher_stats(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
{
    'INTERFACE.operation': {
        'count': int,
        'avg_ms': float,
        'min_ms': float,
        'max_ms': float
    }
}
```

**Usage:**
```python
import metrics
dispatcher_stats = metrics.get_dispatcher_stats()
for key, stats in dispatcher_stats.items():
    print(f"{key}: {stats['avg_ms']:.2f}ms avg")
```

---

### get_operation_metrics()

**Purpose:** Get operation-level metrics

**Signature:**
```python
def get_operation_metrics(**kwargs) -> Dict[str, Any]
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
{
    'operation_name': {
        'count': int,
        'avg_ms': float,
        'total_ms': float
    }
}
```

**Usage:**
```python
import metrics
op_metrics = metrics.get_operation_metrics()
for op, stats in op_metrics.items():
    print(f"{op}: {stats['count']} calls, {stats['avg_ms']:.2f}ms avg")
```

---

### get_performance_report()

**Purpose:** Get comprehensive performance analysis

**Signature:**
```python
def get_performance_report(slow_threshold_ms: float = 100.0, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `slow_threshold_ms` - Threshold for slow operation detection (default: 100.0)
- `**kwargs` - Additional parameters (reserved)

**Returns:**
```python
{
    'timestamp': str,              # ISO format
    'metrics_version': str,
    'slow_threshold_ms': float,
    'operations': {
        'op_name': {
            'count': int,
            'avg_ms': float,
            'min_ms': float,
            'max_ms': float,
            'p50_ms': float,       # Median
            'p95_ms': float,       # 95th percentile
            'p99_ms': float        # 99th percentile
        }
    },
    'slow_operations': [
        {
            'operation': str,
            'p95_ms': float,
            'max_ms': float
        }
    ],
    'slow_operation_count': int
}
```

**Usage:**
```python
import metrics
report = metrics.get_performance_report(slow_threshold_ms=150.0)
print(f"Slow operations: {report['slow_operation_count']}")
for op in report['slow_operations']:
    print(f"  {op['operation']}: {op['p95_ms']:.2f}ms (p95)")
```

---

### reset_metrics()

**Purpose:** Reset all metrics to initial state

**Signature:**
```python
def reset_metrics(**kwargs) -> bool
```

**Parameters:**
- `**kwargs` - Additional parameters (reserved)

**Returns:** `bool` - True if successful

**Usage:**
```python
import metrics
metrics.reset_metrics()  # Clear all metrics
```

---

## Private Class: MetricsCore

### __init__()

**Purpose:** Initialize metrics core singleton

**Initializes:**
- `_metrics` - defaultdict(float) for metric values
- `_counters` - defaultdict(int) for counters
- `_gauges` - defaultdict(float) for gauges
- `_histograms` - defaultdict(list) for histograms
- `_response_metrics` - ResponseMetrics instance
- `_http_metrics` - HTTPClientMetrics instance
- `_circuit_breaker_metrics` - Dict for circuit breaker stats
- `_dispatcher_timings` - defaultdict(list) for dispatcher timings
- `_dispatcher_call_counts` - defaultdict(int) for call counts
- `_operation_metrics` - defaultdict for operation tracking

---

### _build_metric_key()

**Purpose:** Build metric storage key from name and dimensions

**Signature:**
```python
def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str
```

**Parameters:**
- `name` - Metric name
- `dimensions` - Optional dimensions dictionary

**Returns:** `str` - Formatted key (e.g., "api.calls[endpoint=/users,method=GET]")

**Example:**
```python
# name='api.calls', dimensions={'endpoint': '/users', 'method': 'GET'}
# Returns: 'api.calls[endpoint=/users,method=GET]'
```

---

## Module Variables

### _MANAGER

**Type:** MetricsCore  
**Purpose:** SINGLETON instance of MetricsCore  
**Scope:** Module-private  
**Usage:** All public functions delegate to _MANAGER

---

## Performance

**Initialization:** ~1-2ms (SINGLETON pattern)  
**record_metric():** ~0.1-0.5ms (dict insert)  
**increment_counter():** ~0.1-0.3ms (dict update)  
**get_stats():** ~1-5ms (dict copy operations)  
**get_performance_report():** ~5-20ms (percentile calculations)

---

## Memory Usage

**Base overhead:** ~10KB (empty MetricsCore)  
**Per metric:** ~100-200 bytes  
**Per operation history:** ~50 bytes per recorded duration  
**Typical usage:** 50-100KB for 1000 operations

---

## Thread Safety

**Lambda environment:** Single-threaded execution (no threading concerns)  
**SINGLETON:** Safe in single-threaded context  
**No locks required:** AP-08, DEC-04 compliant
