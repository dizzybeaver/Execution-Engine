# get_client_state()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_state  
**Type:** State Query Function

---

## Purpose

Query HTTP client state via gateway singleton registry. Returns existence, initialization status, and statistics.

---

## Signature

```python
def get_client_state(client_type: str = 'urllib3', **kwargs) -> Dict[str, Any]:
```

---

## Parameters

- **client_type** (`str`, optional) - Client type to query
  - Default: `'urllib3'`
  - Common: `'urllib3'`, `'http_client_manager'`
- **kwargs** (`Dict[str, Any]`) - Additional options (reserved)

---

## Returns

**Type:** `Dict[str, Any]`

**Client Exists:**
```python
{
    'exists': True,
    'client_type': str,         # Queried client type
    'state': 'initialized',
    'instance_id': int,         # Python id() of instance
    'stats': {                  # If available
        'requests': int,
        'successful': int,
        'failed': int,
        'retries': int,
        'rate_limited': int,
        'rate_limiter_size': int
    }
}
```

**Client Not Found:**
```python
{
    'exists': False,
    'client_type': str,
    'state': 'not_initialized',
    'error': None
}
```

**Error Occurred:**
```python
{
    'exists': False,
    'client_type': str,
    'state': 'error',
    'error': str               # Error message
}
```

---

## Behavior

1. **Query Singleton Registry**
   - Check for `http_client_{client_type}` key
   - Use `gateway.execute_operation(SINGLETON, 'has', ...)`

2. **If Specific Client Exists**
   - Get client via `gateway.execute_operation(SINGLETON, 'get', ...)`
   - Build state info with instance_id
   - Add stats if client has `get_stats()` method
   - Return state info

3. **Fallback to Default Client**
   - Check for `'http_client_manager'` key
   - Same retrieval process
   - Return state info with actual client type

4. **No Client Found**
   - Return not_initialized state

5. **Error Handling**
   - Catch all exceptions
   - Log error via `gateway.log_error()`
   - Return error state

---

## Usage

```python
from http_client.http_client_state import get_client_state

# Check default client
state = get_client_state()

if state['exists']:
    print(f"Client initialized: {state['instance_id']}")
    print(f"Stats: {state.get('stats', {})}")
else:
    print("Client not initialized")

# Check specific client type
state = get_client_state(client_type='http_client_manager')

# Via gateway
import gateway
state = gateway.http_get_state()
```

---

## Client Types

### 'urllib3' (Default)
- Searches for `'http_client_urllib3'` singleton
- Legacy client type name

### 'http_client_manager'
- Current standard client
- Created by `get_http_client_manager()`

### Fallback Behavior
- Always checks `'http_client_manager'` as fallback
- Ensures state query works regardless of registration name

---

## State Values

### 'initialized'
- Client exists in singleton registry
- Instance is valid and accessible
- May have accumulated statistics

### 'not_initialized'
- Client does not exist
- No error occurred
- Normal state before first use

### 'error'
- Error occurred during state query
- Details in `'error'` field
- Client state unknown

---

## Statistics Included

If client has `get_stats()` method:
```python
'stats': {
    'requests': int,           # Total requests
    'successful': int,         # Successful requests
    'failed': int,             # Failed requests
    'retries': int,            # Retry attempts
    'rate_limited': int,       # Rate limit hits
    'rate_limiter_size': int   # Current window size
}
```

---

## Gateway Integration

**Via Gateway Wrapper:**
```python
import gateway

# Get state
state = gateway.http_get_state()

# Check client type
state = gateway.http_get_state(client_type='http_client_manager')
```

**Via Interface:**
```python
from gateway import execute_operation, GatewayInterface

state = execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'get_state',
    client_type='urllib3'
)
```

---

## Example Outputs

### Fresh Lambda Container
```python
{
    'exists': False,
    'client_type': 'urllib3',
    'state': 'not_initialized',
    'error': None
}
# No client created yet
```

### After First Request
```python
{
    'exists': True,
    'client_type': 'http_client_manager',
    'state': 'initialized',
    'instance_id': 140234567890123,
    'stats': {
        'requests': 1,
        'successful': 1,
        'failed': 0,
        'retries': 0,
        'rate_limited': 0,
        'rate_limiter_size': 1
    }
}
```

### After Multiple Requests
```python
{
    'exists': True,
    'client_type': 'http_client_manager',
    'state': 'initialized',
    'instance_id': 140234567890123,
    'stats': {
        'requests': 100,
        'successful': 98,
        'failed': 2,
        'retries': 3,
        'rate_limited': 0,
        'rate_limiter_size': 45
    }
}
```

---

## Performance

**Time:** ~1ms (singleton lookup + stats retrieval)  
**Memory:** Minimal (state dictionary ~500 bytes)

---

## Error Scenarios

| Scenario | State | Error Field |
|----------|-------|-------------|
| Client not created | not_initialized | None |
| Singleton lookup fails | error | Exception message |
| Gateway unavailable | error | Import error |
| Client malformed | error | AttributeError |

---

## Related Functions

- `reset_client_state()` - Reset client via singleton deletion
- `get_connection_statistics()` - Enhanced statistics
- `get_http_client_manager()` - Create/get client
- `gateway.singleton_get()` - Direct singleton access

---

## Notes

- Queries singleton registry (does not create client)
- Fallback ensures robustness across registration names
- Statistics snapshot (not live reference)
- Safe for monitoring and debugging
- No side effects (read-only operation)

---

**Lines:** 270
