# HTTPClientCore.reset()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_manager  
**Type:** Instance Method

---

## Purpose

Reset HTTP client state including connection pool, statistics, and rate limiter. Enables lifecycle management for singleton pattern.

---

## Signature

```python
def reset(self) -> bool:
```

---

## Parameters

**None**

---

## Returns

**Type:** `bool`

**Values:**
- `True` - Reset successful
- `False` - Reset failed (rate limited or exception)

---

## Behavior

1. **Rate Limit Check**
   - Check if operation is within rate limits
   - If rate limited → Return False immediately

2. **Close Existing Pool**
   - Call `self.http.clear()` to close connections
   - Releases connection pool resources

3. **Reset Statistics**
   - Set `requests`, `successful`, `failed`, `retries` to 0

4. **Reset Rate Limiter**
   - Clear rate limiter deque
   - Reset `_rate_limited_count` to 0

5. **Recreate Connection Pool**
   - Read `HOME_ASSISTANT_VERIFY_SSL` environment variable
   - Create new `PoolManager` with fresh configuration
   - Apply same SSL settings as original

6. **Return Success**
   - Return True if all steps completed
   - Log error and return False if exception occurs

---

## Usage

```python
from http_client.http_client_manager import get_http_client_manager

client = get_http_client_manager()

# Reset client state
success = client.reset()

if success:
    print("Client reset successfully")
else:
    print("Client reset failed (rate limited or error)")

# Via gateway
import gateway
result = gateway.http_reset()
# Returns: {'success': bool, 'message': str}
```

---

## What Gets Reset

**Connection Pool:**
- All existing connections closed
- New PoolManager created
- Fresh connection pool with maxsize=10

**Statistics:**
```python
{
    'requests': 0,
    'successful': 0,
    'failed': 0,
    'retries': 0
}
```

**Rate Limiter:**
- Deque cleared (all timestamps removed)
- Rate limited counter reset to 0
- Fresh rate limit window starts

**SSL Configuration:**
- Re-reads `HOME_ASSISTANT_VERIFY_SSL` environment variable
- Applies current SSL settings to new pool

---

## When to Use

**Container Lifecycle:**
- Lambda container initialization
- Long-running container maintenance
- After configuration changes

**Testing:**
- Between test cases
- Resetting statistics
- Clearing connection state

**Error Recovery:**
- After SSL configuration change
- After connection pool exhaustion
- After extended idle period

---

## Rate Limiting

Reset operation is **rate limited** (500 ops/sec).

If rate limit exceeded:
- Returns `False` immediately
- No reset performed
- Rate limiter NOT cleared (prevents abuse)

---

## Performance

**Typical Time:** 5-10ms  
**Operations:**
- Pool clear: ~2ms
- Dictionary resets: <1ms
- Pool recreation: ~3-5ms

**Impact:**
- Active connections closed
- In-flight requests may fail
- New requests use fresh pool

---

## Error Scenarios

| Scenario | Behavior | Return |
|----------|----------|--------|
| Rate limit exceeded | No reset performed | False |
| Pool clear fails | Log error, continue | False |
| Pool creation fails | Log error | False |
| Normal operation | Full reset | True |

---

## Gateway Integration

```python
# Via gateway wrapper
import gateway

result = gateway.http_reset()
# Returns:
{
    'success': bool,
    'message': 'HTTP client reset successful' | 'HTTP client reset failed'
}
```

---

## Singleton Implications

**Before Reset:**
- Singleton instance exists
- Has accumulated statistics
- May have active connections

**After Reset:**
- Same singleton instance
- Fresh statistics (all zeros)
- New connection pool
- No active connections

**Note:** Reset does NOT destroy singleton. To fully reset:
```python
# Delete singleton
import gateway
gateway.singleton_delete('http_client_manager')

# Next access creates fresh instance
client = get_http_client_manager()
```

---

## Related Functions

- `get_http_client_manager()` - Get singleton instance
- `_check_rate_limit()` - Rate limit validation
- `get_stats()` - Get current statistics
- `gateway.http_reset()` - Gateway wrapper

---

## Notes

- **REF:** LESS-18 (Reset operation for lifecycle management)
- Safe to call multiple times
- Rate limited to prevent abuse
- Preserves singleton instance
- SSL settings re-read from environment
- Error handling logs to gateway

---

**Lines:** 180
