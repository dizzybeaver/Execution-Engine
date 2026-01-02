# security/ Directory

**Version:** 2025-12-13_1  
**Purpose:** Security validation, encryption, and CVE fixes with hierarchical debug support  
**Module:** Security (SECURITY interface)

---

## Files

### __init__.py (73 lines)
Module initialization - exports all public security functions

**Exports:**
- SecurityOperation, ValidationPattern (from security_types)
- SecurityCore, Validators, get_security_manager (from security_manager)
- SecurityValidator, metric validators (from security_validation)
- SecurityCrypto (from security_crypto)
- Implementation functions (from security_core)

---

### security_types.py (51 lines)
Security type definitions and enums

**Classes:**
- SecurityOperation - Enum of all security operations
- ValidationPattern - Enum of validation regex patterns

**Operations:**
- VALIDATE_REQUEST, VALIDATE_TOKEN, VALIDATE_STRING
- VALIDATE_EMAIL, VALIDATE_URL
- ENCRYPT, DECRYPT, HASH, VERIFY_HASH
- SANITIZE, GENERATE_CORRELATION_ID
- VALIDATE_CACHE_KEY (CVE-SUGA-2025-001)
- VALIDATE_TTL (CVE-SUGA-2025-002)
- VALIDATE_MODULE_NAME (CVE-SUGA-2025-004)
- VALIDATE_NUMBER_RANGE

---

### security_manager.py (299 lines)
Security core manager with validators and rate limiting

**Classes:**
- CacheKeyValidator - Cache key validation (CVE-SUGA-2025-001)
- TTLValidator - TTL boundary protection (CVE-SUGA-2025-002)
- ModuleNameValidator - Module name validation (CVE-SUGA-2025-004)
- NumberRangeValidator - Generic number range validation
- SecurityCore - Core security manager

**Functions:**
- get_security_manager() - Singleton instance accessor

**Features:**
- Orchestrates validation and crypto operations
- Rate limiting (1000 ops/sec)
- SINGLETON pattern (LESS-18)
- Debug integration (SECURITY scope)
- Timing measurements for operations
- CVE fixes integrated
- Gateway SINGLETON registry integration

**Key Methods:**
- execute_security_operation() - Execute operation with rate limiting
- reset() - Reset manager state
- get_stats() - Get comprehensive statistics
- get_validator() - Get validator accessor
- get_crypto() - Get crypto accessor

**Validators:**
- CacheKeyValidator: 1-255 chars, [a-zA-Z0-9_-:.], no path traversal
- TTLValidator: 1-86400 seconds, no NaN/infinity
- ModuleNameValidator: Valid Python identifier, 1-100 chars
- NumberRangeValidator: Within min/max, no NaN/infinity

**Compliance:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

### security_validation.py (271 lines)
Security validation functions and metrics validators

**Classes:**
- SecurityValidator - Core validator for requests, tokens, strings

**Functions:**
- validate_metric_name() - Metric name security validation
- validate_dimension_value() - Dimension value security validation
- validate_metric_value() - Metric numeric value validation

**Validator Methods:**
- validate_request() - HTTP request structure validation
- validate_token() - Authentication token format validation
- validate_string() - String length and content validation
- validate_email() - Email address format validation
- validate_url() - URL format validation
- sanitize_input() - Sanitize data for safe processing
- get_stats() - Get validation statistics

**Metrics Validators:**
- validate_metric_name: 1-200 chars, [a-zA-Z0-9_.-], no path separators
- validate_dimension_value: 1-100 chars, printable, no path separators
- validate_metric_value: No NaN/infinity, optional negative check

---

### security_crypto.py (123 lines)
Cryptographic operations

**Classes:**
- SecurityCrypto - Handles all crypto operations

**Methods:**
- get_default_key() - Get default encryption key
- encrypt_data() - Encrypt using XOR cipher (demo only)
- decrypt_data() - Decrypt using XOR cipher (demo only)
- hash_data() - Hash using SHA-256
- verify_hash() - Verify hash using constant-time comparison
- generate_correlation_id() - Generate UUID4 correlation ID
- get_stats() - Get crypto statistics

**Note:**
XOR cipher implementation is for demonstration only. Production use should implement proper encryption using AWS KMS or similar.

---

### security_core.py (249 lines)
Gateway implementation functions for security interface

**Functions:**
- validate_request_implementation()
- validate_token_implementation()
- validate_string_implementation()
- validate_email_implementation()
- validate_url_implementation()
- encrypt_implementation()
- decrypt_implementation()
- hash_implementation()
- verify_hash_implementation()
- sanitize_implementation()
- generate_correlation_id_implementation()
- validate_cache_key_implementation()
- validate_ttl_implementation()
- validate_module_name_implementation()
- validate_number_range_implementation()
- security_reset_implementation()
- get_security_stats_implementation()

**Features:**
- Gateway-facing implementation layer
- Debug integration with correlation ID support
- SINGLETON manager usage
- Parameter validation
- Error handling and exception propagation

---

## Architecture

### SUGA Pattern Compliance
```
Gateway Layer (gateway/wrappers/gateway_wrappers_security.py)
    ↓
Interface Layer (interface/interface_security.py)
    ↓
Implementation Layer (security/security_core.py)
    ↓
Manager Layer (security/security_manager.py)
    ↓
Validators (security_validation.py, security_crypto.py)
```

### Import Patterns

**Public (from other modules):**
```python
import security

# Access public functions
security.validate_request_implementation(...)
security.encrypt_implementation(...)
```

**Private (within security module):**
```python
from security.security_manager import get_security_manager
from security.security_types import SecurityOperation
```

---

## Debug Integration

### Hierarchical Debug Control

**Master Switch:**
- DEBUG_MODE - Enables all debugging

**Scope Switches:**
- SECURITY_DEBUG_MODE - Security debug logging
- SECURITY_DEBUG_TIMING - Security timing measurements

**Debug Points:**
- Operation execution
- Rate limit enforcement
- Validation operations
- Encryption/decryption operations
- Hash operations
- Sanitization operations
- Statistics gathering
- Manager reset

### Debug Output Examples

```
[abc123] [SECURITY-DEBUG] Executing security operation (operation=validate_email)
[abc123] [SECURITY-TIMING] op:validate_email: 1.23ms
[abc123] [SECURITY-DEBUG] validate_email_implementation called (has_email=True)
[abc123] [SECURITY-DEBUG] Executing security operation (operation=encrypt)
[abc123] [SECURITY-TIMING] op:encrypt: 5.67ms
[abc123] [SECURITY-DEBUG] encrypt_implementation called (data_length=256, has_key=True)
[abc123] [SECURITY-DEBUG] Rate limit exceeded (rate_limited_count=15)
[abc123] [SECURITY-DEBUG] Getting statistics
[abc123] [SECURITY-DEBUG] Resetting security core state
[abc123] [SECURITY-DEBUG] Security core reset complete
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import validate_email, encrypt_data, hash_data, validate_cache_key

# Validate email
is_valid = validate_email('user@example.com')

# Encrypt data
encrypted = encrypt_data('sensitive data')

# Hash data
hash_val = hash_data('password')

# Validate cache key (CVE fix)
validate_cache_key('user:123')  # Raises ValueError if invalid
```

### Direct (Testing Only)
```python
import security

# Validate email
is_valid = security.validate_email_implementation(
    email='user@example.com'
)

# Encrypt
encrypted = security.encrypt_implementation(
    data='sensitive',
    key='my-key'
)
```

---

## CVE Fixes

### CVE-SUGA-2025-001: Cache Key Injection

**Vulnerability:**
Unvalidated cache keys could contain path traversal sequences or control characters.

**Fix:**
CacheKeyValidator enforces:
- Length: 1-255 characters
- Characters: [a-zA-Z0-9_-:.]
- Rejects: path traversal (../, ./, etc.)
- Rejects: control characters (0x00-0x1F, 0x7F)

**Usage:**
```python
from gateway import validate_cache_key

validate_cache_key('user:123')  # Valid
validate_cache_key('../etc/passwd')  # Raises ValueError
```

### CVE-SUGA-2025-002: TTL Boundary Exploitation

**Vulnerability:**
Unbounded TTL values could cause resource exhaustion or DoS attacks.

**Fix:**
TTLValidator enforces:
- Minimum: 1 second
- Maximum: 86400 seconds (24 hours)
- Rejects: NaN, infinity, negative values

**Usage:**
```python
from gateway import validate_ttl

validate_ttl(300)  # Valid (5 minutes)
validate_ttl(90000)  # Raises ValueError (> 24 hours)
```

### CVE-SUGA-2025-004: LUGS Dependency Poisoning

**Vulnerability:**
Unvalidated module names in LUGS tracking could be exploited for code injection.

**Fix:**
ModuleNameValidator enforces:
- Valid Python identifier pattern
- Length: 1-100 characters
- Rejects: path separators (/, \)
- Rejects: control characters

**Usage:**
```python
from gateway import validate_module_name

validate_module_name('my_module')  # Valid
validate_module_name('../evil')  # Raises ValueError
```

---

## Statistics

### Security Statistics
- validator_validations_performed - Total validations
- validator_validations_passed - Successful validations
- validator_validations_failed - Failed validations
- crypto_encryptions - Total encryptions
- crypto_decryptions - Total decryptions
- crypto_hashes - Total hashes
- crypto_correlation_ids_generated - Correlation IDs generated
- rate_limit.current_operations - Current operations in window
- rate_limit.rate_limit - Maximum operations per second
- rate_limit.rate_limited_count - Rate limit hits
- rate_limit.window_ms - Rate limit window in milliseconds

---

## Related Files

**Interface:**
- interface/interface_security.py - Interface router

**Gateway:**
- gateway/wrappers/gateway_wrappers_security.py - Gateway wrappers

**Debug:**
- debug/debug_config.py - Debug configuration
- debug/debug_core.py - Debug logging and timing

---

## File Size Summary

| File | Lines | Status |
|------|-------|--------|
| __init__.py | 73 | ✓ Well under limit |
| security_types.py | 51 | ✓ Well under limit |
| security_manager.py | 299 | ✓ Under 300 target |
| security_validation.py | 271 | ✓ Well under limit |
| security_crypto.py | 123 | ✓ Well under limit |
| security_core.py | 249 | ✓ Well under limit |
| **Total** | **1,066** | **6 files** |

---

## Changelog

### 2025-12-13_1
- Split monolithic security_core.py into modular structure
- Added hierarchical debug integration (SECURITY scope)
- Integrated debug_log() and debug_timing() throughout
- Added correlation ID support for debug tracking
- Created module __init__.py for clean imports
- Updated interface to use module import pattern
- All files under 300-line target (max 299 lines)
- Preserved all CVE fixes and validators
- Maintained rate limiting and SINGLETON pattern
- Kept security_types.py, security_validation.py, security_crypto.py as utility files
