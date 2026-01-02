# interface_security.py

**Version:** 2025-12-13_1  
**Module:** SECURITY  
**Layer:** Interface  
**Interface:** INT-05  
**Lines:** ~225

---

## Purpose

Security interface router with comprehensive validation and security operations.

---

## Main Function

### execute_security_operation()

**Signature:**
```python
def execute_security_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route security operation requests using dispatch dictionary

**Parameters:**
- `operation` (str) - Operation name
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (varies by operation)

**Operations:**
- `validate_request` - Validate request
- `validate_token` - Validate authentication token
- `encrypt` - Encrypt data
- `decrypt` - Decrypt data
- `hash` - Hash data
- `verify_hash` - Verify hash
- `sanitize` / `sanitize_data` - Sanitize data
- `generate_correlation_id` - Generate correlation ID
- `validate_string` - Validate string
- `validate_email` - Validate email
- `validate_url` - Validate URL
- `get_stats` - Get security statistics
- `validate_cache_key` - Validate cache key
- `validate_ttl` - Validate TTL
- `validate_module_name` - Validate module name
- `validate_number_range` - Validate number range
- `reset` / `reset_security` - Reset security state

**Raises:**
- `RuntimeError` - If Security interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### validate_request

**Purpose:** Validate incoming request

**Parameters:**
- `request` (dict, required) - Request to validate

**Returns:** bool (True if valid)

**Raises:**
- `ValueError` - If request invalid

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_request',
    request={'method': 'GET', 'path': '/api/users'}
)
```

---

### validate_token

**Purpose:** Validate authentication token

**Parameters:**
- `token` (str, required) - Token to validate

**Returns:** bool (True if valid)

**Validation:**
- Token must be provided
- Token must be string

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_token',
    token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
)
```

---

### encrypt

**Purpose:** Encrypt data

**Parameters:**
- `data` (str, required) - Data to encrypt
- `key` (str, optional) - Encryption key

**Returns:** str (encrypted data)

**Validation:**
- Data must be provided
- Data must be string

**Usage:**
```python
encrypted = execute_security_operation(
    'encrypt',
    data='sensitive information'
)
```

---

### decrypt

**Purpose:** Decrypt data

**Parameters:**
- `data` (str, required) - Encrypted data
- `key` (str, optional) - Decryption key

**Returns:** str (decrypted data)

**Validation:**
- Data must be provided
- Data must be string

**Usage:**
```python
decrypted = execute_security_operation(
    'decrypt',
    data='encrypted_string'
)
```

---

### hash

**Purpose:** Hash data

**Parameters:**
- `data` (str, required) - Data to hash
- `algorithm` (str, optional) - Hash algorithm (default: SHA-256)

**Returns:** str (hash value)

**Validation:**
- Data must be provided
- Data must be string

**Supported Algorithms:**
- SHA-256 (default)
- SHA-512
- MD5 (deprecated, for compatibility)

**Usage:**
```python
hash_value = execute_security_operation(
    'hash',
    data='password123',
    algorithm='SHA-256'
)
```

---

### verify_hash

**Purpose:** Verify data matches hash

**Parameters:**
- `data` (str, required) - Data to verify
- `hash_value` (str, required) - Expected hash value
- `algorithm` (str, optional) - Hash algorithm

**Returns:** bool (True if match)

**Validation:**
- Data must be provided
- Hash value must be provided

**Usage:**
```python
is_valid = execute_security_operation(
    'verify_hash',
    data='password123',
    hash_value='expected_hash_value'
)
```

---

### sanitize / sanitize_data

**Purpose:** Sanitize data for safe use

**Parameters:**
- `data` (Any, required) - Data to sanitize

**Returns:** Sanitized data (same type as input)

**Sanitization:**
- Removes script tags
- Escapes HTML entities
- Removes SQL injection attempts
- Strips dangerous characters

**Usage:**
```python
clean = execute_security_operation(
    'sanitize',
    data='<script>alert("XSS")</script>Hello'
)
# Returns: 'Hello'
```

---

### generate_correlation_id

**Purpose:** Generate unique correlation ID

**Parameters:** None

**Returns:** str (UUID-based correlation ID)

**Usage:**
```python
corr_id = execute_security_operation('generate_correlation_id')
# Returns: 'abc123-def456-...'
```

---

### validate_string

**Purpose:** Validate string meets criteria

**Parameters:**
- `value` (str, required) - String to validate
- `min_length` (int, optional) - Minimum length
- `max_length` (int, optional) - Maximum length
- `pattern` (str, optional) - Regex pattern

**Returns:** bool (True if valid)

**Validation:**
- Value must be provided
- Value must be string

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_string',
    value='username',
    min_length=3,
    max_length=20
)
```

---

### validate_email

**Purpose:** Validate email address

**Parameters:**
- `value` (str, required) - Email to validate

**Returns:** bool (True if valid email)

**Validation:**
- Value must be provided
- Value must be string
- Must match email pattern

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_email',
    value='user@example.com'
)
```

---

### validate_url

**Purpose:** Validate URL

**Parameters:**
- `value` (str, required) - URL to validate

**Returns:** bool (True if valid URL)

**Validation:**
- Value must be provided
- Value must be string
- Must match URL pattern

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_url',
    value='https://example.com/path'
)
```

---

### get_stats

**Purpose:** Get security statistics

**Parameters:** None

**Returns:** Dict with security stats:
- `validations_performed` - Total validations
- `validation_failures` - Failed validations
- `encryptions_performed` - Encryption operations
- `sanitizations_performed` - Sanitization operations

**Usage:**
```python
stats = execute_security_operation('get_stats')
```

---

### validate_cache_key

**Purpose:** Validate cache key

**Parameters:**
- `key` (str, required) - Cache key to validate

**Returns:** bool (True if valid)

**Validation:**
- Key must be provided
- Key must be string
- Key must not contain invalid characters

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_cache_key',
    key='user_123'
)
```

---

### validate_ttl

**Purpose:** Validate TTL (Time To Live)

**Parameters:**
- `ttl` (int/float, required) - TTL value in seconds

**Returns:** bool (True if valid)

**Validation:**
- TTL must be provided
- TTL must be numeric
- TTL must be positive

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_ttl',
    ttl=300
)
```

---

### validate_module_name

**Purpose:** Validate module name

**Parameters:**
- `module_name` (str, required) - Module name to validate

**Returns:** bool (True if valid)

**Validation:**
- Module name must be provided
- Module name must be string
- Must be valid Python identifier

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_module_name',
    module_name='cache_core'
)
```

---

### validate_number_range

**Purpose:** Validate number is within range

**Parameters:**
- `value` (int/float, required) - Value to validate
- `min_val` (int/float, required) - Minimum value
- `max_val` (int/float, required) - Maximum value

**Returns:** bool (True if in range)

**Validation:**
- All parameters must be provided
- All must be numeric

**Usage:**
```python
is_valid = execute_security_operation(
    'validate_number_range',
    value=50,
    min_val=0,
    max_val=100
)
```

---

### reset / reset_security

**Purpose:** Reset security state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_security_operation('reset')
```

---

## Validation Helpers

### _validate_token_param()

**Purpose:** Validate token parameter

**Checks:**
- Token exists
- Token is string

---

### _validate_hash_params()

**Purpose:** Validate hash verification parameters

**Checks:**
- Data exists
- Hash value exists

---

### _validate_data_string_param()

**Purpose:** Validate data parameter is string

**Checks:**
- Data exists
- Data is string

---

### _validate_value_string_param()

**Purpose:** Validate value parameter is string

**Checks:**
- Value exists
- Value is string

---

### _validate_sanitize_data_param()

**Purpose:** Validate data parameter for sanitize operations

**Checks:**
- Data exists

---

### _validate_cache_key_param()

**Purpose:** Validate cache key parameter

**Checks:**
- Key exists
- Key is string

---

### _validate_ttl_param()

**Purpose:** Validate TTL parameter

**Checks:**
- TTL exists
- TTL is numeric

---

### _validate_module_name_param()

**Purpose:** Validate module name parameter

**Checks:**
- Module name exists
- Module name is string

---

### _validate_number_range_params()

**Purpose:** Validate number range parameters

**Checks:**
- Value exists
- Min value exists
- Max value exists

---

## Import Protection

**Pattern:**
```python
try:
    import security
    _SECURITY_AVAILABLE = True
except ImportError as e:
    _SECURITY_AVAILABLE = False
    _SECURITY_IMPORT_ERROR = str(e)
```

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Dispatch Dictionary:** O(1) operation routing  
✅ **Parameter Validation:** Comprehensive checks  
✅ **Type Safety:** Type validation on all inputs  
✅ **Security Focus:** Encryption, hashing, sanitization

---

## Related Files

- `/security/` - Security implementation
- `/gateway/wrappers/gateway_wrappers_security.py` - Gateway wrappers
- `/security/security_DIRECTORY.md` - Directory structure

---

**END OF DOCUMENTATION**
