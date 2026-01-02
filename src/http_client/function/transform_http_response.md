# transform_http_response()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_transformation  
**Type:** Response Transformer Function

---

## Purpose

Transform HTTP response data using a transformer function. Wrapper that applies transformation only to successful responses.

---

## Signature

```python
def transform_http_response(response: Dict[str, Any], 
                           transformer: Callable) -> Dict[str, Any]:
```

---

## Parameters

- **response** (`Dict[str, Any]`) - HTTP response to transform
  - Must have `'success'` and `'data'` keys
  - Standard gateway response format

- **transformer** (`Callable`) - Transformation function
  - Signature: `function(data) -> transformed_data`
  - Applied to `response['data']`

---

## Returns

**Type:** `Dict[str, Any]`

**Success (transformed):**
```python
{
    'success': True,
    'status_code': int,
    'data': transformed_data,      # Transformed
    'headers': {...},
    'transformed': True            # Flag added
}
```

**Success (error in transformation):**
```python
{
    'success': False,
    'error': 'Transformation failed: {error_message}',
    'error_type': 'TRANSFORM_ERROR'
}
```

**Already Failed:**
```python
{
    'success': False,
    'error': str,
    'error_type': str
}
# Returned unchanged - no transformation attempted
```

---

## Behavior

1. **Check Response Success**
   - If `response.get('success')` is False: Return unchanged
   - Skip transformation for failed responses

2. **Extract Data**
   - Get `response.get('data')`

3. **Apply Transformer**
   - Call `transformer(data)`
   - Catch any exceptions

4. **Update Response**
   - Set `response['data'] = transformed`
   - Add `response['transformed'] = True`

5. **Handle Errors**
   - If exception: Return error response
   - Error type: `'TRANSFORM_ERROR'`

6. **Return Response**
   - Modified response with transformed data

---

## Usage

### Basic Usage

```python
from http_client import get_http_client_manager
from http_client.http_client_transformation import transform_http_response

# Make request
client = get_http_client_manager()
response = client.make_request('GET', 'https://api.example.com/user/123')

# Transform response
def extract_user_data(data):
    return {
        'id': data['id'],
        'name': data['name'],
        'email': data['email']
    }

transformed = transform_http_response(response, extract_user_data)

if transformed['success']:
    user = transformed['data']
    print(f"User: {user['name']}")
```

### With ResponseTransformer

```python
from http_client import get_http_client_manager, create_transformer
from http_client.http_client_transformation import transform_http_response

transformer = create_transformer()

# Make request
response = client.make_request('GET', url)

# Flatten nested response
transformed = transform_http_response(
    response,
    lambda d: transformer.flatten(d)
)
```

### Via Gateway

```python
import gateway
from http_client import create_transformer
from http_client.http_client_transformation import transform_http_response

# Make request
response = gateway.http_get('https://api.example.com/data')

# Transform
transformer = create_transformer()
transformed = transform_http_response(
    response,
    lambda d: transformer.extract(d, ['id', 'name', 'status'])
)
```

---

## Complete Example

```python
from http_client import get_http_client_manager, create_transformer
from http_client.http_client_transformation import transform_http_response
import gateway

# Create transformer
transformer = create_transformer()

# Make HA API request
client = get_http_client_manager()
response = client.make_request(
    'GET',
    'https://ha.example.com/api/states/light.living_room'
)

# Define transformation
def process_entity_state(data):
    # Flatten structure
    flat = transformer.flatten(data)
    
    # Extract relevant fields
    extracted = transformer.extract(flat, [
        'entity_id',
        'state',
        'attributes.friendly_name',
        'attributes.brightness'
    ])
    
    # Normalize types
    schema = {
        'state': str,
        'attributes.brightness': int
    }
    normalized = transformer.normalize(extracted, schema)
    
    return normalized

# Transform response
transformed = transform_http_response(response, process_entity_state)

if transformed['success']:
    entity = transformed['data']
    gateway.log_info(f"Entity: {entity}")
else:
    gateway.log_error(f"Failed: {transformed.get('error')}")
```

---

## Transformation Patterns

### Extract Fields

```python
def extract_fields(fields):
    """Create extractor for specific fields."""
    def extractor(data):
        return {k: data.get(k) for k in fields if k in data}
    return extractor

transformed = transform_http_response(
    response,
    extract_fields(['id', 'name', 'email'])
)
```

### Flatten Nested Data

```python
from http_client import create_transformer

transformer = create_transformer()

transformed = transform_http_response(
    response,
    lambda d: transformer.flatten(d, separator='_')
)
```

### Filter Values

```python
def remove_nulls(data):
    """Remove null/None values."""
    return {k: v for k, v in data.items() if v is not None}

transformed = transform_http_response(response, remove_nulls)
```

### Map Field Names

```python
def map_field_names(data):
    """Rename API fields to internal names."""
    mapping = {
        'userId': 'user_id',
        'userName': 'name',
        'userEmail': 'email'
    }
    return {mapping.get(k, k): v for k, v in data.items()}

transformed = transform_http_response(response, map_field_names)
```

---

## Error Handling

### Transformation Errors

```python
def risky_transform(data):
    # May raise exception
    return data['required_field'].upper()

# Safe wrapper
response = client.make_request('GET', url)
transformed = transform_http_response(response, risky_transform)

if not transformed['success']:
    if transformed.get('error_type') == 'TRANSFORM_ERROR':
        gateway.log_error(f"Transformation failed: {transformed['error']}")
    else:
        gateway.log_error(f"Request failed: {transformed['error']}")
```

### Failed Requests

```python
# Request failed
response = {
    'success': False,
    'error': 'Connection timeout',
    'error_type': 'ConnectionError'
}

# Transformation skipped - returns unchanged
transformed = transform_http_response(response, some_transformer)
# Returns original failed response
```

---

## Combining with Validation

```python
from http_client.http_client_validation import validate_http_response
from http_client.http_client_transformation import transform_http_response

# Make request
response = client.make_request('GET', url)

# Validate first
validated = validate_http_response(response, required_fields=['id', 'name'])

if validated['success']:
    # Then transform
    transformed = transform_http_response(
        validated,
        lambda d: {k: str(v).upper() for k, v in d.items()}
    )
```

---

## Performance

**Overhead:** ~0.1ms (wrapper logic)  
**Total Time:** Transformer execution time + overhead  
**Memory:** Depends on transformer (creates new data dict)

**Tips:**
- Keep transformers simple
- Avoid deep copies if possible
- Use in-place modifications when safe

---

## Chaining Transformations

```python
# Multiple transformations
response = client.make_request('GET', url)

# First transformation
step1 = transform_http_response(response, transformer1)

# Second transformation
step2 = transform_http_response(step1, transformer2)

# Third transformation
final = transform_http_response(step2, transformer3)

# Better: Use pipeline instead
from http_client import create_pipeline

pipeline = (create_pipeline()
    .add_transformation(transformer1)
    .add_transformation(transformer2)
    .add_transformation(transformer3))

result = pipeline.execute(response['data'])
```

---

## Transformed Flag

```python
response = client.make_request('GET', url)
transformed = transform_http_response(response, some_transformer)

# Check if transformed
if transformed.get('transformed'):
    print("Response was transformed")
    
# Flag useful for tracking
gateway.log_info(
    "Response processed",
    transformed=transformed.get('transformed', False)
)
```

---

## Related Functions

- `create_transformer()` - Create transformer instance
- `create_pipeline()` - Chain multiple transformations
- `validate_http_response()` - Validate before transforming
- `gateway.create_error_response()` - Error response format

---

## Notes

- **Skip on failure:** Only transforms successful responses
- **Exception safe:** Catches transformer exceptions
- **Adds flag:** Sets `'transformed': True`
- **Non-destructive:** Creates new response dict
- **Gateway format:** Uses standard response format
- **Chainable:** Can chain multiple transforms

---

**Lines:** 310
