# create_common_transformers()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_transformation  
**Type:** Factory Function

---

## Purpose

Create dictionary of common transformation functions. Provides quick access to frequently used transformers without creating a ResponseTransformer instance.

---

## Signature

```python
def create_common_transformers() -> Dict[str, Callable]:
```

---

## Parameters

**None**

---

## Returns

**Type:** `Dict[str, Callable]`

**Dictionary of transformer functions:**
```python
{
    'flatten': callable,         # Flatten nested dicts
    'extract': callable,         # Extract specific keys
    'map': callable,            # Rename fields
    'filter': callable,         # Filter by predicate
    'transform_values': callable, # Transform all values
    'normalize': callable        # Normalize data types
}
```

---

## Behavior

1. **Create ResponseTransformer Instance**
   - Internal instance for accessing methods

2. **Build Dictionary**
   - Map string keys to transformer methods

3. **Return Dictionary**
   - All transformers ready to use

---

## Usage

### Basic Usage

```python
from http_client.http_client_transformation import create_common_transformers

# Get all transformers
transformers = create_common_transformers()

# Use flatten
data = {'a': {'b': {'c': 1}}}
flat = transformers['flatten'](data)
# Returns: {'a.b.c': 1}

# Use extract
data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
extracted = transformers['extract'](data, ['name', 'email'])
# Returns: {'name': 'John', 'email': 'john@example.com'}
```

### Quick Transformations

```python
from http_client.http_client_transformation import create_common_transformers
import gateway

transformers = create_common_transformers()

# Get API data
response = gateway.http_get('https://api.example.com/user/123')

if response['success']:
    data = response['data']
    
    # Quick flatten
    flat_data = transformers['flatten'](data)
    
    # Quick filter
    clean_data = transformers['filter'](
        flat_data,
        lambda k, v: v is not None
    )
```

### Select Specific Transformers

```python
transformers = create_common_transformers()

# Get only needed transformers
flatten = transformers['flatten']
extract = transformers['extract']

# Use directly
data = {'nested': {'field': 'value'}}
flat = flatten(data)
extracted = extract(flat, ['nested.field'])
```

---

## Transformers Included

### flatten

**Purpose:** Flatten nested dictionaries

**Signature:** `flatten(data, separator='.')`

**Example:**
```python
transformers = create_common_transformers()

data = {
    'user': {
        'name': 'John',
        'address': {
            'city': 'NYC'
        }
    }
}

flat = transformers['flatten'](data)
# Returns: {'user.name': 'John', 'user.address.city': 'NYC'}

# With custom separator
flat = transformers['flatten'](data, separator='_')
# Returns: {'user_name': 'John', 'user_address_city': 'NYC'}
```

### extract

**Purpose:** Extract specific keys

**Signature:** `extract(data, keys)`

**Example:**
```python
transformers = create_common_transformers()

data = {
    'id': 1,
    'name': 'John',
    'age': 30,
    'email': 'john@example.com',
    'internal_field': 'secret'
}

extracted = transformers['extract'](data, ['id', 'name', 'email'])
# Returns: {'id': 1, 'name': 'John', 'email': 'john@example.com'}
```

### map

**Purpose:** Rename fields

**Signature:** `map(data, field_map)`

**Example:**
```python
transformers = create_common_transformers()

data = {
    'userId': 123,
    'userName': 'John',
    'userEmail': 'john@example.com'
}

field_map = {
    'userId': 'id',
    'userName': 'name',
    'userEmail': 'email'
}

mapped = transformers['map'](data, field_map)
# Returns: {'id': 123, 'name': 'John', 'email': 'john@example.com'}
```

### filter

**Purpose:** Filter fields by predicate

**Signature:** `filter(data, predicate)`

**Example:**
```python
transformers = create_common_transformers()

data = {
    'name': 'John',
    'age': 30,
    'email': None,
    'active': True,
    'deleted': False
}

# Remove None values
filtered = transformers['filter'](data, lambda k, v: v is not None)
# Returns: {'name': 'John', 'age': 30, 'active': True, 'deleted': False}

# Keep only truthy values
filtered = transformers['filter'](data, lambda k, v: v)
# Returns: {'name': 'John', 'age': 30, 'active': True}
```

### transform_values

**Purpose:** Transform all values

**Signature:** `transform_values(data, transformer)`

**Example:**
```python
transformers = create_common_transformers()

data = {'a': 1, 'b': 2, 'c': 3}

# Double all values
doubled = transformers['transform_values'](data, lambda x: x * 2)
# Returns: {'a': 2, 'b': 4, 'c': 6}

# Convert to strings
stringified = transformers['transform_values'](data, str)
# Returns: {'a': '1', 'b': '2', 'c': '3'}
```

### normalize

**Purpose:** Normalize data types

**Signature:** `normalize(data, schema)`

**Example:**
```python
transformers = create_common_transformers()

data = {
    'id': '123',
    'age': '30',
    'score': '95.5',
    'name': 'John'
}

schema = {
    'id': int,
    'age': int,
    'score': float,
    'name': str
}

normalized = transformers['normalize'](data, schema)
# Returns: {'id': 123, 'age': 30, 'score': 95.5, 'name': 'John'}
```

---

## Complete Example

```python
from http_client.http_client_transformation import create_common_transformers
import gateway

# Get transformers
t = create_common_transformers()

# Get HA entity data
response = gateway.http_get('https://ha.example.com/api/states/light.living_room')

if response['success']:
    data = response['data']
    
    # Step 1: Flatten nested structure
    flat = t['flatten'](data)
    
    # Step 2: Extract relevant fields
    extracted = t['extract'](flat, [
        'entity_id',
        'state',
        'attributes.friendly_name',
        'attributes.brightness'
    ])
    
    # Step 3: Filter out None values
    filtered = t['filter'](extracted, lambda k, v: v is not None)
    
    # Step 4: Normalize types
    schema = {'attributes.brightness': int}
    normalized = t['normalize'](filtered, schema)
    
    gateway.log_info("Processed entity", **normalized)
```

---

## Use Cases

### API Response Processing

```python
transformers = create_common_transformers()

def process_api_response(response):
    """Process and clean API response."""
    data = response.get('data', {})
    
    # Flatten nested response
    flat = transformers['flatten'](data)
    
    # Remove internal fields
    filtered = transformers['filter'](
        flat,
        lambda k, v: not k.startswith('_')
    )
    
    return filtered
```

### Data Migration

```python
transformers = create_common_transformers()

def migrate_old_format(old_data):
    """Migrate old data format to new."""
    # Rename fields
    field_map = {
        'old_id': 'id',
        'old_name': 'name',
        'old_value': 'value'
    }
    mapped = transformers['map'](old_data, field_map)
    
    # Normalize types
    schema = {'id': int, 'name': str, 'value': float}
    normalized = transformers['normalize'](mapped, schema)
    
    return normalized
```

### Data Validation

```python
transformers = create_common_transformers()

def validate_and_clean(data):
    """Validate and clean input data."""
    # Extract allowed fields
    allowed = ['id', 'name', 'email', 'active']
    extracted = transformers['extract'](data, allowed)
    
    # Filter out invalid values
    filtered = transformers['filter'](
        extracted,
        lambda k, v: v is not None and v != ''
    )
    
    return filtered
```

---

## Comparison with ResponseTransformer

### Using create_common_transformers()

```python
# Quick access to individual transformers
transformers = create_common_transformers()
flat = transformers['flatten'](data)
extracted = transformers['extract'](flat, keys)
```

**Pros:**
- Quick access by name
- No instance needed
- Good for one-off transforms

**Cons:**
- Creates internal instance
- Less fluent API

### Using ResponseTransformer Instance

```python
# Fluent API with instance
from http_client import create_transformer

transformer = create_transformer()
flat = transformer.flatten(data)
extracted = transformer.extract(flat, keys)
```

**Pros:**
- Fluent API
- Explicit instance
- Better for chaining

**Cons:**
- Slightly more verbose
- Need to create instance

---

## Performance

**Creation:** <0.1ms (creates one ResponseTransformer)  
**Access:** O(1) dictionary lookup  
**Memory:** ~1KB (dict with 6 functions)

---

## Related Functions

- `create_transformer()` - Create ResponseTransformer instance
- `create_pipeline()` - Create transformation pipeline
- `transform_http_response()` - Transform HTTP response

---

## Notes

- **Convenience function:** Quick access to common transformers
- **Single instance:** Creates one ResponseTransformer internally
- **Dictionary access:** Get transformers by name
- **All methods included:** All ResponseTransformer methods available
- **Stateless:** Transformers have no side effects
- **Reusable:** Same transformers work on any data

---

**Lines:** 340
