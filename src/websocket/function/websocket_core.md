# websocket_core.md

**Version:** 2025-12-13_1  
**Purpose:** Gateway implementation functions for websocket interface  
**Module:** websocket/websocket_core.py  
**Type:** Core Implementation Functions

---

## OVERVIEW

Provides gateway-accessible implementation functions for WebSocket CLIENT operations. All functions delegate to the singleton WebSocketManager and include comprehensive debug integration.

**Pattern:** Gateway → Interface → Core (SUGA)  
**Singleton:** All operations use get_websocket_manager()  
**Debug:** All functions integrate correlation_id tracking

**Important:** This is an OUTBOUND WebSocket CLIENT. Lambda connects TO external servers, does NOT accept inbound connections.

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SUGA: Gateway implementation layer
- SINGLETON: Uses get_websocket_manager()
- Debug Integration: All functions support correlation_id

**Constraints:**
- LESS-21: Rate limiting (300 ops/sec)

---

## FUNCTIONS

### websocket_connect_implementation()

Connect to WebSocket server using manager.

**Signature:**
```python
def websocket_connect_implementation(
    url: str,
    timeout: int = 10,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): WebSocket URL (ws:// or wss://)
- `timeout` (int): Connection timeout in seconds (default: 10)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success response with connection object, or error response

**Success Response:**
```python
{
    'success': True,
    'message': 'WebSocket connected',
    'data': {
        'connection': <websocket_object>,
        'url': 'wss://example.com/ws'
    },
    'timestamp': 1702500000,
    'correlation_id': 'abc123...'
}
```

**Error Response:**
```python
{
    'success': False,
    'error': 'Connection failed: timeout',
    'error_code': 'CONNECTION_ERROR',
    'timestamp': 1702500000,
    'correlation_id': 'abc123...'
}
```

**Example:**
```python
from websocket.websocket_core import websocket_connect_implementation

result = websocket_connect_implementation(
    url='wss://api.example.com/ws',
    timeout=15
)

if result['success']:
    connection = result['data']['connection']
    print("Connected successfully")
else:
    print(f"Connection failed: {result['error']}")
```

---

### websocket_send_implementation()

Send message via WebSocket using manager.

**Signature:**
```python
def websocket_send_implementation(
    connection: Any,
    message: Dict[str, Any],
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `message` (Dict[str, Any]): Dictionary to send (will be JSON-encoded)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success response or error response

**Example:**
```python
from websocket.websocket_core import websocket_send_implementation

result = websocket_send_implementation(
    connection=conn,
    message={'type': 'command', 'action': 'get_state'}
)

if result['success']:
    print("Message sent successfully")
```

---

### websocket_receive_implementation()

Receive message from WebSocket using manager.

**Signature:**
```python
def websocket_receive_implementation(
    connection: Any,
    timeout: int = 10,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `timeout` (int): Receive timeout in seconds (default: 10)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success response with received message, or error response

**Success Response:**
```python
{
    'success': True,
    'message': 'Message received',
    'data': {
        'response': {'status': 'ok', 'data': {...}}
    },
    'timestamp': 1702500000,
    'correlation_id': 'abc123...'
}
```

**Example:**
```python
from websocket.websocket_core import websocket_receive_implementation

result = websocket_receive_implementation(
    connection=conn,
    timeout=20
)

if result['success']:
    response_data = result['data']['response']
    print(f"Received: {response_data}")
```

---

### websocket_close_implementation()

Close WebSocket connection using manager.

**Signature:**
```python
def websocket_close_implementation(
    connection: Any,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success response or error response

**Example:**
```python
from websocket.websocket_core import websocket_close_implementation

result = websocket_close_implementation(connection=conn)

if result['success']:
    print("Connection closed successfully")
```

---

### websocket_request_implementation()

Execute complete WebSocket request using manager.

**Signature:**
```python
def websocket_request_implementation(
    url: str,
    message: Dict[str, Any],
    timeout: int = 10,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): WebSocket URL (ws:// or wss://)
- `message` (Dict[str, Any]): Dictionary to send
- `timeout` (int): Connection and receive timeout in seconds (default: 10)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success response with server's response, or error response

**Behavior:**
1. Connect to WebSocket server
2. Send message
3. Receive response
4. Close connection
5. Return response

**Example:**
```python
from websocket.websocket_core import websocket_request_implementation

# One-shot request (recommended)
result = websocket_request_implementation(
    url='wss://api.example.com/ws',
    message={'type': 'query', 'id': '123'},
    timeout=15
)

if result['success']:
    response = result['data']['response']
    print(f"Response: {response}")
```

---

### websocket_get_stats_implementation()

Get WebSocket statistics using manager.

**Signature:**
```python
def websocket_get_stats_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Statistics Structure:**
```python
{
    'total_operations': 150,
    'connections_count': 50,
    'messages_sent_count': 45,
    'messages_received_count': 43,
    'errors_count': 2,
    'rate_limited_count': 0,
    'current_rate_limit_size': 45,
    'max_rate_limit': 300
}
```

**Example:**
```python
from websocket.websocket_core import websocket_get_stats_implementation

stats = websocket_get_stats_implementation()

print(f"Total operations: {stats['total_operations']}")
print(f"Connections: {stats['connections_count']}")
print(f"Errors: {stats['errors_count']}")
```

---

### websocket_reset_implementation()

Reset WebSocket manager state.

**Signature:**
```python
def websocket_reset_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Success/error response dictionary

**Example:**
```python
from websocket.websocket_core import websocket_reset_implementation

result = websocket_reset_implementation()

if result['success']:
    print("Manager reset successfully")
```

---

## USAGE PATTERNS

### Pattern 1: One-Shot Request (Recommended)

```python
from websocket.websocket_core import websocket_request_implementation

# Best for simple request-response
result = websocket_request_implementation(
    url='wss://api.example.com/ws',
    message={'action': 'get_data', 'id': '123'},
    timeout=10
)

if result['success']:
    data = result['data']['response']
    process(data)
```

---

### Pattern 2: Manual Connection Management

```python
from websocket.websocket_core import (
    websocket_connect_implementation,
    websocket_send_implementation,
    websocket_receive_implementation,
    websocket_close_implementation
)

# Connect
conn_result = websocket_connect_implementation('wss://api.example.com/ws')
if not conn_result['success']:
    print("Connection failed")
    return

connection = conn_result['data']['connection']

try:
    # Send multiple messages
    websocket_send_implementation(connection, {'type': 'subscribe'})
    websocket_send_implementation(connection, {'type': 'query', 'id': '123'})
    
    # Receive responses
    msg1 = websocket_receive_implementation(connection)
    msg2 = websocket_receive_implementation(connection)
    
finally:
    # Always close
    websocket_close_implementation(connection)
```

---

### Pattern 3: Error Handling

```python
from websocket.websocket_core import websocket_request_implementation

result = websocket_request_implementation(
    url='wss://api.example.com/ws',
    message={'action': 'test'},
    timeout=5
)

if not result['success']:
    error_code = result.get('error_code', 'UNKNOWN')
    error_msg = result.get('error', 'Unknown error')
    
    if error_code == 'CONNECTION_ERROR':
        print("Failed to connect to server")
    elif error_code == 'TIMEOUT_ERROR':
        print("Request timed out")
    else:
        print(f"Error: {error_msg}")
    
    return

# Success
response_data = result['data']['response']
process(response_data)
```

---

## EXPORTS

```python
__all__ = [
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
    'websocket_get_stats_implementation',
    'websocket_reset_implementation',
]
```

---

## RELATED DOCUMENTATION

- **websocket_manager.md**: Manager and core logic
- **interface_websocket.md**: Interface layer

---

**END OF DOCUMENTATION**

**Module:** websocket/websocket_core.py  
**Functions:** 7  
**Pattern:** SUGA Core Implementation  
**Type:** Outbound WebSocket CLIENT
