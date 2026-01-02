# Observability Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** observability
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Logging, metrics, debugging

---

## Overview

The Observability domain provides comprehensive logging, metrics collection, debugging utilities, and system diagnosis capabilities.

**Gateway:** ObservabilityGateway
**Interfaces:** 4 (logging, metrics, debug, diagnosis)
**Operations:** ~15

---

## 1. Logging Interface

**Purpose:** Structured logging
**Location:** `EE/observability/logging/`

### Operations

#### 1.1 info

Log an informational message.

**Parameters:**
- `message` (str, required): Log message
- `context` (dict, optional): Structured context data
- `component` (str, optional): Component name (default: from logger)

**Returns:** None

**Examples:**
```python
# Simple log
execute_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="User logged in",
    context={"user_id": 123, "ip": "192.168.1.1"}
)

# With component
execute_operation(
    domain="observability",
    interface="logging",
    operation="info",
    message="API request received",
    component="api.handler",
    context={"endpoint": "/users", "method": "GET"}
)
```

---

#### 1.2 warning

Log a warning message.

**Parameters:**
- `message` (str, required): Warning message
- `context` (dict, optional): Structured context
- `component` (str, optional): Component name

**Returns:** None

**Examples:**
```python
execute_operation(
    domain="observability",
    interface="logging",
    operation="warning",
    message="Cache miss rate high",
    context={"miss_rate": 0.35, "threshold": 0.3}
)
```

---

#### 1.3 error

Log an error message.

**Parameters:**
- `message` (str, required): Error message
- `exception` (Exception, optional): Exception object
- `context` (dict, optional): Structured context
- `component` (str, optional): Component name

**Returns:** None

**Examples:**
```python
try:
    risky_operation()
except Exception as e:
    execute_operation(
        domain="observability",
        interface="logging",
        operation="error",
        message="Operation failed",
        exception=e,
        context={"operation": "risky_operation"}
    )
```

---

#### 1.4 debug

Log a debug message.

**Parameters:**
- `message` (str, required): Debug message
- `context` (dict, optional): Structured context
- `component` (str, optional): Component name

**Returns:** None

**Examples:**
```python
execute_operation(
    domain="observability",
    interface="logging",
    operation="debug",
    message="Processing item",
    context={"item_id": 456, "step": 2, "total": 5}
)
```

---

#### 1.5 critical

Log a critical message.

**Parameters:**
- `message` (str, required): Critical message
- `exception` (Exception, optional): Exception object
- `context` (dict, optional): Structured context
- `component` (str, optional): Component name

**Returns:** None

**Examples:**
```python
try:
    critical_system_operation()
except Exception as e:
    execute_operation(
        domain="observability",
        interface="logging",
        operation="critical",
        message="Database connection lost",
        exception=e,
        context={"host": "db.example.com"}
    )
```

---

## 2. Metrics Interface

**Purpose:** Metrics collection and reporting
**Location:** `EE/observability/metrics/`

### Operations

#### 2.1 increment

Increment a counter metric.

**Parameters:**
- `name` (str, required): Metric name
- `value` (int, optional): Increment amount (default: 1)
- `tags` (dict, optional): Metric tags

**Returns:** None

**Examples:**
```python
# Simple counter
execute_operation(
    domain="observability",
    interface="metrics",
    operation="increment",
    name="api.requests.total"
)

# Counter with tags
execute_operation(
    domain="observability",
    interface="metrics",
    operation="increment",
    name="api.requests.total",
    value=1,
    tags={"endpoint": "/users", "method": "GET", "status": "200"}
)
```

---

#### 2.2 gauge

Set a gauge metric value.

**Parameters:**
- `name` (str, required): Metric name
- `value` (float, required): Gauge value
- `tags` (dict, optional): Metric tags

**Returns:** None

**Examples:**
```python
# Current memory usage
execute_operation(
    domain="observability",
    interface="metrics",
    operation="gauge",
    name="system.memory.used_mb",
    value=1024.5
)

# Active connections
execute_operation(
    domain="observability",
    interface="metrics",
    operation="gauge",
    name="database.connections.active",
    value=25,
    tags={"database": "primary"}
)
```

---

#### 2.3 timing

Record a timing metric.

**Parameters:**
- `name` (str, required): Metric name
- `value_ms` (float, required): Duration in milliseconds
- `tags` (dict, optional): Metric tags

**Returns:** None

**Examples:**
```python
import time

start = time.time()
result = process_request()
duration_ms = (time.time() - start) * 1000

execute_operation(
    domain="observability",
    interface="metrics",
    operation="timing",
    name="api.request.duration_ms",
    value_ms=duration_ms,
    tags={"endpoint": "/users", "method": "GET"}
)
```

---

#### 2.4 histogram

Record a histogram value.

**Parameters:**
- `name` (str, required): Metric name
- `value` (float, required): Histogram value
- `tags` (dict, optional): Metric tags

**Returns:** None

**Examples:**
```python
# Request sizes
execute_operation(
    domain="observability",
    interface="metrics",
    operation="histogram",
    name="api.request.size_bytes",
    value=2048,
    tags={"endpoint": "/upload"}
)
```

---

## 3. Debug Interface

**Purpose:** Debug utilities
**Location:** `EE/observability/debug/`

### Operations

#### 3.1 breakpoint

Set a conditional breakpoint.

**Parameters:**
- `condition` (str, required): Break condition expression
- `action` (str, optional): Action on break (log/stop/notify)

**Returns:** Breakpoint ID (str)

**Examples:**
```python
bp_id = execute_operation(
    domain="observability",
    interface="debug",
    operation="breakpoint",
    condition="user_id == 123",
    action="notify"
)
```

---

#### 3.2 inspect

Inspect variable or expression.

**Parameters:**
- `expression` (str, required): Expression to inspect
- `context` (dict, optional): Local variables context

**Returns:** Inspection result (dict with type, value, repr)

**Examples:**
```python
result = execute_operation(
    domain="observability",
    interface="debug",
    operation="inspect",
    expression="user_data",
    context={"user_data": {"name": "John", "age": 30}}
)
# Returns: {"type": "dict", "value": {...}, "repr": "{'name': 'John', 'age': 30}"}
```

---

#### 3.3 trace

Enable function tracing.

**Parameters:**
- `function_name` (str, required): Function to trace
- `enabled` (bool, optional): Enable or disable (default: True)

**Returns:** True if successful

**Examples:**
```python
# Enable tracing
execute_operation(
    domain="observability",
    interface="debug",
    operation="trace",
    function_name="process_request",
    enabled=True
)

# Disable tracing
execute_operation(
    domain="observability",
    interface="debug",
    operation="trace",
    function_name="process_request",
    enabled=False
)
```

---

## 4. Diagnosis Interface

**Purpose:** System health and diagnostics
**Location:** `EE/observability/diagnosis/`

### Operations

#### 4.1 health_check

Perform health check.

**Parameters:**
- `component` (str, optional): Specific component to check (default: all)

**Returns:** Health status (dict)

**Examples:**
```python
# Check all components
health = execute_operation(
    domain="observability",
    interface="diagnosis",
    operation="health_check"
)
# Returns: {"status": "healthy", "components": {...}}

# Check specific component
db_health = execute_operation(
    domain="observability",
    interface="diagnosis",
    operation="health_check",
    component="database"
)
# Returns: {"status": "healthy", "checks": {...}}
```

---

#### 4.2 status

Get system status.

**Parameters:**
- `verbose` (bool, optional): Detailed status (default: False)

**Returns:** System status (dict)

**Examples:**
```python
# Brief status
status = execute_operation(
    domain="observability",
    interface="diagnosis",
    operation="status"
)

# Detailed status
detailed = execute_operation(
    domain="observability",
    interface="diagnosis",
    operation="status",
    verbose=True
)
```

---

#### 4.3 diagnostics

Run comprehensive diagnostics.

**Parameters:**
- `category` (str, optional): Category to diagnose (default: all)

**Returns:** Diagnostic results (dict)

**Examples:**
```python
results = execute_operation(
    domain="observability",
    interface="diagnosis",
    operation="diagnostics",
    category="performance"
)
# Returns: {"category": "performance", "checks": [...], "summary": "..."}
```

---

## Cross-Domain Operations

**Observability may call:**
- `foundation.config` - For logger/metrics configuration
- `operations.cache` - For metrics caching

**All domains may call:**
- `observability.logging` - For logging
- `observability.metrics` - For metrics

---

## Pooling

**Loggers:** Singleton pool per name
**Metrics collectors:** Pool of 5-10 instances
**Debug utilities:** Stateless (no pooling)

---

## Structured Logging Best Practices

**DO:**
✅ Use structured context data
✅ Include relevant metadata (user_id, request_id, etc.)
✅ Use appropriate log levels
✅ Add tags to metrics for filtering

**DON'T::**
❌ Log sensitive data (passwords, tokens, PII)
❌ Use string formatting for context
❌ Log at wrong level (error for expected failures)

---

## Examples

### Complete Request Logging

```python
import time

def handle_request(request):
    request_id = generate_id()

    # Log start
    execute_operation(
        domain="observability",
        interface="logging",
        operation="info",
        message="Request started",
        context={"request_id": request_id, "path": request.path}
    )

    start = time.time()
    try:
        result = process_request(request)

        # Log success
        execute_operation(
            domain="observability",
            interface="logging",
            operation="info",
            message="Request completed",
            context={"request_id": request_id, "status": "success"}
        )

        # Record metric
        execute_operation(
            domain="observability",
            interface="metrics",
            operation="timing",
            name="api.request.duration_ms",
            value_ms=(time.time() - start) * 1000,
            tags={"endpoint": request.path, "status": "success"}
        )

        return result

    except Exception as e:
        # Log error
        execute_operation(
            domain="observability",
            interface="logging",
            operation="error",
            message="Request failed",
            exception=e,
            context={"request_id": request_id}
        )

        # Error metric
        execute_operation(
            domain="observability",
            interface="metrics",
            operation="increment",
            name="api.errors.total",
            tags={"endpoint": request.path, "error_type": type(e).__name__}
        )

        raise
```

### Metric Collection Pattern

```python
class APIMetrics:
    def __init__(self):
        self.domain = "observability"
        self.interface = "metrics"

    def track_request(self, endpoint, method, duration_ms, status_code):
        # Timing metric
        execute_operation(
            domain=self.domain,
            interface=self.interface,
            operation="timing",
            name="api.request.duration_ms",
            value_ms=duration_ms,
            tags={"endpoint": endpoint, "method": method, "status": status_code}
        )

        # Counter metric
        execute_operation(
            domain=self.domain,
            interface=self.interface,
            operation="increment",
            name="api.requests.total",
            tags={"endpoint": endpoint, "method": method, "status": status_code}
        )
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/observability/logging/` - Logging interface
- `EE/observability/metrics/` - Metrics interface
- `EE/observability/debug/` - Debug interface
- `EE/observability/diagnosis/` - Diagnosis interface

---

**END OF OBSERVABILITY DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 349 (target achieved)
