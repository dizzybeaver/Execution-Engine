# Common-Patterns.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Universal patterns applicable across projects  
**Location:** `/sima/context/shared/`  
**Note:** Examples primarily in Python syntax

---

## IMPORT PATTERNS

### Lazy Import Pattern

**When:** Heavy libraries, cold start optimization

**Pattern:**
```python
def function_using_heavy_lib():
    """Function that needs heavy library."""
    import heavy_library  # Lazy load
    return heavy_library.process()
```

**Benefits:**
- Reduces initialization time
- Loads only when needed
- Breaks circular dependencies

**Avoid:** Module-level imports for heavy libraries

---

### Conditional Import Pattern

**When:** Optional dependencies, platform-specific code

**Pattern:**
```python
try:
    import optional_library
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False

def feature_function():
    """Feature requiring optional library."""
    if not HAS_OPTIONAL:
        raise RuntimeError("Optional library not available")
    return optional_library.process()
```

---

## ERROR HANDLING PATTERNS

### Specific Exception Pattern

**Always use specific exceptions:**

```python
# âŒ WRONG: Bare except
try:
    result = risky_operation()
except:
    log_error("Failed")

# âœ… CORRECT: Specific exception
try:
    result = risky_operation()
except ValueError as e:
    log_error(f"Invalid value: {e}")
    raise
except KeyError as e:
    log_error(f"Missing key: {e}")
    raise
```

---

### Graceful Degradation Pattern

**When:** Non-critical failures

**Pattern:**
```python
def get_with_fallback(key, default=None):
    """Get value with fallback on failure."""
    try:
        return get_from_source(key)
    except SourceUnavailableError:
        log_warning(f"Source unavailable, using default")
        return default
```

---

### Retry Pattern

**When:** Transient failures

**Pattern:**
```python
def retry_operation(max_attempts=3, delay=1.0):
    """Retry operation with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return perform_operation()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay * (2 ** attempt))
```

---

## LOGGING PATTERNS

### Structured Logging Pattern

**Pattern:**
```python
def process_request(request_id, user_id):
    """Process request with structured logging."""
    log_info(
        "Processing request",
        request_id=request_id,
        user_id=user_id
    )
    
    try:
        result = process(request_id)
        log_info(
            "Request completed",
            request_id=request_id,
            result_size=len(result)
        )
        return result
    except ProcessError as e:
        log_error(
            "Request failed",
            request_id=request_id,
            error=str(e)
        )
        raise
```

---

### Performance Logging Pattern

**Pattern:**
```python
import time

def timed_operation(name):
    """Execute operation with timing."""
    start = time.time()
    try:
        result = perform_operation()
        duration = time.time() - start
        log_info(f"{name} completed", duration_ms=duration*1000)
        return result
    except Exception as e:
        duration = time.time() - start
        log_error(f"{name} failed", duration_ms=duration*1000, error=str(e))
        raise
```

---

## VALIDATION PATTERNS

### Input Validation Pattern

**Pattern:**
```python
def validate_input(data):
    """Validate input data structure."""
    if not isinstance(data, dict):
        raise TypeError("Data must be dict")
    
    required = ['id', 'type', 'value']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    
    if not isinstance(data['id'], str):
        raise TypeError("ID must be string")
    
    return True
```

---

### Sanitization Pattern

**Pattern:**
```python
def sanitize_output(data):
    """Remove internal implementation details."""
    if isinstance(data, dict):
        return {
            k: sanitize_output(v)
            for k, v in data.items()
            if not k.startswith('_')  # Remove private fields
        }
    elif isinstance(data, list):
        return [sanitize_output(item) for item in data]
    else:
        # Check for sentinel objects
        if hasattr(data, '__sentinel__'):
            return None
        return data
```

---

## CACHING PATTERNS

### Simple Cache Pattern

**Pattern:**
```python
_cache = {}

def get_cached(key):
    """Get value from cache."""
    if key in _cache:
        return _cache[key]
    
    value = expensive_operation(key)
    _cache[key] = value
    return value
```

---

### TTL Cache Pattern

**Pattern:**
```python
import time

_cache = {}
_expiry = {}
TTL = 300  # 5 minutes

def get_cached_ttl(key):
    """Get value from cache with TTL."""
    now = time.time()
    
    if key in _cache and _expiry.get(key, 0) > now:
        return _cache[key]
    
    value = expensive_operation(key)
    _cache[key] = value
    _expiry[key] = now + TTL
    return value
```

---

## CONFIGURATION PATTERNS

### Environment-Based Config

**Pattern:**
```python
import os

def get_config(key, default=None):
    """Get configuration value."""
    # Try environment variable
    env_value = os.environ.get(key.upper())
    if env_value is not None:
        return env_value
    
    # Try config file
    file_value = load_from_config_file(key)
    if file_value is not None:
        return file_value
    
    # Fall back to default
    return default
```

---

### Type-Safe Config Pattern

**Pattern:**
```python
def get_config_typed(key, expected_type, default=None):
    """Get configuration with type validation."""
    value = get_config(key)
    
    if value is None:
        return default
    
    if expected_type == bool:
        return value.lower() in ('true', '1', 'yes')
    elif expected_type == int:
        return int(value)
    elif expected_type == float:
        return float(value)
    else:
        return str(value)
```

---

## APPLICABILITY

**These patterns apply to:**
- âœ… All programming languages (concepts)
- âœ… Error handling (universal)
- âœ… Logging strategies (universal)
- âœ… Validation approaches (universal)
- âœ… Caching strategies (universal)

**Examples shown in:** Python syntax

**For language-specific variations:** See `/sima/languages/[language]/`

---

## RELATED STANDARDS

**Architecture:** (See project-specific patterns)  
**Artifacts:** Artifact-Standards.md  
**RED FLAGS:** RED-FLAGS.md  
**File Standards:** SPEC-FILE-STANDARDS.md

**Location:** `/sima/context/shared/`

---

**END OF FILE**

**Summary:** Lazy imports, specific exceptions, structured logging, input validation, TTL caching, type-safe config - universal patterns shown with Python examples.