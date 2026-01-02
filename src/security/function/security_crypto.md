# security_crypto.md

**Version:** 2025-12-13_1  
**Purpose:** Cryptographic operations  
**Module:** security/security_crypto.py  
**Type:** Cryptography Class

---

## OVERVIEW

Handles all cryptographic operations including encryption, decryption, hashing, hash verification, and correlation ID generation.

**Features:**
- XOR cipher encryption/decryption (demo implementation)
- SHA-256 hashing
- Constant-time hash verification
- UUID4 correlation ID generation
- Operation statistics tracking

**Note:** Current encryption is demonstration-only. For production, implement proper encryption using AWS KMS.

---

## CLASSES

### SecurityCrypto

Handles all cryptographic operations with statistics tracking.

**Initialization:**
```python
def __init__(self):
    self._crypto_stats = {
        'encryptions': 0,
        'decryptions': 0,
        'hashes': 0,
        'correlation_ids_generated': 0
    }
    self._default_key = "lambda-execution-engine-default-key-2025"
```

**State:**
- `_crypto_stats`: Operation counters
- `_default_key`: Default encryption key for demo

---

## METHODS

### get_default_key()

Get the default encryption key (public accessor).

**Signature:**
```python
def get_default_key(self) -> str
```

**Returns:**
- `str`: Default encryption key

**Example:**
```python
crypto = SecurityCrypto()
key = crypto.get_default_key()
print(f"Default key: {key}")
```

---

### encrypt_data()

Encrypt data using XOR cipher (demonstration implementation).

**Signature:**
```python
def encrypt_data(
    self,
    data: str,
    key: str
) -> str
```

**Parameters:**
- `data` (str): Plain text data to encrypt
- `key` (str): Encryption key

**Returns:**
- `str`: Base64-encoded encrypted data

**Algorithm:**
1. Convert data to bytes
2. XOR each byte with corresponding key byte (cycling)
3. Base64 encode result

**Fallback:**
- On encoding errors, uses simple base64 encoding with key prefix

**WARNING:** This is a demonstration implementation NOT suitable for production use. Use AWS KMS for production encryption.

**Example:**
```python
crypto = SecurityCrypto()

# Encrypt data
plaintext = "secret_message"
key = "my-encryption-key"
encrypted = crypto.encrypt_data(plaintext, key)

print(f"Encrypted: {encrypted}")
# Output: Base64-encoded ciphertext
```

---

### decrypt_data()

Decrypt data using XOR cipher (demonstration implementation).

**Signature:**
```python
def decrypt_data(
    self,
    encrypted_data: str,
    key: str
) -> str
```

**Parameters:**
- `encrypted_data` (str): Base64-encoded encrypted data
- `key` (str): Decryption key (must match encryption key)

**Returns:**
- `str`: Decrypted plaintext data
- Empty string on decryption failure

**Algorithm:**
1. Base64 decode encrypted data
2. XOR each byte with corresponding key byte (cycling)
3. Convert bytes to string

**Fallback:**
- On decoding errors, attempts simple base64 decode with key prefix
- Returns empty string if all decoding attempts fail

**Example:**
```python
crypto = SecurityCrypto()

# Decrypt data
encrypted = "base64_encrypted_data..."
key = "my-encryption-key"
decrypted = crypto.decrypt_data(encrypted, key)

print(f"Decrypted: {decrypted}")
# Output: "secret_message"
```

---

### hash_data()

Hash data using SHA-256.

**Signature:**
```python
def hash_data(
    self,
    data: str
) -> str
```

**Parameters:**
- `data` (str): Data to hash

**Returns:**
- `str`: SHA-256 hash (64-character hexadecimal string)

**Properties:**
- Deterministic: Same input always produces same hash
- One-way: Cannot reverse hash to get original data
- Fixed length: Always 64 hex characters (256 bits)

**Example:**
```python
crypto = SecurityCrypto()

# Hash password
password = "user_password_123"
hashed = crypto.hash_data(password)

print(f"Hash: {hashed}")
# Output: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

# Same input = same hash
hash2 = crypto.hash_data("user_password_123")
assert hashed == hash2  # True
```

---

### verify_hash()

Verify data against hash using constant-time comparison.

**Signature:**
```python
def verify_hash(
    self,
    data: str,
    hash_value: str
) -> bool
```

**Parameters:**
- `data` (str): Original data
- `hash_value` (str): Hash to verify against

**Returns:**
- `bool`: True if hash matches, False otherwise

**Security:**
- Uses `hmac.compare_digest()` for constant-time comparison
- Prevents timing attacks
- Safe for password verification

**Algorithm:**
1. Compute hash of provided data
2. Compare with provided hash using constant-time comparison
3. Return True if match, False otherwise

**Example:**
```python
crypto = SecurityCrypto()

# Store password hash
password = "user_password_123"
stored_hash = crypto.hash_data(password)

# Verify password later
input_password = "user_password_123"
if crypto.verify_hash(input_password, stored_hash):
    print("Password correct!")
else:
    print("Password incorrect")

# Wrong password
wrong_password = "wrong_password"
if not crypto.verify_hash(wrong_password, stored_hash):
    print("Password incorrect")
```

---

### generate_correlation_id()

Generate unique correlation ID using UUID4.

**Signature:**
```python
def generate_correlation_id(self) -> str
```

**Returns:**
- `str`: UUID4 correlation ID (36 characters)

**Format:** `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`

**Properties:**
- Universally unique (collision probability ~0)
- Random (not sequential)
- 128-bit identifier

**Example:**
```python
crypto = SecurityCrypto()

# Generate correlation IDs
id1 = crypto.generate_correlation_id()
id2 = crypto.generate_correlation_id()
id3 = crypto.generate_correlation_id()

print(f"ID 1: {id1}")  # 550e8400-e29b-41d4-a716-446655440000
print(f"ID 2: {id2}")  # 6ba7b810-9dad-11d1-80b4-00c04fd430c8
print(f"ID 3: {id3}")  # 6ba7b811-9dad-11d1-80b4-00c04fd430c8

# All unique
assert id1 != id2 != id3
```

---

### get_stats()

Get cryptographic operation statistics.

**Signature:**
```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Statistics dictionary (copy)

**Statistics:**
- `encryptions`: Total encryption operations
- `decryptions`: Total decryption operations
- `hashes`: Total hash operations
- `correlation_ids_generated`: Total correlation IDs generated

**Example:**
```python
crypto = SecurityCrypto()

# Perform operations
crypto.encrypt_data("data1", "key")
crypto.encrypt_data("data2", "key")
crypto.hash_data("password")
crypto.generate_correlation_id()
crypto.generate_correlation_id()

# Get statistics
stats = crypto.get_stats()

print(f"Encryptions: {stats['encryptions']}")  # 2
print(f"Hashes: {stats['hashes']}")  # 1
print(f"Correlation IDs: {stats['correlation_ids_generated']}")  # 2
```

---

## USAGE PATTERNS

### Pattern 1: Password Storage

```python
from security.security_crypto import SecurityCrypto

crypto = SecurityCrypto()

# Registration - store hash
password = input("Enter password: ")
password_hash = crypto.hash_data(password)
# Store password_hash in database

# Login - verify password
input_password = input("Enter password: ")
if crypto.verify_hash(input_password, password_hash):
    print("Login successful!")
else:
    print("Invalid password")
```

---

### Pattern 2: Data Encryption (Demo)

```python
from security.security_crypto import SecurityCrypto

crypto = SecurityCrypto()

# Encrypt sensitive data
api_key = "sk-abc123def456"
encryption_key = "my-secure-key-2025"

encrypted_key = crypto.encrypt_data(api_key, encryption_key)
# Store encrypted_key in database

# Decrypt when needed
decrypted_key = crypto.decrypt_data(encrypted_key, encryption_key)
# Use decrypted_key for API calls
```

---

### Pattern 3: Request Tracing

```python
from security.security_crypto import SecurityCrypto

crypto = SecurityCrypto()

def lambda_handler(event, context):
    # Generate correlation ID for request tracking
    correlation_id = crypto.generate_correlation_id()
    
    # Use throughout request processing
    logger.info("Processing request", extra={'correlation_id': correlation_id})
    
    # Include in response
    return {
        'statusCode': 200,
        'headers': {
            'X-Correlation-ID': correlation_id
        },
        'body': json.dumps({'result': 'success'})
    }
```

---

### Pattern 4: Data Integrity

```python
from security.security_crypto import SecurityCrypto

crypto = SecurityCrypto()

# Compute checksum before sending
data = "important_data"
checksum = crypto.hash_data(data)

# Send both data and checksum
send_to_remote(data, checksum)

# Verify on receive
received_data, received_checksum = receive_from_remote()
if crypto.verify_hash(received_data, received_checksum):
    print("Data integrity verified")
else:
    print("Data corrupted!")
```

---

## PRODUCTION ENCRYPTION GUIDANCE

**Current Implementation:**
- XOR cipher (demonstration only)
- NOT cryptographically secure
- Suitable for learning/testing only

**Production Recommendations:**

**For AWS Lambda:**
```python
import boto3
from base64 import b64encode, b64decode

kms = boto3.client('kms')

def encrypt_with_kms(plaintext: str, key_id: str) -> str:
    """Encrypt using AWS KMS."""
    response = kms.encrypt(
        KeyId=key_id,
        Plaintext=plaintext.encode('utf-8')
    )
    return b64encode(response['CiphertextBlob']).decode('utf-8')

def decrypt_with_kms(ciphertext: str) -> str:
    """Decrypt using AWS KMS."""
    response = kms.decrypt(
        CiphertextBlob=b64decode(ciphertext)
    )
    return response['Plaintext'].decode('utf-8')
```

**Security Best Practices:**
1. Use AWS KMS for production encryption
2. Rotate encryption keys regularly
3. Never hardcode encryption keys in code
4. Use environment variables or AWS Secrets Manager
5. Implement proper key access controls (IAM)

---

## STATISTICS TRACKING

**Purpose:**
- Monitor cryptographic operations
- Identify performance bottlenecks
- Track usage patterns
- Debug issues

**Statistics Reset:**
- Statistics persist for container lifetime
- Reset when container is recycled
- Not shared across containers

**Example Monitoring:**
```python
crypto = SecurityCrypto()

# Periodic statistics check
stats = crypto.get_stats()

if stats['encryptions'] > 1000:
    logger.warning("High encryption usage", extra=stats)

if stats['hashes'] > 10000:
    logger.info("High hash operation count", extra=stats)
```

---

## EXPORTS

```python
__all__ = [
    'SecurityCrypto'
]
```

---

## RELATED DOCUMENTATION

- **security_manager.md**: Security manager integration
- **security_core.md**: Gateway implementation functions
- **security_validation.md**: Validation functions

---

**END OF DOCUMENTATION**

**Module:** security/security_crypto.py  
**Classes:** 1 (SecurityCrypto)  
**Methods:** 6  
**Note:** Demo encryption - Use AWS KMS for production
