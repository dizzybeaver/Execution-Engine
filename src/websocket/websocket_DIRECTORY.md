# websocket/ Directory

**Version:** 2025-12-13_1  
**Purpose:** WebSocket client implementation with hierarchical debug support  
**Module:** WebSocket (WEBSOCKET interface)

---

## Files

### __init__.py (30 lines)
Module initialization - exports all public websocket functions

**Exports:**
- WebSocketCore, get_websocket_manager (from websocket_manager)
- Implementation functions (from websocket_core)

---

### websocket_manager.py (293 lines)
WebSocket client manager with singleton pattern and rate limiting

**Classes:**
- WebSocketCore - WebSocket client operations manager

**Functions:**
- get_websocket_manager() - Singleton instance accessor

**Features:**
- Outbound WebSocket client (connects FROM Lambda TO external servers)
- Rate limiting (300 ops/sec)
- SINGLETON pattern (LESS-18)
- Debug integration (WEBSOCKET scope)
- Statistics tracking
- Gateway SINGLETON registry integration

**Key Methods:**
- connect() - Establish WebSocket connection
- send() - Send message to server
- receive() - Receive message from server
- close() - Close connection
- request() - Complete request (connect + send + receive + close)
- get_stats() - Get manager statistics
- reset() - Reset manager state

**Important Note:**
This provides OUTBOUND WebSocket CLIENT functionality only. Lambda can connect TO external WebSocket servers. It does NOT accept inbound connections (would require API Gateway).

**Compliance:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

### websocket_core.py (199 lines)
Gateway implementation functions for websocket interface

**Functions:**
- websocket_connect_implementation() - Connect to server
- websocket_send_implementation() - Send message
- websocket_receive_implementation() - Receive message
- websocket_close_implementation() - Close connection
- websocket_request_implementation() - Complete request
- websocket_get_stats_implementation() - Get statistics
- websocket_reset_implementation() - Reset manager

**Features:**
- Gateway-facing implementation layer
- Debug integration with correlation ID support
- SINGLETON manager usage
- Success/error response formatting

---

## Architecture

### SUGA Pattern Compliance
```
Gateway Layer (gateway/wrappers/gateway_wrappers_websocket.py)
    ↓
Interface Layer (interface/interface_websocket.py)
    ↓
Implementation Layer (websocket/websocket_core.py)
    ↓
Manager Layer (websocket/websocket_manager.py)
```

### Import Patterns

**Public (from other modules):**
```python
import websocket

# Access public functions
websocket.websocket_connect_implementation(...)
websocket.websocket_request_implementation(...)
```

**Private (within websocket module):**
```python
from websocket.websocket_manager import get_websocket_manager
```

---

## Debug Integration

### Hierarchical Debug Control

**Master Switch:**
- DEBUG_MODE - Enables all debugging

**Scope Switches:**
- WEBSOCKET_DEBUG_MODE - WebSocket debug logging
- WEBSOCKET_DEBUG_TIMING - WebSocket timing measurements

**Debug Points:**
- Connection establishment
- Message sending/receiving
- Connection closing
- Complete request cycles
- Rate limit enforcement
- Error handling
- Statistics gathering

### Debug Output Examples

```
[abc123] [WEBSOCKET-DEBUG] Connecting to WebSocket (url=wss://example.com, timeout=10)
[abc123] [WEBSOCKET-TIMING] connect: 234.56ms
[abc123] [WEBSOCKET-DEBUG] Connected successfully (url=wss://example.com)
[abc123] [WEBSOCKET-DEBUG] Sending message (message_keys=['type', 'data'])
[abc123] [WEBSOCKET-TIMING] send: 12.34ms
[abc123] [WEBSOCKET-DEBUG] Message sent successfully
[abc123] [WEBSOCKET-DEBUG] Receiving message (timeout=10)
[abc123] [WEBSOCKET-TIMING] receive: 567.89ms
[abc123] [WEBSOCKET-DEBUG] Message received successfully (message_keys=['status', 'result'])
[abc123] [WEBSOCKET-DEBUG] Closing connection
[abc123] [WEBSOCKET-TIMING] close: 5.67ms
[abc123] [WEBSOCKET-DEBUG] Connection closed successfully
[abc123] [WEBSOCKET-DEBUG] Executing request (url=wss://example.com, timeout=10)
[abc123] [WEBSOCKET-TIMING] request: 820.12ms
[abc123] [WEBSOCKET-DEBUG] Request completed successfully
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import websocket_connect, websocket_send, websocket_receive, websocket_close, websocket_request

# Complete request (recommended for one-shot operations)
response = websocket_request(
    url='wss://example.com/ws',
    message={'type': 'query', 'data': 'test'},
    timeout=10
)
print(response['data']['response'])

# Manual connection management
conn_result = websocket_connect('wss://example.com/ws')
connection = conn_result['data']['connection']

websocket_send(connection, {'type': 'ping'})
msg = websocket_receive(connection)
websocket_close(connection)
```

### Direct (Testing Only)
```python
import websocket

# Complete request
result = websocket.websocket_request_implementation(
    url='wss://example.com/ws',
    message={'type': 'test'},
    timeout=10
)

# Manual connection
conn_result = websocket.websocket_connect_implementation(
    url='wss://example.com/ws',
    timeout=10
)
```

---

## Statistics

### Manager Statistics
- total_operations - Total operations performed
- connections_count - Total connections established
- messages_sent_count - Total messages sent
- messages_received_count - Total messages received
- errors_count - Total errors encountered
- rate_limited_count - Rate limit hits
- current_rate_limit_size - Current window size
- max_rate_limit - Maximum operations per window

---

## WebSocket Client vs Server

**This is a CLIENT implementation:**
- Lambda initiates connections TO external WebSocket servers
- Lambda sends messages TO servers
- Lambda receives responses FROM servers
- Lambda closes connections

**NOT a server implementation:**
- Lambda does NOT accept inbound WebSocket connections
- Lambda does NOT listen for incoming connections
- To accept inbound connections would require API Gateway (paid service)

**Use Cases:**
- Connect to Home Assistant WebSocket API
- Query external WebSocket services
- Send commands to WebSocket endpoints
- Receive real-time updates from servers

---

## Related Files

**Interface:**
- interface/interface_websocket.py - Interface router

**Gateway:**
- gateway/wrappers/gateway_wrappers_websocket.py - Gateway wrappers

**Debug:**
- debug/debug_config.py - Debug configuration
- debug/debug_core.py - Debug logging and timing

---

## File Size Summary

| File | Lines | Status |
|------|-------|--------|
| __init__.py | 30 | ✓ Well under limit |
| websocket_manager.py | 293 | ✓ Under 300 target |
| websocket_core.py | 199 | ✓ Well under limit |
| **Total** | **522** | **3 files** |

---

## Changelog

### 2025-12-13_1
- Split monolithic websocket_core.py into 3 logical files
- Added hierarchical debug integration (WEBSOCKET scope)
- Integrated debug_log() and debug_timing() throughout
- Added correlation ID support for debug tracking
- Created module __init__.py for clean imports
- Updated interface to use module import pattern
- All files under 300-line target (max 293 lines)
- Clarified client-only nature (outbound connections)
