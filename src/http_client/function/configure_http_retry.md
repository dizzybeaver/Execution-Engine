# configure_http_retry()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_state  
**Type:** Configuration Function

---

## Purpose

Configure HTTP retry behavior for the client. Sets maximum attempts, backoff timing, and multiplier for exponential backoff.

---

## Signature

```python
def configure_http_retry(max_attempts: int = 3, 
                        backoff_base_ms: int = 100,
                        backoff_multiplier: float = 2.0, 
                        **kwargs) -> Dict[str, Any]:
```

---

## Parameters

- **max_attempts** (`int`) - Maximum retry attempts
  - Range: 1-10
  - Default: 3
  - Total attempts = original + retries

- **backoff_base_ms** (`int`) - Base backoff time in milliseconds
  - Range: 50-1000
  - Default: 100
  - First retry delay

- **backoff_multiplier** (`float`) - Backoff growth multiplier
  - Range: 1.0-5.0
  - Default: 2.0
  - Exponential growth factor

- **kwargs** (`Dict[str, Any]`) - Additional options (reserved)

---

## Returns

**Type:** `Dict[str, Any]`

**Success Response:**
```python
{
    'success': True,
    'message': 'HTTP retry configured',
    'data': {
        'max_attempts': int,
        'backoff_base_ms': int,
        'backoff_multiplier': float
    }
}
```

**Validation Error:**
```python
{
    'success': False,
    'error': str,              # Validation error message
    'error_type': 'VALIDATION_ERROR'
}
```

**Configuration Error:**
```python
{
    'success': False,
    'error': str,              # Error message
    'error_type': 'CONFIGURATION_ERROR'
}
```

---

## Validation Rules

### max_attempts
**Range:** 1-10  
**Reason:** Prevent excessive retries  
**Error:** "max_attempts must be between 1 and 10"

### backoff_base_ms
**Range:** 50-1000  
**Reason:** Balance responsiveness vs server load  
**Error:** "backoff_base_ms must be between 50 and 1000"

### backoff_multiplier
**Range:** 1.0-5.0  
**Reason:** Prevent runaway delays  
**Error:** "backoff_multiplier must be between 1.0 and 5.0"

---

## Behavior

1. **Validate Parameters**
   - Check max_attempts range
   - Check backoff_base_ms range
   - Check backoff_multiplier range
   - Return error if invalid

2. **Get Current Client**
   - Call `get_http_client()`
   - Get singleton instance

3. **Update Configuration**
   - Modify `client._retry_config['max_attempts']`
   - Modify `client._retry_config['backoff_base_ms']`
   - Modify `client._retry_config['backoff_multiplier']`

4. **Log Configuration**
   - Log info with new values

5. **Return Success**
   - Include configured values in response

---

## Usage

### Default Configuration

```python
from http_client.http_client_state import configure_http_retry

# Use defaults (3 attempts, 100ms base, 2.0x multiplier)
result = configure_http_retry()

# Retry delays: 100ms, 200ms, 400ms
```

### Conservative Configuration

```python
# Fewer retries, longer delays
result = configure_http_retry(
    max_attempts=2,
    backoff_base_ms=500,
    backoff_multiplier=3.0
)

# Retry delays: 500ms, 1500ms
```

### Aggressive Configuration

```python
# More retries, shorter delays
result = configure_http_retry(
    max_attempts=5,
    backoff_base_ms=50,
    backoff_multiplier=1.5
)

# Retry delays: 50ms, 75ms, 112ms, 168ms, 252ms
```

### Via Gateway

```python
import gateway

result = gateway.execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'configure_retry',
    max_attempts=4,
    backoff_base_ms=200,
    backoff_multiplier=2.5
)
```

---

## Backoff Calculation

### Formula
```python
delay_ms = backoff_base_ms * (backoff_multiplier ** attempt)
delay_seconds = delay_ms / 1000.0
```

### Examples

**Default (100ms base, 2.0x):**
- Attempt 0: 100ms
- Attempt 1: 200ms
- Attempt 2: 400ms

**Conservative (500ms base, 3.0x):**
- Attempt 0: 500ms
- Attempt 1: 1500ms
- Attempt 2: 4500ms

**Aggressive (50ms base, 1.5x):**
- Attempt 0: 50ms
- Attempt 1: 75ms
- Attempt 2: 112ms
- Attempt 3: 168ms

---

## Configuration Scenarios

### High-Volume API
```python
# Quick retries, many attempts
configure_http_retry(
    max_attempts=5,
    backoff_base_ms=50,
    backoff_multiplier=1.5
)
# Total delay: 50+75+112+168+252 = 657ms
```

### Rate-Limited API
```python
# Longer delays, fewer attempts
configure_http_retry(
    max_attempts=3,
    backoff_base_ms=1000,
    backoff_multiplier=2.0
)
# Total delay: 1000+2000+4000 = 7000ms
```

### Critical API
```python
# Maximum retries, balanced delays
configure_http_retry(
    max_attempts=10,
    backoff_base_ms=200,
    backoff_multiplier=1.8
)
# Many attempts with reasonable delays
```

### Testing/Development
```python
# No retries for fast failure
configure_http_retry(
    max_attempts=1,
    backoff_base_ms=100,
    backoff_multiplier=2.0
)
# Fail immediately on error
```

---

## Retriable Status Codes

**Configuration does NOT change retriable codes:**
```python
{408, 429, 500, 502, 503, 504}
```

**Retriable:**
- 408 Request Timeout
- 429 Too Many Requests
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

**Not Retriable:**
- 4xx (except 408, 429) - Client errors
- 200-299 - Success (no retry needed)

---

## Performance Impact

### More Attempts
**Pros:** Higher success rate  
**Cons:** Longer maximum delay  
**Use:** Critical operations

### Fewer Attempts
**Pros:** Faster failure  
**Cons:** Lower success rate  
**Use:** Best-effort operations

### Longer Backoff
**Pros:** Gentler on server  
**Cons:** Slower recovery  
**Use:** Rate-limited APIs

### Shorter Backoff
**Pros:** Faster recovery  
**Cons:** May overwhelm server  
**Use:** Highly available APIs

---

## Lambda Timeout Considerations

**Lambda timeout:** 30 seconds  
**Consider total retry time:**

```python
# Calculate maximum retry time
total_time = sum(
    backoff_base_ms * (backoff_multiplier ** i) 
    for i in range(max_attempts - 1)
) / 1000.0

# Ensure: total_time < 25 seconds (buffer)
```

**Examples:**
- Default (3, 100ms, 2.0x): 700ms total
- Aggressive (10, 200ms, 1.8x): ~15 seconds total
- Conservative (3, 1000ms, 2.0x): 7 seconds total

---

## Error Handling

```python
result = configure_http_retry(max_attempts=15)

if not result['success']:
    print(f"Configuration error: {result['error']}")
    # Error: "max_attempts must be between 1 and 10"
```

---

## Related Functions

- `HTTPClientCore.make_request()` - Uses retry configuration
- `get_http_client_manager()` - Get client to configure
- `get_connection_statistics()` - View retry statistics
- `reset()` - Reset preserves retry config

---

## Notes

- **Runtime configuration:** Changes apply immediately
- **Singleton:** Configuration persists across requests
- **Reset preserved:** `client.reset()` does NOT reset retry config
- **Lambda lifecycle:** Configuration lost on cold start
- **Thread-safe:** Lambda is single-threaded
- **Validation:** All parameters validated before applying

---

**Lines:** 310
