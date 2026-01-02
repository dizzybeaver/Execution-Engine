# interface_http.py

**Version:** 2025-12-10_1  
**Module:** HTTP  
**Layer:** Interface  
**Interface:** INT-06  
**Lines:** ~125

---

## Purpose

HTTP interface router for REST client operations with dispatch dictionary.

---

## Main Function

### execute_http_operation()

**Signature:**
```python
def execute_http_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route HTTP operation requests to implementations

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** HTTP response (dict or object)

**Operations:**
- `request` - Generic HTTP request
- `get` - HTTP GET request
- `post` - HTTP POST request
- `put` - HTTP PUT request
- `delete` - HTTP DELETE request
- `reset` - Reset HTTP client state
- `get_state` - Get client state
- `reset_state` - Reset state (alias)
- `configure_retry` - Configure retry (not implemented)
- `get_statistics` - Get statistics (not implemented)

**Raises:**
- `RuntimeError` - If HTTP interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### request

**Purpose:** Generic HTTP request with full control

**Parameters:**
- `url` (str, required) - Request URL
- `method` (str, required) - HTTP method (GET, POST, PUT, DELETE, etc.)
- `headers` (dict, optional) - Request headers
- `data` (dict/str, optional) - Request body
- `params` (dict, optional) - Query parameters
- `timeout` (int, optional) - Request timeout in seconds

**Returns:** Response dict with:
- `status_code` - HTTP status code
- `headers` - Response headers
- `body` - Response body
- `url` - Final URL (after redirects)

**Validation:**
- `url` must be provided and be string
- `method` must be provided and be string

**Usage:**
```python
response = execute_http_operation(
    'request',
    url='https://api.example.com/data',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data={'key': 'value'},
    timeout=10
)
```

---

### get

**Purpose:** HTTP GET request

**Parameters:**
- `url` (str, required) - Request URL
- `headers` (dict, optional) - Request headers
- `params` (dict, optional) - Query parameters
- `timeout` (int, optional) - Request timeout

**Returns:** Response dict

**Usage:**
```python
response = execute_http_operation(
    'get',
    url='https://api.example.com/users',
    params={'page': 1, 'limit': 10}
)
```

---

### post

**Purpose:** HTTP POST request

**Parameters:**
- `url` (str, required) - Request URL
- `data` (dict/str, optional) - Request body
- `headers` (dict, optional) - Request headers
- `timeout` (int, optional) - Request timeout

**Returns:** Response dict

**Usage:**
```python
response = execute_http_operation(
    'post',
    url='https://api.example.com/users',
    data={'name': 'Alice', 'email': 'alice@example.com'}
)
```

---

### put

**Purpose:** HTTP PUT request

**Parameters:**
- `url` (str, required) - Request URL
- `data` (dict/str, optional) - Request body
- `headers` (dict, optional) - Request headers
- `timeout` (int, optional) - Request timeout

**Returns:** Response dict

**Usage:**
```python
response = execute_http_operation(
    'put',
    url='https://api.example.com/users/123',
    data={'name': 'Alice Updated'}
)
```

---

### delete

**Purpose:** HTTP DELETE request

**Parameters:**
- `url` (str, required) - Request URL
- `headers` (dict, optional) - Request headers
- `timeout` (int, optional) - Request timeout

**Returns:** Response dict

**Usage:**
```python
response = execute_http_operation(
    'delete',
    url='https://api.example.com/users/123'
)
```

---

### reset

**Purpose:** Reset HTTP client state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_http_operation('reset')
```

---

### get_state

**Purpose:** Get HTTP client state

**Parameters:** None

**Returns:** Dict with client state:
- `request_count` - Total requests made
- `success_count` - Successful requests
- `error_count` - Failed requests
- `average_duration_ms` - Average request duration

**Usage:**
```python
state = execute_http_operation('get_state')
```

---

### reset_state

**Purpose:** Reset state (alias for reset)

**Parameters:** None

**Returns:** bool (True on success)

---

## Not Yet Implemented

### configure_retry

**Status:** NotImplementedError

**Planned Parameters:**
- `max_retries` - Maximum retry attempts
- `backoff_factor` - Exponential backoff factor
- `retry_on` - Status codes to retry

---

### get_statistics

**Status:** NotImplementedError

**Planned Returns:**
- Detailed request statistics
- Per-endpoint metrics
- Error rates

---

## Validation Helpers

### _validate_url_param()

**Purpose:** Validate url parameter exists and is string

**Raises:**
- `ValueError` - If url missing
- `TypeError` - If url not string

---

### _validate_request_params()

**Purpose:** Validate request operation parameters

**Checks:**
- URL exists and is string
- Method exists and is string

---

## Import Structure

```python
from http_client.http_client_operations import (
    http_request_implementation,
    http_get_implementation,
    http_post_implementation,
    http_put_implementation,
    http_delete_implementation,
    http_reset_implementation,
    get_state_implementation,
    reset_state_implementation
)
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Parameter Validation:** Type and presence checks  
✅ **Import Protection:** Graceful failure handling  
✅ **RESTful Operations:** Standard HTTP methods

---

## Related Files

- `/http_client/` - HTTP client implementation
- `/gateway/wrappers/gateway_wrappers_http.py` - Gateway wrappers
- `/http_client/http_client_directory.md` - Directory structure

---

**END OF DOCUMENTATION**
