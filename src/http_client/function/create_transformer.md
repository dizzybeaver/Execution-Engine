# create_transformer()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_transformation  
**Type:** Factory Function

---

## Purpose

Create a ResponseTransformer instance for transforming HTTP response data. Provides chainable operations for data manipulation.

---

## Signature

```python
def create_transformer() -> ResponseTransformer:
```

---

## Parameters

**None**

---

## Returns

**Type:** `ResponseTransformer`

**Instance of ResponseTransformer with methods:**
- `flatten(data, separator='.')` - Flatten nested dictionaries
- `extract(data, keys)` - Extract specific keys
- `map_fields(data, field_map)` - Rename fields
- `filter_fields(data, predicate)` - Filter by predicate
- `transform_values(data, transformer)` - Transform all values
- `normalize(data, schema)` - Normalize types

---

## Usage

### Basic Transformation

```python
from http_client import create_transformer

transformer = create_transformer()

# Flatten nested data
data = {
    'user': {
        'name': 'John',
        'address': {
            'city': 'NYC'
        }
    }
}
result = transformer.flatten(data)
# Returns: {'user.name': 'John', 'user.address.city': 'NYC'}
```

### Extract Fields

```python
transformer = create_transformer()

data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
result = transformer.extract(data, ['name', 'email'])
# Returns: {'name': 'John', 'email': 'john@example.com'}
```

### Map Fields

```python
transformer = create_transformer()

data = {'old_name': 'value1', 'old_email': 'value2'}
field_map = {'old_name': 'name', 'old_email': 'email'}
result = transformer.map_fields(data, field_map)
# Returns: {'name': 'value1', 'email': 'value2'}
```

### Filter Fields

```python
transformer = create_transformer()

data = {'name': 'John', 'age': 30, 'temp': None}
result = transformer.filter_fields(data, lambda k, v: v is not None)
# Returns: {'name': 'John', 'age': 30}
```

### Transform Values

```python
transformer = create_transformer()

data = {'a': '1', 'b': '2', 'c': '3'}
result = transformer.transform_values(data, int)
# Returns: {'a': 1, 'b': 2, 'c': 3}
```

### Normalize Types

```python
transformer = create_transformer()

data = {'age': '30', 'score': '95.5', 'name': 'John'}
schema = {'age': int, 'score': float, 'name': str}
result = transformer.normalize(data, schema)
# Returns: {'age': 30, 'score': 95.5, 'name': 'John'}
```

---

## ResponseTransformer Methods

### flatten(data, separator='.')

**Purpose:** Flatten nested dictionary structure

**Parameters:**
- `data` - Dictionary to flatten
- `separator` - Key separator (default: '.')

**Example:**
```python
input = {'a': {'b': {'c': 1}}}
output = {'a.b.c': 1}
```

### extract(data, keys)

**Purpose:** Extract only specified keys

**Parameters:**
- `data` - Source dictionary
- `keys` - List of keys to extract

**Example:**
```python
input = {'a': 1, 'b': 2, 'c': 3}
keys = ['a', 'c']
output = {'a': 1, 'c': 3}
```

### map_fields(data, field_map)

**Purpose:** Rename fields according to mapping

**Parameters:**
- `data` - Source dictionary
- `field_map` - Dict mapping old names to new names

**Example:**
```python
input = {'old': 'value'}
mapping = {'old': 'new'}
output = {'new': 'value'}
```

### filter_fields(data, predicate)

**Purpose:** Filter fields using predicate function

**Parameters:**
- `data` - Source dictionary
- `predicate` - Function(key, value) -> bool

**Example:**
```python
input = {'a': 1, 'b': None, 'c': 3}
predicate = lambda k, v: v is not None
output = {'a': 1, 'c': 3}
```

### transform_values(data, transformer)

**Purpose:** Transform all values using function

**Parameters:**
- `data` - Source dictionary
- `transformer` - Function(value) -> transformed_value

**Example:**
```python
input = {'a': 1, 'b': 2}
transformer = lambda x: x * 2
output = {'a': 2, 'b': 4}
```

### normalize(data, schema)

**Purpose:** Normalize data types according to schema

**Parameters:**
- `data` - Source dictionary
- `schema` - Dict mapping keys to types

**Example:**
```python
input = {'age': '30', 'score': '95.5'}
schema = {'age': int, 'score': float}
output = {'age': 30, 'score': 95.5}
```

---

## Complete Example

```python
from http_client import create_transformer

# Get HTTP response
response = gateway.http_get('https://api.example.com/user/123')

if response['success']:
    transformer = create_transformer()
    
    # Extract relevant fields
    data = transformer.extract(response['data'], 
                              ['id', 'name', 'email', 'profile'])
    
    # Flatten nested profile
    data = transformer.flatten(data)
    
    # Normalize types
    schema = {'id': int, 'name': str, 'email': str}
    data = transformer.normalize(data, schema)
    
    # Result ready for use
    print(data)
```

---

## Related Functions

- `create_pipeline()` - Create transformation pipeline
- `transform_http_response()` - Transform response wrapper
- `create_common_transformers()` - Get common transformers dict

---

## Performance

**Creation Time:** <0.1ms (object instantiation)  
**Transformation Time:** Varies by operation
- `flatten`: O(n) where n = total fields
- `extract`: O(k) where k = keys to extract
- `map_fields`: O(n) where n = field count
- `filter_fields`: O(n) with predicate call
- `transform_values`: O(n) with transformer call
- `normalize`: O(s) where s = schema size

---

## Notes

- Stateless transformations (no side effects)
- Safe for reuse across multiple transformations
- Non-destructive (returns new data)
- Handles non-dict data gracefully (returns as-is)
- Type conversion errors handled in `normalize()`

---

**Lines:** 240
