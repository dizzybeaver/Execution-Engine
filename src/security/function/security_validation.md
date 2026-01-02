# security_validation.md

**Version:** 2025-12-13_1  
**Purpose:** Security validation functions  
**Module:** security/security_validation.py  
**Type:** Validation Class and Metric Validators

---

## OVERVIEW

Provides comprehensive security validation functions including request validation, token validation, string validation, and specialized metric validators.

**Contents:**
- SecurityValidator class (core validations)
- Metric security validators (3 functions)

---

## CLASSES

### SecurityValidator

Core security validator for requests, tokens, strings, emails, URLs.

**Initialization:**
```python
def __init__(self):
    self._stats = {
        'validations_performed': 0,
        'validations_passed': 0,
        'validations_failed': 0
    }
```

**State:**
- `_stats`: Validation operation counters

---

## METHODS

### validate_request()

Validate HTTP request structure and content.

**Signature:**
```python
def validate_request(
    self,
    request: Dict[str, Any]
) -> bool
```

**Parameters:**
- `request` (Dict[str, Any]): HTTP request dictionary

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Checks:**
1. Request must be dictionary
2. `method` must be string (if present)
3. `headers` must be dictionary (if present)

**Example:**
```python
from security.security_validation import SecurityValidator

validator = SecurityValidator()

# Valid request
request = {
    'method': 'POST',
    'headers': {'Content-Type': 'application/json'},
    'body': '{"key": "value"}'
}
assert validator.validate_request(request)

# Invalid request - method not string
invalid_request = {
    'method': 123,
    'headers': {}
}
assert not validator.validate_request(invalid_request)
```

---

### validate_token()

Validate authentication token format.

**Signature:**
```python
def validate_token(
    self,
    token: str
) -> bool
```

**Parameters:**
- `token` (str): Authentication token

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Checks:**
1. Token must be string
2. Token must not be empty or whitespace
3. Token must be at least 10 characters

**Example:**
```python
validator = SecurityValidator()

# Valid token
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
assert validator.validate_token(token)

# Invalid - too short
short_token = "abc123"
assert not validator.validate_token(short_token)

# Invalid - empty
assert not validator.validate_token("")
```

---

### validate_string()

Validate string length and content.

**Signature:**
```python
def validate_string(
    self,
    value: str,
    min_length: int = 0,
    max_length: int = 1000
) -> bool
```

**Parameters:**
- `value` (str): String to validate
- `min_length` (int): Minimum allowed length (default: 0)
- `max_length` (int): Maximum allowed length (default: 1000)

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Checks:**
1. Value must be string
2. Length >= min_length
3. Length <= max_length

**Example:**
```python
validator = SecurityValidator()

# Valid strings
assert validator.validate_string("hello", min_length=1, max_length=10)
assert validator.validate_string("test", min_length=0, max_length=1000)

# Invalid - too short
assert not validator.validate_string("hi", min_length=5)

# Invalid - too long
long_string = "a" * 1001
assert not validator.validate_string(long_string, max_length=1000)
```

---

### validate_email()

Validate email address format.

**Signature:**
```python
def validate_email(
    self,
    email: str
) -> bool
```

**Parameters:**
- `email` (str): Email address to validate

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Pattern:**
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Example:**
```python
validator = SecurityValidator()

# Valid emails
assert validator.validate_email("user@example.com")
assert validator.validate_email("john.doe+tag@company.co.uk")
assert validator.validate_email("info_2025@my-domain.org")

# Invalid emails
assert not validator.validate_email("user@invalid")  # no TLD
assert not validator.validate_email("@example.com")  # no local part
assert not validator.validate_email("user@")  # no domain
```

---

### validate_url()

Validate URL format.

**Signature:**
```python
def validate_url(
    self,
    url: str
) -> bool
```

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `bool`: True if valid, False otherwise

**Validation:**
- Must start with `http://` or `https://`

**Example:**
```python
validator = SecurityValidator()

# Valid URLs
assert validator.validate_url("http://example.com")
assert validator.validate_url("https://api.example.com/endpoint")
assert validator.validate_url("https://example.com:8080/path?query=value")

# Invalid URLs
assert not validator.validate_url("ftp://example.com")  # not HTTP/HTTPS
assert not validator.validate_url("example.com")  # no protocol
```

---

### sanitize_input()

Sanitize input data for safe processing.

**Signature:**
```python
def sanitize_input(
    self,
    data: Any
) -> Any
```

**Parameters:**
- `data` (Any): Data to sanitize

**Returns:**
- `Any`: Sanitized data (same type as input)

**Sanitization:**
- **Strings:** Removes control characters (keeps \n, \r, \t)
- **Dicts:** Recursively sanitizes all values
- **Lists:** Recursively sanitizes all items
- **Others:** Returns unchanged

**Example:**
```python
validator = SecurityValidator()

# Sanitize string
dirty = "Hello\x00World\x1F!"
clean = validator.sanitize_input(dirty)
assert clean == "HelloWorld!"

# Sanitize nested structure
dirty_data = {
    'name': 'John\x00Doe',
    'items': ['Item\x1F1', 'Item\x1F2'],
    'count': 5
}
clean_data = validator.sanitize_input(dirty_data)
assert clean_data['name'] == "JohnDoe"
assert clean_data['items'] == ['Item1', 'Item2']
assert clean_data['count'] == 5
```

---

### get_stats()

Get validation statistics.

**Signature:**
```python
def get_stats(self) -> Dict[str, int]
```

**Returns:**
- `Dict[str, int]`: Statistics dictionary (copy)

**Statistics:**
- `validations_performed`: Total validations
- `validations_passed`: Successful validations
- `validations_failed`: Failed validations

**Example:**
```python
validator = SecurityValidator()

# Perform validations
validator.validate_email("user@example.com")  # pass
validator.validate_email("invalid")  # fail
validator.validate_url("https://example.com")  # pass

# Get statistics
stats = validator.get_stats()
assert stats['validations_performed'] == 3
assert stats['validations_passed'] == 2
assert stats['validations_failed'] == 1
```

---

## METRIC VALIDATORS

### validate_metric_name()

Validate metric name for security and sanity.

**Signature:**
```python
def validate_metric_name(name: str) -> None
```

**Parameters:**
- `name` (str): Metric name to validate

**Raises:**
- `ValueError`: If name is invalid with specific reason

**Validation Rules:**
1. Length: 1-200 characters
2. Characters: [a-zA-Z0-9_.-] only
3. No path separators (/, \)
4. No control characters
5. No leading/trailing whitespace
6. Cannot start/end with . or -

**Security Protection:**
- Prevents path traversal attacks
- Prevents memory exhaustion (200 char limit)
- Prevents control character injection

**Example:**
```python
from security.security_validation import validate_metric_name

# Valid names
validate_metric_name("cache_hit_rate")
validate_metric_name("http.requests.total")
validate_metric_name("lambda-invocations")

# Invalid - path separator
try:
    validate_metric_name("metrics/cache/hits")
except ValueError as e:
    print(f"Error: {e}")  # "cannot contain path separators"

# Invalid - too long
try:
    validate_metric_name("x" * 201)
except ValueError as e:
    print(f"Error: {e}")  # "too long: 201 characters (max: 200)"
```

---

### validate_dimension_value()

Validate metric dimension value for security.

**Signature:**
```python
def validate_dimension_value(value: str) -> None
```

**Parameters:**
- `value` (str): Dimension value to validate (auto-converted to string)

**Raises:**
- `ValueError`: If value is invalid with specific reason

**Validation Rules:**
1. Length: 1-100 characters
2. No control characters
3. No path separators
4. Must be printable

**Security Protection:**
- Prevents memory exhaustion (100 char limit)
- Prevents control character injection
- Prevents path traversal attacks

**Example:**
```python
from security.security_validation import validate_dimension_value

# Valid values
validate_dimension_value("production")
validate_dimension_value("us-east-1")
validate_dimension_value("lambda-function-v2")

# Invalid - path separator
try:
    validate_dimension_value("env/production")
except ValueError as e:
    print(f"Error: {e}")  # "cannot contain path separators"

# Invalid - control character
try:
    validate_dimension_value("value\x00with\x00nulls")
except ValueError as e:
    print(f"Error: {e}")  # "contains non-printable characters"
```

---

### validate_metric_value()

Validate metric numeric value is valid.

**Signature:**
```python
def validate_metric_value(
    value: float,
    allow_negative: bool = True
) -> None
```

**Parameters:**
- `value` (float): Numeric value to validate
- `allow_negative` (bool): Whether negative values are allowed (default: True)

**Raises:**
- `ValueError`: If value is invalid with specific reason

**Validation:**
- Rejects NaN (Not a Number)
- Rejects Infinity (positive or negative)
- Optionally rejects negative values

**Security Protection:**
- Prevents calculation errors from NaN propagation
- Prevents overflow from infinity values
- Validates domain-specific constraints (non-negative)

**Example:**
```python
from security.security_validation import validate_metric_value

# Valid values
validate_metric_value(42.5)
validate_metric_value(-10.0, allow_negative=True)
validate_metric_value(0.0)

# Invalid - NaN
try:
    validate_metric_value(float('nan'))
except ValueError as e:
    print(f"Error: {e}")  # "cannot be NaN"

# Invalid - Infinity
try:
    validate_metric_value(float('inf'))
except ValueError as e:
    print(f"Error: {e}")  # "cannot be infinity"

# Invalid - negative when not allowed
try:
    validate_metric_value(-5.0, allow_negative=False)
except ValueError as e:
    print(f"Error: {e}")  # "cannot be negative"
```

---

## USAGE PATTERNS

### Pattern 1: Input Validation Pipeline

```python
from security.security_validation import SecurityValidator

validator = SecurityValidator()

def process_user_input(user_input: dict) -> dict:
    """Process and validate user input."""
    # Validate request structure
    if not validator.validate_request(user_input):
        raise ValueError("Invalid request structure")
    
    # Sanitize all input data
    sanitized = validator.sanitize_input(user_input)
    
    # Validate specific fields
    if 'email' in sanitized:
        if not validator.validate_email(sanitized['email']):
            raise ValueError("Invalid email address")
    
    if 'token' in sanitized:
        if not validator.validate_token(sanitized['token']):
            raise ValueError("Invalid authentication token")
    
    return sanitized
```

---

### Pattern 2: Metric Recording with Validation

```python
from security.security_validation import (
    validate_metric_name,
    validate_dimension_value,
    validate_metric_value
)

def record_metric(name: str, value: float, dimensions: dict):
    """Record metric with full validation."""
    # Validate metric name
    validate_metric_name(name)
    
    # Validate metric value
    validate_metric_value(value)
    
    # Validate all dimension values
    for dim_key, dim_value in dimensions.items():
        validate_metric_name(dim_key)  # dimension keys use same rules
        validate_dimension_value(str(dim_value))
    
    # Safe to record metric
    metrics_client.put_metric(name, value, dimensions)
```

---

### Pattern 3: Statistics Monitoring

```python
from security.security_validation import SecurityValidator

validator = SecurityValidator()

# Perform validations
for request in requests:
    validator.validate_request(request)

# Monitor validation health
stats = validator.get_stats()
success_rate = stats['validations_passed'] / stats['validations_performed']

if success_rate < 0.95:
    logger.warning(
        "High validation failure rate",
        extra={
            'success_rate': success_rate,
            'total': stats['validations_performed'],
            'failed': stats['validations_failed']
        }
    )
```

---

### Pattern 4: Multi-Field Validation

```python
from security.security_validation import SecurityValidator

validator = SecurityValidator()

def validate_user_registration(data: dict) -> list:
    """Validate user registration data, return list of errors."""
    errors = []
    
    # Validate email
    email = data.get('email', '')
    if not validator.validate_email(email):
        errors.append("Invalid email address")
    
    # Validate username
    username = data.get('username', '')
    if not validator.validate_string(username, min_length=3, max_length=20):
        errors.append("Username must be 3-20 characters")
    
    # Validate password
    password = data.get('password', '')
    if not validator.validate_string(password, min_length=8):
        errors.append("Password must be at least 8 characters")
    
    return errors

# Usage
data = {'email': 'user@example.com', 'username': 'ab', 'password': 'pass123'}
errors = validate_user_registration(data)
if errors:
    print("Validation errors:", errors)
    # Output: ['Username must be 3-20 characters']
```

---

## EXPORTS

```python
__all__ = [
    'SecurityValidator',
    'validate_metric_name',
    'validate_dimension_value',
    'validate_metric_value',
]
```

---

## RELATED DOCUMENTATION

- **security_core.md**: Gateway implementation functions
- **security_manager.md**: Validation orchestration
- **security_types.md**: Validation patterns

---

**END OF DOCUMENTATION**

**Module:** security/security_validation.py  
**Classes:** 1 (SecurityValidator)  
**Functions:** 3 (metric validators)  
**Methods:** 7
