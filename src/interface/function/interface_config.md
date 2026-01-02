# interface_config.py

**Version:** 2025-12-09_1  
**Module:** CONFIG  
**Layer:** Interface  
**Interface:** INT-02  
**Lines:** ~165

---

## Purpose

Config interface router with dispatch dictionary for configuration management.

---

## Main Function

### execute_config_operation()

**Signature:**
```python
def execute_config_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route config operations to implementations

**Parameters:**
- `operation` (str) - Operation name to execute
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (type varies by operation)

**Operations:**
- `initialize` - Initialize configuration system
- `get` / `get_parameter` - Get configuration parameter
- `set` / `set_parameter` - Set configuration parameter
- `get_category` - Get category configuration
- `get_state` - Get configuration state
- `reload` - Reload configuration
- `switch_preset` - Switch to configuration preset
- `load_environment` - Load from environment variables
- `load_file` - Load from file
- `validate_all` - Validate all sections
- `reset` - Reset configuration

**Raises:**
- `RuntimeError` - If Config interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### initialize

**Purpose:** Initialize configuration system

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_config_operation('initialize')
```

---

### get / get_parameter

**Purpose:** Get configuration parameter by key

**Parameters:**
- `key` (str, required) - Configuration key
- `default` (Any, optional) - Default value if key not found

**Returns:** Configuration value or default

**Validation:**
- `key` must be provided
- `key` must be string type

**Usage:**
```python
value = execute_config_operation('get', key='log_level', default='INFO')
timeout = execute_config_operation('get_parameter', key='timeout')
```

---

### set / set_parameter

**Purpose:** Set configuration parameter

**Parameters:**
- `key` (str, required) - Configuration key
- `value` (Any, required) - Value to set

**Returns:** bool (True on success)

**Validation:**
- `key` must be provided and be string
- `value` must be provided

**Usage:**
```python
execute_config_operation('set', key='log_level', value='DEBUG')
execute_config_operation('set_parameter', key='timeout', value=30)
```

---

### get_category

**Purpose:** Get all configuration parameters for a category

**Parameters:**
- `category` (str, required) - Category name

**Returns:** Dict of category configuration

**Validation:**
- `category` must be provided
- `category` must be string type

**Usage:**
```python
db_config = execute_config_operation('get_category', category='database')
# Returns: {'host': 'localhost', 'port': 5432, ...}
```

---

### get_state

**Purpose:** Get current configuration state

**Parameters:** None

**Returns:** Dict with configuration state

**Fields:**
- `initialized` - Whether config initialized
- `parameter_count` - Number of parameters
- `categories` - List of categories
- `preset` - Current preset name (if any)

**Usage:**
```python
state = execute_config_operation('get_state')
```

---

### reload

**Purpose:** Reload configuration from sources

**Parameters:**
- `validate` (bool, optional) - Validate after reload (default: True)

**Returns:** bool (True on success)

**Usage:**
```python
execute_config_operation('reload')
execute_config_operation('reload', validate=False)
```

---

### switch_preset

**Purpose:** Switch to a configuration preset

**Parameters:**
- `preset_name` (str, required) - Preset name

**Returns:** bool (True on success)

**Validation:**
- `preset_name` must be provided
- `preset_name` must be string type

**Usage:**
```python
execute_config_operation('switch_preset', preset_name='production')
execute_config_operation('switch_preset', preset_name='development')
```

**Common Presets:**
- `development` - Development settings
- `production` - Production settings
- `testing` - Testing settings

---

### load_environment

**Purpose:** Load configuration from environment variables

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_config_operation('load_environment')
```

---

### load_file

**Purpose:** Load configuration from file

**Parameters:**
- `filepath` (str, required) - Path to configuration file

**Returns:** bool (True on success)

**Validation:**
- `filepath` must be provided
- `filepath` must be string type

**Supported Formats:**
- JSON (.json)
- YAML (.yaml, .yml)
- INI (.ini)
- ENV (.env)

**Usage:**
```python
execute_config_operation('load_file', filepath='/config/app.json')
```

---

### validate_all

**Purpose:** Validate all configuration sections

**Parameters:** None

**Returns:** Dict with validation results

**Fields:**
- `valid` - Overall validation result
- `errors` - List of validation errors
- `warnings` - List of warnings

**Usage:**
```python
result = execute_config_operation('validate_all')
if not result['valid']:
    print(result['errors'])
```

---

### reset

**Purpose:** Reset configuration to initial state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_config_operation('reset')
```

---

## Validation Helpers

### _validate_key_param()

**Purpose:** Validate key parameter exists and is string

**Raises:**
- `ValueError` - If key missing
- `TypeError` - If key not string

---

### _validate_set_params()

**Purpose:** Validate set operation parameters

**Checks:**
- Key exists and is string
- Value exists

---

### _validate_category_param()

**Purpose:** Validate category parameter

**Checks:**
- Category exists and is string

---

### _validate_preset_param()

**Purpose:** Validate preset_name parameter

**Checks:**
- Preset name exists and is string

---

### _validate_filepath_param()

**Purpose:** Validate filepath parameter

**Checks:**
- Filepath exists and is string

---

## Dispatch Dictionary

**Pattern:**
```python
_OPERATION_DISPATCH = {
    'initialize': lambda **kwargs: initialize_config(),
    'get': lambda **kwargs: (
        _validate_key_param(kwargs, 'get'),
        get_parameter(kwargs['key'], kwargs.get('default'))
    )[1],
    # ... other operations
}
```

**Benefits:**
- O(1) operation lookup
- Clean separation of validation and execution
- Easy to extend with new operations

---

## Import Structure

**Imports:**
```python
from config.config_parameters import (
    initialize_config, get_parameter, set_parameter,
    get_category_config, get_state
)
from config.config_loader import (
    load_from_environment, load_from_file, reload_config
)
from config.config_presets import switch_preset
from config.config_validator import validate_all_sections
from config.config_core import get_config_manager
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Parameter Validation:** Type and presence checks  
✅ **Import Protection:** Graceful failure handling  
✅ **Operation Aliases:** get/get_parameter, set/set_parameter

---

## Related Files

- `/config/` - Config implementation
- `/gateway/wrappers/gateway_wrappers_config.py` - Gateway wrappers
- `/config/config_directory.md` - Directory structure

---

**END OF DOCUMENTATION**
