# Foundation Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** foundation
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Configuration, dependency injection, utilities

---

## Overview

The Foundation domain provides core infrastructure services including configuration management, dependency injection, system initialization, singleton management, and utility functions.

**Gateway:** FoundationGateway
**Interfaces:** 5 (config, di, initialization, singleton, utility)
**Operations:** ~20

---

## 1. Config Interface

**Purpose:** Configuration management
**Location:** `EE/foundation/config/`

### Operations

#### 1.1 get

Retrieve a configuration value.

**Parameters:**
- `key` (str, required): Configuration key (e.g., "database.host")
- `default` (Any, optional): Default value if key not found
- `reload` (bool, optional): Force config reload before reading (default: False)

**Returns:** Configuration value (type depends on config)

**Raises:**
- `InvalidOperationError`: Key not found and no default provided

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

# Force reload
config = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host",
    reload=True
)
```

---

#### 1.2 set

Set a configuration value.

**Parameters:**
- `key` (str, required): Configuration key
- `value` (Any, required): Value to set
- `persist` (bool, optional): Persist to disk (default: False)

**Returns:** True if successful

**Raises:**
- `InvalidOperationError`: Invalid key or value

**Examples:**
```python
# Set in-memory
execute_operation(
    domain="foundation",
    interface="config",
    operation="set",
    key="debug.enabled",
    value=True
)

# Persist to disk
execute_operation(
    domain="foundation",
    interface="config",
    operation="set",
    key="api.key",
    value="abc123",
    persist=True
)
```

---

#### 1.3 list

List configuration keys.

**Parameters:**
- `prefix` (str, optional): Filter keys by prefix (default: "")
- `recursive` (bool, optional): Include nested keys (default: True)

**Returns:** List of configuration keys (List[str])

**Examples:**
```python
# List all keys
all_keys = execute_operation(
    domain="foundation",
    interface="config",
    operation="list"
)

# List database keys
db_keys = execute_operation(
    domain="foundation",
    interface="config",
    operation="list",
    prefix="database"
)

# List top-level keys only
top_level = execute_operation(
    domain="foundation",
    interface="config",
    operation="list",
    recursive=False
)
```

---

#### 1.4 delete

Delete a configuration value.

**Parameters:**
- `key` (str, required): Configuration key
- `persist` (bool, optional): Persist deletion to disk (default: False)

**Returns:** True if deleted, False if not found

**Examples:**
```python
deleted = execute_operation(
    domain="foundation",
    interface="config",
    operation="delete",
    key="temp.cache"
)
```

---

#### 1.5 reload

Reload configuration from source.

**Parameters:** None

**Returns:** True if successful

**Examples:**
```python
execute_operation(
    domain="foundation",
    interface="config",
    operation="reload"
)
```

---

## 2. DI (Dependency Injection) Interface

**Purpose:** Dependency injection container
**Location:** `EE/foundation/di/`

### Operations

#### 2.1 inject

Register a dependency.

**Parameters:**
- `name` (str, required): Dependency name
- `factory` (Callable, required): Factory function or class
- `singleton` (bool, optional): Use singleton pattern (default: True)
- `lazy` (bool, optional): Lazy initialization (default: True)

**Returns:** True if registered

**Examples:**
```python
# Register singleton
execute_operation(
    domain="foundation",
    interface="di",
    operation="inject",
    name="database.connection",
    factory=lambda: DatabaseConnection(),
    singleton=True
)

# Register transient (new instance each time)
execute_operation(
    domain="foundation",
    interface="di",
    operation="inject",
    name="request.validator",
    factory=RequestValidator,
    singleton=False
)
```

---

#### 2.2 resolve

Resolve a dependency.

**Parameters:**
- `name` (str, required): Dependency name

**Returns:** Resolved dependency instance

**Raises:**
- `InvalidOperationError`: Dependency not found

**Examples:**
```python
# Resolve dependency
db = execute_operation(
    domain="foundation",
    interface="di",
    operation="resolve",
    name="database.connection"
)

# Use the dependency
db.query("SELECT * FROM users")
```

---

#### 2.3 singleton

Get or create singleton instance.

**Parameters:**
- `name` (str, required): Singleton name
- `factory` (Callable, optional): Factory if not exists

**Returns:** Singleton instance

**Examples:**
```python
# Get existing
cache = execute_operation(
    domain="foundation",
    interface="di",
    operation="singleton",
    name="app.cache"
)

# Create if not exists
logger = execute_operation(
    domain="foundation",
    interface="di",
    operation="singleton",
    name="app.logger",
    factory=lambda: logging.getLogger("app")
)
```

---

## 3. Initialization Interface

**Purpose:** System initialization and lifecycle
**Location:** `EE/foundation/initialization/`

### Operations

#### 3.1 init

Initialize the system.

**Parameters:**
- `config_path` (str, optional): Path to config file
- `config_overrides` (dict, optional): Config override values

**Returns:** True if successful

**Examples:**
```python
execute_operation(
    domain="foundation",
    interface="initialization",
    operation="init",
    config_path="/etc/ee/config.yaml",
    config_overrides={"debug": True}
)
```

---

#### 3.2 bootstrap

Bootstrap all domains.

**Parameters:**
- `domains` (List[str], optional): Domains to bootstrap (default: all)

**Returns:** True if successful

**Examples:**
```python
# Bootstrap all
execute_operation(
    domain="foundation",
    interface="initialization",
    operation="bootstrap"
)

# Bootstrap specific domains
execute_operation(
    domain="foundation",
    interface="initialization",
    operation="bootstrap",
    domains=["networking", "security"]
)
```

---

#### 3.3 shutdown

Shutdown the system gracefully.

**Parameters:**
- `force` (bool, optional): Force shutdown (default: False)

**Returns:** True if successful

**Examples:**
```python
# Graceful shutdown
execute_operation(
    domain="foundation",
    interface="initialization",
    operation="shutdown"
)

# Force shutdown
execute_operation(
    domain="foundation",
    interface="initialization",
    operation="shutdown",
    force=True
)
```

---

## 4. Singleton Interface

**Purpose:** Singleton management
**Location:** `EE/foundation/singleton/`

### Operations

#### 4.1 get

Get singleton instance.

**Parameters:**
- `name` (str, required): Singleton name

**Returns:** Singleton instance or None

**Examples:**
```python
cache = execute_operation(
    domain="foundation",
    interface="singleton",
    operation="get",
    name="app.cache"
)
```

---

#### 4.2 reset

Reset singleton instance.

**Parameters:**
- `name` (str, required): Singleton name

**Returns:** True if reset

**Examples:**
```python
execute_operation(
    domain="foundation",
    interface="singleton",
    operation="reset",
    name="app.cache"
)
```

---

#### 4.3 exists

Check if singleton exists.

**Parameters:**
- `name` (str, required): Singleton name

**Returns:** Boolean

**Examples:**
```python
has_cache = execute_operation(
    domain="foundation",
    interface="singleton",
    operation="exists",
    name="app.cache"
)
```

---

## 5. Utility Interface

**Purpose:** Common utility functions
**Location:** `EE/foundation/utility/`

### Operations

#### 5.1 parse

Parse string data.

**Parameters:**
- `data` (str, required): Data to parse
- `format` (str, required): Format type (json, yaml, xml, csv)

**Returns:** Parsed data (dict/list)

**Examples:**
```python
# Parse JSON
data = execute_operation(
    domain="foundation",
    interface="utility",
    operation="parse",
    data='{"key": "value"}',
    format="json"
)

# Parse YAML
config = execute_operation(
    domain="foundation",
    interface="utility",
    operation="parse",
    data="key: value\n",
    format="yaml"
)
```

---

#### 5.2 validate

Validate data against schema.

**Parameters:**
- `data` (Any, required): Data to validate
- `schema` (dict, required): Validation schema
- `strict` (bool, optional): Strict validation (default: False)

**Returns:** True if valid

**Raises:**
- `InvalidOperationError`: Validation failed

**Examples:**
```python
is_valid = execute_operation(
    domain="foundation",
    interface="utility",
    operation="validate",
    data={"name": "John", "age": 30},
    schema={
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        }
    }
)
```

---

#### 5.3 sanitize

Sanitize input data.

**Parameters:**
- `data` (str, required): Data to sanitize
- `mode` (str, required): Sanitization mode (html, sql, filename, path)

**Returns:** Sanitized string

**Examples:**
```python
# Sanitize HTML
clean = execute_operation(
    domain="foundation",
    interface="utility",
    operation="sanitize",
    data="<script>alert('xss')</script>",
    mode="html"
)

# Sanitize filename
safe_name = execute_operation(
    domain="foundation",
    interface="utility",
    operation="sanitize",
    data="../../../etc/passwd",
    mode="filename"
)
```

---

## Cross-Domain Operations

**Foundation may call:**
- `security.encryption` - For encrypted config values
- `observability.logging` - For initialization logging

**All domains may call:**
- `foundation.config` - For domain configuration
- `foundation.di` - For dependency injection

---

## Pooling

**Config readers:** Pool of 5-10 instances
**DI containers:** Singleton pool
**Utilities:** Stateless (no pooling needed)

---

## See Also

**Architecture:**
- [ARCH-EE-02](../../SIMA/projects/EE/architecture/ARCH-EE-02-foundation-domain-architecture.md) - Foundation domain architecture
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/foundation/foundation_gateway.py` - Gateway implementation
- `EE/foundation/config/` - Config interface
- `EE/foundation/di/` - DI interface

---

**END OF FOUNDATION DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 350 (target achieved)
