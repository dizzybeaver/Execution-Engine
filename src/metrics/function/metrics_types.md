# metrics_types.py - Type Reference

**Version:** 2025-12-11_1  
**Module:** metrics/metrics_types.py  
**Purpose:** Metrics type definitions and data structures  
**Lines:** 61

---

## Data Classes

### ResponseMetrics

**Purpose:** Track response metrics and statistics

**Type:** Dataclass

**Definition:**
```python
@dataclass
class ResponseMetrics:
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    timeout_responses: int = 0
    cached_responses: int = 0
    fallback_responses: int = 0
    avg_response_time_ms: float = 0.0
    fastest_response_ms: float = float('inf')
    slowest_response_ms: float = 0.0
    cache_hit_rate: float = 0.0
```

**Fields:**
- `total_responses` - Total number of responses (default: 0)
- `successful_responses` - Number of successful responses (default: 0)
- `error_responses` - Number of error responses (default: 0)
- `timeout_responses` - Number of timeout responses (default: 0)
- `cached_responses` - Number of cached responses (default: 0)
- `fallback_responses` - Number of fallback responses (default: 0)
- `avg_response_time_ms` - Average response time in milliseconds (default: 0.0)
- `fastest_response_ms` - Fastest response time in milliseconds (default: inf)
- `slowest_response_ms` - Slowest response time in milliseconds (default: 0.0)
- `cache_hit_rate` - Cache hit rate percentage (default: 0.0)

**Methods:**

#### success_rate()

**Purpose:** Calculate success rate percentage

**Signature:**
```python
def success_rate(self) -> float
```

**Returns:** `float` - Success rate as percentage (0-100)

**Behavior:**
1. Use safe_divide() helper
2. Divide successful_responses by total_responses
3. Multiply by 100 to get percentage
4. Return 0.0 if total_responses is 0

**Usage:**
```python
from metrics.metrics_types import ResponseMetrics

metrics = ResponseMetrics(
    total_responses=100,
    successful_responses=95,
    error_responses=5
)

rate = metrics.success_rate()
print(f"Success rate: {rate:.2f}%")  # Output: Success rate: 95.00%
```

**Creation:**
```python
from metrics.metrics_types import ResponseMetrics

# Default (all zeros)
metrics = ResponseMetrics()

# With initial values
metrics = ResponseMetrics(
    total_responses=100,
    successful_responses=95,
    error_responses=5,
    avg_response_time_ms=45.2
)

# Update fields
metrics.total_responses += 1
metrics.successful_responses += 1
```

**Use Cases:**
- Tracking Lambda function responses
- Monitoring API success rates
- Analyzing error patterns
- Performance monitoring

**Memory:** ~80 bytes per instance

---

### HTTPClientMetrics

**Purpose:** Track HTTP client request statistics

**Type:** Dataclass

**Definition:**
```python
@dataclass
class HTTPClientMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    requests_by_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
```

**Fields:**
- `total_requests` - Total number of requests made (default: 0)
- `successful_requests` - Number of successful requests (2xx status) (default: 0)
- `failed_requests` - Number of failed requests (non-2xx status) (default: 0)
- `avg_response_time_ms` - Average response time in milliseconds (default: 0.0)
- `total_response_time_ms` - Total cumulative response time (default: 0.0)
- `requests_by_method` - Count of requests per HTTP method (default: empty defaultdict)
- `requests_by_status` - Count of requests per status code (default: empty defaultdict)

**Creation:**
```python
from metrics.metrics_types import HTTPClientMetrics

# Default (all zeros)
metrics = HTTPClientMetrics()

# With initial values
metrics = HTTPClientMetrics(
    total_requests=100,
    successful_requests=95,
    failed_requests=5
)

# Accessing dictionaries
metrics.requests_by_method['GET'] += 1
metrics.requests_by_status[200] += 1

# Calculate average
if metrics.total_requests > 0:
    metrics.avg_response_time_ms = metrics.total_response_time_ms / metrics.total_requests
```

**Usage Example:**
```python
from metrics.metrics_types import HTTPClientMetrics

metrics = HTTPClientMetrics()

# Record request
metrics.total_requests += 1
metrics.requests_by_method['GET'] += 1
metrics.requests_by_status[200] += 1
metrics.successful_requests += 1
metrics.total_response_time_ms += 45.2

# Update average
metrics.avg_response_time_ms = metrics.total_response_time_ms / metrics.total_requests

# Analyze
print(f"Total requests: {metrics.total_requests}")
print(f"Success rate: {metrics.successful_requests / metrics.total_requests * 100:.2f}%")
print(f"GET requests: {metrics.requests_by_method['GET']}")
print(f"200 responses: {metrics.requests_by_status[200]}")
```

**Use Cases:**
- HTTP client monitoring
- API performance tracking
- Request method distribution analysis
- Status code distribution analysis

**Memory:** 
- Base: ~60 bytes
- Per method entry: ~50 bytes
- Per status entry: ~50 bytes
- Typical: ~500 bytes (5-10 methods, 5-10 status codes)

---

### CircuitBreakerMetrics

**Purpose:** Track circuit breaker state and events

**Type:** Dataclass

**Definition:**
```python
@dataclass
class CircuitBreakerMetrics:
    circuit_name: str = ""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_opens: int = 0
    half_open_attempts: int = 0
    current_state: str = "closed"
```

**Fields:**
- `circuit_name` - Circuit breaker identifier (default: empty string)
- `total_calls` - Total number of calls through circuit (default: 0)
- `successful_calls` - Number of successful calls (default: 0)
- `failed_calls` - Number of failed calls (default: 0)
- `circuit_opens` - Number of times circuit opened (default: 0)
- `half_open_attempts` - Number of half-open test attempts (default: 0)
- `current_state` - Current circuit state: "closed", "open", "half_open" (default: "closed")

**Creation:**
```python
from metrics.metrics_types import CircuitBreakerMetrics

# Default
metrics = CircuitBreakerMetrics()

# With circuit name
metrics = CircuitBreakerMetrics(circuit_name="ha_api")

# Full initialization
metrics = CircuitBreakerMetrics(
    circuit_name="ha_api",
    total_calls=100,
    successful_calls=95,
    failed_calls=5,
    circuit_opens=1,
    current_state="closed"
)
```

**Usage Example:**
```python
from metrics.metrics_types import CircuitBreakerMetrics

# Create circuit metrics
metrics = CircuitBreakerMetrics(circuit_name="ha_api")

# Record successful call
metrics.total_calls += 1
metrics.successful_calls += 1

# Record failed call
metrics.total_calls += 1
metrics.failed_calls += 1

# Circuit opens
if metrics.failed_calls > threshold:
    metrics.circuit_opens += 1
    metrics.current_state = "open"

# Half-open test
if time_elapsed > timeout:
    metrics.current_state = "half_open"
    metrics.half_open_attempts += 1

# Calculate failure rate
failure_rate = metrics.failed_calls / metrics.total_calls * 100
print(f"Failure rate: {failure_rate:.2f}%")
print(f"Circuit opened {metrics.circuit_opens} times")
print(f"Current state: {metrics.current_state}")
```

**Circuit States:**
- **closed** - Normal operation, requests pass through
- **open** - Circuit tripped, requests blocked
- **half_open** - Testing if service recovered

**Use Cases:**
- Monitoring circuit breaker health
- Tracking service failures
- Analyzing recovery patterns
- Alert thresholds

**Memory:** ~100 bytes per instance

---

## Usage Patterns

### Tracking Responses
```python
from metrics.metrics_types import ResponseMetrics

metrics = ResponseMetrics()

# Successful response
metrics.total_responses += 1
metrics.successful_responses += 1
metrics.avg_response_time_ms = (
    (metrics.avg_response_time_ms * (metrics.total_responses - 1) + duration_ms) 
    / metrics.total_responses
)

# Error response
metrics.total_responses += 1
metrics.error_responses += 1

# Check success rate
if metrics.success_rate() < 95.0:
    print("WARNING: Success rate below 95%")
```

### HTTP Client Monitoring
```python
from metrics.metrics_types import HTTPClientMetrics

metrics = HTTPClientMetrics()

# Record request
method = 'GET'
status = 200
duration = 45.2

metrics.total_requests += 1
metrics.requests_by_method[method] += 1
metrics.requests_by_status[status] += 1
metrics.total_response_time_ms += duration

if 200 <= status < 300:
    metrics.successful_requests += 1
else:
    metrics.failed_requests += 1

# Update average
metrics.avg_response_time_ms = metrics.total_response_time_ms / metrics.total_requests

# Analyze distribution
for method, count in metrics.requests_by_method.items():
    percentage = count / metrics.total_requests * 100
    print(f"{method}: {percentage:.2f}%")
```

### Circuit Breaker Tracking
```python
from metrics.metrics_types import CircuitBreakerMetrics

metrics = CircuitBreakerMetrics(circuit_name="external_api")

# Record call result
def record_call(success: bool):
    metrics.total_calls += 1
    if success:
        metrics.successful_calls += 1
    else:
        metrics.failed_calls += 1
        
    # Check if should open
    failure_rate = metrics.failed_calls / metrics.total_calls
    if failure_rate > 0.5:  # 50% threshold
        metrics.circuit_opens += 1
        metrics.current_state = "open"

# Record call
record_call(success=True)
record_call(success=False)

# Check state
if metrics.current_state == "open":
    print("Circuit breaker is OPEN - blocking requests")
```

---

## Dependencies

**Internal:**
- `metrics.metrics_helper` - safe_divide() for success_rate()

**External:**
- `dataclasses` - dataclass, field decorators
- `typing` - Dict type hint
- `collections` - defaultdict for dictionary fields

---

## Performance

**Creation:** ~0.1-0.2ms per instance  
**Field access:** ~0.01ms (direct attribute access)  
**success_rate():** ~0.05-0.1ms (calls safe_divide)  
**Memory per instance:**
- ResponseMetrics: ~80 bytes
- HTTPClientMetrics: ~500 bytes (typical with data)
- CircuitBreakerMetrics: ~100 bytes

---

## Thread Safety

**Lambda environment:** Single-threaded execution  
**Instance safety:** Safe to modify in single-threaded context  
**No locks required:** AP-08, DEC-04 compliant  
**No shared state:** Each instance independent
