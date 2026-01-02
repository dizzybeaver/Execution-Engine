# HTTPClientCore.get_stats()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_manager  
**Type:** Instance Method

---

## Purpose

Get HTTP client statistics including request counts, success/failure rates, and rate limiter state.

---

## Signature

```python
def get_stats(self) -> Dict[str, Any]:
```

---

## Parameters

**None**

---

## Returns

**Type:** `Dict[str, Any]`

**Structure:**
```python
{
    'requests': int,           # Total requests made
    'successful': int,         # Successful requests (2xx status)
    'failed': int,             # Failed requests
    'retries': int,            # Total retry attempts
    'rate_limited': int,       # Rate limit violations
    'rate_limiter_size': int   # Current rate limiter window size
}
```

---

## Statistics Tracked

### requests
**Type:** `int`  
**Description:** Total number of HTTP requests attempted  
**Includes:** All requests (successful, failed, retried)  
**Updated:** Every request attempt

### successful
**Type:** `int`  
**Description:** Requests with 2xx status codes  
**Range:** 200-299 status codes  
**Updated:** On successful response

### failed
**Type:** `int`  
**Description:** Requests with non-2xx status or exceptions  
**Includes:** 4xx, 5xx, connection errors  
**Updated:** On failed response or exception

### retries
**Type:** `int`  
**Description:** Number of retry attempts made  
**Note:** Does NOT include original attempt  
**Updated:** Each retry attempt (not the first try)

### rate_limited
**Type:** `int`  
**Description:** Number of operations rejected due to rate limiting  
**Includes:** Both request operations and reset operations  
**Updated:** Each rate limit violation

### rate_limiter_size
**Type:** `int`  
**Description:** Current number of timestamps in rate limit window  
**Range:** 0-500  
**Meaning:** Number of operations in the last second

---

## Usage

```python
from http_client.http_client_manager import get_http_client_manager

client = get_http_client_manager()

# Get statistics
stats = client.get_stats()

print(f"Total requests: {stats['requests']}")
print(f"Success rate: {stats['successful'] / stats['requests'] * 100:.1f}%")
print(f"Retry rate: {stats['retries'] / stats['requests'] * 100:.1f}%")
print(f"Rate limited: {stats['rate_limited']}")
```

---

## Calculated Metrics

### Success Rate
```python
success_rate = (successful / requests) * 100
# Example: (95 / 100) * 100 = 95.0%
```

### Failure Rate
```python
failure_rate = (failed / requests) * 100
# Example: (5 / 100) * 100 = 5.0%
```

### Retry Rate
```python
retry_rate = (retries / requests) * 100
# Example: (10 / 100) * 100 = 10.0%
```

### Average Retries Per Request
```python
avg_retries = retries / requests
# Example: 10 / 100 = 0.1 retries per request
```

---

## Via Gateway

```python
import gateway

# Get full state including stats
state = gateway.http_get_state()
# Returns:
{
    'exists': True,
    'client_type': 'http_client_manager',
    'state': 'initialized',
    'instance_id': int,
    'stats': {
        'requests': int,
        'successful': int,
        'failed': int,
        'retries': int,
        'rate_limited': int,
        'rate_limiter_size': int
    }
}

# Get enhanced statistics
stats = gateway.execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'get_statistics'
)
# Returns: Enhanced stats with rates and retry config
```

---

## Statistics Lifecycle

**Created:** When HTTPClientCore instance created  
**Updated:** During request operations  
**Reset:** When `client.reset()` called  
**Persisted:** While singleton instance exists

**Lambda Container Lifecycle:**
- Statistics accumulate across invocations (warm container)
- Reset when container recycled (cold start)
- Reset when `reset()` called explicitly

---

## Example Outputs

### Healthy Client
```python
{
    'requests': 1000,
    'successful': 980,
    'failed': 20,
    'retries': 15,
    'rate_limited': 0,
    'rate_limiter_size': 45
}
# 98% success rate, 1.5% retry rate, no rate limiting
```

### Under Load
```python
{
    'requests': 5000,
    'successful': 4500,
    'failed': 500,
    'retries': 300,
    'rate_limited': 50,
    'rate_limiter_size': 500
}
# 90% success rate, 6% retry rate, rate limiter at max
```

### Rate Limited
```python
{
    'requests': 600,
    'successful': 500,
    'failed': 100,
    'retries': 0,
    'rate_limited': 100,
    'rate_limiter_size': 500
}
# 100 requests rejected at rate limit (500 ops/sec)
```

---

## Performance

**Time:** <0.1ms (dictionary copy)  
**Memory:** ~200 bytes (6 integers)  
**Thread-safe:** Yes (Lambda is single-threaded)

---

## Monitoring

**CloudWatch Metrics:**
```python
from gateway import metrics_put

stats = client.get_stats()

# Put metrics
metrics_put('HTTPRequests', stats['requests'], 'Count')
metrics_put('HTTPSuccessRate', 
           (stats['successful'] / stats['requests']) * 100, 
           'Percent')
metrics_put('HTTPRetryRate',
           (stats['retries'] / stats['requests']) * 100,
           'Percent')
```

**Logging:**
```python
from gateway import log_info

stats = client.get_stats()
log_info("HTTP client statistics", **stats)
```

---

## Related Functions

- `reset()` - Reset statistics to zero
- `get_client_state()` - Get state including stats
- `get_connection_statistics()` - Enhanced statistics with rates
- `_check_rate_limit()` - Updates rate_limited counter

---

## Notes

- Statistics are cumulative (not per-request)
- Reset only via `reset()` or singleton deletion
- Rate limiter size indicates current load
- Used for monitoring and debugging
- All counters are integers (no floats)

---

**Lines:** 240
