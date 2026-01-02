# Security Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** security
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Authentication, encryption, validation

---

## Overview

The Security domain provides authentication, encryption/decryption, input validation, and access control services.

**Gateway:** SecurityGateway
**Interfaces:** 3 (authentication, encryption, validation)
**Operations:** ~10

---

## 1. Authentication Interface

**Purpose:** Authentication and authorization
**Location:** `EE/security/authentication/`

### Operations

#### 1.1 login

Authenticate user credentials.

**Parameters:**
- `username` (str, required): Username
- `password` (str, required): Password
- `mfa_code` (str, optional): Multi-factor auth code

**Returns:** Auth token (str) or session info (dict)

**Raises:**
- `InvalidOperationError`: Invalid credentials

**Examples:**
```python
# Standard login
token = execute_operation(
    domain="security",
    interface="authentication",
    operation="login",
    username="john@example.com",
    password="securepass123"
)

# Login with MFA
session = execute_operation(
    domain="security",
    interface="authentication",
    operation="login",
    username="john@example.com",
    password="securepass123",
    mfa_code="123456"
)
```

---

#### 1.2 logout

Logout user/session.

**Parameters:**
- `token` (str, required): Auth token or session ID

**Returns:** True if successful

**Examples:**
```python
execute_operation(
    domain="security",
    interface="authentication",
    operation="logout",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
```

---

#### 1.3 verify

Verify authentication token.

**Parameters:**
- `token` (str, required): Auth token to verify

**Returns:** User info (dict) if valid

**Raises:**
- `InvalidOperationError`: Invalid or expired token

**Examples:**
```python
user_info = execute_operation(
    domain="security",
    interface="authentication",
    operation="verify",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
# Returns: {"user_id": 123, "username": "john", "exp": 1234567890}
```

---

#### 1.4 refresh

Refresh authentication token.

**Parameters:**
- `token` (str, required): Current auth token

**Returns:** New auth token (str)

**Examples:**
```python
new_token = execute_operation(
    domain="security",
    interface="authentication",
    operation="refresh",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
```

---

## 2. Encryption Interface

**Purpose:** Cryptographic operations
**Location:** `EE/security/encryption/`

### Operations

#### 2.1 encrypt

Encrypt data.

**Parameters:**
- `value` (str, required): Data to encrypt
- `algorithm` (str, optional): Encryption algorithm (default: "aes-256-gcm")
- `key_id` (str, optional): Key identifier for key management

**Returns:** Encrypted data (str, base64-encoded)

**Examples:**
```python
# Simple encryption
encrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value="sensitive data"
)

# With specific algorithm
encrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="encrypt",
    value="sensitive data",
    algorithm="aes-256-gcm",
    key_id="production-key-1"
)
```

---

#### 2.2 decrypt

Decrypt data.

**Parameters:**
- `value` (str, required): Encrypted data (base64-encoded)
- `key_id` (str, optional): Key identifier if needed

**Returns:** Decrypted data (str)

**Raises:**
- `InvalidOperationError`: Decryption failed

**Examples:**
```python
decrypted = execute_operation(
    domain="security",
    interface="encryption",
    operation="decrypt",
    value="U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=",
    key_id="production-key-1"
)
```

---

#### 2.3 hash

Generate hash of data.

**Parameters:**
- `value` (str, required): Data to hash
- `algorithm` (str, optional): Hash algorithm (default: "sha256")

**Returns:** Hash value (str, hex-encoded)

**Examples:**
```python
# SHA-256 hash (default)
hash_value = execute_operation(
    domain="security",
    interface="encryption",
    operation="hash",
    value="password123"
)

# SHA-512 hash
hash_value = execute_operation(
    domain="security",
    interface="encryption",
    operation="hash",
    value="password123",
    algorithm="sha512"
)
```

---

#### 2.4 verify_hash

Verify data against hash.

**Parameters:**
- `value` (str, required): Data to verify
- `hash_value` (str, required): Expected hash (hex-encoded)
- `algorithm` (str, optional): Hash algorithm (default: "sha256")

**Returns:** Boolean

**Examples:**
```python
is_valid = execute_operation(
    domain="security",
    interface="encryption",
    operation="verify_hash",
    value="password123",
    hash_value="ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
)
```

---

## 3. Validation Interface

**Purpose:** Input validation and sanitization
**Location:** `EE/security/validation/`

### Operations

#### 3.1 validate_input

Validate user input.

**Parameters:**
- `input` (Any, required): Input to validate
- `rules` (dict, required): Validation rules

**Returns:** True if valid

**Raises:**
- `InvalidOperationError`: Validation failed

**Examples:**
```python
# Validate email
is_valid = execute_operation(
    domain="security",
    interface="validation",
    operation="validate_input",
    input="user@example.com",
    rules={"type": "email"}
)

# Validate with multiple rules
is_valid = execute_operation(
    domain="security",
    interface="validation",
    operation="validate_input",
    input="password123",
    rules={
        "type": "string",
        "min_length": 8,
        "max_length": 128,
        "pattern": "^[a-zA-Z0-9]+$"
    }
)
```

---

#### 3.2 sanitize

Sanitize user input.

**Parameters:**
- `input` (str, required): Input to sanitize
- `mode` (str, required): Sanitization mode (html, sql, json, path)

**Returns:** Sanitized string (str)

**Examples:**
```python
# Sanitize HTML (prevent XSS)
clean = execute_operation(
    domain="security",
    interface="validation",
    operation="sanitize",
    input="<script>alert('xss')</script>",
    mode="html"
)
# Returns: "&lt;script&gt;alert('xss')&lt;/script&gt;"

# Sanitize for SQL (prevent SQL injection)
clean = execute_operation(
    domain="security",
    interface="validation",
    operation="sanitize",
    input="'; DROP TABLE users; --",
    mode="sql"
)
```

---

#### 3.3 check_permission

Check user permission.

**Parameters:**
- `user_id` (int, required): User ID
- `permission` (str, required): Permission to check
- `resource` (str, optional): Resource identifier

**Returns:** Boolean

**Examples:**
```python
# Check permission
has_access = execute_operation(
    domain="security",
    interface="validation",
    operation="check_permission",
    user_id=123,
    permission="users.delete",
    resource="user:456"
)
```

---

## Cross-Domain Operations

**Security may call:**
- `foundation.config` - For security configuration
- `observability.logging` - For audit logs

**All domains may call:**
- `security.authentication` - For auth
- `security.encryption` - For encryption
- `security.validation` - For input validation

---

## Pooling

**Encryption engines:** Pool of 3-5 instances
**Auth sessions:** Pool of 10-20 instances
**Validators:** Stateless (no pooling)

---

## Security Best Practices

**DO:**
✅ Always hash passwords before storage
✅ Use encryption for sensitive data
✅ Validate all user input
✅ Check permissions before operations
✅ Log security events

**DON'T:**
❌ Store passwords in plaintext
❌ Log sensitive data (tokens, passwords)
❌ Trust client-side validation
❌ Use weak encryption algorithms
❌ Ignore security errors

---

## Examples

### Complete Auth Flow

```python
def authenticate_user(username, password):
    # Hash password for comparison
    password_hash = execute_operation(
        domain="security",
        interface="encryption",
        operation="hash",
        value=password
    )

    # Verify credentials (would check DB here)
    # ... verification logic ...

    # Generate token
    token = execute_operation(
        domain="security",
        interface="authentication",
        operation="login",
        username=username,
        password=password_hash
    )

    # Log security event
    execute_operation(
        domain="observability",
        interface="logging",
        operation="info",
        message="User logged in",
        context={"username": username, "event": "login"}
    )

    return token
```

### Data Encryption Pattern

```python
class SecureStorage:
    def save_sensitive_data(self, user_id, data):
        # Encrypt data
        encrypted = execute_operation(
            domain="security",
            interface="encryption",
            operation="encrypt",
            value=data,
            key_id="storage-key"
        )

        # Save to storage
        # ... storage logic ...

        # Log security event (no sensitive data)
        execute_operation(
            domain="observability",
            interface="logging",
            operation="info",
            message="Encrypted data saved",
            context={"user_id": user_id, "operation": "save"}
        )

    def read_sensitive_data(self, user_id, encrypted_data):
        # Decrypt data
        decrypted = execute_operation(
            domain="security",
            interface="encryption",
            operation="decrypt",
            value=encrypted_data,
            key_id="storage-key"
        )

        return decrypted
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory
- [DEC-EE-07](../../SIMA/projects/EE/decisions/DEC-EE-07-security-extraction-factories.md) - Security extraction decision

**Implementation:**
- `EE/security/security_gateway.py` - Gateway implementation
- `EE/security/authentication/` - Authentication interface
- `EE/security/encryption/` - Encryption interface
- `EE/security/validation/` - Validation interface

---

**END OF SECURITY DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 349 (target achieved)
