# logging_manager.py

**Version:** 2025-12-08_1  
**Module:** LOGGING Interface  
**Layer:** Core  
**Lines:** 281

---

## Purpose

Core logging manager class with singleton pattern, rate limiting, template optimization, and error tracking. Provides LoggingCore class and singleton factory function.

---

## Classes

### RateLimitTracker

**Purpose:** Track log count per Lambda invocation for rate limiting

**Attributes:**
```python
invocation_id: Optional[str]  # Current Lambda invocation ID
log_count: int                # Number of logs in current invocation
limit_warning_shown: bool     # Whether limit warning was already shown
```

**Methods:**

#### \_\_init\_\_()

**Signature:**
```python
def __init__(self)
```

**Behavior:** Initialize tracker with None invocation_id and zero counts

---

#### reset_for_invocation()

**Signature:**
```python
def reset_for_invocation(self, invocation_id: str)
```

**Parameters:**
- `invocation_id` - Lambda invocation ID

**Behavior:**
1. Set new invocation_id
2. Reset log_count to 0
3. Reset limit_warning_shown to False

**Usage:**
```python
_RATE_LIMITER.reset_for_invocation("req_12345")
```

---

#### reset()

**Signature:**
```python
def reset(self)
```

**Behavior:**
1. Clear invocation_id (set to None)
2. Reset log_count to 0
3. Reset limit_warning_shown to False

**Usage:** For testing/debugging

---

#### increment()

**Signature:**
```python
def increment(self) -> bool
```

**Returns:** 
- `True` if log should proceed
- `False` if rate limit exceeded

**Behavior:**
1. Increment log_count
2. If `LOG_RATE_LIMIT_ENABLED=false` → return True
3. If log_count > `MAX_LOGS_PER_INVOCATION`:
   - Print warning (once per invocation)
   - Return False
4. Otherwise return True

**Configuration:**
- `LOG_RATE_LIMIT_ENABLED` - Enable/disable (default: true)
- `MAX_LOGS_PER_INVOCATION` - Max logs (default: 500)

**Usage:**
```python
if _RATE_LIMITER.increment():
    # Log the message
    logger.log(level, message)
else:
    # Silently suppress log
    pass
```

---

#### get_stats()

**Signature:**
```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    'invocation_id': str,           # Current invocation ID
    'log_count': int,               # Number of logs so far
    'limit': int,                   # MAX_LOGS_PER_INVOCATION
    'limit_exceeded': bool,         # Whether limit was exceeded
    'rate_limiting_enabled': bool   # LOG_RATE_LIMIT_ENABLED
}
```

**Usage:**
```python
stats = _RATE_LIMITER.get_stats()
print(f"Logged {stats['log_count']} / {stats['limit']}")
```

---

### LoggingCore

**Purpose:** Unified logging manager with template optimization and rate limiting

**Attributes:**
```python
logger: logging.Logger                      # Python logger instance
_templates: Dict[str, LogTemplate]          # Template cache
_template_hits: int                         # Template cache hits
_template_misses: int                       # Template cache misses
_error_log: deque                          # Error entry deque (maxlen=100)
_error_count_by_type: Dict[str, int]       # Error counts by type
```

**Methods:**

#### \_\_init\_\_()

**Signature:**
```python
def __init__(self)
```

**Behavior:**
1. Create logger named 'SUGA-ISP'
2. Initialize template cache (empty dict)
3. Initialize template statistics (0 hits, 0 misses)
4. Create error log deque (maxlen=100)
5. Initialize error count dictionary

---

#### set_invocation_id()

**Signature:**
```python
def set_invocation_id(self, invocation_id: str)
```

**Parameters:**
- `invocation_id` - Lambda invocation ID

**Behavior:** Calls `_RATE_LIMITER.reset_for_invocation(invocation_id)`

**Usage:**
```python
core = get_logging_core()
core.set_invocation_id(context.aws_request_id)
```

---

#### reset()

**Signature:**
```python
def reset(self) -> bool
```

**Returns:** True on success

**Behavior:**
1. Clear template cache
2. Reset template statistics (hits=0, misses=0)
3. Clear error log deque
4. Clear error count dictionary
5. Reset rate limiter

**Usage:**
```python
core = get_logging_core()
success = core.reset()
```

**Purpose:** Phase 1 requirement - reset state for testing

---

#### log()

**Signature:**
```python
def log(self, message: str, level: int = logging.INFO, **kwargs) -> None
```

**Parameters:**
- `message` - Log message
- `level` - Python logging level (default: INFO)
- `**kwargs` - Extra context for logging

**Behavior:**
1. Check rate limiter (return if exceeded)
2. If `USE_LOG_TEMPLATES=true`:
   - Generate template key (first 100 chars)
   - Check if template cached:
     - Yes → Use cached template, increment hits
     - No → Cache new template, increment misses
3. Log message with Python logger

**Configuration:**
- `USE_LOG_TEMPLATES` - Enable template caching (default: false)

**Performance:**
- With templates: ~0.5ms (cache hit), ~1ms (cache miss)
- Without templates: ~0.5ms

**Usage:**
```python
core = get_logging_core()
core.log("User logged in", level=logging.INFO, user_id="user123")
```

---

#### log_error_with_tracking()

**Signature:**
```python
def log_error_with_tracking(
    self, 
    message: str, 
    error: Optional[str] = None,
    level: ErrorLogLevel = ErrorLogLevel.MEDIUM,
    **kwargs
) -> None
```

**Parameters:**
- `message` - Error message
- `error` - Error details (optional)
- `level` - Error severity level (default: MEDIUM)
- `**kwargs` - Additional context (must include `error_type`)

**Behavior:**
1. Check rate limiter (return if exceeded)
2. Create ErrorEntry:
   - timestamp = now
   - error_type from kwargs (default: "UnknownError")
   - message from parameter
   - level from parameter
   - details from error parameter
3. Append entry to error log deque
4. Increment error count for error_type
5. Map ErrorLogLevel to Python logging level:
   - LOW → WARNING
   - MEDIUM → ERROR
   - HIGH → ERROR
   - CRITICAL → CRITICAL
6. Log with Python logger

**Usage:**
```python
core = get_logging_core()
core.log_error_with_tracking(
    "Database connection failed",
    error="Connection timeout after 30s",
    level=ErrorLogLevel.HIGH,
    error_type="ConnectionError",
    db_host="localhost"
)
```

**Error Log Storage:**
- Deque with maxlen=100 (oldest entries auto-removed)
- Each entry is ErrorEntry dataclass
- Accessible via `get_error_stats()`

---

#### get_template_stats()

**Signature:**
```python
def get_template_stats(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    'templates_cached': int,     # Number of templates in cache
    'template_hits': int,        # Cache hits
    'template_misses': int,      # Cache misses
    'hit_rate': float           # Hit rate percentage (0-100)
}
```

**Calculation:**
```python
hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0.0
```

**Usage:**
```python
core = get_logging_core()
stats = core.get_template_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2f}%")
```

---

#### get_error_stats()

**Signature:**
```python
def get_error_stats(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    'total_errors': int,                    # Total errors logged
    'errors_by_type': Dict[str, int],      # Count by error type
    'recent_errors': List[Dict[str, Any]]  # Last 10 errors
}
```

**Recent Errors Format:**
```python
{
    'timestamp': str,      # ISO format datetime
    'type': str,           # Error type
    'message': str,        # Error message
    'level': str          # Severity level value
}
```

**Usage:**
```python
core = get_logging_core()
stats = core.get_error_stats()
print(f"Total errors: {stats['total_errors']}")
for error_type, count in stats['errors_by_type'].items():
    print(f"  {error_type}: {count}")
```

---

#### get_rate_limit_stats()

**Signature:**
```python
def get_rate_limit_stats(self) -> Dict[str, Any]
```

**Returns:** Output from `_RATE_LIMITER.get_stats()`

**Usage:**
```python
core = get_logging_core()
stats = core.get_rate_limit_stats()
print(f"Logs: {stats['log_count']} / {stats['limit']}")
```

---

## Functions

### get_logging_core()

**Purpose:** Get logging core singleton (SINGLETON pattern)

**Signature:**
```python
def get_logging_core() -> LoggingCore
```

**Returns:** LoggingCore singleton instance

**Behavior:**
1. Try to get from gateway SINGLETON:
   ```python
   from gateway import singleton_get, singleton_register
   manager = singleton_get('logging_manager')
   ```
2. If None, create new LoggingCore instance
3. Register with gateway SINGLETON
4. Return instance
5. If gateway unavailable (ImportError):
   - Fall back to module-level singleton
   - Create if needed
   - Return instance

**Thread Safety:** Safe for Lambda (single-threaded)

**Usage:**
```python
from logging.logging_manager import get_logging_core

core = get_logging_core()
core.log("System initialized")
```

---

## Module-Level Variables

### _LOGGING_CORE

**Type:** `Optional[LoggingCore]`  
**Purpose:** Module-level singleton fallback  
**Initial Value:** None

**Usage:** Internal only - use `get_logging_core()` instead

---

### _RATE_LIMITER

**Type:** `RateLimitTracker`  
**Purpose:** Global rate limiter instance  
**Initial Value:** `RateLimitTracker()`

**Usage:** Shared across all LoggingCore instances

---

## Configuration

### Environment Variables

**Rate Limiting:**
```bash
LOG_RATE_LIMIT_ENABLED=true      # Enable rate limiting (default: true)
MAX_LOGS_PER_INVOCATION=500      # Max logs per invocation (default: 500)
```

**Template Optimization:**
```bash
USE_LOG_TEMPLATES=false          # Enable template caching (default: false)
```

**Log Level:**
```bash
LOG_LEVEL=INFO                   # Python logging level
                                 # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Logging Configuration

**Format:**
```
%(asctime)s [%(levelname)s] %(message)s
```

**Date Format:**
```
%Y-%m-%d %H:%M:%S
```

**Example Output:**
```
2025-12-08 10:30:45 [INFO] Operation started: user_authentication
2025-12-08 10:30:45 [ERROR] Database connection failed: Connection timeout
```

---

## Dependencies

**Internal:**
- `logging.logging_types` (LogTemplate, ErrorEntry, ErrorLogLevel)
- `gateway` (singleton_get, singleton_register) - lazy import, optional

**External:**
- `os` - Environment variable access
- `time` - Performance timing
- `logging` - Python logging framework
- `typing` - Type hints
- `collections.deque` - Error log storage
- `datetime` - Timestamp management

---

## Performance

**Memory Usage:**
- LoggingCore: ~8KB base
- Error log: ~2KB (100 entries × ~20 bytes)
- Template cache: ~4KB (varies)
- Total: ~14KB per instance

**Operation Timing:**
- log(): <1ms
- log_error_with_tracking(): <2ms
- get_*_stats(): <1ms
- reset(): <1ms

---

## Exports

```python
__all__ = [
    'LoggingCore',
    'get_logging_core',
    'RateLimitTracker'
]
```

---

## Related Files

**Core:**
- logging_types.py - Type definitions used by LoggingCore
- logging_core.py - Implementation functions that call get_logging_core()

**Interface:**
- interface_logging.py - Routes to logging_core implementations

---

## Changelog

### 2025-12-08_1
- Moved to logging/ subdirectory
- Updated imports for subdirectory structure
- Integrated hierarchical debug control (preparation)

### 2025-10-22_01
- Added reset() method for Phase 1 compliance
- SINGLETON pattern with gateway integration
- Rate limiting to prevent log flooding

### 2025-10-21_03
- Fixed ErrorEntry dataclass usage
- Enhanced error tracking with limits
