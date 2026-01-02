# Operations Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** operations
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Caching, file I/O, pooling

---

## Overview

The Operations domain provides caching, file I/O, object pooling, circuit breakers, serialization, templates, and threading operations.

**Gateway:** OperationsGateway
**Interfaces:** 7 (cache, fileio, object_pool, circuit_breaker, serialization, template, threading_ops)
**Operations:** ~25

---

## 1. Cache Interface

**Purpose:** In-memory caching
**Location:** `EE/operations/cache/`

### Operations

#### get, set, delete, clear, exists

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

---

## 2. File I/O Interface

**Purpose:** File operations
**Location:** `EE/operations/fileio/`

### Operations

#### read, write, delete, exists, list

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

---

## 3. Object Pool Interface

**Purpose:** Object pooling for performance
**Location:** `EE/operations/object_pool/`

### Operations

#### acquire, release, size, clear

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

---

## 4. Circuit Breaker Interface

**Purpose:** Circuit breaker pattern
**Location:** `EE/operations/circuit_breaker/`

### Operations

#### check_state, record_success, record_failure

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

---

## 5. Serialization Interface

**Purpose:** Data serialization
**Location:** `EE/operations/serialization/`

### Operations

#### serialize, deserialize, to_json, from_json

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

---

## 6. Template Interface

**Purpose:** Template rendering
**Location:** `EE/operations/template/`

### Operations

#### render, compile, load_template

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

---

## 7. Threading Interface

**Purpose:** Thread management
**Location:** `EE/operations/threading_ops/`

### Operations

#### spawn, join, cancel, list_threads

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

## Cross-Domain Operations

**Operations may call:**
- `foundation.config` - For cache/config settings
- `observability.metrics` - For cache metrics

**All domains may call:**
- `operations.cache` - For caching
- `operations.fileio` - For file access
- `operations.object_pool` - For object pooling

---

## Pooling

**File handles:** Pool of 10-20 instances
**Cache connections:** Pool of 5-10 instances
**Thread pools:** Configurable pool sizes

---

## Examples

### Caching Pattern

```python
def get_user_data(user_id):
    # Try cache first
    cached = execute_operation(
        domain="operations",
        interface="cache",
        operation="get",
        key=f"user:{user_id}"
    )

    if cached is not None:
        return cached

    # Cache miss - fetch from DB
    data = fetch_from_database(user_id)

    # Store in cache
    execute_operation(
        domain="operations",
        interface="cache",
        operation="set",
        key=f"user:{user_id}",
        value=data,
        ttl=3600
    )

    return data
```

### File Operations Pattern

```python
def process_file(input_path, output_path):
    # Read input
    content = execute_operation(
        domain="operations",
        interface="fileio",
        operation="read",
        path=input_path
    )

    # Process content
    processed = content.upper()

    # Write output
    execute_operation(
        domain="operations",
        interface="fileio",
        operation="write",
        path=output_path,
        data=processed
    )
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/operations/operations_gateway.py` - Gateway implementation
- Individual interface directories

---

**END OF OPERATIONS DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 201
