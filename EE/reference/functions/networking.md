# Networking Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** networking
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** HTTP clients, protocol clients, networking

---

## Overview

The Networking domain provides HTTP clients, WebSocket clients, protocol clients (Redis, MQTT, LDAP, SNMP, NTP, Memcached, RPC), and network connectivity operations.

**Gateway:** NetworkingGateway
**Interfaces:** 10 (connectivity, http_client, websocket_client, redis, mqtt, ldap, snmp, ntp, memcached, rpc)
**Operations:** ~35

---

## 1. Connectivity Interface

**Purpose:** Network connectivity operations
**Location:** `EE/networking/connectivity/`

### Operations

#### check_connection

Check network connectivity to target.

**Parameters:**
- `target` (str, required): Hostname or IP address
- `port` (int, optional): Port number (default: 80)
- `timeout` (int, optional): Timeout in seconds (default: 5)

**Returns:** Boolean (True if reachable)

**Examples:**
```python
# Check host
status = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="check_connection",
    target="example.com",
    port=443
)
```

---

#### test_latency

Test network latency.

**Parameters:**
- `target` (str, required): Hostname or IP
- `count` (int, optional): Number of pings (default: 5)
- `timeout` (int, optional): Timeout per ping (default: 5)

**Returns:** Latency stats (dict with avg, min, max, packet_loss)

**Examples:**
```python
stats = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="test_latency",
    target="api.example.com",
    count=10
)
# Returns: {"avg_ms": 45.2, "min_ms": 38, "max_ms": 62, "packet_loss": 0.0}
```

---

#### get_network_info

Get network information.

**Parameters:** None

**Returns:** Network info (dict with hostname, ips, interfaces)

**Examples:**
```python
info = execute_operation(
    domain="networking",
    interface="connectivity",
    operation="get_network_info"
)
# Returns: {"hostname": "server01", "ips": ["192.168.1.10"], ...}
```

---

## 2. HTTP Client Interface

**Purpose:** HTTP/HTTPS operations
**Location:** `EE/networking/http_client/`

### Operations

#### get, post, put, delete, patch, request

**Parameters:**
- `url` (str, required): Request URL
- `headers` (dict, optional): Request headers
- `data` (Any, optional): Request body
- `params` (dict, optional): Query parameters
- `timeout` (int, optional): Request timeout (default: 30)
- `verify_ssl` (bool, optional): Verify SSL (default: True)

**Returns:** Response object (dict with status, headers, body)

**Examples:**
```python
# GET request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="get",
    url="https://api.example.com/users",
    headers={"Authorization": "Bearer token123"}
)

# POST request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="post",
    url="https://api.example.com/users",
    data={"name": "John", "email": "john@example.com"},
    headers={"Content-Type": "application/json"}
)

# PUT request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="put",
    url="https://api.example.com/users/123",
    data={"name": "John Updated"}
)

# DELETE request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="delete",
    url="https://api.example.com/users/123"
)

# PATCH request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="patch",
    url="https://api.example.com/users/123",
    data={"email": "newemail@example.com"}
)

# Generic request
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="request",
    method="GET",
    url="https://api.example.com/data"
)
```

---

## 3. WebSocket Client Interface

**Purpose:** WebSocket operations
**Location:** `EE/networking/websocket_client/`

### Operations

#### connect, send, receive, close

**Parameters:**
- `url` (str, required): WebSocket URL
- `message` (str/dict, optional): Message to send
- `timeout` (int, optional): Operation timeout

**Returns:** Connection ID or message data

**Examples:**
```python
# Connect
conn_id = execute_operation(
    domain="networking",
    interface="websocket_client",
    operation="connect",
    url="wss://example.com/socket"
)

# Send message
execute_operation(
    domain="networking",
    interface="websocket_client",
    operation="send",
    connection_id=conn_id,
    message={"type": "greeting", "text": "Hello"}
)

# Receive message
message = execute_operation(
    domain="networking",
    interface="websocket_client",
    operation="receive",
    connection_id=conn_id
)

# Close connection
execute_operation(
    domain="networking",
    interface="websocket_client",
    operation="close",
    connection_id=conn_id
)
```

---

## 4. Protocol Client Interfaces

### Redis Interface

**Location:** `EE/networking/protocols/redis/`

```python
# Redis operations
execute_operation(domain="networking", interface="redis", operation="get", key="user:123")
execute_operation(domain="networking", interface="redis", operation="set", key="user:123", value="data")
execute_operation(domain="networking", interface="redis", operation="delete", key="user:123")
execute_operation(domain="networking", interface="redis", operation="hget", key="user:123", field="name")
execute_operation(domain="networking", interface="redis", operation="hset", key="user:123", field="name", value="John")
execute_operation(domain="networking", interface="redis", operation="publish", channel="events", message="data")
```

---

### MQTT Interface

**Location:** `EE/networking/protocols/mqtt/`

```python
# MQTT operations
conn_id = execute_operation(domain="networking", interface="mqtt", operation="connect",
                           host="broker.example.com", port=1883)
execute_operation(domain="networking", interface="mqtt", operation="publish",
                 connection_id=conn_id, topic="sensor/data", message="temp:22.5")
execute_operation(domain="networking", interface="mqtt", operation="subscribe",
                 connection_id=conn_id, topic="sensor/#")
execute_operation(domain="networking", interface="mqtt", operation="unsubscribe",
                 connection_id=conn_id, topic="sensor/#")
```

---

### LDAP Interface

**Location:** `EE/networking/protocols/ldap/`

```python
# LDAP operations
conn_id = execute_operation(domain="networking", interface="ldap", operation="bind",
                           uri="ldap://server.example.com", bind_dn="cn=admin,dc=example,dc=com",
                           bind_password="secret")
results = execute_operation(domain="networking", interface="ldap", operation="search",
                           connection_id=conn_id, base_dn="ou=users,dc=example,dc=com",
                           search_filter="(objectClass=person)")
execute_operation(domain="networking", interface="ldap", operation="unbind", connection_id=conn_id)
```

---

### SNMP Interface

**Location:** `EE/networking/protocols/snmp/`

```python
# SNMP operations
result = execute_operation(domain="networking", interface="snmp", operation="get",
                          host="router.example.com", community="public", oid="1.3.6.1.2.1.1.1.0")
execute_operation(domain="networking", interface="snmp", operation="set",
                  host="router.example.com", community="private", oid="1.3.6.1.2.1.1.1.0", value="value")
results = execute_operation(domain="networking", interface="snmp", operation="walk",
                           host="router.example.com", community="public", oid="1.3.6.1.2.1.1")
```

---

### NTP Interface

**Location:** `EE/networking/protocols/ntp/`

```python
# NTP operations
time = execute_operation(domain="networking", interface="ntp", operation="get_time",
                        server="pool.ntp.org")
execute_operation(domain="networking", interface="ntp", operation="sync_time",
                 server="pool.ntp.org")
status = execute_operation(domain="networking", interface="ntp", operation="check_sync",
                          server="pool.ntp.org")
```

---

### Memcached Interface

**Location:** `EE/networking/protocols/memcached/`

```python
# Memcached operations
execute_operation(domain="networking", interface="memcached", operation="get", key="user:123")
execute_operation(domain="networking", interface="memcached", operation="set",
                 key="user:123", value="data", expiry=3600)
execute_operation(domain="networking", interface="memcached", operation="delete", key="user:123")
execute_operation(domain="networking", interface="memcached", operation="add",
                 key="user:123", value="data", expiry=3600)
execute_operation(domain="networking", interface="memcached", operation="replace",
                 key="user:123", value="data", expiry=3600)
```

---

### RPC Interface

**Location:** `EE/networking/protocols/rpc/`

```python
# RPC operations
result = execute_operation(domain="networking", interface="rpc", operation="call",
                          method="user.get", params={"user_id": 123})
execute_operation(domain="networking", interface="rpc", operation="notify",
                 method="user.update", params={"user_id": 123, "name": "John"})
results = execute_operation(domain="networking", interface="rpc", operation="batch",
                           calls=[{"method": "user.get", "params": {"user_id": 1}},
                                 {"method": "user.get", "params": {"user_id": 2}}])
execute_operation(domain="networking", interface="rpc", operation="register",
                 method="custom.method", handler=lambda x: process(x))
```

---

## Cross-Domain Operations

**Networking may call:**
- `foundation.config` - For connection settings
- `security.authentication` - For auth
- `observability.logging` - For connection logs

**All domains may call:**
- `networking.http_client` - For HTTP operations
- `networking.connectivity` - For connectivity checks

---

## Pooling

**HTTP sessions:** Pool of 10-20 instances
**WebSocket connections:** Pool of 5-10 instances
**Protocol connections:** Pool per protocol
**Connectivity checkers:** Pool of 3-5 instances

---

## Examples

### HTTP Client with Retries

```python
def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = execute_operation(
                domain="networking",
                interface="http_client",
                operation="get",
                url=url,
                timeout=10
            )

            if response["status"] == 200:
                return response["body"]

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Connectivity Check

```python
def check_service_health(host, port):
    reachable = execute_operation(
        domain="networking",
        interface="connectivity",
        operation="check_connection",
        target=host,
        port=port,
        timeout=5
    )

    if not reachable:
        execute_operation(
            domain="observability",
            interface="logging",
            operation="warning",
            message=f"Service unreachable: {host}:{port}"
        )

    return reachable
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory
- [DEC-EE-03](../../SIMA/projects/EE/decisions/DEC-EE-03-ISP-Domain-Merge.md) - ISP domain merger

**Implementation:**
- `EE/networking/networking_gateway.py` - Gateway implementation
- Individual protocol interface directories

---

**END OF NETWORKING DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 349 (target achieved)
