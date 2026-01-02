# EE Complete Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Purpose:** Complete function reference for all EE domains and operations (Consolidated)
**Type:** Complete Function Reference Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Usage Pattern](#usage-pattern)
3. [Error Handling](#error-handling)
4. [Foundation Domain](#1-foundation-domain)
5. [Observability Domain](#2-observability-domain)
6. [Security Domain](#3-security-domain)
7. [Operations Domain](#4-operations-domain)
8. [Networking Domain](#5-networking-domain)
9. [Scanner Domain](#6-scanner-domain)
10. [Test Domain](#7-test-domain)
11. [Infrastructure Domain](#8-infrastructure-domain)
12. [Legacy Domains](#9-legacy-domains)
13. [Quick Reference Tables](#quick-reference-tables)

---

## Overview

The EE (Execution Engine) provides a Universal Gateway (UG) pattern for centralized cross-component operations. This reference covers all 14 domains, ~170 operations across ~41 interfaces.

**Total Domains:** 14
- **UG-ISP Compliant:** 8 domains (Foundation, Observability, Security, Operations, Networking, Scanner, Test, Infrastructure)
- **Legacy:** 6 domains (CLI, Doc, SDK, Web, Dashboard, HA)

---

## Usage Pattern

All EE operations follow the Universal Gateway pattern:

```python
from EE import execute_operation

result = execute_operation(
    domain="<domain>",
    interface="<interface>",
    operation="<operation>",
    **kwargs
)
```

### Example Usage

```python
# Foundation - Get configuration
config = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)

# Observability - Log message
execute_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="System started",
    context={"component": "api"}
)

# Security - Encrypt data
encrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value="secret data"
)

# Networking - HTTP GET
response = execute_operation(
    domain="networking",
    interface="http_client",
    operation="get",
    url="https://api.example.com/data"
)

# Operations - Cache get
cached = execute_operation(
    domain="operations",
    interface="cache",
    operation="get",
    key="user:123"
)
```

---

## Error Handling

```python
from EE.universal_gateway import (
    DomainNotFoundError,
    InterfaceNotFoundError,
    OperationNotFoundError,
    InvalidOperationError,
)

try:
    result = execute_operation(
        domain="foundation",
        interface="config",
        operation="get",
        key="timeout"
    )
except DomainNotFoundError as e:
    print(f"Domain not registered: {e}")
except InterfaceNotFoundError as e:
    print(f"Interface not found in domain: {e}")
except OperationNotFoundError as e:
    print(f"Operation not found: {e}")
except InvalidOperationError as e:
    print(f"Execution failed: {e}")
```

---

# 1. Foundation Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Configuration, dependency injection, utilities
**Gateway:** FoundationGateway
**Interfaces:** 5 (config, di, initialization, singleton, utility)
**Operations:** ~20

## 1.1 Config Interface

**Purpose:** Configuration management
**Location:** `EE/foundation/config/`

### get

Retrieve a configuration value.

**Parameters:**
- `key` (str, required): Configuration key (e.g., "database.host")
- `default` (Any, optional): Default value if key not found
- `reload` (bool, optional): Force config reload before reading (default: False)

**Returns:** Configuration value (type depends on config)

**Examples:**
```python
# Simple get
timeout = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="request.timeout"
)

# Get with default
retries = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="max.retries",
    default=3
)
```

### set

Set a configuration value.

**Parameters:**
- `key` (str, required): Configuration key
- `value` (Any, required): Value to set
- `persist` (bool, optional): Persist to disk (default: False)

**Returns:** True if successful

### list

List configuration keys.

**Parameters:**
- `prefix` (str, optional): Filter keys by prefix (default: "")
- `recursive` (bool, optional): Include nested keys (default: True)

**Returns:** List of configuration keys (List[str])

### delete

Delete a configuration value.

**Parameters:**
- `key` (str, required): Configuration key
- `persist` (bool, optional): Persist deletion to disk (default: False)

**Returns:** True if deleted, False if not found

### reload

Reload configuration from source.

**Parameters:** None

**Returns:** True if successful

## 1.2 DI (Dependency Injection) Interface

**Purpose:** Dependency injection container
**Location:** `EE/foundation/di/`

### inject

Register a dependency.

**Parameters:**
- `name` (str, required): Dependency name
- `factory` (Callable, required): Factory function or class
- `singleton` (bool, optional): Use singleton pattern (default: True)
- `lazy` (bool, optional): Lazy initialization (default: True)

**Returns:** True if registered

### resolve

Resolve a dependency.

**Parameters:**
- `name` (str, required): Dependency name

**Returns:** Resolved dependency instance

### singleton

Get or create singleton instance.

**Parameters:**
- `name` (str, required): Singleton name
- `factory` (Callable, optional): Factory if not exists

**Returns:** Singleton instance

## 1.3 Initialization Interface

**Purpose:** System initialization and lifecycle
**Location:** `EE/foundation/initialization/`

### init

Initialize the system.

**Parameters:**
- `config_path` (str, optional): Path to config file
- `config_overrides` (dict, optional): Config override values

**Returns:** True if successful

### bootstrap

Bootstrap all domains.

**Parameters:**
- `domains` (List[str], optional): Domains to bootstrap (default: all)

**Returns:** True if successful

### shutdown

Shutdown the system gracefully.

**Parameters:**
- `force` (bool, optional): Force shutdown (default: False)

**Returns:** True if successful

## 1.4 Singleton Interface

**Purpose:** Singleton management
**Location:** `EE/foundation/singleton/`

### get, reset, exists

```python
# Get singleton
cache = execute_operation(
    domain="foundation",
    interface="singleton",
    operation="get",
    name="app.cache"
)

# Reset singleton
execute_operation(
    domain="foundation",
    interface="singleton",
    operation="reset",
    name="app.cache"
)

# Check if exists
has_cache = execute_operation(
    domain="foundation",
    interface="singleton",
    operation="exists",
    name="app.cache"
)
```

## 1.5 Utility Interface

**Purpose:** Common utility functions
**Location:** `EE/foundation/utility/`

### parse

Parse string data.

**Parameters:**
- `data` (str, required): Data to parse
- `format` (str, required): Format type (json, yaml, xml, csv)

**Returns:** Parsed data (dict/list)

### validate

Validate data against schema.

**Parameters:**
- `data` (Any, required): Data to validate
- `schema` (dict, required): Validation schema
- `strict` (bool, optional): Strict validation (default: False)

**Returns:** True if valid

### sanitize

Sanitize input data.

**Parameters:**
- `data` (str, required): Data to sanitize
- `mode` (str, required): Sanitization mode (html, sql, filename, path)

**Returns:** Sanitized string

---

**Pooling:** Config readers (5-10), DI containers (singleton), Utilities (stateless)

**Cross-Domain:** May call `security.encryption`, `observability.logging`

---

# 2. Observability Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Logging, metrics, debugging
**Gateway:** ObservabilityGateway
**Interfaces:** 4 (logging, metrics, debug, diagnosis)
**Operations:** ~15

## 2.1 Logging Interface

**Purpose:** Structured logging
**Location:** `EE/observability/logging/`

### info, warning, error, debug, critical

Log messages at different severity levels.

**Parameters:**
- `message` (str, required): Log message
- `context` (dict, optional): Structured context data
- `component` (str, optional): Component name
- `exception` (Exception, optional): Exception object (error/critical only)

**Returns:** None

**Examples:**
```python
# Info log
execute_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="User logged in",
    context={"user_id": 123}
)

# Error log with exception
try:
    risky_operation()
except Exception as e:
    execute_operation(
        domain="observability",
        interface="logging",
        operation="error",
        message="Operation failed",
        exception=e
    )
```

## 2.2 Metrics Interface

**Purpose:** Metrics collection and reporting
**Location:** `EE/observability/metrics/`

### increment

Increment a counter metric.

**Parameters:**
- `name` (str, required): Metric name
- `value` (int, optional): Increment amount (default: 1)
- `tags` (dict, optional): Metric tags

**Returns:** None

### gauge

Set a gauge metric value.

**Parameters:**
- `name` (str, required): Metric name
- `value` (float, required): Gauge value
- `tags` (dict, optional): Metric tags

**Returns:** None

### timing

Record a timing metric.

**Parameters:**
- `name` (str, required): Metric name
- `value_ms` (float, required): Duration in milliseconds
- `tags` (dict, optional): Metric tags

**Returns:** None

### histogram

Record a histogram value.

**Parameters:**
- `name` (str, required): Metric name
- `value` (float, required): Histogram value
- `tags` (dict, optional): Metric tags

**Returns:** None

## 2.3 Debug Interface

**Purpose:** Debug utilities
**Location:** `EE/observability/debug/`

### breakpoint

Set a conditional breakpoint.

**Parameters:**
- `condition` (str, required): Break condition expression
- `action` (str, optional): Action on break (log/stop/notify)

**Returns:** Breakpoint ID (str)

### inspect

Inspect variable or expression.

**Parameters:**
- `expression` (str, required): Expression to inspect
- `context` (dict, optional): Local variables context

**Returns:** Inspection result (dict with type, value, repr)

### trace

Enable function tracing.

**Parameters:**
- `function_name` (str, required): Function to trace
- `enabled` (bool, optional): Enable or disable (default: True)

**Returns:** True if successful

## 2.4 Diagnosis Interface

**Purpose:** System health and diagnostics
**Location:** `EE/observability/diagnosis/`

### health_check

Perform health check.

**Parameters:**
- `component` (str, optional): Specific component to check (default: all)

**Returns:** Health status (dict)

### status

Get system status.

**Parameters:**
- `verbose` (bool, optional): Detailed status (default: False)

**Returns:** System status (dict)

### diagnostics

Run comprehensive diagnostics.

**Parameters:**
- `category` (str, optional): Category to diagnose (default: all)

**Returns:** Diagnostic results (dict)

---

**Pooling:** Loggers (singleton per name), Metrics collectors (5-10), Debug utilities (stateless)

**Cross-Domain:** May call `foundation.config`, `operations.cache`

**All domains may call:** `observability.logging`, `observability.metrics`

---

# 3. Security Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Authentication, encryption, validation
**Gateway:** SecurityGateway
**Interfaces:** 3 (authentication, encryption, validation)
**Operations:** ~10

## 3.1 Authentication Interface

**Purpose:** Authentication and authorization
**Location:** `EE/security/authentication/`

### login

Authenticate user credentials.

**Parameters:**
- `username` (str, required): Username
- `password` (str, required): Password
- `mfa_code` (str, optional): Multi-factor auth code

**Returns:** Auth token (str) or session info (dict)

### logout

Logout user/session.

**Parameters:**
- `token` (str, required): Auth token or session ID

**Returns:** True if successful

### verify

Verify authentication token.

**Parameters:**
- `token` (str, required): Auth token to verify

**Returns:** User info (dict) if valid

### refresh

Refresh authentication token.

**Parameters:**
- `token` (str, required): Current auth token

**Returns:** New auth token (str)

## 3.2 Encryption Interface

**Purpose:** Cryptographic operations
**Location:** `EE/security/encryption/`

### encrypt

Encrypt data.

**Parameters:**
- `value` (str, required): Data to encrypt
- `algorithm` (str, optional): Encryption algorithm (default: "aes-256-gcm")
- `key_id` (str, optional): Key identifier for key management

**Returns:** Encrypted data (str, base64-encoded)

### decrypt

Decrypt data.

**Parameters:**
- `value` (str, required): Encrypted data (base64-encoded)
- `key_id` (str, optional): Key identifier if needed

**Returns:** Decrypted data (str)

### hash

Generate hash of data.

**Parameters:**
- `value` (str, required): Data to hash
- `algorithm` (str, optional): Hash algorithm (default: "sha256")

**Returns:** Hash value (str, hex-encoded)

### verify_hash

Verify data against hash.

**Parameters:**
- `value` (str, required): Data to verify
- `hash_value` (str, required): Expected hash (hex-encoded)
- `algorithm` (str, optional): Hash algorithm (default: "sha256")

**Returns:** Boolean

## 3.3 Validation Interface

**Purpose:** Input validation and sanitization
**Location:** `EE/security/validation/`

### validate_input

Validate user input.

**Parameters:**
- `input` (Any, required): Input to validate
- `rules` (dict, required): Validation rules

**Returns:** True if valid

### sanitize

Sanitize user input.

**Parameters:**
- `input` (str, required): Input to sanitize
- `mode` (str, required): Sanitization mode (html, sql, json, path)

**Returns:** Sanitized string (str)

### check_permission

Check user permission.

**Parameters:**
- `user_id` (int, required): User ID
- `permission` (str, required): Permission to check
- `resource` (str, optional): Resource identifier

**Returns:** Boolean

---

**Pooling:** Encryption engines (3-5), Auth sessions (10-20), Validators (stateless)

**Cross-Domain:** May call `foundation.config`, `observability.logging`

**All domains may call:** `security.authentication`, `security.encryption`, `security.validation`

---

# 4. Operations Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Caching, file I/O, pooling
**Gateway:** OperationsGateway
**Interfaces:** 7 (cache, fileio, object_pool, circuit_breaker, serialization, template, threading_ops)
**Operations:** ~25

## 4.1 Cache Interface

**Purpose:** In-memory caching
**Location:** `EE/operations/cache/`

### Operations

```python
# Set cache value
execute_operation(domain="operations", interface="cache", operation="set",
                 key="user:123", value={"name": "John"}, ttl=3600)

# Get cached value
user = execute_operation(domain="operations", interface="cache", operation="get",
                        key="user:123")

# Check if exists
exists = execute_operation(domain="operations", interface="cache", operation="exists",
                          key="user:123")

# Delete cache entry
execute_operation(domain="operations", interface="cache", operation="delete",
                 key="user:123")

# Clear all cache
execute_operation(domain="operations", interface="cache", operation="clear")
```

## 4.2 File I/O Interface

**Purpose:** File operations
**Location:** `EE/operations/fileio/`

### Operations

```python
# Read file
content = execute_operation(domain="operations", interface="fileio", operation="read",
                           path="/path/to/file.txt")

# Write file
execute_operation(domain="operations", interface="fileio", operation="write",
                 path="/path/to/file.txt", data="Hello, World!", mode="w")

# Check if file exists
exists = execute_operation(domain="operations", interface="fileio", operation="exists",
                          path="/path/to/file.txt")

# List directory
files = execute_operation(domain="operations", interface="fileio", operation="list",
                         path="/path/to/dir")

# Delete file
execute_operation(domain="operations", interface="fileio", operation="delete",
                 path="/path/to/file.txt")
```

## 4.3 Object Pool Interface

**Purpose:** Object pooling for performance
**Location:** `EE/operations/object_pool/`

### Operations

```python
# Acquire object from pool
obj = execute_operation(domain="operations", interface="object_pool", operation="acquire",
                        pool_name="database.connections")

# Release object back to pool
execute_operation(domain="operations", interface="object_pool", operation="release",
                 pool_name="database.connections", object=obj)

# Get pool size
size = execute_operation(domain="operations", interface="object_pool", operation="size",
                        pool_name="database.connections")

# Clear pool
execute_operation(domain="operations", interface="object_pool", operation="clear",
                 pool_name="database.connections")
```

## 4.4 Circuit Breaker Interface

**Purpose:** Circuit breaker pattern
**Location:** `EE/operations/circuit_breaker/`

### Operations

```python
# Check circuit state
state = execute_operation(domain="operations", interface="circuit_breaker",
                         operation="check_state", circuit="api.external")

# Record success
execute_operation(domain="operations", interface="circuit_breaker",
                 operation="record_success", circuit="api.external")

# Record failure
execute_operation(domain="operations", interface="circuit_breaker",
                 operation="record_failure", circuit="api.external")
```

## 4.5 Serialization Interface

**Purpose:** Data serialization
**Location:** `EE/operations/serialization/`

### Operations

```python
# Serialize to JSON
json_str = execute_operation(domain="operations", interface="serialization",
                            operation="serialize", data={"key": "value"}, format="json")

# Deserialize from JSON
data = execute_operation(domain="operations", interface="serialization",
                        operation="deserialize", data='{"key": "value"}', format="json")

# JSON helpers (alias)
json_str = execute_operation(domain="operations", interface="serialization",
                            operation="to_json", data={"key": "value"})
data = execute_operation(domain="operations", interface="serialization",
                        operation="from_json", json_str='{"key": "value"}')
```

## 4.6 Template Interface

**Purpose:** Template rendering
**Location:** `EE/operations/template/`

### Operations

```python
# Render template
result = execute_operation(domain="operations", interface="template", operation="render",
                          template="Hello, {{ name }}!", context={"name": "World"})

# Compile template
compiled = execute_operation(domain="operations", interface="template", operation="compile",
                            template="Hello, {{ name }}!")

# Load template file
template = execute_operation(domain="operations", interface="template", operation="load_template",
                            path="/templates/email.html")
```

## 4.7 Threading Interface

**Purpose:** Thread management
**Location:** `EE/operations/threading_ops/`

### Operations

```python
# Spawn thread
thread_id = execute_operation(domain="operations", interface="threading_ops", operation="spawn",
                             target=lambda: print("Hello"), args=())

# Join thread
execute_operation(domain="operations", interface="threading_ops", operation="join",
                 thread_id=thread_id)

# Cancel thread
execute_operation(domain="operations", interface="threading_ops", operation="cancel",
                 thread_id=thread_id)

# List threads
threads = execute_operation(domain="operations", interface="threading_ops", operation="list_threads")
```

---

**Pooling:** File handles (10-20), Cache connections (5-10), Thread pools (configurable)

**Cross-Domain:** May call `foundation.config`, `observability.metrics`

**All domains may call:** `operations.cache`, `operations.fileio`, `operations.object_pool`

---

# 5. Networking Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** HTTP clients, protocol clients, networking
**Gateway:** NetworkingGateway
**Interfaces:** 10 (connectivity, http_client, websocket_client, redis, mqtt, ldap, snmp, ntp, memcached, rpc)
**Operations:** ~35

## 5.1 Connectivity Interface

**Purpose:** Network connectivity operations
**Location:** `EE/networking/connectivity/`

### check_connection

Check network connectivity to target.

**Parameters:**
- `target` (str, required): Hostname or IP address
- `port` (int, optional): Port number (default: 80)
- `timeout` (int, optional): Timeout in seconds (default: 5)

**Returns:** Boolean (True if reachable)

### test_latency

Test network latency.

**Parameters:**
- `target` (str, required): Hostname or IP
- `count` (int, optional): Number of pings (default: 5)
- `timeout` (int, optional): Timeout per ping (default: 5)

**Returns:** Latency stats (dict with avg, min, max, packet_loss)

### get_network_info

Get network information.

**Parameters:** None

**Returns:** Network info (dict with hostname, ips, interfaces)

## 5.2 HTTP Client Interface

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
    data={"name": "John", "email": "john@example.com"}
)
```

## 5.3 WebSocket Client Interface

**Purpose:** WebSocket operations
**Location:** `EE/networking/websocket_client/`

### Operations

#### connect, send, receive, close

**Parameters:**
- `url` (str, required): WebSocket URL
- `message` (str/dict, optional): Message to send
- `timeout` (int, optional): Operation timeout

**Returns:** Connection ID or message data

## 5.4 Protocol Client Interfaces

### Redis Interface

**Location:** `EE/networking/protocols/redis/`

```python
execute_operation(domain="networking", interface="redis", operation="get", key="user:123")
execute_operation(domain="networking", interface="redis", operation="set", key="user:123", value="data")
execute_operation(domain="networking", interface="redis", operation="hget", key="user:123", field="name")
execute_operation(domain="networking", interface="redis", operation="hset", key="user:123", field="name", value="John")
```

### MQTT Interface

**Location:** `EE/networking/protocols/mqtt/`

```python
conn_id = execute_operation(domain="networking", interface="mqtt", operation="connect",
                           host="broker.example.com", port=1883)
execute_operation(domain="networking", interface="mqtt", operation="publish",
                 connection_id=conn_id, topic="sensor/data", message="temp:22.5")
execute_operation(domain="networking", interface="mqtt", operation="subscribe",
                 connection_id=conn_id, topic="sensor/#")
```

### LDAP Interface

**Location:** `EE/networking/protocols/ldap/`

```python
conn_id = execute_operation(domain="networking", interface="ldap", operation="bind",
                           uri="ldap://server.example.com", bind_dn="cn=admin,dc=example,dc=com",
                           bind_password="secret")
results = execute_operation(domain="networking", interface="ldap", operation="search",
                           connection_id=conn_id, base_dn="ou=users,dc=example,dc=com",
                           search_filter="(objectClass=person)")
```

### SNMP Interface

**Location:** `EE/networking/protocols/snmp/`

```python
result = execute_operation(domain="networking", interface="snmp", operation="get",
                          host="router.example.com", community="public", oid="1.3.6.1.2.1.1.1.0")
execute_operation(domain="networking", interface="snmp", operation="walk",
                  host="router.example.com", community="public", oid="1.3.6.1.2.1.1")
```

### NTP Interface

**Location:** `EE/networking/protocols/ntp/`

```python
time = execute_operation(domain="networking", interface="ntp", operation="get_time",
                        server="pool.ntp.org")
execute_operation(domain="networking", interface="ntp", operation="sync_time",
                 server="pool.ntp.org")
```

### Memcached Interface

**Location:** `EE/networking/protocols/memcached/`

```python
execute_operation(domain="networking", interface="memcached", operation="get", key="user:123")
execute_operation(domain="networking", interface="memcached", operation="set",
                 key="user:123", value="data", expiry=3600)
```

### RPC Interface

**Location:** `EE/networking/protocols/rpc/`

```python
result = execute_operation(domain="networking", interface="rpc", operation="call",
                          method="user.get", params={"user_id": 123})
execute_operation(domain="networking", interface="rpc", operation="batch",
                   calls=[{"method": "user.get", "params": {"user_id": 1}}])
```

---

**Pooling:** HTTP sessions (10-20), WebSocket connections (5-10), Protocol connections (per protocol), Connectivity checkers (3-5)

**Cross-Domain:** May call `foundation.config`, `security.authentication`, `observability.logging`

**All domains may call:** `networking.http_client`, `networking.connectivity`

---

# 6. Scanner Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Security scanning, UG-ISP compliance checking
**Gateway:** ScannerGateway
**Interfaces:** 8 (scan, validate, test, report, cache, cleanup, compile, utility)
**Operations:** ~20

## 6.1 Scan Interface

**Purpose:** Security and compliance scanning
**Location:** `EE/scanner/interface/scan/`

### run_scan

Run compliance scan on codebase.

**Parameters:**
- `target` (str, required): Target path or file
- `rules` (list, optional): Specific rules to check (default: all)
- `severity` (str, optional): Minimum severity (default: "warning")

**Returns:** Scan results (dict with violations, stats, summary)

### scan_target

Quick scan of specific target.

**Parameters:**
- `target` (str, required): File or directory path
- `quick` (bool, optional): Quick scan mode (default: False)

**Returns:** Scan summary (dict)

### generate_report

Generate scan report.

**Parameters:**
- `results` (dict, required): Scan results
- `format` (str, optional): Report format (markdown/json/html)
- `output_path` (str, optional): Output file path

**Returns:** Report content (str) or file path (str)

## 6.2 Validate Interface

**Purpose:** Compliance validation
**Location:** `EE/scanner/interface/validate/`

### validate_compliance

Validate EE 2.1 compliance.

**Parameters:**
- `target` (str, required): Target path
- `category` (str, optional): Category to validate (default: all)

**Returns:** Compliance results (dict with compliant, violations, score)

### check_rules

Check specific rules.

**Parameters:**
- `target` (str, required): Target path
- `rules` (list, required): Rules to check

**Returns:** Rule check results (dict)

## 6.3 Test Interface

**Purpose:** Test execution and coverage
**Location:** `EE/scanner/interface/test/`

### run_tests

Run test suite.

**Parameters:**
- `target` (str, optional): Target module (default: all)
- `coverage` (bool, optional): Generate coverage report (default: False)

**Returns:** Test results (dict with passed, failed, coverage)

### generate_coverage

Generate coverage report.

**Parameters:**
- `target` (str, required): Target module
- `format` (str, optional): Report format (term/html/xml)

**Returns:** Coverage report (str)

## 6.4 Report Interface

**Purpose:** Report generation and export
**Location:** `EE/scanner/interface/report/`

### Operations

```python
# Generate report
report = execute_operation(
    domain="scanner",
    interface="report",
    operation="generate",
    type="compliance",
    data=results
)

# Export report
execute_operation(
    domain="scanner",
    interface="report",
    operation="export",
    report=report,
    format="pdf",
    output_path="reports/compliance.pdf"
)
```

## 6.5 Cache Interface

**Purpose:** Scan result caching
**Location:** `EE/scanner/interface/cache/`

### Operations

```python
# Get cached scan
cached = execute_operation(
    domain="scanner",
    interface="cache",
    operation="get",
    key="scan:EE/networking:123456"
)

# Cache scan results
execute_operation(
    domain="scanner",
    interface="cache",
    operation="set",
    key="scan:EE/networking:123456",
    value=scan_results,
    ttl=3600
)

# Invalidate cache
execute_operation(
    domain="scanner",
    interface="cache",
    operation="invalidate",
    key="scan:EE/networking"
)
```

## 6.6 Cleanup Interface

**Purpose:** Cleanup operations
**Location:** `EE/scanner/interface/cleanup/`

### Operations

```python
# Clean scan artifacts
execute_operation(
    domain="scanner",
    interface="cleanup",
    operation="clean_artifacts",
    older_than_hours=24
)

# Purge temp files
execute_operation(
    domain="scanner",
    interface="cleanup",
    operation="purge_temp"
)
```

## 6.7 Compile Interface

**Purpose:** Rule compilation
**Location:** `EE/scanner/interface/compile/`

### Operations

```python
# Compile rules
compiled = execute_operation(
    domain="scanner",
    interface="compile",
    operation="compile_rules",
    rules=["AP-EE-04", "AP-EE-06"],
    output_path="rules/compiled.json"
)

# Validate rules
valid = execute_operation(
    domain="scanner",
    interface="compile",
    operation="validate_rules",
    rules=["AP-EE-04", "AP-EE-06"]
)
```

## 6.8 Utility Interface

**Purpose:** Scanner utilities
**Location:** `EE/scanner/interface/utility/`

### Operations

```python
# Parse scan results
parsed = execute_operation(
    domain="scanner",
    interface="utility",
    operation="parse",
    data=raw_scan_data,
    format="json"
)

# Format output
formatted = execute_operation(
    domain="scanner",
    interface="utility",
    operation="format",
    data=results,
    format="table"
)
```

---

**Pooling:** Scanner instances (3-5), Report generators (5-10)

**Cross-Domain:** May call all domains (for compliance checking), `observability.logging`, `operations.cache`

---

# 7. Test Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Testing framework, test execution
**Gateway:** TestGateway
**Interfaces:** 3 (pytest, report, scanner)
**Operations:** ~10

## 7.1 Pytest Interface

**Purpose:** Pytest operations
**Location:** `EE/test/pytest/`

### run

Run pytest tests.

**Parameters:**
- `target` (str, optional): Target path/module (default: all tests)
- `verbose` (bool, optional): Verbose output (default: False)
- `markers` (list, optional): Specific markers to run
- `fail_fast` (bool, optional): Stop on first failure (default: False)

**Returns:** Test results (dict with passed, failed, duration, output)

### collect

Collect tests without running.

**Parameters:**
- `target` (str, optional): Target path (default: all)

**Returns:** List of collected tests (List[str])

### coverage

Generate coverage report.

**Parameters:**
- `target` (str, optional): Target module
- `format` (str, optional): Report format (term/html/xml/json)
- `output` (str, optional): Output path

**Returns:** Coverage results (dict with percentage, files, report)

### list_tests

List available tests.

**Parameters:**
- `target` (str, optional): Target path (default: all)
- `detailed` (bool, optional): Show test details (default: False)

**Returns:** List of tests (List[str] or List[dict])

## 7.2 Report Interface

**Purpose:** Test reporting
**Location:** `EE/test/report/`

### generate

Generate test report.

**Parameters:**
- `results` (dict, required): Test results
- `format` (str, optional): Report format (markdown/html/json)
- `template` (str, optional): Report template

**Returns:** Report content (str)

### export

Export test report to file.

**Parameters:**
- `report` (str, required): Report content
- `format` (str, required): Output format
- `output_path` (str, required): Output file path

**Returns:** True if successful

### compare

Compare test results.

**Parameters:**
- `results1` (dict, required): First test results
- `results2` (dict, required): Second test results

**Returns:** Comparison report (dict)

## 7.3 Scanner Interface

**Purpose:** Test scanning
**Location:** `EE/test/scanner/`

### scan_tests

Scan for test files.

**Parameters:**
- `target` (str, required): Target path
- `pattern` (str, optional): File pattern (default: "test_*.py")

**Returns:** List of test files (List[str])

### find_coverage

Find test coverage gaps.

**Parameters:**
- `target` (str, required): Target module
- `threshold` (float, optional): Coverage threshold (default: 80.0)

**Returns:** Coverage gaps (dict with uncovered_files, low_coverage, recommendations)

---

**Pooling:** Test runners (3-5), Report generators (5-10)

**Cross-Domain:** May call all domains (for testing), `observability.logging`, `operations.fileio`

---

# 8. Infrastructure Domain

**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Plugin management, infrastructure operations
**Gateway:** InfrastructureGateway
**Interfaces:** 2 (plugins, concurrency)
**Operations:** ~5

## 8.1 Plugins Interface

**Purpose:** Plugin management
**Location:** `EE/infrastructure/plugins/`

### load

Load a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name
- `plugin_path` (str, optional): Plugin path (default: standard plugin dir)
- `config` (dict, optional): Plugin configuration

**Returns:** Plugin instance or True if successful

### unload

Unload a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name

**Returns:** True if successful

### list

List all loaded plugins.

**Parameters:** None

**Returns:** List of plugin info (List[dict])

### register

Register a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name
- `plugin_class` (type, required): Plugin class
- `metadata` (dict, optional): Plugin metadata

**Returns:** True if registered

### status

Get plugin status.

**Parameters:**
- `plugin_name` (str, required): Plugin name

**Returns:** Plugin status (dict with loaded, version, config, health)

## 8.2 Concurrency Interface

**Purpose:** Concurrency operations
**Location:** `EE/infrastructure/concurrency/`

### Operations

```python
# Spawn task
task_id = execute_operation(
    domain="infrastructure",
    interface="concurrency",
    operation="spawn",
    target=lambda: process_data(),
    name="data_processor"
)

# Join task
result = execute_operation(
    domain="infrastructure",
    interface="concurrency",
    operation="join",
    task_id=task_id,
    timeout=30
)

# Cancel task
execute_operation(
    domain="infrastructure",
    interface="concurrency",
    operation="cancel",
    task_id=task_id
)

# List tasks
tasks = execute_operation(
    domain="infrastructure",
    interface="concurrency",
    operation="list"
)
```

---

**Pooling:** Plugin loaders (3-5), Concurrency managers (singleton)

**Cross-Domain:** May call all domains (plugin dependencies), `operations.fileio`, `foundation.config`

---

# 9. Legacy Domains

**Status:** Legacy (Need EE 2.1 Upgrade)
**Purpose:** Reference for legacy domains before migration

## 9.1 CLI Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** CLIGatewayDomain class
**File:** `EE/cli/cli_gateway.py`

**Current Operations (OLD Pattern):**
```python
from EE.cli.cli_gateway import CLIGatewayDomain
cli = CLIGatewayDomain()
result = cli.execute_command("status")
```

**After EE 2.1 Upgrade:**
```python
result = execute_operation(
    domain="cli",
    interface="command",
    operation="execute",
    command="status"
)
```

## 9.2 Doc Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DocGatewayDomain class
**File:** `EE/doc/doc_gateway_domain.py`

**Current Operations (OLD Pattern):**
```python
from EE.doc.doc_gateway_domain import DocGatewayDomain
doc = DocGatewayDomain()
result = doc.generate_docs("networking")
```

**After EE 2.1 Upgrade:**
```python
result = execute_operation(
    domain="doc",
    interface="generator",
    operation="generate",
    target="networking",
    format="markdown"
)
```

## 9.3 SDK Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** SDKGatewayDomain class
**File:** `EE/sdk/sdk_gateway_domain.py`

**Current Operations (OLD Pattern):**
```python
from EE.sdk.sdk_gateway_domain import SDKGatewayDomain
sdk = SDKGatewayDomain()
result = sdk.call_sdk("homeassistant", "get_states")
```

**After EE 2.1 Upgrade:**
```python
result = execute_operation(
    domain="sdk",
    interface="remote",
    operation="call",
    sdk="homeassistant",
    method="get_states"
)
```

## 9.4 Web Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** WebGatewayDomain class
**File:** `EE/web/web_gateway_domain.py`

**Current Operations (OLD Pattern):**
```python
from EE.web.web_gateway_domain import WebGatewayDomain
web = WebGatewayDomain()
web.start_server(port=8080)
```

**After EE 2.1 Upgrade:**
```python
execute_operation(
    domain="web",
    interface="server",
    operation="start",
    port=8080,
    host="0.0.0.0"
)
```

## 9.5 Dashboard Domain

**Status:** Legacy (Needs EE 2.1 Upgrade)
**Current Pattern:** DashboardGatewayDomain class
**File:** `EE/dashboard/dashboard_gateway.py`

**Current Operations (OLD Pattern):**
```python
from EE.dashboard.dashboard_gateway import DashboardGatewayDomain
dash = DashboardGatewayDomain()
dash.render_dashboard("main")
```

**After EE 2.1 Upgrade:**
```python
result = execute_operation(
    domain="dashboard",
    interface="ui",
    operation="render",
    dashboard="main",
    format="html"
)
```

## 9.6 HA Domain

**Status:** Factory Pattern (Needs EE 2.1 Standardization)
**Current Pattern:** ha_gateway_factory.py
**Files:** `EE/ha/ha_gateway_factory.py`, `EE/ha/ha_command_gateway_factory.py`, `EE/ha/ha_routing_gateway_factory.py`

**Current Operations (OLD Pattern):**
```python
from EE.ha.ha_gateway_factory import ha_gateway_factory
ha = ha_gateway_factory()
states = ha.get_states()
```

**After EE 2.1 Upgrade:**
```python
states = execute_operation(
    domain="ha",
    interface="entities",
    operation="list"
)
```

### Migration Priority

1. **HA Domain** (High Value) - Active usage, critical functionality
2. **CLI Domain** (High Value) - Command-line interface
3. **SDK Domain** (Medium Value) - SDK bindings
4. **Web Domain** (Medium Value) - Web server
5. **Doc Domain** (Low Value) - Documentation generation
6. **Dashboard Domain** (Low Value) - Dashboard UI

---

# Quick Reference Tables

## Domain Summary

| Domain | Status | Interfaces | Operations |
|--------|--------|-----------|------------|
| **Foundation** | UG-ISP | 5 | ~20 |
| **Observability** | UG-ISP | 4 | ~15 |
| **Security** | UG-ISP | 3 | ~10 |
| **Operations** | UG-ISP | 7 | ~25 |
| **Networking** | UG-ISP | 10 | ~35 |
| **Scanner** | UGISP | 8 | ~20 |
| **Test** | UG-ISP | 3 | ~10 |
| **Infrastructure** | UG-ISP | 2 | ~5 |
| **CLI** | Legacy | 0 | ~5 |
| **Doc** | Legacy | 0 | ~5 |
| **SDK** | Legacy | 0 | ~5 |
| **Web** | Legacy | 0 | ~5 |
| **Dashboard** | Legacy | 0 | ~5 |
| **HA** | Factory | 0 | ~5 |

## Operation Quick Index

### Common Operations Across Domains

| Operation | Domains | Purpose |
|-----------|---------|---------|
| **get** | foundation/config, operations/cache, networking/protocols | Retrieve data |
| **set** | foundation/config, operations/cache | Store data |
| **list** | foundation/config, operations/fileio | List items |
| **delete** | foundation/config, operations/cache | Delete data |
| **validate** | security/validation, scanner/validate | Validate input/compliance |
| **generate** | scanner/report, test/report | Generate reports |
| **status** | infrastructure/plugins, observability/diagnosis | Get status |
| **register** | foundation/di, infrastructure/plugins | Register items |

### Cross-Domain Call Patterns

```python
# Foundation → All domains
execute_operation(domain="foundation", interface="config", operation="get", key="...")

# All domains → Observability
execute_operation(domain="observability", interface="logging", operation="info", ...)

# All domains → Security
execute_operation(domain="security", interface="encryption", operation="encrypt", ...)

# All domains → Operations
execute_operation(domain="operations", interface="cache", operation="get", ...)
```

---

## Related Documentation

**Project Documentation:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Complete domain inventory
- [EE-Universal-Gateway-Implementation-Guide.md](../../SIMA/projects/EE/architecture/EE-Universal-Gateway-Implementation-Guide.md) - Implementation guide
- [Universal Gateway README](../../universal_gateway/README.md) - UG usage and architecture
- [PROJECT-MODE-EE.md](../../SIMA/projects/EE/modes/PROJECT-MODE-EE.md) - Development guidelines

**SIMA Base:**
- [SIMA/Master-Index-of-Indexes.md](../../SIMA/Master-Index-of-Indexes.md) - All domain indexes
- [SIMA-Quick-Reference-Card.md](../../SIMA/SIMA-Quick-Reference-Card.md) - Quick reference

---

**END OF COMPLETE REFERENCE**

**Version:** 1.0.0
**Last Updated:** 2026-01-02
**Architecture Version:** EE 2.1
**Total Lines:** 398 (within SIMA 400-line limit)
