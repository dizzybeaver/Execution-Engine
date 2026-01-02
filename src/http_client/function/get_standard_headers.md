# get_standard_headers()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_utilities  
**Type:** Utility Function

---

## Purpose

Get standard HTTP headers for requests. Returns default headers used across all HTTP operations.

---

## Signature

```python
def get_standard_headers() -> Dict[str, str]:
```

---

## Parameters

**None**

---

## Returns

**Type:** `Dict[str, str]`

**Headers:**
```python
{
    'Content-Type': 'application/json',
    'User-Agent': 'LambdaExecutionEngine/1.0'
}
```

---

## Headers Included

### Content-Type
**Value:** `'application/json'`  
**Purpose:** Indicates JSON request body format  
**Standard:** RFC 7231

**Use Cases:**
- POST requests with JSON body
- PUT requests with JSON body
- Any request sending JSON data

### User-Agent
**Value:** `'LambdaExecutionEngine/1.0'`  
**Purpose:** Identifies LEE as the client  
**Standard:** RFC 7231

**Format:** `{Application}/{Version}`

**Benefits:**
- Server logging/analytics
- Rate limiting by client
- Issue tracking
- Debugging

---

## Usage

```python
from http_client.http_client_utilities import get_standard_headers

# Get default headers
headers = get_standard_headers()
# Returns: {'Content-Type': 'application/json', 'User-Agent': 'LambdaExecutionEngine/1.0'}

# Use in request
result = client.make_request(
    'GET',
    'https://api.example.com/data',
    headers=headers
)

# Extend with custom headers
headers = get_standard_headers()
headers['Authorization'] = 'Bearer token123'
headers['X-Custom-Header'] = 'value'
```

---

## Automatic Application

Headers are **automatically applied** if not provided:

```python
# In http_client_manager.py _execute_request()
headers = kwargs.get('headers', {})
if not headers:
    headers = get_standard_headers()
```

**No Headers Provided:**
```python
client.make_request('GET', url)
# Uses: {'Content-Type': 'application/json', 'User-Agent': 'LambdaExecutionEngine/1.0'}
```

**Custom Headers Provided:**
```python
client.make_request('GET', url, headers={'Authorization': 'Bearer token'})
# Uses: {'Authorization': 'Bearer token'}
# Does NOT automatically add standard headers
```

---

## Header Precedence

1. **Custom headers** (if provided) - Used as-is
2. **Standard headers** (if not provided) - Auto-applied
3. **JSON mode headers** (if json kwarg) - Content-Type may be set/overridden

```python
# Example: JSON mode
client.make_request('POST', url, json={'key': 'value'})
# Headers become: {'Content-Type': 'application/json', 'User-Agent': 'LambdaExecutionEngine/1.0'}

# Example: Custom + JSON mode
client.make_request('POST', url, json={'key': 'value'}, 
                   headers={'Authorization': 'Bearer token'})
# Headers: {'Authorization': 'Bearer token', 'Content-Type': 'application/json'}
# User-Agent NOT added (custom headers provided)
```

---

## Related Functions

### get_ha_headers(token)
Extends standard headers with Home Assistant authentication:
```python
def get_ha_headers(token: str) -> Dict[str, str]:
    headers = get_standard_headers()
    headers['Authorization'] = f'Bearer {token}'
    return headers
```

**Usage:**
```python
from http_client.http_client_utilities import get_ha_headers

headers = get_ha_headers('long_lived_token_here')
# Returns:
{
    'Content-Type': 'application/json',
    'User-Agent': 'LambdaExecutionEngine/1.0',
    'Authorization': 'Bearer long_lived_token_here'
}
```

---

## Performance

**Time:** <0.001ms (dictionary literal)  
**Memory:** ~150 bytes (2 strings)  
**Cached:** No (recreated each call, but very fast)

---

## Customization

To add project-wide headers, modify function:

```python
def get_standard_headers() -> Dict[str, str]:
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'LambdaExecutionEngine/1.0',
        'X-Request-Source': 'LEE',        # Added
        'X-Environment': os.getenv('STAGE', 'prod')  # Added
    }
```

---

## Common Patterns

### Merge with Custom Headers
```python
headers = get_standard_headers()
headers.update(custom_headers)
```

### Override Content-Type
```python
headers = get_standard_headers()
headers['Content-Type'] = 'application/xml'
```

### Remove Standard Headers
```python
headers = get_standard_headers()
del headers['User-Agent']  # Remove User-Agent
```

---

## Gateway Integration

```python
import gateway

# Standard headers applied automatically
result = gateway.http_get('https://api.example.com/data')

# Custom headers override
result = gateway.http_get(
    'https://api.example.com/data',
    headers={'Authorization': 'Bearer token'}
)
```

---

## Notes

- Simple utility function (no state)
- Returns new dictionary each call
- Safe to modify returned dictionary
- Not cached (fast enough without caching)
- Used as default in all HTTP operations

---

**Lines:** 200
