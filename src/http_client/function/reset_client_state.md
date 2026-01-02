# reset_client_state()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_state  
**Type:** State Management Function

---

## Purpose

Reset HTTP client state by deleting singleton instance(s) from gateway registry. Enables complete client reset including statistics and configuration.

---

## Signature

```python
def reset_client_state(client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
```

---

## Parameters

- **client_type** (`str`, optional) - Specific client type to reset
  - If provided: Reset only that client type
  - If None: Reset all HTTP clients
  - Default: `None`
- **kwargs** (`Dict[str, Any]`) - Additional options (reserved)

---

## Returns

**Type:** `Dict[str, Any]`

**Single Client Reset:**
```python
{
    'success': bool,          # True if deleted
    'client_type': str,       # Client type reset
    'message': str            # Status message
}
```

**All Clients Reset:**
```python
{
    'success': True,
    'count': int,             # Number of clients reset
    'message': str            # Status message
}
```

**Error Response:**
```python
{
    'success': False,
    'error': str              # Error message
}
```

---

## Behavior

### Reset Specific Client

1. **Build Singleton Key**
   - Format: `f'http_client_{client_type}'`
   - Example: `'http_client_urllib3'`

2. **Delete from Singleton Registry**
   - Use `gateway.execute_operation(SINGLETON, 'delete', ...)`
   - Returns True if deleted, False if not found

3. **Log Result**
   - Success: Log info message
   - Not found: Return success=False

4. **Return Status**
   - Include client type and message

### Reset All Clients

1. **Iterate Known Client Types**
   - Try: `'http_client_manager'`
   - Try: `'http_client_urllib3'`

2. **Delete Each Client**
   - Count successful deletions
   - Continue even if some fail

3. **Log Total**
   - Log number of clients reset

4. **Return Count**
   - Include total count in response

---

## Usage

### Reset Specific Client

```python
from http_client.http_client_state import reset_client_state

# Reset urllib3 client
result = reset_client_state(client_type='urllib3')

if result['success']:
    print(f"Reset {result['client_type']}")
else:
    print("Client not found or already reset")
```

### Reset All Clients

```python
# Reset all HTTP clients
result = reset_client_state()

print(f"Reset {result['count']} client(s)")
# Example output: "Reset 2 client(s)"
```

### Via Gateway

```python
import gateway

# Reset all
result = gateway.http_reset_state()

# Reset specific
result = gateway.http_reset_state(client_type='http_client_manager')
```

---

## Difference from HTTPClientCore.reset()

### HTTPClientCore.reset()
- **Scope:** Resets client state (stats, pool, rate limiter)
- **Singleton:** Preserved (same instance)
- **Effect:** Fresh state, same object
- **Use:** Periodic maintenance, stat reset

### reset_client_state()
- **Scope:** Deletes singleton instance
- **Singleton:** Destroyed
- **Effect:** Next access creates new instance
- **Use:** Complete reset, config changes

---

## When to Use

### Use reset_client_state()

**Configuration Changes:**
- Environment variable changes
- SSL verification toggle
- Complete reconfiguration

**Memory Management:**
- Long-running Lambda containers
- Force garbage collection
- Resource cleanup

**Testing:**
- Between test suites
- Isolation between tests
- Fresh instance per test

### Use HTTPClientCore.reset()

**Statistics Reset:**
- Clear counters
- Fresh metrics
- Preserve configuration

**Connection Pool:**
- Close stale connections
- Reset connection state
- Keep singleton

**Periodic Maintenance:**
- Regular cleanup
- Rate limiter reset
- Quick reset

---

## Example Workflows

### Configuration Change

```python
import os
import gateway

# Change SSL setting
os.environ['HOME_ASSISTANT_VERIFY_SSL'] = 'false'

# Complete reset to apply change
gateway.http_reset_state()

# Next request uses new config
result = gateway.http_get(url)
```

### Test Isolation

```python
import http_client

def setup():
    """Reset before each test."""
    http_client.reset_client_state()

def test_http_request():
    """Test with fresh client."""
    client = http_client.get_http_client_manager()
    result = client.make_request('GET', url)
    assert result['success']
    
def teardown():
    """Clean up after test."""
    http_client.reset_client_state()
```

### Production Maintenance

```python
import gateway
import time

def periodic_reset():
    """Reset client every hour."""
    last_reset = time.time()
    
    while True:
        # ... handle requests ...
        
        # Reset every 3600 seconds
        if time.time() - last_reset > 3600:
            gateway.http_reset_state()
            last_reset = time.time()
```

---

## Performance

**Time:** ~1-2ms (singleton deletion)  
**Memory Impact:** Frees client instance (~500KB)  
**Next Access:** Creates fresh instance (~5ms)

---

## Error Scenarios

| Scenario | Behavior | Success |
|----------|----------|---------|
| Client exists | Delete from registry | True |
| Client not found | Log message | False |
| Multiple clients | Delete all found | True (with count) |
| Gateway unavailable | Exception caught | False (with error) |

---

## Gateway Integration

```python
# Via wrapper
import gateway
result = gateway.http_reset_state()

# Via interface
from gateway import execute_operation, GatewayInterface

result = execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'reset_state',
    client_type='urllib3'
)
```

---

## Logging

**Success:**
```python
log_info(f"Reset HTTP client state: {client_type}")
# Or
log_info(f"Reset {count} HTTP client(s)")
```

**Error:**
```python
log_error(f"Failed to reset client state: {e}", error=e)
```

---

## Related Functions

- `HTTPClientCore.reset()` - Reset client state (preserve singleton)
- `get_client_state()` - Query client state
- `get_http_client_manager()` - Get/create client
- `gateway.singleton_delete()` - Direct singleton deletion

---

## Notes

- **Destructive:** Deletes singleton instance
- **Next access:** Creates new instance with fresh state
- **Safe:** Error handling prevents crashes
- **Logging:** All operations logged
- **Testing:** Useful for test isolation
- **Production:** Use sparingly (prefer HTTPClientCore.reset())

---

**Lines:** 280
