# config_presets.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 150

---

## Purpose

Configuration preset management for quick switching between predefined configurations (minimal, standard, debug, performance).

---

## Presets

### Available Presets

**minimal:**
```python
{
    'description': 'Minimal resource usage',
    'config': {
        'cache.enabled': 'false',
        'metrics.enabled': 'false',
        'logging.level': 'ERROR'
    }
}
```

**standard:**
```python
{
    'description': 'Standard production configuration',
    'config': {
        'cache.enabled': 'true',
        'cache.ttl': '300',
        'metrics.enabled': 'true',
        'logging.level': 'INFO'
    }
}
```

**debug:**
```python
{
    'description': 'Debug mode with verbose logging',
    'config': {
        'cache.enabled': 'true',
        'metrics.enabled': 'true',
        'logging.level': 'DEBUG',
        'debug.enabled': 'true'
    }
}
```

**performance:**
```python
{
    'description': 'Performance optimized',
    'config': {
        'cache.enabled': 'true',
        'cache.ttl': '600',
        'metrics.enabled': 'true',
        'logging.level': 'WARNING'
    }
}
```

---

## Functions

### switch_preset()

**Purpose:** Switch to a configuration preset

**Signature:**
```python
def switch_preset(preset_name: str) -> Dict[str, Any]
```

**Parameters:**
- `preset_name: str` - Name of preset ('minimal', 'standard', 'debug', 'performance')

**Returns:**
```python
# Success:
{
    'success': True,
    'preset': str,              # Preset name
    'description': str,         # Preset description
    'applied_count': int        # Number of parameters applied
}

# Error:
{
    'success': False,
    'error': str,               # Error message
    'available': List[str]      # Available preset names
}
```

**Behavior:**
1. Get configuration manager
2. Validate preset name
3. If unknown: return error with available list
4. Get preset definition
5. Apply preset configuration parameters
6. Log preset application
7. Return success result

**Performance:** ~50μs for 10 parameters

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "switch_preset"):
    gateway.debug_log("CONFIG", "CONFIG", "Switching preset", preset=preset_name)
    # ... apply ...
    gateway.debug_log("CONFIG", "CONFIG", "Preset applied",
                    preset=preset_name, param_count=len(preset['config']))
```

**Usage:**
```python
# Switch to debug mode
result = switch_preset('debug')
if result['success']:
    print(f"Switched to {result['preset']}: {result['description']}")
    print(f"Applied {result['applied_count']} parameters")
else:
    print(f"Failed: {result['error']}")
    print(f"Available: {result['available']}")

# Switch to minimal (save resources)
result = switch_preset('minimal')

# Switch to performance
result = switch_preset('performance')

# Invalid preset
result = switch_preset('invalid')
# Returns: {'success': False, 'error': '...', 'available': [...]}
```

**When to Use:**
- Development: 'debug' preset
- Production: 'standard' preset
- Resource-constrained: 'minimal' preset
- High-traffic: 'performance' preset

**Error Scenarios:**
- Unknown preset → Error with available list
- Exception during apply → Error logged, error dict returned

---

### get_preset_list()

**Purpose:** Get list of available presets

**Signature:**
```python
def get_preset_list() -> List[Dict[str, str]]
```

**Returns:**
```python
[
    {
        'name': str,
        'description': str
    },
    ...
]
```

**Behavior:**
1. Iterate through preset definitions
2. Extract name and description
3. Return list of preset info

**Performance:** ~5μs

**Usage:**
```python
presets = get_preset_list()
for preset in presets:
    print(f"{preset['name']}: {preset['description']}")

# Output:
# minimal: Minimal resource usage
# standard: Standard production configuration
# debug: Debug mode with verbose logging
# performance: Performance optimized
```

**Display Example:**
```python
print("Available Presets:")
for preset in get_preset_list():
    print(f"  {preset['name']:12} - {preset['description']}")
```

---

### get_preset_config()

**Purpose:** Get configuration for a specific preset

**Signature:**
```python
def get_preset_config(preset_name: str) -> Dict[str, Any]
```

**Parameters:**
- `preset_name: str` - Preset name

**Returns:**
- `Dict[str, Any]` - Preset configuration (copy)
- `{}` - Empty dict if preset not found

**Behavior:**
1. Check if preset exists
2. If not: return empty dict
3. Copy preset config
4. Return copy

**Performance:** ~3μs

**Usage:**
```python
# Get debug preset config
config = get_preset_config('debug')
# Returns: {'cache.enabled': 'true', 'logging.level': 'DEBUG', ...}

# Check what a preset would apply
config = get_preset_config('performance')
for key, value in config.items():
    print(f"Would set {key} = {value}")

# Invalid preset
config = get_preset_config('invalid')
# Returns: {}
```

**Use Cases:**
- Preview preset before applying
- Merge preset with custom config
- Validate preset contents
- Documentation generation

---

## Preset Details

### minimal Preset

**Purpose:** Absolute minimum resource usage

**Use Cases:**
- Cost optimization
- Resource-constrained environments
- Emergency fallback mode
- Testing minimal viable functionality

**Configuration:**
```python
{
    'cache.enabled': 'false',      # No caching overhead
    'metrics.enabled': 'false',    # No metrics collection
    'logging.level': 'ERROR'       # Minimal logging
}
```

**Impact:**
- Memory: ~10MB (lowest)
- Performance: Reduced (no cache)
- Observability: Minimal (errors only)
- Cost: Lowest

---

### standard Preset

**Purpose:** Balanced production configuration

**Use Cases:**
- Production deployments
- Default configuration
- Most common use case
- Balanced performance/observability

**Configuration:**
```python
{
    'cache.enabled': 'true',       # Enable caching
    'cache.ttl': '300',            # 5 minute TTL
    'metrics.enabled': 'true',     # Collect metrics
    'logging.level': 'INFO'        # Standard logging
}
```

**Impact:**
- Memory: ~30MB
- Performance: Good (with cache)
- Observability: Standard
- Cost: Moderate

---

### debug Preset

**Purpose:** Development and troubleshooting

**Use Cases:**
- Development environments
- Troubleshooting issues
- Detailed analysis
- Integration testing

**Configuration:**
```python
{
    'cache.enabled': 'true',       # Cache for performance
    'metrics.enabled': 'true',     # Full metrics
    'logging.level': 'DEBUG',      # Verbose logging
    'debug.enabled': 'true'        # Debug features
}
```

**Impact:**
- Memory: ~35MB
- Performance: Good
- Observability: Maximum
- Cost: Higher (verbose logging)

---

### performance Preset

**Purpose:** Maximum performance optimization

**Use Cases:**
- High-traffic deployments
- Performance-critical paths
- Cost optimization with caching
- Reduced logging overhead

**Configuration:**
```python
{
    'cache.enabled': 'true',       # Cache enabled
    'cache.ttl': '600',            # 10 minute TTL (longer)
    'metrics.enabled': 'true',     # Metrics for monitoring
    'logging.level': 'WARNING'     # Reduced logging
}
```

**Impact:**
- Memory: ~32MB
- Performance: Maximum
- Observability: Reduced
- Cost: Optimized

---

## Preset Strategies

### Environment-Based

**Pattern:**
```python
import os

# Select preset by environment
env = os.getenv('ENVIRONMENT', 'production')

preset_map = {
    'development': 'debug',
    'staging': 'standard',
    'production': 'performance'
}

preset = preset_map.get(env, 'standard')
result = switch_preset(preset)
```

### Time-Based

**Pattern:**
```python
import datetime

# Debug during business hours, performance otherwise
hour = datetime.datetime.now().hour

if 9 <= hour <= 17:
    switch_preset('debug')
else:
    switch_preset('performance')
```

### Load-Based

**Pattern:**
```python
# Switch based on traffic
if current_requests_per_second > 100:
    switch_preset('performance')
elif current_requests_per_second < 10:
    switch_preset('minimal')
else:
    switch_preset('standard')
```

---

## Debug Integration

### Scope

**Scope Name:** CONFIG  
**Operations:** Preset switching

### Environment Variables

```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Enable debug
CONFIG_DEBUG_TIMING=true         # Enable timing
```

### Debug Output

**Switching Preset:**
```
[corr-id] [CONFIG-DEBUG] Switching preset (preset=debug)
[corr-id] [CONFIG-TIMING] switch_preset: 45.67μs
[corr-id] [CONFIG-DEBUG] Preset applied (preset=debug, param_count=4)
```

---

## Performance

### Operation Timing

| Operation | Timing | Notes |
|-----------|--------|-------|
| switch_preset | ~50μs | For 10 parameters |
| get_preset_list | ~5μs | List creation |
| get_preset_config | ~3μs | Dict copy |

### Memory Impact

| Preset | Memory | Delta from Minimal |
|--------|--------|-------------------|
| minimal | ~10MB | baseline |
| standard | ~30MB | +20MB |
| debug | ~35MB | +25MB |
| performance | ~32MB | +22MB |

---

## Extending Presets

### Adding Custom Preset

**Pattern:**
```python
# In config_presets.py
_PRESETS = {
    # ... existing presets ...
    
    'custom': {
        'description': 'Custom configuration',
        'config': {
            'cache.enabled': 'true',
            'cache.ttl': '900',
            'custom.feature': 'enabled'
        }
    }
}
```

### Dynamic Preset

**Pattern:**
```python
def create_dynamic_preset(memory_mb: int) -> Dict[str, Any]:
    """Create preset based on available memory."""
    if memory_mb < 64:
        return get_preset_config('minimal')
    elif memory_mb < 128:
        return get_preset_config('standard')
    else:
        return get_preset_config('performance')
```

---

## Dependencies

**Internal:**
- `config.config_core` - get_config_manager()

**Gateway:**
- `gateway.debug_log()` - Debug logging
- `gateway.debug_timing()` - Timing context
- `gateway.log_error()` - Error logging

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Added debug integration
- Four presets defined
- Comprehensive documentation

---

**END OF DOCUMENTATION**
