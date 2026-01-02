# config_validator.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 140

---

## Purpose

Configuration validation logic for ensuring parameter integrity and configuration correctness.

---

## Classes

### ConfigurationValidator

**Purpose:** Configuration validation with debug integration

**Usage:**
```python
from config.config_validator import ConfigurationValidator

validator = ConfigurationValidator()
result = validator.validate_parameter('key', 'value')
```

---

## Methods

### validate_parameter()

**Purpose:** Validate a single parameter

**Signature:**
```python
def validate_parameter(self, key: str, value: Any) -> Dict[str, Any]
```

**Parameters:**
- `key: str` - Parameter key
- `value: Any` - Parameter value

**Returns:**
```python
# Valid:
{
    'valid': True
}

# Invalid:
{
    'valid': False,
    'error': str  # Error description
}
```

**Validation Rules:**
1. Key must be non-empty string
2. Value cannot be None

**Behavior:**
1. Log validation attempt (if debug enabled)
2. Check key is string
3. Check key is non-empty
4. Check value is not None
5. Return validation result

**Performance:** ~5μs per parameter

**Debug Integration:**
```python
gateway.debug_log("CONFIG", "CONFIG", "Validating parameter", key=key)
```

**Usage:**
```python
validator = ConfigurationValidator()

# Valid parameter
result = validator.validate_parameter('cache.ttl', 300)
# Returns: {'valid': True}

# Invalid key (empty)
result = validator.validate_parameter('', 'value')
# Returns: {'valid': False, 'error': 'Key must be non-empty string'}

# Invalid key (not string)
result = validator.validate_parameter(123, 'value')
# Returns: {'valid': False, 'error': 'Key must be non-empty string'}

# Invalid value (None)
result = validator.validate_parameter('key', None)
# Returns: {'valid': False, 'error': 'Value cannot be None'}
```

**Error Messages:**
- `'Key must be non-empty string'` - Key is not string or is empty
- `'Value cannot be None'` - Value is None

---

### validate_section()

**Purpose:** Validate a configuration section

**Signature:**
```python
def validate_section(self, section: str, config: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `section: str` - Section name (e.g., 'cache', 'logging')
- `config: Dict[str, Any]` - Section configuration

**Returns:**
```python
{
    'valid': bool,                    # Overall section validity
    'section': str,                   # Section name
    'errors': List[Dict[str, str]]    # List of errors (if any)
}

# Each error:
{
    'key': str,      # Parameter key with error
    'error': str     # Error description
}
```

**Behavior:**
1. Log validation attempt
2. Initialize errors list
3. For each parameter in section:
   - Validate parameter
   - If invalid: add to errors list
4. Determine overall validity (no errors = valid)
5. Return result

**Performance:** ~20μs for 10 parameters

**Debug Integration:**
```python
gateway.debug_log("CONFIG", "CONFIG", "Validating section", section=section)
```

**Usage:**
```python
validator = ConfigurationValidator()

# Valid section
section_config = {
    'cache.enabled': 'true',
    'cache.ttl': '300'
}
result = validator.validate_section('cache', section_config)
# Returns: {'valid': True, 'section': 'cache', 'errors': []}

# Invalid section
section_config = {
    'cache.enabled': 'true',
    'cache.invalid': None,  # Invalid value
    '': 'value'             # Invalid key
}
result = validator.validate_section('cache', section_config)
# Returns:
{
    'valid': False,
    'section': 'cache',
    'errors': [
        {'key': 'cache.invalid', 'error': 'Value cannot be None'},
        {'key': '', 'error': 'Key must be non-empty string'}
    ]
}
```

---

### validate_all_sections()

**Purpose:** Validate all configuration sections

**Signature:**
```python
def validate_all_sections(self, config: Dict[str, Any] = None) -> Dict[str, Any]
```

**Parameters:**
- `config: Dict[str, Any]` - Configuration to validate (optional)
  - If None: validates current config from manager

**Returns:**
```python
{
    'valid': bool,                     # Overall validity
    'sections': Dict[str, Dict]        # Per-section results
}

# Each section result:
{
    'valid': bool,
    'section': str,
    'errors': List[Dict[str, str]]
}

# On error:
{
    'valid': False,
    'error': str
}
```

**Behavior:**
1. If no config provided: get from manager
2. Group parameters by section
   - Extract section from key (before '.')
   - 'root' for keys without '.'
3. Validate each section
4. Collect results
5. Determine overall validity (all sections valid)
6. Return results

**Performance:** ~50μs for 50 parameters in 5 sections

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "validate_all"):
    # ... validation ...
    gateway.debug_log("CONFIG", "CONFIG", "Validation complete",
                    valid=all_valid, section_count=len(sections))
```

**Usage:**
```python
validator = ConfigurationValidator()

# Validate current config
result = validator.validate_all_sections()

# Validate specific config
custom_config = {
    'cache.enabled': 'true',
    'cache.ttl': '300',
    'logging.level': 'INFO',
    'invalid.key': None  # Invalid
}
result = validator.validate_all_sections(custom_config)

# Check result
if result['valid']:
    print("Configuration valid")
else:
    print("Configuration invalid:")
    for section, details in result['sections'].items():
        if not details['valid']:
            print(f"  Section {section}:")
            for error in details['errors']:
                print(f"    {error['key']}: {error['error']}")
```

**Section Grouping:**
```python
# Input config:
{
    'cache.enabled': 'true',
    'cache.ttl': '300',
    'logging.level': 'INFO',
    'standalone': 'value'
}

# Grouped into sections:
{
    'cache': {
        'cache.enabled': 'true',
        'cache.ttl': '300'
    },
    'logging': {
        'logging.level': 'INFO'
    },
    'root': {
        'standalone': 'value'
    }
}
```

**Error Handling:**
- Exception during validation → Error logged, error dict returned

---

## Functions

### validate_all_sections()

**Purpose:** Convenience function for validation

**Signature:**
```python
def validate_all_sections() -> Dict[str, Any]
```

**Returns:**
- Same as ConfigurationValidator.validate_all_sections()

**Behavior:**
1. Create ConfigurationValidator instance
2. Call validate_all_sections() method
3. Return result

**Performance:** ~50μs for 50 parameters

**Usage:**
```python
from config.config_validator import validate_all_sections

# Validate current config
result = validate_all_sections()

if result['valid']:
    print("All valid")
else:
    print("Validation failed")
```

**Why Convenience Function:**
- Simpler API for common case
- No need to instantiate validator
- Matches module-level function pattern

---

## Validation Rules

### Current Rules

**Key Validation:**
- Must be string type
- Must be non-empty
- No whitespace restrictions (allows spaces)
- No format restrictions

**Value Validation:**
- Cannot be None
- Any other type allowed
- No type-specific validation

**Section Validation:**
- Per-parameter validation
- No section-level rules
- No cross-parameter validation

---

### Future Enhancements

**Type Validation:**
```python
VALIDATION_RULES = {
    'cache.ttl': {'type': int, 'min': 0, 'max': 3600},
    'logging.level': {'type': str, 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR']},
    'cache.enabled': {'type': bool}
}
```

**Format Validation:**
```python
def validate_parameter(self, key: str, value: Any):
    rules = VALIDATION_RULES.get(key)
    if rules:
        if 'type' in rules and not isinstance(value, rules['type']):
            return {'valid': False, 'error': f'Must be {rules["type"].__name__}'}
        if 'choices' in rules and value not in rules['choices']:
            return {'valid': False, 'error': f'Must be one of {rules["choices"]}'}
    return {'valid': True}
```

**Cross-Parameter Validation:**
```python
def validate_section(self, section: str, config: Dict[str, Any]):
    # Existing validation...
    
    # Cross-parameter rules
    if section == 'cache':
        if config.get('cache.enabled') == 'true':
            if 'cache.ttl' not in config:
                errors.append({
                    'key': 'cache.ttl',
                    'error': 'Required when cache.enabled=true'
                })
```

---

## Debug Integration

### Scope

**Scope Name:** CONFIG  
**Operations:** All validation operations

### Environment Variables

```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Enable debug
CONFIG_DEBUG_TIMING=true         # Enable timing
```

### Debug Output

**Validating Parameter:**
```
[corr-id] [CONFIG-DEBUG] Validating parameter (key=cache.ttl)
```

**Validating Section:**
```
[corr-id] [CONFIG-DEBUG] Validating section (section=cache)
```

**Validating All:**
```
[corr-id] [CONFIG-TIMING] validate_all: 45.32μs
[corr-id] [CONFIG-DEBUG] Validation complete (valid=True, section_count=5)
```

---

## Performance

### Operation Timing

| Operation | Small | Medium | Large |
|-----------|-------|--------|-------|
| validate_parameter | ~5μs | N/A | N/A |
| validate_section | ~20μs | ~50μs | ~100μs |
| validate_all_sections | ~50μs | ~150μs | ~500μs |

**Size Definitions:**
- Small: <10 parameters
- Medium: 10-50 parameters
- Large: 50+ parameters

### Optimization Tips

1. **Validate once, cache result:**
```python
# Validate after load
result = validate_all_sections()
if result['valid']:
    cache_validation_result(result)
```

2. **Skip validation in production:**
```python
if not is_production():
    validate_all_sections()
```

3. **Validate on change only:**
```python
def set_parameter(key, value):
    # Validate new parameter
    result = validator.validate_parameter(key, value)
    if not result['valid']:
        raise ValueError(result['error'])
    # Set if valid
    config[key] = value
```

---

## Error Reporting

### Validation Report

**Pattern:**
```python
def print_validation_report(result: Dict[str, Any]) -> None:
    """Print human-readable validation report."""
    if result['valid']:
        print("✓ Configuration valid")
        return
    
    print("✗ Configuration invalid:")
    for section, details in result['sections'].items():
        if not details['valid']:
            print(f"\n  Section: {section}")
            for error in details['errors']:
                print(f"    ✗ {error['key']}: {error['error']}")
```

**Example Output:**
```
✗ Configuration invalid:

  Section: cache
    ✗ cache.ttl: Value cannot be None
    ✗ cache.invalid: Key must be non-empty string

  Section: logging
    ✗ logging.level: Value cannot be None
```

---

## Integration Points

### With reload_config()

**Pattern:**
```python
def reload_config(validate: bool = True):
    # ... reload ...
    
    if validate:
        validation = validate_all_sections()
        if not validation['valid']:
            return {
                'success': False,
                'error': 'Validation failed',
                'validation': validation
            }
    
    return {'success': True}
```

### With set_parameter()

**Pattern:**
```python
def set_parameter(key: str, value: Any):
    validator = ConfigurationValidator()
    result = validator.validate_parameter(key, value)
    
    if not result['valid']:
        raise ValueError(f"Invalid parameter: {result['error']}")
    
    config[key] = value
```

---

## Dependencies

**Gateway:**
- `gateway.debug_log()` - Debug logging
- `gateway.debug_timing()` - Timing context
- `gateway.log_error()` - Error logging

**Internal:**
- `config.config_core` - get_config_manager()

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Added debug integration
- Simplified validation rules
- Added comprehensive documentation

---

**END OF DOCUMENTATION**
