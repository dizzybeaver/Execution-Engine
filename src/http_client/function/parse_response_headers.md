# parse_response_headers()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_utilities  
**Type:** Utility Function

---

## Purpose

Parse and normalize HTTP response headers. Converts all header names to lowercase for consistent access.

---

## Signature

```python
def parse_response_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
```

---

## Parameters

- **headers** (`Dict[str, Any]`) - Raw response headers
  - Keys: Header names (any case)
  - Values: Header values

---

## Returns

**Type:** `Dict[str, Any]`

**Normalized headers with lowercase keys**

---

## Behavior

1. **Create Empty Result Dict**
   - Initialize `normalized = {}`

2. **Iterate Headers**
   - For each `key, value` in input headers

3. **Normalize Key**
   - Convert key to lowercase: `key.lower()`

4. **Store Value**
   - `normalized[key.lower()] = value`

5. **Return Normalized**
   - All keys lowercase, values unchanged

---

## Usage

### Basic Usage

```python
from http_client.http_client_utilities import parse_response_headers

# Raw headers (mixed case)
raw_headers = {
    'Content-Type': 'application/json',
    'Content-Length': '1234',
    'X-Custom-Header': 'value'
}

# Parse and normalize
headers = parse_response_headers(raw_headers)

# Returns:
{
    'content-type': 'application/json',
    'content-length': '1234',
    'x-custom-header': 'value'
}

# Access consistently
content_type = headers['content-type']  # Always works
```

### Case-Insensitive Access

```python
# Problem: HTTP headers are case-insensitive
raw = {
    'Content-Type': 'application/json',  # Server A
    'content-type': 'application/json',  # Server B
    'CONTENT-TYPE': 'application/json'   # Server C
}

# Solution: Normalize to lowercase
headers = parse_response_headers(raw)
content_type = headers.get('content-type')  # Always works
```

### With HTTP Response

```python
from http_client import get_http_client_manager
from http_client.http_client_utilities import parse_response_headers

client = get_http_client_manager()
result = client.make_request('GET', url)

if result['success']:
    # Normalize response headers
    headers = parse_response_headers(result['headers'])
    
    # Access normalized headers
    content_type = headers.get('content-type')
    cache_control = headers.get('cache-control')
    etag = headers.get('etag')
```

---

## Common Headers

### Standard Headers (Normalized)

```python
{
    # Content headers
    'content-type': 'application/json',
    'content-length': '1234',
    'content-encoding': 'gzip',
    
    # Cache headers
    'cache-control': 'no-cache',
    'etag': '"abc123"',
    'last-modified': 'Wed, 21 Oct 2015 07:28:00 GMT',
    
    # Response headers
    'server': 'nginx/1.18.0',
    'date': 'Thu, 12 Dec 2024 10:30:00 GMT',
    
    # Custom headers
    'x-custom-header': 'value',
    'x-request-id': 'req-123'
}
```

---

## HTTP Header Case Sensitivity

### RFC 7230 Standard

**Header names are case-insensitive:**
- `Content-Type` = `content-type` = `CONTENT-TYPE`
- Servers may use any case
- Clients must handle any case

**Why normalize:**
- Consistent access
- No case-sensitivity bugs
- Simpler code

---

## Header Access Patterns

### Before Normalization (Fragile)

```python
# ❌ Fragile - depends on server's case
content_type = headers.get('Content-Type')  # Works if server uses this case
content_type = headers.get('content-type')  # Works if server uses this case

# Need to check multiple cases
content_type = (headers.get('Content-Type') or 
                headers.get('content-type') or
                headers.get('CONTENT-TYPE'))
```

### After Normalization (Robust)

```python
# ✅ Robust - always works
headers = parse_response_headers(raw_headers)
content_type = headers.get('content-type')  # Always works
```

---

## Complete Example

```python
from http_client import get_http_client_manager
from http_client.http_client_utilities import parse_response_headers
import gateway

client = get_http_client_manager()

# Make request
result = client.make_request('GET', 'https://api.example.com/data')

if result['success']:
    # Parse headers
    headers = parse_response_headers(result['headers'])
    
    # Check content type
    content_type = headers.get('content-type', '')
    if 'application/json' not in content_type:
        gateway.log_warning(f"Unexpected content type: {content_type}")
    
    # Check caching
    cache_control = headers.get('cache-control', '')
    if 'no-cache' in cache_control:
        gateway.log_info("Response not cacheable")
    
    # Get custom headers
    request_id = headers.get('x-request-id')
    if request_id:
        gateway.log_info(f"Request ID: {request_id}")
```

---

## Header Extraction Patterns

### Extract Specific Headers

```python
def extract_cache_headers(headers):
    """Extract cache-related headers."""
    normalized = parse_response_headers(headers)
    
    return {
        'cache_control': normalized.get('cache-control'),
        'expires': normalized.get('expires'),
        'etag': normalized.get('etag'),
        'last_modified': normalized.get('last-modified')
    }
```

### Check Header Existence

```python
def has_compression(headers):
    """Check if response is compressed."""
    normalized = parse_response_headers(headers)
    encoding = normalized.get('content-encoding', '').lower()
    return encoding in ['gzip', 'deflate', 'br']
```

### Parse Content-Type

```python
def get_content_type_parts(headers):
    """Parse content-type into type and charset."""
    normalized = parse_response_headers(headers)
    content_type = normalized.get('content-type', '')
    
    # Example: "application/json; charset=utf-8"
    parts = content_type.split(';')
    mime_type = parts[0].strip() if parts else ''
    charset = None
    
    if len(parts) > 1:
        for part in parts[1:]:
            if 'charset=' in part:
                charset = part.split('=')[1].strip()
    
    return mime_type, charset
```

---

## Edge Cases

### Duplicate Headers

```python
# HTTP allows duplicate headers
# Most are combined with commas
raw = {
    'Set-Cookie': 'cookie1=value1',  # First cookie
    'set-cookie': 'cookie2=value2'   # Second cookie (duplicate)
}

# After normalization, one overwrites the other
headers = parse_response_headers(raw)
# One value is lost - this is a limitation
```

**Note:** For headers that can appear multiple times (like Set-Cookie), use raw headers or specialized parsing.

### Empty Headers

```python
raw = {}
headers = parse_response_headers(raw)
# Returns: {}
```

### Non-String Keys

```python
raw = {123: 'numeric-key'}
headers = parse_response_headers(raw)
# Returns: {'123': 'numeric-key'}
# Keys converted to lowercase strings
```

---

## Performance

**Time:** O(n) where n = number of headers  
**Memory:** O(n) for normalized dict  
**Typical:** <0.1ms for 10-20 headers

---

## Related Functions

- `parse_response_headers_fast()` - Alias (same implementation)
- `get_standard_headers()` - Build request headers
- `process_response()` - Process full response

---

## Alternative: Fast Variant

```python
def parse_response_headers_fast(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Fast header parser (optimized)."""
    return parse_response_headers(headers)
```

**Note:** Currently identical implementations. `_fast` variant exists for future optimization if needed.

---

## Notes

- **Lowercase keys:** All keys converted to lowercase
- **Values unchanged:** Header values preserved as-is
- **Case-insensitive:** Enables consistent access
- **Standard practice:** Common pattern in HTTP libraries
- **Duplicate headers:** May lose duplicates (limitation)
- **Stateless:** No side effects
- **Simple implementation:** Just dict comprehension

---

**Lines:** 260
