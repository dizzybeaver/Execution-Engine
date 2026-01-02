# interface_websocket.py

**Version:** 2025-12-13_1  
**Module:** WEBSOCKET  
**Layer:** Interface  
**Interface:** INT-07  
**Lines:** ~115

---

## Purpose

WebSocket client interface router with import protection for real-time communication.

---

## Main Function

### execute_websocket_operation()

**Signature:**
```python
def execute_websocket_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route WebSocket CLIENT operation requests to internal implementations

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (varies by operation)

**Operations:**
- `connect` - Connect to WebSocket server
- `send` - Send message to WebSocket
- `receive` - Receive message from WebSocket
- `close` - Close WebSocket connection
- `request` - Send request and wait for response
- `get_stats` - Get WebSocket statistics
- `reset` - Reset WebSocket state

**Raises:**
- `RuntimeError` - If WebSocket interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### connect

**Purpose:** Connect to WebSocket server

**Parameters:**
- `url` (str, required) - WebSocket URL (ws:// or wss://)
- `headers` (dict, optional) - Connection headers
- `timeout` (int, optional) - Connection timeout in seconds

**Returns:** WebSocket connection object

**Validation:**
- URL must be provided
- URL must be string

**Usage:**
```python
connection = execute_websocket_operation(
    'connect',
    url='wss://example.com/ws',
    headers={'Authorization': 'Bearer token'},
    timeout=10
)
```

**Behavior:**
- Establishes WebSocket connection
- Returns connection object for subsequent operations
- Raises error if connection fails

---

### send

**Purpose:** Send message to WebSocket

**Parameters:**
- `connection` (WebSocket, required) - WebSocket connection
- `message` (str/dict, required) - Message to send
- `timeout` (int, optional) - Send timeout

**Returns:** bool (True on success)

**Validation:**
- Connection must be provided
- Message must be provided

**Usage:**
```python
success = execute_websocket_operation(
    'send',
    connection=ws_connection,
    message={'type': 'ping', 'data': 'hello'}
)
```

**Behavior:**
- Serializes dict messages to JSON
- Sends string messages directly
- Returns True on successful send

---

### receive

**Purpose:** Receive message from WebSocket

**Parameters:**
- `connection` (WebSocket, required) - WebSocket connection
- `timeout` (int, optional) - Receive timeout in seconds

**Returns:** str or dict (received message)

**Validation:**
- Connection must be provided

**Usage:**
```python
message = execute_websocket_operation(
    'receive',
    connection=ws_connection,
    timeout=30
)
```

**Behavior:**
- Waits for message from server
- Attempts JSON parsing
- Returns raw string if not JSON
- Raises timeout error if no message within timeout

---

### close

**Purpose:** Close WebSocket connection

**Parameters:**
- `connection` (WebSocket, required) - WebSocket connection
- `code` (int, optional) - Close code (default: 1000)
- `reason` (str, optional) - Close reason

**Returns:** bool (True on success)

**Validation:**
- Connection must be provided

**Usage:**
```python
execute_websocket_operation(
    'close',
    connection=ws_connection,
    code=1000,
    reason='Normal closure'
)
```

**Close Codes:**
- 1000: Normal closure
- 1001: Going away
- 1002: Protocol error
- 1003: Unsupported data
- 1006: Abnormal closure

---

### request

**Purpose:** Send request and wait for response (request-response pattern)

**Parameters:**
- `url` (str, required) - WebSocket URL
- `message` (str/dict, required) - Request message
- `timeout` (int, optional) - Response timeout (default: 30)

**Returns:** dict or str (response message)

**Validation:**
- URL must be provided
- Message must be provided

**Usage:**
```python
response = execute_websocket_operation(
    'request',
    url='wss://example.com/ws',
    message={'type': 'get_user', 'id': '123'},
    timeout=10
)
```

**Behavior:**
- Connects to WebSocket
- Sends message
- Waits for response
- Closes connection
- Returns response

**Use Case:** One-time request-response over WebSocket

---

### get_stats

**Purpose:** Get WebSocket statistics

**Parameters:** None

**Returns:** Dict with WebSocket stats:
- `connections_opened` - Total connections opened
- `connections_closed` - Total connections closed
- `messages_sent` - Total messages sent
- `messages_received` - Total messages received
- `errors` - Error count
- `active_connections` - Currently active connections

**Usage:**
```python
stats = execute_websocket_operation('get_stats')
```

---

### reset

**Purpose:** Reset WebSocket state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_websocket_operation('reset')
```

**Behavior:**
- Closes all active connections
- Resets statistics
- Clears connection pool

---

## Validation Helpers

### _validate_url_param()

**Purpose:** Validate url parameter exists

**Parameters:**
- `kwargs` (dict) - Operation kwargs
- `operation` (str) - Operation name

**Raises:**
- `ValueError` - If url missing

---

### _validate_connection_param()

**Purpose:** Validate connection parameter exists

**Parameters:**
- `kwargs` (dict) - Operation kwargs
- `operation` (str) - Operation name

**Raises:**
- `ValueError` - If connection missing

---

### _validate_message_param()

**Purpose:** Validate message parameter exists

**Parameters:**
- `kwargs` (dict) - Operation kwargs
- `operation` (str) - Operation name

**Raises:**
- `ValueError` - If message missing

---

### _validate_send_params()

**Purpose:** Validate send operation parameters

**Checks:**
- Connection exists
- Message exists

---

### _validate_request_params()

**Purpose:** Validate request operation parameters

**Checks:**
- URL exists
- Message exists

---

## WebSocket Patterns

### Long-Lived Connection

```python
# Connect once
connection = execute_websocket_operation(
    'connect',
    url='wss://api.example.com/ws'
)

# Send multiple messages
for msg in messages:
    execute_websocket_operation('send', connection=connection, message=msg)
    response = execute_websocket_operation('receive', connection=connection)
    process_response(response)

# Close when done
execute_websocket_operation('close', connection=connection)
```

---

### Request-Response

```python
# One-time request
response = execute_websocket_operation(
    'request',
    url='wss://api.example.com/ws',
    message={'action': 'get_data', 'id': '123'}
)
```

---

### Event Streaming

```python
connection = execute_websocket_operation('connect', url='wss://events.example.com')

try:
    while True:
        event = execute_websocket_operation('receive', connection=connection, timeout=60)
        handle_event(event)
except TimeoutError:
    # No events for 60 seconds
    pass
finally:
    execute_websocket_operation('close', connection=connection)
```

---

## Home Assistant Integration

**Primary Use Case:** WebSocket connection to Home Assistant for real-time control

**Example:**
```python
# Connect to Home Assistant
connection = execute_websocket_operation(
    'connect',
    url='wss://homeassistant.local:8123/api/websocket',
    timeout=10
)

# Authenticate
execute_websocket_operation(
    'send',
    connection=connection,
    message={'type': 'auth', 'access_token': token}
)

# Call service
execute_websocket_operation(
    'send',
    connection=connection,
    message={
        'type': 'call_service',
        'domain': 'light',
        'service': 'turn_on',
        'service_data': {'entity_id': 'light.living_room'}
    }
)

# Get response
result = execute_websocket_operation('receive', connection=connection)
```

---

## Import Protection

**Pattern:**
```python
try:
    import websocket
    _WEBSOCKET_AVAILABLE = True
except ImportError as e:
    _WEBSOCKET_AVAILABLE = False
    _WEBSOCKET_IMPORT_ERROR = str(e)
```

---

## Dispatch Dictionary

```python
_OPERATION_DISPATCH = {
    'connect': lambda **kwargs: (
        _validate_url_param(kwargs, 'connect'),
        websocket.websocket_connect_implementation(**kwargs)
    )[1],
    'send': lambda **kwargs: (
        _validate_send_params(kwargs),
        websocket.websocket_send_implementation(**kwargs)
    )[1],
    # ... other operations
}
```

---

## Error Handling

**Connection Errors:**
- Connection refused
- Timeout
- Invalid URL
- SSL/TLS errors

**Protocol Errors:**
- Invalid message format
- Unexpected close
- Protocol violation

**Best Practices:**
- Always close connections
- Handle timeouts gracefully
- Retry on connection failure
- Validate message format

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Parameter Validation:** Comprehensive checks  
✅ **Import Protection:** Graceful failure handling  
✅ **WebSocket CLIENT:** Home Assistant integration ready

---

## Related Files

- `/websocket/` - WebSocket implementation
- `/gateway/wrappers/gateway_wrappers_websocket.py` - Gateway wrappers
- `/websocket/websocket_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
