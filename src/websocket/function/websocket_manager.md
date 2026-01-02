# websocket_manager.md

**Version:** 2025-12-13_1  
**Purpose:** WebSocket client manager with singleton pattern and rate limiting  
**Module:** websocket/websocket_manager.py  
**Type:** Singleton Manager

---

## OVERVIEW

Manages WebSocket CLIENT connections with rate limiting, statistics tracking, and comprehensive error handling. This is an OUTBOUND client only - Lambda connects TO external WebSocket servers.

**Key Features:**
- Singleton instance per Lambda container
- Rate limiting (300 ops/sec)
- Outbound connections only
- Connection lifecycle management
- Statistics tracking
- Lambda-safe (no threading)

**Important:** Lambda can connect TO WebSocket servers but cannot ACCEPT inbound connections (would require API Gateway).

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SINGLETON: Single instance via get_websocket_manager()
- Rate Limiting: 300 operations/second protection

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

## CLASSES

### WebSocketCore

Main manager class for WebSocket client operations.

**Initialization:**
```python
def __init__(self):
    self._rate_limiter = deque(maxlen=300)
    self._rate_limit_window_ms = 1000
    self._rate_limited_count = 0
    
    # Statistics
    self._stats = {
        'total_operations': 0,
        'connections_count': 0,
        'messages_sent_count': 0,
        'messages_received_count': 0,
        'errors_count': 0
    }
```

**State:**
- `_rate_limiter`: Deque tracking operation timestamps
- `_rate_limit_window_ms`: Rate limit window (1000ms)
- `_rate_limited_count`: Count of rate-limited operations
- `_stats`: Operation statistics

---

## METHODS

### _check_rate_limit()

**Private method** - Check if operation is within rate limit.

**Signature:**
```python
def _check_rate_limit(self) -> bool
```

**Returns:**
- `bool`: True if allowed, False if rate limited

**Algorithm:** Sliding window with deque (same as other managers)

**Rate Limit:** 300 operations per second

---

### connect()

Establish WebSocket connection to server.

**Signature:**
```python
def connect(
    self,
    url: str,
    timeout: int = 10,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): WebSocket URL (ws:// or wss://)
- `timeout` (int): Connection timeout in seconds
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Success response with connection object, or error response

**Behavior:**
1. Check rate limit
2. Validate URL format
3. Establish WebSocket connection
4. Update statistics
5. Return connection object

**Example:**
```python
manager = get_websocket_manager()

result = manager.connect('wss://api.example.com/ws', timeout=15)

if result['success']:
    connection = result['data']['connection']
    print("Connected successfully")
```

---

### send()

Send message to WebSocket server.

**Signature:**
```python
def send(
    self,
    connection: Any,
    message: Dict[str, Any],
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `message` (Dict[str, Any]): Dictionary to send (JSON-encoded)
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Success response or error response

**Behavior:**
1. Check rate limit
2. Validate connection
3. JSON-encode message
4. Send to server
5. Update statistics

**Example:**
```python
manager = get_websocket_manager()

result = manager.send(
    connection,
    {'type': 'command', 'action': 'get_state'}
)

if result['success']:
    print("Message sent")
```

---

### receive()

Receive message from WebSocket server.

**Signature:**
```python
def receive(
    self,
    connection: Any,
    timeout: int = 10,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `timeout` (int): Receive timeout in seconds
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Success response with received message, or error response

**Behavior:**
1. Check rate limit
2. Validate connection
3. Wait for message (with timeout)
4. JSON-decode message
5. Update statistics

**Example:**
```python
manager = get_websocket_manager()

result = manager.receive(connection, timeout=20)

if result['success']:
    message = result['data']['response']
    print(f"Received: {message}")
```

---

### close()

Close WebSocket connection.

**Signature:**
```python
def close(
    self,
    connection: Any,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `connection` (Any): Active WebSocket connection object
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Success response or error response

**Behavior:**
1. Check rate limit
2. Validate connection
3. Close connection gracefully
4. Update statistics

**Example:**
```python
manager = get_websocket_manager()

result = manager.close(connection)

if result['success']:
    print("Connection closed")
```

---

### request()

Execute complete WebSocket request (connect + send + receive + close).

**Signature:**
```python
def request(
    self,
    url: str,
    message: Dict[str, Any],
    timeout: int = 10,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): WebSocket URL (ws:// or wss://)
- `message` (Dict[str, Any]): Dictionary to send
- `timeout` (int): Connection and receive timeout in seconds
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Success response with server's response, or error response

**Behavior:**
1. Connect to server
2. Send message
3. Receive response
4. Close connection (even on error)
5. Return response

**Atomicity:** Connection always closed, even if send/receive fails

**Example:**
```python
manager = get_websocket_manager()

result = manager.request(
    'wss://api.example.com/ws',
    {'type': 'query', 'id': '123'},
    timeout=15
)

if result['success']:
    response = result['data']['response']
    print(f"Response: {response}")
```

---

### get_stats()

Get WebSocket statistics.

**Signature:**
```python
def get_stats(
    self,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Statistics:**
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
manager = get_websocket_manager()

stats = manager.get_stats()

print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {(stats['total_operations'] - stats['errors_count']) / stats['total_operations'] * 100:.1f}%")
```

---

### reset()

Reset WebSocket manager state.

**Signature:**
```python
def reset(
    self,
    correlation_id: str = None
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `bool`: True if reset successful, False if rate limited

**Behavior:**
- Clears rate limiter deque
- Resets rate limited count to 0
- Resets all statistics to 0

**Example:**
```python
manager = get_websocket_manager()

if manager.reset():
    print("Manager reset successfully")
```

---

## SINGLETON PATTERN

### get_websocket_manager()

Get WebSocket manager singleton.

**Function:** Module-level singleton factory

**Signature:**
```python
def get_websocket_manager() -> WebSocketCore
```

**Returns:**
- `WebSocketCore`: The singleton manager instance

**Implementation:**
```python
_manager_core = None  # Module-level singleton

def get_websocket_manager() -> WebSocketCore:
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        # Try gateway SINGLETON registry first
        manager = singleton_get('websocket_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = WebSocketCore()
            singleton_register('websocket_manager', _manager_core)
            manager = _manager_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _manager_core is None:
            _manager_core = WebSocketCore()
        return _manager_core
```

**Usage:**
```python
# Always use this function to get manager
manager = get_websocket_manager()

# Never instantiate directly
# manager = WebSocketCore()  # ❌ WRONG
```

---

## CLIENT vs SERVER

**This is a CLIENT implementation:**

**Can Do:**
- Connect TO external WebSocket servers
- Send messages TO servers
- Receive responses FROM servers
- Close connections

**Cannot Do:**
- Accept inbound WebSocket connections
- Listen for incoming connections
- Act as WebSocket server

**Why No Server?**
- Lambda is event-driven (triggered by events)
- Accepting connections requires API Gateway WebSocket API (paid service)
- Client use is sufficient for most Lambda use cases

**Use Cases:**
- Connect to Home Assistant WebSocket API
- Query external WebSocket services
- Send commands to IoT devices via WebSocket
- Receive real-time updates from servers

---

## USAGE PATTERNS

### Pattern 1: Simple Request

```python
from websocket.websocket_manager import get_websocket_manager

manager = get_websocket_manager()

result = manager.request(
    'wss://api.example.com/ws',
    {'action': 'get_data'},
    timeout=10
)

if result['success']:
    data = result['data']['response']
    process(data)
```

---

### Pattern 2: Multiple Messages

```python
manager = get_websocket_manager()

# Connect once
conn_result = manager.connect('wss://api.example.com/ws')
connection = conn_result['data']['connection']

try:
    # Send multiple messages
    for i in range(10):
        manager.send(connection, {'id': i, 'action': 'query'})
        response = manager.receive(connection)
        process(response['data']['response'])
finally:
    # Always close
    manager.close(connection)
```

---

### Pattern 3: Monitoring

```python
manager = get_websocket_manager()

# Periodic health check
stats = manager.get_stats()

error_rate = stats['errors_count'] / stats['total_operations'] if stats['total_operations'] > 0 else 0

if error_rate > 0.1:
    logger.warning(
        "High WebSocket error rate",
        extra={
            'error_rate': error_rate,
            'total_ops': stats['total_operations'],
            'errors': stats['errors_count']
        }
    )
```

---

## EXPORTS

```python
__all__ = [
    'WebSocketCore',
    'get_websocket_manager',
]
```

---

## RELATED DOCUMENTATION

- **websocket_core.md**: Gateway implementation functions
- **interface_websocket.md**: Interface layer

---

**END OF DOCUMENTATION**

**Module:** websocket/websocket_manager.py  
**Classes:** 1 (WebSocketCore)  
**Functions:** 1 (get_websocket_manager)  
**Type:** Outbound WebSocket CLIENT
