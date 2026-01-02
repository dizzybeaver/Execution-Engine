# HTTPClientCore.make_request()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_manager  
**Type:** Instance Method

---

## Purpose

Execute HTTP request with retry logic and rate limiting. Handles request execution, error recovery, and statistics tracking.

---

## Signature

```python
def make_request(self, method: str, url: str, correlation_id: str = None,
                **kwargs) -> Dict[str, Any]:
```

---

## Parameters

- **method** (`str`) - HTTP method (GET, POST, PUT, DELETE, etc.)
- **url** (`str`) - Target URL for request
- **correlation_id** (`str`, optional) - Correlation ID for debug tracking
- **kwargs** (`Dict[str, Any]`) - Additional parameters:
  - `headers` - Custom headers dictionary
  - `json` - JSON data to send (auto-encodes)
  - `body` - Raw body data
  - `timeout` - Request timeout override

---

## Returns

**Type:** `Dict[str, Any]`

**Success Response:**
```python
{
    'success': True,
    'status_code': int,        # HTTP status code
    'data': Any,               # Parsed response data
    'headers': Dict[str, str]  # Response headers
}
```

**Error Response:**
```python
{
    'success': False,
    'error': str,              # Error message
    'error_type': str,         # Exception type name
    'rate_limited': bool       # True if rate limited (optional)
}
```

**Retry Exhausted:**
```python
{
    'success': False,
    'error': 'Max retry attempts exceeded',
    'attempts': int            # Number of attempts made
}
```

---

## Behavior

1. **Retry Loop**
   - Iterate up to `max_attempts` (default: 3)
   - Call `_execute_request()` for each attempt

2. **Execute Request**
   - Rate limit check (500 ops/sec)
   - Debug logging (if enabled)
   - HTTP request execution
   - Response parsing
   - Statistics update

3. **Handle Result**
   - If success → Return immediately
   - If rate limited → Return immediately (no retry)
   - If retriable error → Sleep with backoff, retry
   - If non-retriable → Return error

4. **Retry Logic**
   - Check if status code is retriable (408, 429, 500, 502, 503, 504)
   - Calculate exponential backoff
   - Sleep for backoff duration
   - Increment retry counter
   - Continue to next attempt

5. **Max Retries Exceeded**
   - Return error response with attempt count

---

## Usage

```python
from http_client.http_client_manager import get_http_client_manager

client = get_http_client_manager()

# Simple GET request
result = client.make_request('GET', 'https://api.example.com/data')

# POST with JSON and correlation tracking
result = client.make_request(
    'POST',
    'https://api.example.com/create',
    correlation_id='abc123',
    json={'key': 'value'}
)

# With custom headers
result = client.make_request(
    'GET',
    'https://api.example.com/data',
    headers={'Authorization': 'Bearer token123'}
)
```

---

## Retry Configuration

**Default Config:**
```python
{
    'max_attempts': 3,
    'backoff_base_ms': 100,
    'backoff_multiplier': 2.0,
    'retriable_status_codes': {408, 429, 500, 502, 503, 504}
}
```

**Backoff Calculation:**
```python
delay_ms = backoff_base_ms * (backoff_multiplier ** attempt)
delay_seconds = delay_ms / 1000.0

# Attempt 0: 100ms
# Attempt 1: 200ms
# Attempt 2: 400ms
```

---

## Rate Limiting

**Limit:** 500 operations per second  
**Window:** 1000ms (1 second)  
**Implementation:** `deque` with automatic eviction

**Rate Limit Response:**
```python
{
    'success': False,
    'error': 'Rate limit exceeded',
    'error_type': 'RateLimitError',
    'rate_limited': True
}
```

**Note:** Rate limit errors are NOT retried

---

## Debug Integration

**Debug Logging:**
```python
gateway.debug_log(correlation_id, 'HTTP', 'Request start',
                 method=method, url=url[:50])
gateway.debug_log(correlation_id, 'HTTP', 'Request success',
                 status=status_code)
gateway.debug_log(correlation_id, 'HTTP', 'Request exception',
                 error=str(e))
```

**Timing Measurement:**
```python
with gateway.debug_timing(correlation_id, 'HTTP', f'{method} {url[:30]}'):
    response = self.http.request(...)
```

**Scope:** `HTTP`

---

## Performance

**Typical Timings:**
- Fast response: 50-200ms
- Slow response: 500-2000ms
- With retries: +100ms, +200ms, +400ms per retry

**Statistics Tracked:**
- `requests` - Total request count
- `successful` - Successful requests
- `failed` - Failed requests
- `retries` - Retry attempts

---

## Error Scenarios

| Scenario | Behavior | Retry? |
|----------|----------|--------|
| Rate limit exceeded | Return rate limit error | No |
| Network timeout | Return error | Yes (if 408) |
| Server error (500) | Return error | Yes |
| Bad request (400) | Return error | No |
| Success (200-299) | Return success | N/A |
| Connection error | Return exception error | No |

---

## Related Functions

- `_execute_request()` - Single request execution (internal)
- `_check_rate_limit()` - Rate limit validation (internal)
- `_is_retriable_error()` - Retry decision (internal)
- `_calculate_backoff()` - Backoff calculation (internal)

---

## Notes

- **REF:** LESS-21 (Rate limiting for DoS protection)
- Automatically retries transient errors
- Does not retry client errors (4xx except 408, 429)
- Always retries server errors (5xx)
- Exponential backoff prevents thundering herd
- Debug integration for request tracing

---

**Lines:** 220
