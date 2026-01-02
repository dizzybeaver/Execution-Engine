# utility_validation.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_validation.py  
**Module:** Utility validation operations

---

## Overview

Validation operations for strings, data structures, and parameters. Provides comprehensive validation with detailed error messages.

**File:** `utility/utility_validation.py`  
**Lines:** 116  
**Pattern:** Operation class with manager reference

---

## Classes

### UtilityValidationOperations

**Purpose:** Validation operations for data integrity  
**Pattern:** Operation class initialized with manager reference

**Initialization:**
```python
def __init__(self, manager):
    """Initialize with reference to SharedUtilityCore manager."""
    self._manager = manager
```

---

## Methods

### validate_string()

**Purpose:** Validate string input  
**Returns:** dict (validation result)

**Parameters:**
- `value` (str): String to validate
- `min_length` (int, default=0): Minimum length
- `max_length` (int, default=1000): Maximum length
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityValidationOperations(manager)

# Valid string
result = ops.validate_string('test', min_length=1, max_length=100)
# Result: {'valid': True}

# Too short
result = ops.validate_string('', min_length=1)
# Result: {'valid': False, 'error': 'String too short (min: 1)'}

# Too long
result = ops.validate_string('a' * 2000, max_length=1000)
# Result: {'valid': False, 'error': 'String too long (max: 1000)'}

# Not a string
result = ops.validate_string(123, min_length=1)
# Result: {'valid': False, 'error': 'Value must be a string'}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] String validation passed (length=4)
[abc123] [UTILITY-DEBUG] String validation failed: too short (length=0, min_length=1)
[abc123] [UTILITY-DEBUG] String validation failed: too long (length=2000, max_length=1000)
[abc123] [UTILITY-DEBUG] String validation failed: not a string (value_type=int)
```

---

### validate_data_structure()

**Purpose:** Validate data structure type and required fields  
**Returns:** bool (True if valid)

**Parameters:**
- `data` (Any): Data to validate
- `expected_type` (type): Expected type
- `required_fields` (list[str], optional): Required fields (for dicts)
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
ops = UtilityValidationOperations(manager)

# Valid dict with required fields
data = {'name': 'Alice', 'age': 30}
valid = ops.validate_data_structure(data, dict, required_fields=['name', 'age'])
# Result: True

# Missing field
data = {'name': 'Alice'}
valid = ops.validate_data_structure(data, dict, required_fields=['name', 'age'])
# Result: False

# Wrong type
data = "not a dict"
valid = ops.validate_data_structure(data, dict)
# Result: False

# List validation
data = [1, 2, 3]
valid = ops.validate_data_structure(data, list)
# Result: True
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Data structure validation passed (expected_type=dict)
[abc123] [UTILITY-DEBUG] Data structure validation failed: wrong type (expected_type=dict, actual_type=str)
[abc123] [UTILITY-DEBUG] Data structure validation failed: missing field (field=age)
```

---

### validate_operation_parameters()

**Purpose:** Generic parameter validation for any interface operation  
**Returns:** dict (validation result)

**Parameters:**
- `required_params` (list[str]): Required parameter names
- `optional_params` (list[str], optional): Optional parameter names
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Parameters to validate

**Usage:**
```python
ops = UtilityValidationOperations(manager)

# Valid parameters
result = ops.validate_operation_parameters(
    required_params=['name', 'age'],
    optional_params=['email', 'phone'],
    name='Alice',
    age=30,
    email='alice@example.com'
)
# Result: {'valid': True}

# Missing required parameter
result = ops.validate_operation_parameters(
    required_params=['name', 'age'],
    name='Alice'
)
# Result: {
#     'valid': False,
#     'missing_params': ['age'],
#     'error': 'Missing required parameters: age'
# }

# Unexpected parameter (warning only)
result = ops.validate_operation_parameters(
    required_params=['name'],
    optional_params=['age'],
    name='Alice',
    age=30,
    unexpected_param='value'
)
# Result: {
#     'valid': True,
#     'warning': 'Unexpected parameters: unexpected_param'
# }
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Parameter validation passed (required_count=2)
[abc123] [UTILITY-DEBUG] Parameter validation failed: missing params (missing_params=['age'])
[abc123] [UTILITY-DEBUG] Parameter validation passed with warnings (unexpected_params=['unexpected_param'])
```

---

## Usage Patterns

### Initialization
```python
from utility.utility_manager import get_utility_manager
from utility.utility_validation import UtilityValidationOperations

manager = get_utility_manager()
ops = UtilityValidationOperations(manager)
```

### String Validation
```python
# Username validation
result = ops.validate_string(username, min_length=3, max_length=20)
if result['valid']:
    # Process username
    pass
else:
    return {'error': result['error']}
```

### Data Structure Validation
```python
# API request validation
if ops.validate_data_structure(request, dict, required_fields=['action', 'data']):
    # Process request
    pass
else:
    return {'error': 'Invalid request structure'}
```

### Parameter Validation
```python
# Function parameter validation
result = ops.validate_operation_parameters(
    required_params=['user_id', 'action'],
    optional_params=['data', 'metadata'],
    correlation_id=correlation_id,
    **kwargs
)
if not result['valid']:
    return {'error': result['error']}
```

---

## Debug Integration

**Master Switch:**
- `DEBUG_MODE` - Enables all debugging

**Scope Switches:**
- `UTILITY_DEBUG_MODE` - Utility debug logging

**Correlation ID:**
- All methods accept optional `correlation_id` parameter
- Auto-generated via gateway if not provided

---

## Related Files

- **Manager:** `utility/utility_manager.py`
- **Core:** `utility/utility_core.py`
- **Interface:** `interface/interface_utility.py`
- **Advanced:** `utility/utility_validation_advanced.py`
- **Core Validators:** `utility/utility_validation_core.py`

---

**END OF DOCUMENTATION**
