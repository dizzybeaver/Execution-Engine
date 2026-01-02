# validate_http_response()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_validation  
**Type:** Validation Function

---

## Purpose

Validate HTTP response structure and required fields. Simple helper function for common validation scenarios.

---

## Signature

```python
def validate_http_response(response: Dict[str, Any], 
                          required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
```

---

## Parameters

- **response** (`Dict[str, Any]`) - HTTP response to validate
  - Must have `'success'` key
  - May have `'data'` key with response data

- **required_fields** (`List[str]`, optional) - Required fields in response data
  - If None: No field validation
  - If provided: All fields must be in `response['data']`

---

## Returns

**Type:** `Dict[str, Any]`

**Valid Response (unchanged):**
```python
{
    'success': True,
    'status_code': int,
    'data': {...},      # All required fields present
    'headers': {...}
}
```

**Failed Response (unchanged):**
```python
{
    'success': False,
    'error': str,
    'error_type': str
}
# Returned unchanged - no validation performed
```

**Validation Error:**
```python
{
    'success': False,
    'error': 'Missing required fields: field1, field2',
    'error_type': 'VALIDATION_ERROR'
}
```

---

## Behavior

1. **Check Response Success**
   - If `response.get('success')` is False: Return unchanged
   - Skip validation for failed responses

2. **Check Required Fields**
   - If `required_fields` is None: Return unchanged
   - No field validation needed

3. **Extract Data**
   - Get `response.get('data', {})`

4. **Validate Fields**
   - Check if each required field in data
   - Build list of missing fields

5. **Handle Missing Fields**
   - If any missing: Return validation error
   - Include list of missing fields in error message

6. **Return Valid Response**
   - If all fields present: Return unchanged

---

## Usage

### Basic Validation

```python
from http_client.http_client_validation import validate_http_response
import gateway

# Make request
response = gateway.http_get('https://api.example.com/user/123')

# Validate required fields
validated = validate_http_response(response, required_fields=['id', 'name', 'email'])

if validated['success']:
    user = validated['data']
    print(f"User: {user['name']}")
else:
    print(f"Validation failed: {validated['error']}")
```

### No Field Validation

```python
# Just pass through successful responses
validated = validate_http_response(response)

# Returns response unchanged (no required_fields specified)
```

### With Error Handling

```python
response = gateway.http_get(url)

# Validate
validated = validate_http_response(response, required_fields=['id', 'status'])

if not validated['success']:
    if validated.get('error_type') == 'VALIDATION_ERROR':
        gateway.log_error(f"Missing fields: {validated['error']}")
    else:
        gateway.log_error(f"Request failed: {validated['error']}")
```

---

## Complete Example

```python
from http_client.http_client_validation import validate_http_response
import gateway

def get_user_data(user_id):
    """Get and validate user data."""
    # Make API request
    response = gateway.http_get(f'https://api.example.com/users/{user_id}')
    
    # Validate response structure
    validated = validate_http_response(
        response,
        required_fields=['id', 'name', 'email', 'status']
    )
    
    if not validated['success']:
        gateway.log_error(f"User data validation failed: {validated['error']}")
        return None
    
    return validated['data']

# Use function
user = get_user_data(123)
if user:
    print(f"User: {user['name']} ({user['email']})")
```

---

## Validation Scenarios

### API Contract Validation

```python
# Ensure API returns expected fields
def validate_api_contract(response):
    """Validate API contract."""
    return validate_http_response(
        response,
        required_fields=['id', 'type', 'attributes', 'relationships']
    )
```

### Home Assistant Entity

```python
def validate_ha_entity(response):
    """Validate HA entity response."""
    return validate_http_response(
        response,
        required_fields=['entity_id', 'state', 'attributes']
    )

# Use
response = gateway.http_get(f'{ha_url}/api/states/light.living_room')
validated = validate_ha_entity(response)
```

### Pagination Response

```python
def validate_paginated_response(response):
    """Validate paginated API response."""
    return validate_http_response(
        response,
        required_fields=['items', 'total', 'page', 'per_page']
    )
```

---

## Error Messages

### Missing Single Field

```python
response = {
    'success': True,
    'data': {'name': 'John'}
}

validated = validate_http_response(response, required_fields=['id', 'name'])

# Error: "Missing required fields: id"
```

### Missing Multiple Fields

```python
response = {
    'success': True,
    'data': {'name': 'John'}
}

validated = validate_http_response(
    response,
    required_fields=['id', 'email', 'status']
)

# Error: "Missing required fields: id, email, status"
```

### All Fields Present

```python
response = {
    'success': True,
    'data': {'id': 123, 'name': 'John', 'email': 'john@example.com'}
}

validated = validate_http_response(response, required_fields=['id', 'name', 'email'])

# Returns: response (unchanged)
```

---

## Combining with Transformation

```python
from http_client.http_client_validation import validate_http_response
from http_client.http_client_transformation import transform_http_response
import gateway

# Make request
response = gateway.http_get(url)

# Validate first
validated = validate_http_response(response, required_fields=['id', 'name'])

if validated['success']:
    # Then transform
    transformed = transform_http_response(
        validated,
        lambda d: {k: str(v).upper() for k, v in d.items()}
    )
    
    if transformed['success']:
        result = transformed['data']
```

---

## Advanced Validation

For more complex validation, use ResponseValidator:

```python
from http_client import create_validator

# Complex validation
validator = (create_validator()
    .add_status_code_rule([200, 201])
    .add_field_rule('id', lambda x: isinstance(x, int) and x > 0)
    .add_field_rule('email', lambda x: '@' in str(x))
    .add_custom_rule(lambda r: len(r.get('data', {})) > 0))

is_valid = validator.validate(response)
```

---

## Performance

**Time:** O(n) where n = number of required fields  
**Memory:** Minimal (list of missing fields)  
**Overhead:** ~0.1ms for typical validation

---

## Failed Response Handling

```python
# Failed request
response = {
    'success': False,
    'error': 'Connection timeout',
    'error_type': 'ConnectionError'
}

# Validation skipped
validated = validate_http_response(response, required_fields=['id'])

# Returns original failed response unchanged
assert validated == response
```

---

## Edge Cases

### Empty Data

```python
response = {
    'success': True,
    'data': {}
}

validated = validate_http_response(response, required_fields=['id'])

# Error: "Missing required fields: id"
```

### No Data Key

```python
response = {
    'success': True
    # No 'data' key
}

validated = validate_http_response(response, required_fields=['id'])

# Error: "Missing required fields: id"
# (treats missing 'data' as empty dict)
```

### None as Data

```python
response = {
    'success': True,
    'data': None
}

validated = validate_http_response(response, required_fields=['id'])

# Error: "Missing required fields: id"
```

---

## Related Functions

- `create_validator()` - Advanced validation
- `transform_http_response()` - Transform after validation
- `gateway.create_error_response()` - Error format

---

## Notes

- **Skip on failure:** Only validates successful responses
- **Simple validation:** Checks field presence only
- **No type checking:** Use ResponseValidator for type checks
- **Gateway format:** Uses standard error response
- **Non-destructive:** Returns unchanged or error
- **Helper function:** Quick field validation

---

**Lines:** 300
