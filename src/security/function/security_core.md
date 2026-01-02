# security_core.md

**Version:** 2025-12-13_1  
**Purpose:** Gateway implementation functions for security interface  
**Module:** security/security_core.py  
**Type:** Core Implementation Functions

---

## OVERVIEW

Provides gateway-accessible implementation functions for security operations including validation, encryption, hashing, and CVE mitigations. All functions delegate to the singleton SecurityManager.

**Pattern:** Gateway → Interface → Core (SUGA)  
**Singleton:** All operations use get_security_manager()  
**Debug:** All functions integrate correlation_id tracking

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SUGA: Gateway implementation layer
- SINGLETON: Uses get_security_manager()
- Debug Integration: All functions support correlation_id

**Security Fixes:**
- CVE-SUGA-2025-001: Cache key validation
- CVE-SUGA-2025-002: TTL boundary protection
- CVE-SUGA-2025-004: Module name validation

**Constraints:**
- LESS-21: Rate limiting (1000 ops/sec)

---

## VALIDATION FUNCTIONS

### validate_request_implementation()

Validate HTTP request structure and content.

**Signature:**
```python
def validate_request_implementation(
    request: Dict[str, Any],
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `request` (Dict[str, Any]): HTTP request dictionary
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Checks:**
- Request must be dictionary
- `method` must be string (if present)
- `headers` must be dictionary (if present)

**Example:**
```python
from security.security_core import validate_request_implementation

request = {
    'method': 'POST',
    'headers': {'Content-Type': 'application/json'},
    'body': '{"key": "value"}'
}

if validate_request_implementation(request):
    print("Valid request")
else:
    print("Invalid request")
```

---

### validate_token_implementation()

Validate authentication token format.

**Signature:**
```python
def validate_token_implementation(
    token: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `token` (str): Authentication token
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Checks:**
- Token must be string
- Token must not be empty
- Token must be at least 10 characters

**Example:**
```python
from security.security_core import validate_token_implementation

token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

if validate_token_implementation(token):
    print("Valid token")
else:
    print("Invalid token - too short or empty")
```

---

### validate_string_implementation()

Validate string length within bounds.

**Signature:**
```python
def validate_string_implementation(
    value: str,
    min_length: int = 0,
    max_length: int = 1000,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `value` (str): String to validate
- `min_length` (int): Minimum allowed length (default: 0)
- `max_length` (int): Maximum allowed length (default: 1000)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
from security.security_core import validate_string_implementation

# Username validation
username = "john_doe"
if validate_string_implementation(username, min_length=3, max_length=20):
    print("Valid username")

# Description validation
description = "A" * 500
if validate_string_implementation(description, max_length=1000):
    print("Valid description")
```

---

### validate_email_implementation()

Validate email address format.

**Signature:**
```python
def validate_email_implementation(
    email: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `email` (str): Email address to validate
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Pattern:**
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Example:**
```python
from security.security_core import validate_email_implementation

email = "user@example.com"
if validate_email_implementation(email):
    print("Valid email")

invalid_email = "user@invalid"
if not validate_email_implementation(invalid_email):
    print("Invalid email - missing domain extension")
```

---

### validate_url_implementation()

Validate URL format (HTTP/HTTPS only).

**Signature:**
```python
def validate_url_implementation(
    url: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `url` (str): URL to validate
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid, False otherwise

**Validation:**
- Must start with `http://` or `https://`

**Example:**
```python
from security.security_core import validate_url_implementation

url = "https://api.example.com/endpoint"
if validate_url_implementation(url):
    print("Valid URL")

invalid_url = "ftp://example.com"
if not validate_url_implementation(invalid_url):
    print("Invalid URL - must be HTTP/HTTPS")
```

---

## CRYPTOGRAPHY FUNCTIONS

### encrypt_implementation()

Encrypt data using XOR cipher (demo implementation).

**Signature:**
```python
def encrypt_implementation(
    data: str,
    key: Optional[str] = None,
    correlation_id: str = None,
    **kwargs
) -> str
```

**Parameters:**
- `data` (str): Data to encrypt
- `key` (Optional[str]): Encryption key (uses default if None)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `str`: Base64-encoded encrypted data

**Note:** Demo implementation using XOR cipher. For production, use AWS KMS.

**Example:**
```python
from security.security_core import encrypt_implementation, decrypt_implementation

# Encrypt sensitive data
data = "secret_value"
encrypted = encrypt_implementation(data, key="my-encryption-key")
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = decrypt_implementation(encrypted, key="my-encryption-key")
print(f"Decrypted: {decrypted}")  # "secret_value"
```

---

### decrypt_implementation()

Decrypt data using XOR cipher (demo implementation).

**Signature:**
```python
def decrypt_implementation(
    data: str,
    key: Optional[str] = None,
    correlation_id: str = None,
    **kwargs
) -> str
```

**Parameters:**
- `data` (str): Base64-encoded encrypted data
- `key` (Optional[str]): Decryption key (uses default if None)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `str`: Decrypted data

---

### hash_implementation()

Hash data using SHA-256.

**Signature:**
```python
def hash_implementation(
    data: str,
    correlation_id: str = None,
    **kwargs
) -> str
```

**Parameters:**
- `data` (str): Data to hash
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `str`: SHA-256 hash (hexadecimal)

**Example:**
```python
from security.security_core import hash_implementation

password = "user_password_123"
hashed = hash_implementation(password)
print(f"Hash: {hashed}")
# Output: Hash: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
```

---

### verify_hash_implementation()

Verify data against hash using constant-time comparison.

**Signature:**
```python
def verify_hash_implementation(
    data: str,
    hash_value: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `data` (str): Original data
- `hash_value` (str): Hash to verify against
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if hash matches, False otherwise

**Example:**
```python
from security.security_core import hash_implementation, verify_hash_implementation

# Store password hash
password = "user_password_123"
stored_hash = hash_implementation(password)

# Verify password later
input_password = "user_password_123"
if verify_hash_implementation(input_password, stored_hash):
    print("Password correct")
else:
    print("Password incorrect")
```

---

## UTILITY FUNCTIONS

### sanitize_implementation()

Sanitize input data for safe processing.

**Signature:**
```python
def sanitize_implementation(
    data: Any,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `data` (Any): Data to sanitize
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Any`: Sanitized data (same type as input)

**Sanitization:**
- Strings: Removes control characters (keeps \n, \r, \t)
- Dicts: Recursively sanitizes all values
- Lists: Recursively sanitizes all items
- Others: Returns unchanged

**Example:**
```python
from security.security_core import sanitize_implementation

# Sanitize user input
user_input = "Hello\x00World\x1F!"
sanitized = sanitize_implementation(user_input)
print(f"Sanitized: {sanitized}")  # "HelloWorld!"

# Sanitize nested data
data = {
    'name': 'John\x00Doe',
    'items': ['Item\x1F1', 'Item\x1F2']
}
clean_data = sanitize_implementation(data)
```

---

### generate_correlation_id_implementation()

Generate unique correlation ID using UUID4.

**Signature:**
```python
def generate_correlation_id_implementation(
    correlation_id: str = None,
    **kwargs
) -> str
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `str`: UUID4 correlation ID

**Example:**
```python
from security.security_core import generate_correlation_id_implementation

corr_id = generate_correlation_id_implementation()
print(f"Correlation ID: {corr_id}")
# Output: Correlation ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## CVE MITIGATION FUNCTIONS

### validate_cache_key_implementation()

Validate cache key for security (CVE-SUGA-2025-001 fix).

**Signature:**
```python
def validate_cache_key_implementation(
    key: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `key` (str): Cache key to validate
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValueError`: If key is invalid (with specific reason)

**Validation Rules:**
- Length: 1-255 characters
- Characters: [a-zA-Z0-9_-:.] only
- No path traversal patterns (../, ./, etc.)
- No control characters

**Example:**
```python
from security.security_core import validate_cache_key_implementation

# Valid key
try:
    validate_cache_key_implementation("user:123:profile")
    print("Valid cache key")
except ValueError as e:
    print(f"Invalid: {e}")

# Invalid key (path traversal)
try:
    validate_cache_key_implementation("user/../admin")
except ValueError as e:
    print(f"Rejected: {e}")
```

---

### validate_ttl_implementation()

Validate TTL with boundary protection (CVE-SUGA-2025-002 fix).

**Signature:**
```python
def validate_ttl_implementation(
    ttl: float,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `ttl` (float): TTL value in seconds
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValueError`: If TTL is invalid

**Validation Rules:**
- Range: 1 to 86400 seconds (24 hours)
- No NaN or Infinity values

**Example:**
```python
from security.security_core import validate_ttl_implementation

# Valid TTL
try:
    validate_ttl_implementation(300)  # 5 minutes
    print("Valid TTL")
except ValueError as e:
    print(f"Invalid: {e}")

# Invalid TTL
try:
    validate_ttl_implementation(float('inf'))
except ValueError as e:
    print(f"Rejected: {e}")  # "Invalid TTL: TTL cannot be infinity"
```

---

### validate_module_name_implementation()

Validate module name for LUGS (CVE-SUGA-2025-004 fix).

**Signature:**
```python
def validate_module_name_implementation(
    module_name: str,
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `module_name` (str): Module name to validate
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValueError`: If module name is invalid

**Validation Rules:**
- Valid Python identifier pattern
- Max 100 characters
- No path separators
- No control characters

**Example:**
```python
from security.security_core import validate_module_name_implementation

# Valid module names
validate_module_name_implementation("interface_cache")
validate_module_name_implementation("gateway.wrappers.cache")

# Invalid module name
try:
    validate_module_name_implementation("../../../etc/passwd")
except ValueError as e:
    print(f"Rejected: {e}")
```

---

### validate_number_range_implementation()

Validate number is within specified range (generic validator).

**Signature:**
```python
def validate_number_range_implementation(
    value: float,
    min_val: float,
    max_val: float,
    name: str = 'value',
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `value` (float): Number to validate
- `min_val` (float): Minimum allowed value
- `max_val` (float): Maximum allowed value
- `name` (str): Parameter name for error messages (default: 'value')
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValueError`: If value is out of range

**Example:**
```python
from security.security_core import validate_number_range_implementation

# Validate timeout
validate_number_range_implementation(
    value=30,
    min_val=1,
    max_val=60,
    name='timeout'
)

# Validate percentage
try:
    validate_number_range_implementation(
        value=150,
        min_val=0,
        max_val=100,
        name='percentage'
    )
except ValueError as e:
    print(f"Error: {e}")  # "percentage above maximum (max: 100, got: 150)"
```

---

## MANAGEMENT FUNCTIONS

### security_reset_implementation()

Reset security manager state.

**Signature:**
```python
def security_reset_implementation(
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True on success

---

### get_security_stats_implementation()

Get security statistics.

**Signature:**
```python
def get_security_stats_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Statistics including validator, crypto, and rate limit stats

**Example:**
```python
from security.security_core import get_security_stats_implementation

stats = get_security_stats_implementation()

print(f"Validations: {stats['validator_validations_performed']}")
print(f"Encryptions: {stats['crypto_encryptions']}")
print(f"Rate limited: {stats['rate_limit']['rate_limited_count']}")
```

---

## EXPORTS

```python
__all__ = [
    'validate_request_implementation',
    'validate_token_implementation',
    'validate_string_implementation',
    'validate_email_implementation',
    'validate_url_implementation',
    'encrypt_implementation',
    'decrypt_implementation',
    'hash_implementation',
    'verify_hash_implementation',
    'sanitize_implementation',
    'generate_correlation_id_implementation',
    'validate_cache_key_implementation',
    'validate_ttl_implementation',
    'validate_module_name_implementation',
    'validate_number_range_implementation',
    'security_reset_implementation',
    'get_security_stats_implementation',
]
```

---

**END OF DOCUMENTATION**

**Module:** security/security_core.py  
**Functions:** 17  
**Pattern:** SUGA Core Implementation  
**CVE Fixes:** 3 (001, 002, 004)
