# create_validator()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_validation  
**Type:** Factory Function

---

## Purpose

Create a ResponseValidator instance for validating HTTP responses. Provides chainable validation rules.

---

## Signature

```python
def create_validator() -> ResponseValidator:
```

---

## Parameters

**None**

---

## Returns

**Type:** `ResponseValidator`

**Instance with methods:**
- `add_status_code_rule(allowed_codes)` - Validate status codes
- `add_field_rule(field, validator)` - Validate specific field
- `add_custom_rule(validator)` - Add custom validation
- `validate(response)` - Execute all rules

---

## Usage

### Status Code Validation

```python
from http_client import create_validator

validator = create_validator()
validator.add_status_code_rule([200, 201, 204])

response = {'success': True, 'status_code': 200, 'data': {...}}
is_valid = validator.validate(response)  # True

response = {'success': True, 'status_code': 404, 'data': {...}}
is_valid = validator.validate(response)  # False
```

### Field Validation

```python
validator = create_validator()
validator.add_field_rule('user_id', lambda x: x is not None and x > 0)

response = {
    'success': True,
    'data': {'user_id': 123, 'name': 'John'}
}
is_valid = validator.validate(response)  # True

response = {
    'success': True,
    'data': {'user_id': None, 'name': 'John'}
}
is_valid = validator.validate(response)  # False
```

### Custom Validation

```python
validator = create_validator()

def check_required_fields(response):
    data = response.get('data', {})
    required = ['id', 'name', 'email']
    return all(field in data for field in required)

validator.add_custom_rule(check_required_fields)

response = {
    'success': True,
    'data': {'id': 1, 'name': 'John', 'email': 'john@example.com'}
}
is_valid = validator.validate(response)  # True
```

---

## ResponseValidator Methods

### add_status_code_rule(allowed_codes)

**Purpose:** Validate HTTP status code

**Parameters:**
- `allowed_codes` (`List[int]`) - List of acceptable status codes

**Returns:** `self` (for chaining)

**Example:**
```python
validator.add_status_code_rule([200, 201, 202])
```

### add_field_rule(field, validator)

**Purpose:** Validate specific response data field

**Parameters:**
- `field` (`str`) - Field name in response['data']
- `validator` (`Callable`) - Function(value) -> bool

**Returns:** `self` (for chaining)

**Example:**
```python
validator.add_field_rule('age', lambda x: x >= 0 and x <= 150)
validator.add_field_rule('email', lambda x: '@' in str(x))
```

### add_custom_rule(validator)

**Purpose:** Add custom validation function

**Parameters:**
- `validator` (`Callable`) - Function(response) -> bool

**Returns:** `self` (for chaining)

**Example:**
```python
def custom_check(response):
    return response.get('success') and len(response.get('data', {})) > 0

validator.add_custom_rule(custom_check)
```

### validate(response)

**Purpose:** Execute all validation rules

**Parameters:**
- `response` (`Dict[str, Any]`) - Response to validate

**Returns:** `bool` - True if all rules pass, False otherwise

**Behavior:** Short-circuits on first failure (uses `all()`)

---

## Chaining Rules

```python
validator = (create_validator()
    .add_status_code_rule([200, 201])
    .add_field_rule('id', lambda x: x > 0)
    .add_field_rule('name', lambda x: len(x) > 0)
    .add_custom_rule(lambda r: 'data' in r))

is_valid = validator.validate(response)
```

---

## Complete Example

```python
from http_client import create_validator
import gateway

# Create validator for user API
validator = (create_validator()
    .add_status_code_rule([200])
    .add_field_rule('user_id', lambda x: isinstance(x, int) and x > 0)
    .add_field_rule('email', lambda x: '@' in str(x) and '.' in str(x))
    .add_field_rule('age', lambda x: 0 <= x <= 150)
    .add_custom_rule(lambda r: r.get('success')))

# Make request
response = gateway.http_get('https://api.example.com/users/123')

# Validate response
if validator.validate(response):
    print("Response valid!")
    user_data = response['data']
else:
    print("Response validation failed!")
```

---

## Validation Patterns

### API Contract Validation
```python
def create_api_validator():
    return (create_validator()
        .add_status_code_rule([200, 201, 204])
        .add_custom_rule(lambda r: r.get('success'))
        .add_custom_rule(lambda r: 'data' in r))
```

### Required Fields Validation
```python
def create_fields_validator(required_fields):
    validator = create_validator()
    for field in required_fields:
        validator.add_field_rule(field, lambda x: x is not None)
    return validator
```

### Type Validation
```python
validator = (create_validator()
    .add_field_rule('id', lambda x: isinstance(x, int))
    .add_field_rule('name', lambda x: isinstance(x, str))
    .add_field_rule('active', lambda x: isinstance(x, bool)))
```

---

## Integration with Response Processing

```python
from http_client import create_validator, validate_http_response

# Create validator
validator = create_validator().add_status_code_rule([200])

# Make request
response = gateway.http_get(url)

# Method 1: Direct validation
if validator.validate(response):
    process_data(response['data'])

# Method 2: Via helper function
validated = validate_http_response(response, required_fields=['id', 'name'])
if validated.get('success'):
    process_data(validated['data'])
```

---

## Error Handling

```python
validator = create_validator()
validator.add_status_code_rule([200, 201])
validator.add_field_rule('data', lambda x: x is not None)

response = gateway.http_get(url)

if not validator.validate(response):
    # Validation failed
    status = response.get('status_code', 'unknown')
    data_present = 'data' in response
    
    gateway.log_error(
        f"Response validation failed: status={status}, data={data_present}"
    )
    return gateway.create_error_response(
        'Invalid response format',
        'VALIDATION_ERROR'
    )
```

---

## Performance

**Creation:** <0.1ms (object instantiation)  
**Rule Addition:** <0.001ms per rule  
**Validation:** O(n) where n = number of rules  
**Short-circuit:** Stops on first failure

**Optimization:**
- Add most likely to fail rules first
- Use simple validators for quick checks
- Complex validators last

---

## Related Functions

- `validate_http_response()` - Helper for field validation
- `create_transformer()` - Transform before validation
- `create_pipeline()` - Combine validation and transformation

---

## Notes

- Chainable API for readable validation
- All rules must pass (AND logic)
- Short-circuits on first failure
- Stateless (no side effects)
- Reusable across requests
- Field validators receive field value only
- Custom validators receive full response

---

**Lines:** 260
