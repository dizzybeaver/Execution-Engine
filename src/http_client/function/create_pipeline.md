# create_pipeline()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_transformation  
**Type:** Factory Function

---

## Purpose

Create a TransformationPipeline instance for chainable HTTP response transformations. Enables validation, transformation, and filtering in sequence.

---

## Signature

```python
def create_pipeline() -> TransformationPipeline:
```

---

## Parameters

**None**

---

## Returns

**Type:** `TransformationPipeline`

**Instance with methods:**
- `add_validation(validator, error_handler=None)` - Add validation step
- `add_transformation(transformer, metadata=None)` - Add transformation
- `add_filter(filter_func)` - Add filter step
- `execute(data)` - Execute pipeline on data

---

## Usage

### Basic Pipeline

```python
from http_client import create_pipeline

# Create pipeline
pipeline = (create_pipeline()
    .add_validation(lambda d: isinstance(d, dict))
    .add_transformation(lambda d: {k: v for k, v in d.items() if v is not None})
    .add_filter(lambda d: len(d) > 0))

# Execute on data
data = {'name': 'John', 'age': None, 'email': 'john@example.com'}
result = pipeline.execute(data)

# Returns:
{
    'success': True,
    'data': {'name': 'John', 'email': 'john@example.com'}
}
```

### Validation with Error Handler

```python
pipeline = create_pipeline()

# Add validation with custom error handler
def validate_user(data):
    return 'user_id' in data and 'email' in data

def handle_error(data):
    return {'user_id': 0, 'email': 'unknown@example.com'}

pipeline.add_validation(validate_user, error_handler=handle_error)

# Missing required fields - error handler provides defaults
data = {'name': 'John'}
result = pipeline.execute(data)
# Uses error handler to provide defaults
```

### Transformation Chain

```python
from http_client import create_pipeline, create_transformer

pipeline = create_pipeline()
transformer = create_transformer()

# Chain multiple transformations
pipeline.add_transformation(lambda d: transformer.flatten(d))
pipeline.add_transformation(lambda d: transformer.extract(d, ['id', 'name', 'email']))
pipeline.add_transformation(lambda d: transformer.normalize(d, {'id': int, 'name': str}))

# Execute
data = {
    'user': {
        'id': '123',
        'name': 'John',
        'email': 'john@example.com',
        'metadata': {...}
    }
}
result = pipeline.execute(data)

# Returns flattened, extracted, normalized data
```

---

## TransformationPipeline Methods

### add_validation(validator, error_handler=None)

**Purpose:** Add validation step to pipeline

**Parameters:**
- `validator` (`Callable`) - Function(data) -> bool
- `error_handler` (`Callable`, optional) - Function(data) -> corrected_data

**Returns:** `self` (for chaining)

**Behavior:**
- If validator returns True: Continue
- If validator returns False and error_handler: Use handler result
- If validator returns False and no handler: Return error response

**Example:**
```python
pipeline.add_validation(
    lambda d: 'id' in d,
    error_handler=lambda d: {**d, 'id': 0}
)
```

### add_transformation(transformer, metadata=None)

**Purpose:** Add transformation step to pipeline

**Parameters:**
- `transformer` (`Callable`) - Function(data) -> transformed_data
- `metadata` (`Dict`, optional) - Transformation metadata

**Returns:** `self` (for chaining)

**Example:**
```python
pipeline.add_transformation(
    lambda d: {k: str(v).upper() for k, v in d.items()},
    metadata={'step': 'uppercase_values'}
)
```

### add_filter(filter_func)

**Purpose:** Add filter step to pipeline

**Parameters:**
- `filter_func` (`Callable`) - Function(data) -> filtered_data

**Returns:** `self` (for chaining)

**Example:**
```python
pipeline.add_filter(
    lambda d: {k: v for k, v in d.items() if v not in [None, '', []]}
)
```

### execute(data)

**Purpose:** Execute all pipeline steps on data

**Parameters:**
- `data` (`Any`) - Data to transform

**Returns:** `Dict[str, Any]`

**Success:**
```python
{
    'success': True,
    'data': transformed_data
}
```

**Failure:**
```python
{
    'success': False,
    'error': str,
    'data': partial_data  # Data at point of failure
}
```

---

## Complete Example

```python
from http_client import create_pipeline, create_transformer
import gateway

# Create transformer
transformer = create_transformer()

# Build pipeline
pipeline = (create_pipeline()
    # Validate: Must be dict with required fields
    .add_validation(
        lambda d: isinstance(d, dict) and 'entities' in d,
        error_handler=lambda d: {'entities': []}
    )
    
    # Transform: Flatten nested structure
    .add_transformation(lambda d: transformer.flatten(d))
    
    # Transform: Extract relevant fields
    .add_transformation(lambda d: transformer.extract(
        d, 
        ['entities.state', 'entities.attributes.brightness']
    ))
    
    # Filter: Remove None values
    .add_filter(lambda d: {k: v for k, v in d.items() if v is not None})
)

# Get HA data
response = gateway.http_get('https://ha.example.com/api/states')

if response['success']:
    # Run through pipeline
    result = pipeline.execute(response['data'])
    
    if result['success']:
        processed_data = result['data']
        gateway.log_info(f"Processed {len(processed_data)} fields")
    else:
        gateway.log_error(f"Pipeline failed: {result['error']}")
```

---

## Pipeline Patterns

### API Response Normalization

```python
def create_api_normalizer():
    """Pipeline to normalize API responses."""
    return (create_pipeline()
        .add_validation(lambda d: 'data' in d)
        .add_transformation(lambda d: d.get('data', {}))
        .add_filter(lambda d: {k: v for k, v in d.items() if v})
        .add_transformation(lambda d: {
            k: str(v).lower() if isinstance(v, str) else v 
            for k, v in d.items()
        }))
```

### Home Assistant Entity Processing

```python
def create_ha_entity_pipeline():
    """Pipeline for HA entity data."""
    transformer = create_transformer()
    
    return (create_pipeline()
        .add_validation(lambda d: 'entity_id' in d and 'state' in d)
        .add_transformation(lambda d: transformer.flatten(d))
        .add_transformation(lambda d: transformer.extract(d, [
            'entity_id', 
            'state', 
            'attributes.friendly_name',
            'attributes.brightness'
        ]))
        .add_filter(lambda d: {k: v for k, v in d.items() if v != 'unknown'}))
```

### Data Sanitization

```python
def create_sanitizer():
    """Pipeline to sanitize untrusted data."""
    return (create_pipeline()
        .add_validation(lambda d: isinstance(d, dict))
        .add_filter(lambda d: {
            k: v for k, v in d.items() 
            if not k.startswith('_')  # Remove private fields
        })
        .add_transformation(lambda d: {
            k: str(v)[:100] if isinstance(v, str) else v  # Truncate strings
            for k, v in d.items()
        })
        .add_filter(lambda d: {
            k: v for k, v in d.items() 
            if k in ['id', 'name', 'value']  # Whitelist fields
        }))
```

---

## Error Handling

```python
pipeline = (create_pipeline()
    .add_validation(lambda d: 'required_field' in d)
    .add_transformation(lambda d: d['required_field'].upper()))

# Execute with error handling
try:
    result = pipeline.execute(data)
    
    if not result['success']:
        gateway.log_error(f"Pipeline failed: {result['error']}")
        gateway.log_debug(f"Failed at data: {result.get('data')}")
    else:
        processed = result['data']
        
except Exception as e:
    gateway.log_error(f"Pipeline exception: {e}")
```

---

## Pipeline Execution Order

```python
pipeline = (create_pipeline()
    .add_validation(step1)      # Step 1: Validation
    .add_transformation(step2)  # Step 2: Transform
    .add_filter(step3)          # Step 3: Filter
    .add_transformation(step4)  # Step 4: Transform
    .add_validation(step5))     # Step 5: Validation

# Execution: step1 → step2 → step3 → step4 → step5
# Stops on first failure
```

---

## Performance

**Pipeline Creation:** <0.1ms  
**Execution:** Sum of all step times  
**Overhead:** Minimal (~0.01ms per step)

**Optimization Tips:**
- Put fast validations first
- Minimize transformations
- Combine similar operations
- Use filters to reduce data early

---

## Related Functions

- `create_transformer()` - Create transformer for use in pipeline
- `create_validator()` - Create validator for validation steps
- `transform_http_response()` - Apply transformer to response

---

## Notes

- **Chainable:** All add methods return `self`
- **Sequential:** Steps execute in order added
- **Short-circuit:** Stops on first failure
- **Error data:** Returns data at point of failure
- **Reusable:** Same pipeline can transform multiple datasets
- **Stateless:** No side effects

---

**Lines:** 320
