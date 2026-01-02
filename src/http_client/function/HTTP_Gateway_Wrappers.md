# HTTP Gateway Wrappers

**Version:** 2025-12-10_1  
**Module:** gateway.wrappers.gateway_wrappers_http_client  
**Type:** Gateway Wrapper Functions

---

## Overview

Gateway wrapper functions for HTTP_CLIENT interface operations. These functions provide the recommended gateway-based access pattern for HTTP operations.

---

## Functions

### http_request()
### http_get()
### http_post()
### http_put()
### http_delete()
### http_reset()
### http_get_state()
### http_reset_state()

---

## http_request()

**Purpose:** Execute HTTP request with specified method

**Signature:**
```python
def http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `method` (`str`) - HTTP method (GET, POST, PUT, DELETE)
- `url` (`str`) - Target URL
- `**kwargs` - Additional parameters:
  - `headers` - Custom headers dict
  - `json` - JSON data to send
  - `body` - Raw body data
  - `timeout` - Request timeout
  - `correlation_id` - Debug correlation ID

**Returns:** Response dict with success status, data, and metadata

**Usage:**
```python
import gateway

# Generic request
result = gateway.http_request('POST', url, json={'key': 'value'})

# With correlation ID
result = gateway.http_request(
    'GET', 
    url,
    correlation_id='abc-123',
    headers={'Authorization': 'Bearer token'}
)
```

**Implementation:**
```python
return execute_operation(
    GatewayInterface.HTTP_CLIENT, 
    'request',
    method=method,
    url=url,
    **kwargs
)
```

---

## http_get()

**Purpose:** Execute HTTP GET request

**Signature:**
```python
def http_get(url: str, **kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `url` (`str`) - Target URL
- `**kwargs` - Additional parameters:
  - `headers` - Custom headers dict
  - `timeout` - Request timeout
  - `correlation_id` - Debug correlation ID

**Returns:** Response dict with success status, data, and metadata

**Usage:**
```python
import gateway

# Simple GET
result = gateway.http_get('https://api.example.com/data')

# With headers and correlation ID
result = gateway.http_get(
    'https://api.example.com/user/123',
    headers={'Authorization': 'Bearer token'},
    correlation_id='req-456'
)

# With timeout
result = gateway.http_get(url, timeout=10)
```

**Debug Integration:**
```python
# Automatically logged when HTTP_DEBUG_MODE=true
# [req-456] [HTTP-DEBUG] Request start (method=GET, url=https://...)
# [req-456] [HTTP-TIMING] GET https://api.example.com/data: 145.23ms
```

---

## http_post()

**Purpose:** Execute HTTP POST request

**Signature:**
```python
def http_post(url: str, **kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `url` (`str`) - Target URL
- `**kwargs` - Additional parameters:
  - `json` - JSON data to send (auto-encodes)
  - `body` - Raw body data
  - `headers` - Custom headers dict
  - `timeout` - Request timeout
  - `correlation_id` - Debug correlation ID

**Returns:** Response dict with success status, data, and metadata

**Usage:**
```python
import gateway

# POST with JSON
result = gateway.http_post(
    'https://api.example.com/users',
    json={'name': 'John', 'email': 'john@example.com'}
)

# POST with custom body
result = gateway.http_post(
    url,
    body='custom data',
    headers={'Content-Type': 'text/plain'}
)

# Home Assistant service call
result = gateway.http_post(
    f'{ha_url}/api/services/light/turn_on',
    json={'entity_id': 'light.living_room', 'brightness': 255},
    headers=get_ha_headers(token),
    correlation_id=corr_id
)
```

---

## http_put()

**Purpose:** Execute HTTP PUT request

**Signature:**
```python
def http_put(url: str, **kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `url` (`str`) - Target URL
- `**kwargs` - Additional parameters:
  - `json` - JSON data to send
  - `body` - Raw body data
  - `headers` - Custom headers dict
  - `timeout` - Request timeout
  - `correlation_id` - Debug correlation ID

**Returns:** Response dict with success status, data, and metadata

**Usage:**
```python
import gateway

# PUT with JSON
result = gateway.http_put(
    'https://api.example.com/users/123',
    json={'name': 'John Updated', 'email': 'newemail@example.com'}
)

# Update HA entity
result = gateway.http_put(
    f'{ha_url}/api/states/input_number.target_temp',
    json={'state': 72, 'attributes': {'unit_of_measurement': '°F'}},
    headers=get_ha_headers(token)
)
```

---

## http_delete()

**Purpose:** Execute HTTP DELETE request

**Signature:**
```python
def http_delete(url: str, **kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `url` (`str`) - Target URL
- `**kwargs` - Additional parameters:
  - `headers` - Custom headers dict
  - `timeout` - Request timeout
  - `correlation_id` - Debug correlation ID

**Returns:** Response dict with success status, data, and metadata

**Usage:**
```python
import gateway

# Simple DELETE
result = gateway.http_delete('https://api.example.com/users/123')

# With headers
result = gateway.http_delete(
    url,
    headers={'Authorization': 'Bearer token'},
    correlation_id='del-789'
)
```

---

## http_reset()

**Purpose:** Reset HTTP client state

**Signature:**
```python
def http_reset() -> Dict[str, Any]:
```

**Parameters:** None

**Returns:** Dict with success status and reset confirmation

**Resets:**
- Connection pool (closes all connections)
- Statistics counters
- Rate limiter state

**Usage:**
```python
import gateway

# Reset client
result = gateway.http_reset()

if result['success']:
    print("HTTP client reset successfully")
else:
    print("Reset failed or rate limited")

# Example response:
{
    'success': True,
    'message': 'HTTP client reset successful'
}
```

**When to Use:**
- After SSL configuration change
- Periodic maintenance
- Clear statistics
- Force connection pool reset

**Note:** Preserves singleton instance, just resets state

---

## http_get_state()

**Purpose:** Get HTTP client state information

**Signature:**
```python
def http_get_state(**kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `**kwargs` - Optional parameters:
  - `client_type` (`str`) - Client type to query (default: 'urllib3')

**Returns:** Dict with client state and statistics

**Usage:**
```python
import gateway

# Get state
state = gateway.http_get_state()

if state['exists']:
    print(f"Client type: {state['client_type']}")
    print(f"Instance ID: {state['instance_id']}")
    
    if 'stats' in state:
        stats = state['stats']
        print(f"Requests: {stats['requests']}")
        print(f"Success rate: {stats['successful'] / stats['requests'] * 100:.1f}%")

# Example response:
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

**Monitoring:**
```python
def check_http_health():
    """Check HTTP client health."""
    state = gateway.http_get_state()
    
    if not state['exists']:
        return 'not_initialized'
    
    stats = state.get('stats', {})
    if stats.get('requests', 0) == 0:
        return 'healthy'
    
    success_rate = stats['successful'] / stats['requests'] * 100
    
    if success_rate >= 95:
        return 'healthy'
    elif success_rate >= 90:
        return 'degraded'
    else:
        return 'critical'
```

---

## http_reset_state()

**Purpose:** Reset HTTP client state (legacy operation)

**Signature:**
```python
def http_reset_state(**kwargs) -> Dict[str, Any]:
```

**Parameters:**
- `**kwargs` - Optional parameters:
  - `client_type` (`str`) - Specific client to reset

**Returns:** Dict with reset status

**Usage:**
```python
import gateway

# Reset all clients
result = gateway.http_reset_state()

# Reset specific client
result = gateway.http_reset_state(client_type='http_client_manager')

# Example response:
{
    'success': True,
    'count': 2,
    'message': 'Reset 2 client(s)'
}
```

**Note:** Deletes singleton instances (more destructive than `http_reset()`)

---

## Complete Examples

### Basic HTTP Operations

```python
import gateway

# GET request
users = gateway.http_get('https://api.example.com/users')

if users['success']:
    for user in users['data']:
        print(f"User: {user['name']}")

# POST request
new_user = gateway.http_post(
    'https://api.example.com/users',
    json={'name': 'Alice', 'email': 'alice@example.com'}
)

if new_user['success']:
    print(f"Created user: {new_user['data']['id']}")

# PUT request
updated = gateway.http_put(
    f"https://api.example.com/users/{user_id}",
    json={'name': 'Alice Updated'}
)

# DELETE request
deleted = gateway.http_delete(f"https://api.example.com/users/{user_id}")
```

### Home Assistant Integration

```python
import gateway
from http_client import get_ha_headers

# Configuration
ha_url = gateway.config_get('/lee/ha/url')
ha_token = gateway.config_get('/lee/ha/token')
headers = get_ha_headers(ha_token)

# Get entity state
state = gateway.http_get(
    f'{ha_url}/api/states/light.living_room',
    headers=headers
)

if state['success']:
    entity = state['data']
    print(f"Light state: {entity['state']}")
    print(f"Brightness: {entity['attributes'].get('brightness')}")

# Turn on light
result = gateway.http_post(
    f'{ha_url}/api/services/light/turn_on',
    json={
        'entity_id': 'light.living_room',
        'brightness': 255
    },
    headers=headers
)
```

### With Debug Tracking

```python
import gateway

# Generate correlation ID
corr_id = gateway.generate_correlation_id()

# Make tracked request
result = gateway.http_get(
    'https://api.example.com/data',
    correlation_id=corr_id
)

# Debug output (if HTTP_DEBUG_MODE=true):
# [abc-123] [HTTP-DEBUG] Request start (method=GET, url=https://api...)
# [abc-123] [HTTP-TIMING] GET https://api.example.com/data: 156.78ms
# [abc-123] [HTTP-DEBUG] Request success (status=200)
```

---

## Architecture

**Gateway Layer:**
```
gateway.http_get(url)
    ↓
gateway.wrappers.gateway_wrappers_http_client.http_get(url)
    ↓
gateway.gateway_core.execute_operation(HTTP_CLIENT, 'get', url=url)
    ↓
interfaces.interface_http.execute_http_operation('get', url=url)
    ↓
http_client.http_client_operations.http_get_implementation(url=url)
    ↓
http_client.http_client_manager.HTTPClientCore.make_request('GET', url)
```

---

## Debug Integration

**All HTTP wrapper functions support debug integration:**

**Flags:**
- `HTTP_DEBUG_MODE=true` - Enable debug logging
- `HTTP_DEBUG_TIMING=true` - Enable timing measurements

**Scope:** `HTTP`

**Logged Information:**
- Request start with method and URL
- Request duration (timing)
- Request success/failure with status
- Exception details

---

## Related Documentation

- http_client/function/make_request.md - Core request function
- http_client/function/get_http_client_manager.md - Singleton manager
- http_client/function/reset.md - Client reset
- http_client/function/get_client_state.md - State query

---

**Lines:** 420  
**Functions Documented:** 8  
**Module:** gateway.wrappers.gateway_wrappers_http_client
