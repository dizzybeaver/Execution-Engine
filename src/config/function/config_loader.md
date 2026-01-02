# config_loader.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 130

---

## Purpose

Configuration loading from various sources (environment, file) with reload capabilities and validation integration.

---

## Functions

### load_from_environment()

**Purpose:** Load configuration from environment variables

**Signature:**
```python
def load_from_environment() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]` - Configuration dictionary loaded from environment

**Behavior:**
1. Initialize empty config dict
2. Define environment variable prefixes to scan
3. Iterate through all environment variables
4. Filter by known prefixes
5. Add matching variables to config
6. Log key count
7. Return config dict

**Prefixes Scanned:**
- `LEE_` - LEE-specific config
- `HA_` - Home Assistant config
- `LAMBDA_` - Lambda config
- `AWS_` - AWS config
- `CONFIG_` - General config

**Performance:** ~100μs for 50 environment variables

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "load_environment"):
    gateway.debug_log("CONFIG", "CONFIG", "Environment loaded",
                    key_count=len(config))
```

**Usage:**
```python
config = load_from_environment()
# Returns: {'LEE_VERSION': '1.0', 'HA_URL': 'http://...', ...}

# Check what was loaded
print(f"Loaded {len(config)} parameters")
for key, value in config.items():
    print(f"{key} = {value}")
```

**Example Environment:**
```bash
LEE_VERSION=1.0.0
HA_URL=http://homeassistant.local:8123
LAMBDA_TIMEOUT=30
AWS_REGION=us-east-1
CONFIG_DEBUG=true
OTHER_VAR=ignored    # Not matched by any prefix
```

**Result:**
```python
{
    'LEE_VERSION': '1.0.0',
    'HA_URL': 'http://homeassistant.local:8123',
    'LAMBDA_TIMEOUT': '30',
    'AWS_REGION': 'us-east-1',
    'CONFIG_DEBUG': 'true'
    # 'OTHER_VAR' not included
}
```

**Error Handling:**
- Catches all exceptions
- Logs via gateway.log_error()
- Returns empty dict on error

---

### load_from_file()

**Purpose:** Load configuration from file (JSON or key=value format)

**Signature:**
```python
def load_from_file(filepath: str) -> Dict[str, Any]
```

**Parameters:**
- `filepath: str` - Path to configuration file

**Returns:**
- `Dict[str, Any]` - Configuration dictionary from file

**Supported Formats:**

**JSON (.json):**
```json
{
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "cache": {
        "enabled": true
    }
}
```

**Key=Value (.conf, .ini, .txt):**
```
database.host=localhost
database.port=5432
cache.enabled=true
# Comments are ignored
```

**Behavior:**
```python
# 1. Check file extension
if filepath.endswith('.json'):
    # Parse as JSON
    with open(filepath) as f:
        config = json.load(f)
else:
    # Parse as key=value
    config = {}
    for line in file:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
```

**Performance:** ~500μs for 100-line file

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "load_file"):
    gateway.debug_log("CONFIG", "CONFIG", "Loading file", filepath=filepath)
    # ... load ...
    gateway.debug_log("CONFIG", "CONFIG", "File loaded",
                    filepath=filepath, key_count=len(config))
```

**Usage:**
```python
# Load JSON config
config = load_from_file('/etc/lee/config.json')

# Load key=value config
config = load_from_file('/etc/lee/config.conf')

# Check result
if config:
    print(f"Loaded {len(config)} parameters from {filepath}")
else:
    print(f"Failed to load {filepath}")
```

**Error Scenarios:**
- File not found → Error logged, empty dict returned
- Invalid JSON → Error logged, empty dict returned
- Permission denied → Error logged, empty dict returned
- Invalid format → Error logged, empty dict returned

---

### reload_config()

**Purpose:** Reload configuration from environment with validation

**Signature:**
```python
def reload_config(validate: bool = True) -> Dict[str, Any]
```

**Parameters:**
- `validate: bool` - Whether to validate after reload (default: True)

**Returns:**
```python
# Success:
{
    'success': True,
    'parameter_count': int
}

# Validation failure:
{
    'success': False,
    'error': 'Validation failed',
    'validation': {...}
}

# Error:
{
    'success': False,
    'error': str
}
```

**Behavior:**
1. Get configuration manager
2. Clear existing config
3. Load from environment
4. Update config storage
5. If validate requested:
   - Call validate_all_sections()
   - Check validation result
   - Return error if invalid
6. Return success with count

**Performance:** ~500μs (includes validation)

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "reload"):
    gateway.debug_log("CONFIG", "CONFIG", "Reloading config", validate=validate)
```

**Usage:**
```python
# Reload with validation
result = reload_config(validate=True)
if result['success']:
    print(f"Reloaded {result['parameter_count']} parameters")
else:
    print(f"Reload failed: {result['error']}")

# Reload without validation (faster)
result = reload_config(validate=False)

# Check validation details
if not result['success'] and 'validation' in result:
    for section, details in result['validation']['sections'].items():
        if not details['valid']:
            print(f"Section {section} invalid:")
            for error in details['errors']:
                print(f"  {error['key']}: {error['error']}")
```

**When to Use:**
- Configuration changed in environment
- After SSM parameter updates
- Periodic refresh in long-running processes
- After configuration file updates

**Error Handling:**
- Environment load fails → Error logged, error dict returned
- Validation fails → Validation result returned
- Exception during reload → Error logged, error dict returned

---

### merge_configs()

**Purpose:** Merge two configuration dictionaries

**Signature:**
```python
def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `base: Dict[str, Any]` - Base configuration
- `override: Dict[str, Any]` - Override configuration

**Returns:**
- `Dict[str, Any]` - Merged configuration

**Behavior:**
1. Copy base configuration
2. Update with override values
3. Return merged dict

**Merge Strategy:**
- Override values replace base values
- New keys from override are added
- Base keys not in override are preserved

**Performance:** ~10μs for 100 keys

**Usage:**
```python
# Base config
base = {
    'database.host': 'localhost',
    'database.port': 5432,
    'cache.ttl': 300
}

# Override config
override = {
    'database.host': 'prod-db',  # Override
    'cache.enabled': True        # New key
}

# Merge
merged = merge_configs(base, override)
# Result:
{
    'database.host': 'prod-db',    # Overridden
    'database.port': 5432,         # Preserved
    'cache.ttl': 300,              # Preserved
    'cache.enabled': True          # Added
}
```

**Use Cases:**
- Combining environment and file configs
- Applying user overrides
- Preset configuration with customization
- Multi-stage configuration loading

**Example Multi-Stage:**
```python
# 1. Load defaults
defaults = {'timeout': 30, 'retries': 3}

# 2. Load environment
env = load_from_environment()

# 3. Load file
file_config = load_from_file('config.json')

# 4. Merge in priority order
config = merge_configs(defaults, env)
config = merge_configs(config, file_config)
# File overrides env, env overrides defaults
```

---

## Loading Strategies

### Priority Layering

**Recommended approach:**
```python
# 1. Start with hardcoded defaults
config = DEFAULT_CONFIG.copy()

# 2. Merge environment variables
env_config = load_from_environment()
config = merge_configs(config, env_config)

# 3. Merge file config (highest priority)
if os.path.exists(CONFIG_FILE):
    file_config = load_from_file(CONFIG_FILE)
    config = merge_configs(config, file_config)

# Result: file > env > defaults
```

### Hot Reload Pattern

**For long-running processes:**
```python
def reload_if_changed():
    """Reload config if file changed."""
    current_mtime = os.path.getmtime(CONFIG_FILE)
    if current_mtime > last_reload_time:
        result = reload_config(validate=True)
        if result['success']:
            last_reload_time = current_mtime
            return True
    return False

# In main loop
if reload_if_changed():
    print("Configuration reloaded")
```

---

## Debug Integration

### Scope

**Scope Name:** CONFIG  
**Operations:** All loader operations

### Environment Variables

```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Enable debug
CONFIG_DEBUG_TIMING=true         # Enable timing
```

### Debug Output

**Loading Environment:**
```
[corr-id] [CONFIG-TIMING] load_environment: 87.23μs
[corr-id] [CONFIG-DEBUG] Environment loaded (key_count=23)
```

**Loading File:**
```
[corr-id] [CONFIG-DEBUG] Loading file (filepath=/etc/config.json)
[corr-id] [CONFIG-TIMING] load_file: 412.56μs
[corr-id] [CONFIG-DEBUG] File loaded (filepath=/etc/config.json, key_count=45)
```

**Reloading:**
```
[corr-id] [CONFIG-DEBUG] Reloading config (validate=True)
[corr-id] [CONFIG-TIMING] reload: 523.18μs
```

---

## Performance

### Operation Timing

| Operation | Small | Medium | Large |
|-----------|-------|--------|-------|
| load_from_environment | 50μs | 100μs | 200μs |
| load_from_file (JSON) | 200μs | 500μs | 2ms |
| load_from_file (K=V) | 100μs | 300μs | 1ms |
| reload_config | 500μs | 1ms | 2ms |
| merge_configs | 5μs | 10μs | 50μs |

**Size Definitions:**
- Small: <20 parameters
- Medium: 20-100 parameters
- Large: 100+ parameters

---

## Dependencies

**Internal:**
- `config.config_core` - get_config_manager()
- `config.config_validator` - validate_all_sections()

**Standard Library:**
- `os` - Environment variables
- `json` - JSON parsing

**Gateway:**
- `gateway.debug_log()` - Debug logging
- `gateway.debug_timing()` - Timing context
- `gateway.log_error()` - Error logging

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Added debug integration
- Improved error handling
- Simplified function signatures
- Added comprehensive documentation

---

**END OF DOCUMENTATION**
