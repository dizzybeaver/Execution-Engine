# get_connection_statistics()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_state  
**Type:** Statistics Function

---

## Purpose

Get enhanced HTTP client statistics including calculated metrics like success rate, failure rate, and retry configuration. Enhanced version of `HTTPClientCore.get_stats()`.

---

## Signature

```python
def get_connection_statistics(**kwargs) -> Dict[str, Any]:
```

---

## Parameters

- **kwargs** (`Dict[str, Any]`) - Additional options (reserved)

---

## Returns

**Type:** `Dict[str, Any]`

**Success Response:**
```python
{
    'success': True,
    'message': 'Statistics retrieved',
    'data': {
        # Raw counts
        'requests': int,
        'successful': int,
        'failed': int,
        'retries': int,
        
        # Calculated rates
        'success_rate': float,    # 0.00-100.00
        'failure_rate': float,    # 0.00-100.00
        
        # Configuration
        'retry_config': {
            'max_attempts': int,
            'backoff_base_ms': int,
            'backoff_multiplier': float,
            'retriable_status_codes': set
        }
    }
}
```

**Error Response:**
```python
{
    'success': False,
    'error': str,
    'error_type': 'STATISTICS_ERROR'
}
```

---

## Statistics Included

### Raw Counts

**requests**
- Total HTTP requests attempted
- Includes original + retry attempts

**successful**
- Requests with 2xx status codes
- HTTP 200-299 range

**failed**
- Requests with non-2xx status or exceptions
- Includes 4xx, 5xx, network errors

**retries**
- Number of retry attempts
- Does NOT include original attempt

### Calculated Rates

**success_rate**
- Formula: `(successful / requests) * 100`
- Range: 0.00-100.00
- Rounded to 2 decimal places
- Returns 0.0 if no requests

**failure_rate**
- Formula: `(failed / requests) * 100`
- Range: 0.00-100.00
- Rounded to 2 decimal places
- Returns 0.0 if no requests

### Retry Configuration

**max_attempts** - Maximum retry attempts  
**backoff_base_ms** - Base backoff milliseconds  
**backoff_multiplier** - Exponential multiplier  
**retriable_status_codes** - Set of retriable status codes

---

## Usage

### Basic Usage

```python
from http_client.http_client_state import get_connection_statistics

result = get_connection_statistics()

if result['success']:
    stats = result['data']
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Failure rate: {stats['failure_rate']}%")
    print(f"Total requests: {stats['requests']}")
```

### Monitoring

```python
import gateway

# Get statistics periodically
stats_result = get_connection_statistics()

if stats_result['success']:
    stats = stats_result['data']
    
    # Check health
    if stats['success_rate'] < 90.0:
        gateway.log_error(f"Low success rate: {stats['success_rate']}%")
    
    # Check retry rate
    retry_rate = (stats['retries'] / stats['requests']) * 100
    if retry_rate > 10.0:
        gateway.log_warning(f"High retry rate: {retry_rate:.2f}%")
```

### CloudWatch Metrics

```python
result = get_connection_statistics()

if result['success']:
    stats = result['data']
    
    # Put metrics
    gateway.metrics_put('HTTPSuccessRate', stats['success_rate'], 'Percent')
    gateway.metrics_put('HTTPFailureRate', stats['failure_rate'], 'Percent')
    gateway.metrics_put('HTTPRequests', stats['requests'], 'Count')
```

---

## Example Outputs

### Healthy Client

```python
{
    'success': True,
    'message': 'Statistics retrieved',
    'data': {
        'requests': 1000,
        'successful': 980,
        'failed': 20,
        'retries': 15,
        'success_rate': 98.00,
        'failure_rate': 2.00,
        'retry_config': {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2.0,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504}
        }
    }
}
```

### High Failure Rate

```python
{
    'success': True,
    'message': 'Statistics retrieved',
    'data': {
        'requests': 100,
        'successful': 70,
        'failed': 30,
        'retries': 20,
        'success_rate': 70.00,
        'failure_rate': 30.00,
        'retry_config': {...}
    }
}
```

### Fresh Client (No Requests)

```python
{
    'success': True,
    'message': 'Statistics retrieved',
    'data': {
        'requests': 0,
        'successful': 0,
        'failed': 0,
        'retries': 0,
        'success_rate': 0.0,
        'failure_rate': 0.0,
        'retry_config': {...}
    }
}
```

---

## Calculated Metrics

### Success Rate

```python
success_rate = (successful / requests) * 100 if requests > 0 else 0.0
success_rate = round(success_rate, 2)
```

**Interpretation:**
- 95-100%: Excellent
- 90-95%: Good
- 80-90%: Concerning
- <80%: Critical

### Failure Rate

```python
failure_rate = (failed / requests) * 100 if requests > 0 else 0.0
failure_rate = round(failure_rate, 2)
```

**Interpretation:**
- 0-5%: Excellent
- 5-10%: Acceptable
- 10-20%: Concerning
- >20%: Critical

### Retry Rate

```python
# Not included in response, but can be calculated
retry_rate = (retries / requests) * 100 if requests > 0 else 0.0
```

**Interpretation:**
- 0-5%: Normal
- 5-15%: Elevated
- 15-30%: High
- >30%: Excessive

### Average Retries Per Request

```python
# Not included in response, but can be calculated
avg_retries = retries / requests if requests > 0 else 0.0
```

---

## Difference from get_stats()

### HTTPClientCore.get_stats()
- **Returns:** Raw dictionary
- **Rates:** Not calculated
- **Config:** Not included
- **Response:** Direct dict
- **Use:** Internal/low-level

### get_connection_statistics()
- **Returns:** Standardized response
- **Rates:** Calculated and rounded
- **Config:** Included
- **Response:** Gateway format
- **Use:** Monitoring/reporting

---

## Monitoring Patterns

### Alerting

```python
stats_result = get_connection_statistics()

if stats_result['success']:
    stats = stats_result['data']
    
    # Alert on low success rate
    if stats['success_rate'] < 90.0:
        send_alert(f"HTTP success rate: {stats['success_rate']}%")
    
    # Alert on high retries
    retry_rate = (stats['retries'] / stats['requests']) * 100
    if retry_rate > 20.0:
        send_alert(f"HTTP retry rate: {retry_rate:.2f}%")
```

### Logging

```python
stats_result = get_connection_statistics()

if stats_result['success']:
    stats = stats_result['data']
    
    gateway.log_info("HTTP client statistics", **{
        'success_rate': stats['success_rate'],
        'failure_rate': stats['failure_rate'],
        'requests': stats['requests'],
        'retries': stats['retries']
    })
```

### Dashboard Data

```python
def get_http_health_metrics():
    """Get metrics for dashboard."""
    result = get_connection_statistics()
    
    if not result['success']:
        return None
    
    stats = result['data']
    
    return {
        'health': 'healthy' if stats['success_rate'] >= 95.0 else 'degraded',
        'success_rate': stats['success_rate'],
        'failure_rate': stats['failure_rate'],
        'total_requests': stats['requests'],
        'retry_rate': (stats['retries'] / stats['requests'] * 100) if stats['requests'] > 0 else 0.0
    }
```

---

## Performance

**Time:** <1ms (stats retrieval + calculations)  
**Memory:** Minimal (~1KB response)  
**Thread-safe:** Yes (Lambda single-threaded)

---

## Error Scenarios

| Scenario | Behavior | Success |
|----------|----------|---------|
| Normal operation | Return full statistics | True |
| Client not initialized | May fail | False |
| Exception during retrieval | Log error, return error response | False |

---

## Gateway Integration

```python
import gateway

# Via interface (when implemented)
result = gateway.execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'get_statistics'
)

# Direct call
from http_client.http_client_state import get_connection_statistics
result = get_connection_statistics()
```

---

## Related Functions

- `HTTPClientCore.get_stats()` - Raw statistics
- `get_client_state()` - Includes basic stats
- `configure_http_retry()` - Configure retry behavior
- `gateway.create_success_response()` - Response format

---

## Notes

- **Enhanced version:** Adds calculated rates
- **Includes config:** Retry configuration included
- **Standardized format:** Gateway response format
- **Monitoring-ready:** Designed for metrics/alerting
- **Zero division safe:** Returns 0.0 when no requests
- **Rounding:** Rates rounded to 2 decimal places

---

**Lines:** 320
