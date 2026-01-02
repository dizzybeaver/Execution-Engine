# utility_response.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_response.py  
**Module:** Utility response formatting

---

## Overview

Response formatting utilities for Lambda and API responses. Provides template-based fast path with recursion protection and JSON sanitization.

**File:** `utility/utility_response.py`  
**Lines:** 243  
**Pattern:** ResponseFormatter class with public function exports

---

## Classes

### ResponseFormatter

**Purpose:** Response formatting utilities for Lambda and API responses  
**Pattern:** Singleton instance (_RESPONSE_FORMATTER)

---

## Methods (via Singleton)

### format_response_fast()

**Purpose:** Fast Lambda response formatting using templates  
**Returns:** dict (Lambda response)

**Parameters:**
- `status_code` (int): HTTP status code
- `body` (Any): Response body (string or object)
- `headers` (str, optional): JSON headers string

**Template:** `{"statusCode":%d,"body":%s,"headers":%s}`

**Usage:**
```python
# Via singleton
response = format_response_fast(200, '{"success": true}')

# Via class
response = ResponseFormatter.format_response_fast(200, {'success': True})
```

**Returns:**
```python
{
    'statusCode': 200,
    'body': '{"success": true}',
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
}
```

**Fallback:** Uses `_format_response_fallback()` on error (no recursion)

---

### format_response()

**Purpose:** Format Lambda response (standard path)  
**Returns:** dict (Lambda response)

**Parameters:**
- `status_code` (int): HTTP status code
- `body` (Any): Response body
- `headers` (dict, optional): Custom headers

**Usage:**
```python
# Default headers
response = format_response(200, {'success': True})

# Custom headers
response = format_response(200, {'data': 'test'}, headers={'Custom-Header': 'value'})
```

**Behavior:**
- Uses fast path if templates enabled and headers are default
- Sanitizes body for JSON
- Falls back to standard path on error

---

### create_success_response()

**Purpose:** Create success response with template optimization  
**Returns:** dict (success response)

**Parameters:**
- `message` (str): Success message
- `data` (Any, optional): Response data
- `correlation_id` (str, optional): Correlation ID

**Usage:**
```python
# Simple success
response = create_success_response('Operation completed')
# Result: {
#     'success': True,
#     'message': 'Operation completed',
#     'timestamp': 1702480800
# }

# With data
response = create_success_response('User created', data={'user_id': '123'})
# Result: {
#     'success': True,
#     'message': 'User created',
#     'timestamp': 1702480800,
#     'data': {'user_id': '123'}
# }

# With correlation ID
response = create_success_response('Done', correlation_id='req-123')
# Result: {
#     'success': True,
#     'message': 'Done',
#     'timestamp': 1702480800,
#     'correlation_id': 'req-123'
# }
```

**Template (with correlation):**
```
{"success":true,"message":"%s","timestamp":%d,"data":%s,"correlation_id":"%s"}
```

---

### create_error_response()

**Purpose:** Create error response with template optimization  
**Returns:** dict (error response)

**Parameters:**
- `message` (str): Error message
- `error_code` (str, default="UNKNOWN_ERROR"): Error code
- `details` (Any, optional): Error details
- `correlation_id` (str, optional): Correlation ID

**Usage:**
```python
# Simple error
response = create_error_response('Operation failed')
# Result: {
#     'success': False,
#     'error': 'Operation failed',
#     'error_code': 'UNKNOWN_ERROR',
#     'timestamp': 1702480800
# }

# With error code
response = create_error_response('Not found', error_code='NOT_FOUND')

# With details
response = create_error_response(
    'Validation failed',
    error_code='VALIDATION_ERROR',
    details={'field': 'email', 'reason': 'invalid format'}
)

# With correlation ID
response = create_error_response(
    'Internal error',
    error_code='INTERNAL_ERROR',
    correlation_id='req-123'
)
```

---

## Helper Functions

### _sanitize_for_json()

**Purpose:** Sanitize object for JSON serialization  
**Access:** Private

**Parameters:**
- `obj` (Any): Object to sanitize
- `max_depth` (int, default=10): Maximum recursion depth

**Behavior:**
- Converts tuples to lists
- Converts tuple keys to strings
- Recursively sanitizes nested structures
- Prevents infinite recursion

**Handled Types:**
- None, str, int, float, bool → Pass through
- list, tuple → Recursive sanitization
- dict → Key and value sanitization
- Other → Convert to string

---

### _safe_json_dumps()

**Purpose:** Safely convert object to JSON string  
**Access:** Private

**Parameters:**
- `obj` (Any): Object to convert

**Behavior:**
1. Try normal JSON serialization
2. If fails, sanitize and retry
3. If still fails, return error JSON

**Returns:** str (JSON string)

---

### _format_response_fallback()

**Purpose:** Fallback response formatter (breaks recursion cycle)  
**Access:** Private (static method)

**Parameters:**
- `status_code` (int): HTTP status code
- `body` (Any): Response body

**Critical:** NEVER calls `format_response_fast()` to prevent recursion

---

## Runtime Configuration

**Environment Variable:**
- `USE_JSON_TEMPLATES` (default: 'true')

**Values:**
- 'true' → Enable template optimization
- 'false' → Use standard path

---

## Usage Patterns

### Lambda Response
```python
# Success response
return format_response(200, {'success': True, 'data': result})

# Error response
return format_response(400, {'error': 'Invalid input'})

# Custom headers
return format_response(200, result, headers={'Cache-Control': 'no-cache'})
```

### Success/Error Helpers
```python
# Success
return create_success_response('User created', data={'user_id': '123'})

# Error
return create_error_response(
    'Validation failed',
    error_code='VALIDATION_ERROR',
    details={'field': 'email'}
)
```

### Fast Path
```python
# When headers are default
response = format_response_fast(200, '{"success": true}')
```

---

## Recursion Protection

**Problem:** Previous versions had recursion between `format_response_fast()` and error handling

**Solution:**
- `_format_response_fallback()` NEVER calls `format_response_fast()`
- Three-tier fallback strategy:
  1. Try fast path with template
  2. Fall back to sanitize + standard
  3. Last resort: hardcoded safe response

---

## Related Files

- **Types:** `utility/utility_types.py` (templates and constants)
- **Core:** `utility/utility_core.py`
- **Interface:** `interface/interface_utility.py`

---

**END OF DOCUMENTATION**
