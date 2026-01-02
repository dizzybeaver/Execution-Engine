# build_query_string()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_utilities  
**Type:** Utility Function

---

## Purpose

Build URL query string from parameters dictionary. Handles URL encoding and formatting for HTTP GET requests.

---

## Signature

```python
def build_query_string(params: Dict[str, Any]) -> str:
```

---

## Parameters

- **params** (`Dict[str, Any]`) - Query parameters
  - Keys: Parameter names (strings)
  - Values: Parameter values (any type)
  - Empty dict returns empty string

---

## Returns

**Type:** `str`

**Format:** URL-encoded query string

**Examples:**
- Empty dict: `''`
- Single param: `'key=value'`
- Multiple params: `'key1=value1&key2=value2'`
- Special chars: `'name=John+Doe&email=user%40example.com'`

---

## Behavior

1. **Check for Empty**
   - If `not params`: Return `''`
   - Empty string is valid (no query params)

2. **URL Encode**
   - Use `urllib.parse.urlencode(params)`
   - Automatically encodes special characters
   - Uses `+` for spaces (can use `%20` with quote_plus)

3. **Return Query String**
   - Returns encoded string
   - Does NOT include leading `?`

---

## Usage

### Basic Usage

```python
from http_client.http_client_utilities import build_query_string

# Simple parameters
params = {'key': 'value', 'limit': 10}
query = build_query_string(params)
# Returns: 'key=value&limit=10'

# Build full URL
base_url = 'https://api.example.com/data'
full_url = f'{base_url}?{query}'
# Returns: 'https://api.example.com/data?key=value&limit=10'
```

### Special Characters

```python
params = {
    'name': 'John Doe',
    'email': 'user@example.com',
    'message': 'Hello, World!'
}
query = build_query_string(params)
# Returns: 'name=John+Doe&email=user%40example.com&message=Hello%2C+World%21'
```

### Empty Parameters

```python
params = {}
query = build_query_string(params)
# Returns: ''

# Use in URL
base_url = 'https://api.example.com/data'
full_url = f'{base_url}{"?" + query if query else ""}'
# Returns: 'https://api.example.com/data'
```

### Numeric Values

```python
params = {
    'page': 1,
    'limit': 50,
    'offset': 0
}
query = build_query_string(params)
# Returns: 'page=1&limit=50&offset=0'
```

### Boolean Values

```python
params = {
    'active': True,
    'verified': False
}
query = build_query_string(params)
# Returns: 'active=True&verified=False'
```

---

## Complete Request Example

```python
from http_client import get_http_client_manager
from http_client.http_client_utilities import build_query_string

# Build query parameters
params = {
    'entity_id': 'light.living_room',
    'state': 'on',
    'brightness': 255
}

# Build query string
query = build_query_string(params)

# Build full URL
base_url = 'https://api.example.com/entities'
url = f'{base_url}?{query}'
# url: 'https://api.example.com/entities?entity_id=light.living_room&state=on&brightness=255'

# Make request
client = get_http_client_manager()
result = client.make_request('GET', url)
```

---

## URL Encoding Details

### Space Character
```python
params = {'name': 'John Doe'}
query = build_query_string(params)
# Returns: 'name=John+Doe'
# Note: Uses + for space (not %20)
```

### Special Characters
```python
params = {
    '@': 'at sign',
    '#': 'hash',
    '&': 'ampersand',
    '=': 'equals'
}
# Keys and values are both encoded
```

### Reserved Characters
- `!` → `%21`
- `#` → `%23`
- `$` → `%24`
- `&` → `%26`
- `'` → `%27`
- `(` → `%28`
- `)` → `%29`
- `*` → `%2A`
- `+` → `%2B`
- `,` → `%2C`
- `/` → `%2F`
- `:` → `%3A`
- `;` → `%3B`
- `=` → `%3D`
- `?` → `%3F`
- `@` → `%40`
- `[` → `%5B`
- `]` → `%5D`

---

## Common Patterns

### Pagination

```python
def get_page_url(base_url, page, limit=50):
    params = {'page': page, 'limit': limit}
    query = build_query_string(params)
    return f'{base_url}?{query}'

url = get_page_url('https://api.example.com/items', page=2, limit=25)
# Returns: 'https://api.example.com/items?page=2&limit=25'
```

### Filtering

```python
filters = {
    'status': 'active',
    'category': 'electronics',
    'min_price': 100,
    'max_price': 500
}
query = build_query_string(filters)
url = f'https://api.example.com/products?{query}'
```

### Search

```python
search_params = {
    'q': 'smart lights',
    'limit': 20,
    'sort': 'relevance'
}
query = build_query_string(search_params)
url = f'https://api.example.com/search?{query}'
```

### Optional Parameters

```python
def build_url(base, required_params, optional_params=None):
    params = required_params.copy()
    if optional_params:
        params.update(optional_params)
    
    query = build_query_string(params)
    return f'{base}?{query}' if query else base

# With optional params
url = build_url(
    'https://api.example.com/data',
    {'id': 123},
    {'include': 'details', 'format': 'json'}
)

# Without optional params
url = build_url(
    'https://api.example.com/data',
    {'id': 123}
)
```

---

## Parameter Order

**Note:** Dictionary order is preserved in Python 3.7+

```python
params = {
    'c': 3,
    'a': 1,
    'b': 2
}
query = build_query_string(params)
# Returns: 'c=3&a=1&b=2' (insertion order)
```

---

## Edge Cases

### None Values

```python
params = {'key': None}
query = build_query_string(params)
# Returns: 'key=None'
# Note: None becomes string 'None'
```

### Empty String Values

```python
params = {'key': ''}
query = build_query_string(params)
# Returns: 'key='
```

### List Values

```python
params = {'ids': [1, 2, 3]}
query = build_query_string(params)
# Returns: 'ids=%5B1%2C+2%2C+3%5D'
# Note: List becomes string '[1, 2, 3]'

# For multiple values, repeat key:
from urllib.parse import urlencode
params = [('id', 1), ('id', 2), ('id', 3)]
query = urlencode(params)
# Returns: 'id=1&id=2&id=3'
```

---

## Performance

**Time:** <1ms for typical params (<100 items)  
**Memory:** Minimal (proportional to params size)  
**Encoding:** Native urllib.parse (fast C implementation)

---

## Related Functions

- `build_query_string_fast()` - Alias (same implementation)
- `parse_response_headers()` - Parse response headers
- `http_get()` - Use built query strings

---

## Alternative: Manual Construction

```python
# Simple case (no encoding needed)
url = f"{base}?key={value}&limit={limit}"

# Better: Use build_query_string for safety
params = {'key': value, 'limit': limit}
query = build_query_string(params)
url = f"{base}?{query}"
```

---

## Notes

- **No leading `?`:** Function returns query string only
- **Empty dict:** Returns empty string
- **Auto-encoding:** Handles special characters
- **Stateless:** No side effects
- **Type conversion:** All values converted to strings
- **Order preserved:** Python 3.7+ dict order

---

**Lines:** 280
