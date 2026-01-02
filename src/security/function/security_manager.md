# security_manager.md

**Version:** 2025-12-13_1  
**Purpose:** Security core manager with validators and rate limiting  
**Module:** security/security_manager.py  
**Type:** Singleton Manager with CVE Mitigations

---

## OVERVIEW

Core security manager orchestrating validation and cryptographic operations with comprehensive CVE mitigations, rate limiting, and singleton pattern.

**Key Features:**
- Singleton instance per Lambda container
- Rate limiting (1000 ops/sec)
- CVE mitigations (001, 002, 004)
- Validation orchestration
- Cryptography integration
- Lambda-safe (no threading)

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SINGLETON: Single instance via get_security_manager()
- Rate Limiting: 1000 operations/second protection

**CVE Mitigations:**
- CVE-SUGA-2025-001: Cache key validation
- CVE-SUGA-2025-002: TTL boundary protection
- CVE-SUGA-2025-004: Module name validation

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting

---

## VALIDATOR CLASSES

### CacheKeyValidator

Comprehensive cache key validation (fixes CVE-SUGA-2025-001).

**Constants:**
```python
SAFE_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_\-:.]+$')
PATH_TRAVERSAL_PATTERNS = ['../', './', '..\\', '.\\', '/../', '/..']
CONTROL_CHARS = set(chr(i) for i in range(0x00, 0x20)) | {chr(0x7F)}
MIN_LENGTH = 1
MAX_LENGTH = 255
```

**Method: validate()**

```python
@classmethod
def validate(cls, key: str) -> tuple
```

**Parameters:**
- `key` (str): Cache key to validate

**Returns:**
- `tuple`: (is_valid, error_message)
  - `is_valid` (bool): True if valid, False otherwise
  - `error_message` (str): Error description (None if valid)

**Validation Rules:**
1. Must be string type
2. Length: 1-255 characters
3. No control characters (0x00-0x1F, 0x7F)
4. No path traversal patterns
5. Characters: [a-zA-Z0-9_-:.] only

**Example:**
```python
from security.security_manager import CacheKeyValidator

# Valid keys
is_valid, error = CacheKeyValidator.validate("user:123:profile")
assert is_valid and error is None

is_valid, error = CacheKeyValidator.validate("cache-key_2025.v1")
assert is_valid

# Invalid key - path traversal
is_valid, error = CacheKeyValidator.validate("user/../admin")
assert not is_valid
assert "path traversal" in error

# Invalid key - control character
is_valid, error = CacheKeyValidator.validate("user\x00admin")
assert not is_valid
assert "control character" in error
```

---

### TTLValidator

TTL validation with boundary protection (fixes CVE-SUGA-2025-002).

**Constants:**
```python
MIN_TTL = 1
MAX_TTL = 86400  # 24 hours
```

**Method: validate()**

```python
@classmethod
def validate(cls, ttl: float) -> tuple
```

**Parameters:**
- `ttl` (float): TTL value in seconds

**Returns:**
- `tuple`: (is_valid, error_message)

**Validation Rules:**
1. Must be numeric (int or float)
2. No NaN values
3. No Infinity values
4. Range: 1 to 86400 seconds

**Example:**
```python
from security.security_manager import TTLValidator

# Valid TTLs
is_valid, error = TTLValidator.validate(300)  # 5 minutes
assert is_valid

is_valid, error = TTLValidator.validate(3600)  # 1 hour
assert is_valid

# Invalid - infinity
is_valid, error = TTLValidator.validate(float('inf'))
assert not is_valid
assert "infinity" in error

# Invalid - too large
is_valid, error = TTLValidator.validate(100000)
assert not is_valid
assert "too large" in error
```

---

### ModuleNameValidator

Module name validation for LUGS (fixes CVE-SUGA-2025-004).

**Constants:**
```python
MODULE_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$')
MAX_LENGTH = 100
```

**Method: validate()**

```python
@classmethod
def validate(cls, module_name: str) -> tuple
```

**Parameters:**
- `module_name` (str): Module name to validate

**Returns:**
- `tuple`: (is_valid, error_message)

**Validation Rules:**
1. Must be string type
2. Cannot be empty
3. Max 100 characters
4. No path separators (/ or \)
5. No control characters
6. Must match Python identifier pattern

**Example:**
```python
from security.security_manager import ModuleNameValidator

# Valid module names
is_valid, error = ModuleNameValidator.validate("interface_cache")
assert is_valid

is_valid, error = ModuleNameValidator.validate("gateway.wrappers.cache")
assert is_valid

# Invalid - path separator
is_valid, error = ModuleNameValidator.validate("../../../etc/passwd")
assert not is_valid
assert "path separator" in error

# Invalid - not Python identifier
is_valid, error = ModuleNameValidator.validate("my-module")
assert not is_valid
assert "valid Python identifier" in error
```

---

### NumberRangeValidator

Generic number range validation.

**Method: validate()**

```python
@classmethod
def validate(
    cls,
    value: float,
    min_val: float,
    max_val: float,
    name: str = 'value'
) -> tuple
```

**Parameters:**
- `value` (float): Number to validate
- `min_val` (float): Minimum allowed value
- `max_val` (float): Maximum allowed value
- `name` (str): Parameter name for error messages

**Returns:**
- `tuple`: (is_valid, error_message)

**Validation Rules:**
1. Must be numeric (int or float)
2. No NaN values
3. No Infinity values
4. Must be within [min_val, max_val] range

**Example:**
```python
from security.security_manager import NumberRangeValidator

# Valid values
is_valid, error = NumberRangeValidator.validate(50, 0, 100, 'percentage')
assert is_valid

# Invalid - below minimum
is_valid, error = NumberRangeValidator.validate(-5, 0, 100, 'percentage')
assert not is_valid
assert "below minimum" in error

# Invalid - NaN
is_valid, error = NumberRangeValidator.validate(float('nan'), 0, 100, 'score')
assert not is_valid
assert "NaN" in error
```

---

## MAIN MANAGER CLASS

### SecurityCore

Core security manager orchestrating validation and crypto operations.

**Initialization:**
```python
def __init__(self):
    self._validator = SecurityValidator()
    self._crypto = SecurityCrypto()
    
    # Rate limiting (1000 ops/sec)
    self._rate_limiter = deque(maxlen=1000)
    self._rate_limit_window_ms = 1000
    self._rate_limited_count = 0
```

**State:**
- `_validator`: SecurityValidator instance
- `_crypto`: SecurityCrypto instance
- `_rate_limiter`: Deque tracking operation timestamps
- `_rate_limit_window_ms`: Rate limit window (1000ms)
- `_rate_limited_count`: Count of rate-limited operations

---

## METHODS

### _check_rate_limit()

**Private method** - Check rate limit (1000 ops/sec).

**Signature:**
```python
def _check_rate_limit(self) -> bool
```

**Returns:**
- `bool`: True if allowed, False if rate limited

**Algorithm:** Same as other manager rate limiters (sliding window with deque)

---

### reset()

Reset security core state.

**Signature:**
```python
def reset(
    self,
    correlation_id: str = None
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `bool`: True on success

**Behavior:**
- Clears rate limiter deque
- Resets rate limited count to 0
- Logs reset operation

---

### execute_security_operation()

Generic security operation executor with rate limiting.

**Signature:**
```python
def execute_security_operation(
    self,
    operation: SecurityOperation,
    correlation_id: str = None,
    *args,
    **kwargs
) -> Any
```

**Parameters:**
- `operation` (SecurityOperation): Security operation enum
- `correlation_id` (str): Optional correlation ID for debug tracking
- `*args`: Positional arguments for operation
- `**kwargs`: Keyword arguments for operation

**Returns:**
- `Any`: Operation result

**Raises:**
- `RuntimeError`: If rate limited
- `ValueError`: If operation unknown or parameters invalid
- `TypeError`: If parameter types incorrect

**Supported Operations:**
- VALIDATE_REQUEST
- VALIDATE_TOKEN
- VALIDATE_STRING
- VALIDATE_EMAIL
- VALIDATE_URL
- ENCRYPT
- DECRYPT
- HASH
- VERIFY_HASH
- SANITIZE
- GENERATE_CORRELATION_ID
- VALIDATE_CACHE_KEY
- VALIDATE_TTL
- VALIDATE_MODULE_NAME
- VALIDATE_NUMBER_RANGE

**Example:**
```python
from security.security_manager import get_security_manager, SecurityOperation

manager = get_security_manager()

# Execute validation
is_valid = manager.execute_security_operation(
    SecurityOperation.VALIDATE_EMAIL,
    None,  # correlation_id
    "user@example.com"
)

# Execute encryption
encrypted = manager.execute_security_operation(
    SecurityOperation.ENCRYPT,
    None,
    "secret_data",
    "encryption_key"
)
```

---

### get_stats()

Get combined security statistics with rate limiting metrics.

**Signature:**
```python
def get_stats(
    self,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Combined statistics dictionary

**Statistics Structure:**
```python
{
    'validator_validations_performed': 100,
    'validator_validations_passed': 95,
    'validator_validations_failed': 5,
    'crypto_encryptions': 10,
    'crypto_decryptions': 10,
    'crypto_hashes': 50,
    'crypto_correlation_ids_generated': 20,
    'rate_limit': {
        'current_operations': 45,
        'rate_limit': 1000,
        'rate_limited_count': 2,
        'window_ms': 1000
    }
}
```

---

### get_validator()

Public accessor for validator instance.

**Signature:**
```python
def get_validator(self) -> SecurityValidator
```

**Returns:**
- `SecurityValidator`: The validator instance

---

### get_crypto()

Public accessor for crypto instance.

**Signature:**
```python
def get_crypto(self) -> SecurityCrypto
```

**Returns:**
- `SecurityCrypto`: The crypto instance

---

## SINGLETON PATTERN

### get_security_manager()

Get security manager singleton.

**Function:** Module-level singleton factory

**Signature:**
```python
def get_security_manager() -> SecurityCore
```

**Returns:**
- `SecurityCore`: The singleton manager instance

**Implementation:**
```python
_MANAGER = None  # Module-level singleton

def get_security_manager() -> SecurityCore:
    global _MANAGER
    
    try:
        from gateway import singleton_get, singleton_register
        
        # Try gateway SINGLETON registry first
        manager = singleton_get('security_manager')
        if manager is None:
            if _MANAGER is None:
                _MANAGER = SecurityCore()
            singleton_register('security_manager', _MANAGER)
            manager = _MANAGER
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _MANAGER is None:
            _MANAGER = SecurityCore()
        return _MANAGER
```

**Usage:**
```python
# Always use this function to get manager
manager = get_security_manager()

# Never instantiate directly
# manager = SecurityCore()  # ❌ WRONG
```

---

## CVE MITIGATIONS

### CVE-SUGA-2025-001: Cache Key Validation

**Vulnerability:** Path traversal via malicious cache keys

**Mitigation:** CacheKeyValidator enforces strict character set

**Example Attack Prevented:**
```python
# Attacker attempts path traversal
malicious_key = "../../etc/passwd"

# Validation catches it
is_valid, error = CacheKeyValidator.validate(malicious_key)
# Returns: (False, "Cache key contains path traversal pattern: ../")
```

---

### CVE-SUGA-2025-002: TTL Boundary Protection

**Vulnerability:** Memory exhaustion via infinite TTL

**Mitigation:** TTLValidator enforces 1-86400 second range

**Example Attack Prevented:**
```python
# Attacker attempts infinite TTL
malicious_ttl = float('inf')

# Validation catches it
is_valid, error = TTLValidator.validate(malicious_ttl)
# Returns: (False, "TTL cannot be infinity")
```

---

### CVE-SUGA-2025-004: Module Name Validation

**Vulnerability:** Arbitrary code loading via malicious module names

**Mitigation:** ModuleNameValidator enforces Python identifier pattern

**Example Attack Prevented:**
```python
# Attacker attempts path traversal in module import
malicious_module = "../../../malicious_code"

# Validation catches it
is_valid, error = ModuleNameValidator.validate(malicious_module)
# Returns: (False, "Module name cannot contain path separators")
```

---

## USAGE PATTERNS

### Pattern 1: Validate Before Cache

```python
from security.security_manager import CacheKeyValidator, TTLValidator

def cache_set(key: str, value: Any, ttl: float):
    # Validate key
    is_valid, error = CacheKeyValidator.validate(key)
    if not is_valid:
        raise ValueError(f"Invalid cache key: {error}")
    
    # Validate TTL
    is_valid, error = TTLValidator.validate(ttl)
    if not is_valid:
        raise ValueError(f"Invalid TTL: {error}")
    
    # Proceed with caching
    _cache[key] = (value, time.time() + ttl)
```

---

### Pattern 2: Validate Module Import

```python
from security.security_manager import ModuleNameValidator

def safe_import_module(module_name: str):
    # Validate module name
    is_valid, error = ModuleNameValidator.validate(module_name)
    if not is_valid:
        raise ValueError(f"Invalid module name: {error}")
    
    # Safe to import
    import importlib
    return importlib.import_module(module_name)
```

---

### Pattern 3: Range Validation

```python
from security.security_manager import NumberRangeValidator

def set_timeout(timeout: float):
    # Validate timeout range
    is_valid, error = NumberRangeValidator.validate(
        timeout, 1.0, 60.0, 'timeout'
    )
    if not is_valid:
        raise ValueError(f"Invalid timeout: {error}")
    
    # Use validated timeout
    self._timeout = timeout
```

---

## EXPORTS

```python
__all__ = [
    'CacheKeyValidator',
    'TTLValidator',
    'ModuleNameValidator',
    'NumberRangeValidator',
    'SecurityCore',
    'get_security_manager',
]
```

---

## RELATED DOCUMENTATION

- **security_core.md**: Gateway implementation functions
- **security_crypto.md**: Cryptographic operations
- **security_validation.md**: Validation functions
- **security_types.md**: Type definitions

---

**END OF DOCUMENTATION**

**Module:** security/security_manager.py  
**Classes:** 5 (4 validators + SecurityCore)  
**Functions:** 1 (get_security_manager)  
**CVE Fixes:** 3 (001, 002, 004)
