# Infrastructure Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** infrastructure
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Plugin management, infrastructure operations

---

## Overview

The Infrastructure domain provides plugin management and infrastructure operations for the EE system.

**Gateway:** InfrastructureGateway
**Interfaces:** 2 (plugins, concurrency)
**Operations:** ~5

---

## 1. Plugins Interface

**Purpose:** Plugin management
**Location:** `EE/infrastructure/plugins/`

### Operations

#### load

Load a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name
- `plugin_path` (str, optional): Plugin path (default: standard plugin dir)
- `config` (dict, optional): Plugin configuration

**Returns:** Plugin instance or True if successful

**Raises:**
- `InvalidOperationError`: Plugin not found or load failed

**Examples:**
```python
# Load plugin
plugin = execute_operation(
    domain="infrastructure",
    interface="plugins",
    operation="load",
    plugin_name="ha_integration",
    config={"host": "homeassistant.local", "token": "abc123"}
)
```

---

#### unload

Unload a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name

**Returns:** True if successful

**Examples:**
```python
execute_operation(
    domain="infrastructure",
    interface="plugins",
    operation="unload",
    plugin_name="ha_integration"
)
```

---

#### list

List all loaded plugins.

**Parameters:** None

**Returns:** List of plugin info (List[dict])

**Examples:**
```python
plugins = execute_operation(
    domain="infrastructure",
    interface="plugins",
    operation="list"
)
# Returns: [{"name": "ha_integration", "version": "1.0.0", "loaded": True}, ...]
```

---

#### register

Register a plugin.

**Parameters:**
- `plugin_name` (str, required): Plugin name
- `plugin_class` (type, required): Plugin class
- `metadata` (dict, optional): Plugin metadata

**Returns:** True if registered

**Examples:**
```python
execute_operation(
    domain="infrastructure",
    interface="plugins",
    operation="register",
    plugin_name="custom_plugin",
    plugin_class=CustomPlugin,
    metadata={"version": "1.0.0", "author": "John Doe"}
)
```

---

#### status

Get plugin status.

**Parameters:**
- `plugin_name` (str, required): Plugin name

**Returns:** Plugin status (dict with loaded, version, config, health)

**Examples:**
```python
status = execute_operation(
    domain="infrastructure",
    interface="plugins",
    operation="status",
    plugin_name="ha_integration"
)
# Returns: {"loaded": True, "version": "1.0.0", "health": "healthy"}
```

---

## 2. Concurrency Interface

**Purpose:** Concurrency operations
**Location:** `EE/infrastructure/concurrency/`

### Operations

#### spawn, join, cancel, list

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

## Cross-Domain Operations

**Infrastructure may call:**
- All domains (plugin dependencies)
- `operations.fileio` - For plugin loading
- `foundation.config` - For plugin config

---

## Pooling

**Plugin loaders:** Pool of 3-5 instances
**Concurrency managers:** Singleton pool

---

## Examples

### Plugin Lifecycle

```python
def manage_plugin(plugin_name):
    # Load plugin
    plugin = execute_operation(
        domain="infrastructure",
        interface="plugins",
        operation="load",
        plugin_name=plugin_name
    )

    # Check status
    status = execute_operation(
        domain="infrastructure",
        interface="plugins",
        operation="status",
        plugin_name=plugin_name
    )

    if status["health"] == "healthy":
        print(f"Plugin {plugin_name} is healthy")

    # List all plugins
    plugins = execute_operation(
        domain="infrastructure",
        interface="plugins",
        operation="list"
    )

    print(f"Loaded plugins: {[p['name'] for p in plugins]}")

    return plugin
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/infrastructure/infrastructure_gateway.py` - Gateway implementation
- `EE/infrastructure/plugins/` - Plugins interface
- `EE/infrastructure/concurrency/` - Concurrency interface

---

**END OF INFRASTRUCTURE DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 199
