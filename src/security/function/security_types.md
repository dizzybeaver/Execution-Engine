# security_types.md

**Version:** 2025-12-13_1  
**Purpose:** Security type definitions and enums  
**Module:** security/security_types.py  
**Type:** Type Definitions

---

## OVERVIEW

Defines security operation types and validation patterns used throughout the security interface.

**Contents:**
- SecurityOperation enum (15 operations)
- ValidationPattern enum (5 regex patterns)

---

## ENUMS

### SecurityOperation

Enumeration of all security operations.

**Definition:**
```python
class SecurityOperation(Enum):
    """Security operations enumeration."""
    
    # Core validation operations
    VALIDATE_REQUEST = "validate_request"
    VALIDATE_TOKEN = "validate_token"
    VALIDATE_STRING = "validate_string"
    VALIDATE_EMAIL = "validate_email"
    VALIDATE_URL = "validate_url"
    
    # Cryptographic operations
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    HASH = "hash"
    VERIFY_HASH = "verify_hash"
    
    # Utility operations
    SANITIZE = "sanitize"
    GENERATE_CORRELATION_ID = "generate_correlation_id"
    
    # CVE mitigation operations
    VALIDATE_CACHE_KEY = "validate_cache_key"
    VALIDATE_TTL = "validate_ttl"
    VALIDATE_MODULE_NAME = "validate_module_name"
    VALIDATE_NUMBER_RANGE = "validate_number_range"
```

**Usage:**
```python
from security.security_types import SecurityOperation

# Use in execute operation
operation = SecurityOperation.VALIDATE_EMAIL
result = execute_security_operation(operation, "user@example.com")

# Access string value
print(operation.value)  # "validate_email"

# Iterate all operations
for op in SecurityOperation:
    print(f"{op.name}: {op.value}")
```

---

## OPERATION CATEGORIES

### Core Validation Operations

**VALIDATE_REQUEST:**
- Purpose: Validate HTTP request structure
- Parameters: request (Dict)
- Returns: bool

**VALIDATE_TOKEN:**
- Purpose: Validate authentication token format
- Parameters: token (str)
- Returns: bool

**VALIDATE_STRING:**
- Purpose: Validate string length within bounds
- Parameters: value (str), min_length (int), max_length (int)
- Returns: bool

**VALIDATE_EMAIL:**
- Purpose: Validate email address format
- Parameters: email (str)
- Returns: bool

**VALIDATE_URL:**
- Purpose: Validate URL format (HTTP/HTTPS)
- Parameters: url (str)
- Returns: bool

---

### Cryptographic Operations

**ENCRYPT:**
- Purpose: Encrypt data
- Parameters: data (str), key (str)
- Returns: str (encrypted)

**DECRYPT:**
- Purpose: Decrypt data
- Parameters: data (str), key (str)
- Returns: str (decrypted)

**HASH:**
- Purpose: Hash data using SHA-256
- Parameters: data (str)
- Returns: str (hash)

**VERIFY_HASH:**
- Purpose: Verify data against hash
- Parameters: data (str), hash_value (str)
- Returns: bool

---

### Utility Operations

**SANITIZE:**
- Purpose: Sanitize input data for safe processing
- Parameters: data (Any)
- Returns: Any (sanitized)

**GENERATE_CORRELATION_ID:**
- Purpose: Generate unique correlation ID
- Parameters: None
- Returns: str (UUID4)

---

### CVE Mitigation Operations

**VALIDATE_CACHE_KEY:**
- Purpose: Validate cache key for security (CVE-SUGA-2025-001)
- Parameters: key (str)
- Returns: bool (raises ValueError if invalid)

**VALIDATE_TTL:**
- Purpose: Validate TTL with boundary protection (CVE-SUGA-2025-002)
- Parameters: ttl (float)
- Returns: bool (raises ValueError if invalid)

**VALIDATE_MODULE_NAME:**
- Purpose: Validate module name for LUGS (CVE-SUGA-2025-004)
- Parameters: module_name (str)
- Returns: bool (raises ValueError if invalid)

**VALIDATE_NUMBER_RANGE:**
- Purpose: Validate number is within specified range
- Parameters: value (float), min_val (float), max_val (float), name (str)
- Returns: bool (raises ValueError if invalid)

---

## VALIDATION PATTERNS

### ValidationPattern

Validation regex patterns enum.

**Definition:**
```python
class ValidationPattern(Enum):
    """Validation regex patterns."""
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL = r'^https?://[^\s]+$'
    TOKEN = r'^[A-Za-z0-9-_]{20,}$'
    ALPHANUMERIC = r'^[a-zA-Z0-9]+$'
    NUMERIC = r'^\d+$'
```

**Usage:**
```python
import re
from security.security_types import ValidationPattern

# Validate email
email = "user@example.com"
if re.match(ValidationPattern.EMAIL.value, email):
    print("Valid email")

# Validate alphanumeric
username = "john123"
if re.match(ValidationPattern.ALPHANUMERIC.value, username):
    print("Valid username")
```

---

## PATTERN DETAILS

### EMAIL Pattern

**Regex:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Matches:**
- `user@example.com`
- `john.doe+tag@company.co.uk`
- `info_2025@my-domain.org`

**Rejects:**
- `user@invalid` (no domain extension)
- `@example.com` (no local part)
- `user@` (no domain)

---

### URL Pattern

**Regex:** `^https?://[^\s]+$`

**Matches:**
- `http://example.com`
- `https://api.example.com/endpoint`
- `https://example.com:8080/path?query=value`

**Rejects:**
- `ftp://example.com` (not HTTP/HTTPS)
- `example.com` (no protocol)
- `http://example com` (contains space)

---

### TOKEN Pattern

**Regex:** `^[A-Za-z0-9-_]{20,}$`

**Matches:**
- `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9` (JWT)
- `sk_live_1234567890abcdefghij` (API key)
- `Bearer_token_1234567890_abcdefghij`

**Rejects:**
- `short` (less than 20 characters)
- `token with spaces` (contains space)
- `token@#$%` (invalid characters)

---

### ALPHANUMERIC Pattern

**Regex:** `^[a-zA-Z0-9]+$`

**Matches:**
- `username123`
- `ABC123XYZ`
- `test2025`

**Rejects:**
- `user_name` (contains underscore)
- `user-name` (contains hyphen)
- `user name` (contains space)

---

### NUMERIC Pattern

**Regex:** `^\d+$`

**Matches:**
- `123`
- `42`
- `99999`

**Rejects:**
- `12.34` (contains decimal point)
- `-123` (contains minus sign)
- `1a2` (contains letter)

---

## USAGE EXAMPLES

### Example 1: Operation Dispatch

```python
from security.security_types import SecurityOperation
from security.security_manager import get_security_manager

def validate_input(input_type: str, value: Any) -> bool:
    """Generic input validation using SecurityOperation enum."""
    manager = get_security_manager()
    
    operation_map = {
        'email': SecurityOperation.VALIDATE_EMAIL,
        'url': SecurityOperation.VALIDATE_URL,
        'token': SecurityOperation.VALIDATE_TOKEN,
    }
    
    operation = operation_map.get(input_type)
    if not operation:
        raise ValueError(f"Unknown input type: {input_type}")
    
    return manager.execute_security_operation(operation, None, value)

# Usage
is_valid_email = validate_input('email', 'user@example.com')
is_valid_url = validate_input('url', 'https://api.example.com')
```

---

### Example 2: Pattern-Based Validation

```python
import re
from security.security_types import ValidationPattern

def validate_username(username: str) -> bool:
    """Validate username is alphanumeric."""
    return bool(re.match(ValidationPattern.ALPHANUMERIC.value, username))

def validate_user_id(user_id: str) -> bool:
    """Validate user ID is numeric."""
    return bool(re.match(ValidationPattern.NUMERIC.value, user_id))

# Usage
assert validate_username("john123")
assert not validate_username("john_doe")  # underscore not allowed

assert validate_user_id("42")
assert not validate_user_id("42a")  # letter not allowed
```

---

### Example 3: All Operations Iteration

```python
from security.security_types import SecurityOperation

# List all available operations
print("Available Security Operations:")
for operation in SecurityOperation:
    print(f"  {operation.name}: {operation.value}")

# Output:
# VALIDATE_REQUEST: validate_request
# VALIDATE_TOKEN: validate_token
# VALIDATE_STRING: validate_string
# ...
```

---

### Example 4: Type-Safe Operation Selection

```python
from security.security_types import SecurityOperation
from typing import Dict, Any

def execute_operation(
    operation: SecurityOperation,
    *args,
    **kwargs
) -> Any:
    """Type-safe operation executor."""
    # Operation is guaranteed to be SecurityOperation enum
    # No risk of typos or invalid operation names
    
    from security.security_manager import get_security_manager
    manager = get_security_manager()
    return manager.execute_security_operation(operation, None, *args, **kwargs)

# Usage - IDE provides autocomplete for SecurityOperation values
result = execute_operation(
    SecurityOperation.VALIDATE_EMAIL,
    "user@example.com"
)
```

---

## OPERATION COUNT

**Total Operations:** 15

**By Category:**
- Core Validation: 5
- Cryptographic: 4
- Utility: 2
- CVE Mitigation: 4

---

## PATTERN COUNT

**Total Patterns:** 5

**By Type:**
- Communication: 2 (EMAIL, URL)
- Authentication: 1 (TOKEN)
- Character Sets: 2 (ALPHANUMERIC, NUMERIC)

---

## EXPORTS

```python
__all__ = [
    'SecurityOperation',
    'ValidationPattern'
]
```

---

## RELATED DOCUMENTATION

- **security_core.md**: Implementation of all operations
- **security_manager.md**: Operation execution logic
- **security_validation.md**: Pattern usage in validators

---

**END OF DOCUMENTATION**

**Module:** security/security_types.py  
**Enums:** 2  
**Operations:** 15  
**Patterns:** 5
