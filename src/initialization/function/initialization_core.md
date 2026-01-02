# initialization_core.md

**Version:** 2025-12-13_1  
**Purpose:** Gateway implementation functions for initialization interface  
**Module:** initialization/initialization_core.py  
**Type:** Core Implementation Functions

---

## OVERVIEW

Provides gateway-accessible implementation functions for Lambda initialization operations. All functions delegate to the singleton InitializationManager and include comprehensive debug integration.

**Pattern:** Gateway → Interface → Core (SUGA)  
**Singleton:** All operations use get_initialization_manager()  
**Debug:** All functions integrate correlation_id tracking

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SUGA: Gateway implementation layer
- SINGLETON: Uses get_initialization_manager() (LESS-18)
- Debug Integration: All functions support correlation_id

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-21: Rate limiting (1000 ops/sec)

---

## FUNCTIONS

### execute_initialization_operation()

Universal initialization operation executor with error handling.

**Signature:**
```python
def execute_initialization_operation(
    operation: InitializationOperation,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `operation` (InitializationOperation): Operation enum value
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Operation-specific parameters

**Returns:**
- `Any`: Result from the specific operation

**Raises:**
- `ValueError`: If operation is unknown
- `Exception`: If operation execution fails

**Supported Operations:**
- `INITIALIZE`: Initialize Lambda environment
- `GET_CONFIG`: Get configuration
- `IS_INITIALIZED`: Check initialization status
- `RESET`: Reset initialization state
- `GET_STATUS`: Get comprehensive status
- `GET_STATS`: Get statistics
- `SET_FLAG`: Set initialization flag
- `GET_FLAG`: Get flag value

**Example:**
```python
from initialization.initialization_core import execute_initialization_operation
from initialization.initialization_manager import InitializationOperation

# Initialize
result = execute_initialization_operation(
    InitializationOperation.INITIALIZE,
    config={'debug_mode': True}
)

# Check status
is_ready = execute_initialization_operation(
    InitializationOperation.IS_INITIALIZED
)
```

---

### initialize_implementation()

Execute initialization operation.

**Signature:**
```python
def initialize_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Configuration parameters to store

**Returns:**
- `Dict[str, Any]`: Initialization status dictionary:
  - First call: `{'status': 'initialized', 'cached': False, ...}`
  - Subsequent calls: `{'status': 'already_initialized', 'cached': True, ...}`

**Response Fields:**
- `status`: 'initialized', 'already_initialized', or 'rate_limited'
- `cached`: Boolean indicating if result is cached
- `timestamp`: Unix timestamp of initialization
- `duration_ms`: Initialization duration (first call only)
- `init_duration_ms`: Original init duration (cached calls)
- `uptime_seconds`: Time since initialization
- `config_keys`: List of configuration keys

**Idempotency:**
- Multiple calls are safe
- First call initializes and returns fresh result
- Subsequent calls return cached result
- No re-initialization on subsequent calls

**Example:**
```python
from initialization.initialization_core import initialize_implementation

# First call - performs initialization
result = initialize_implementation(
    debug_mode=True,
    log_level='INFO',
    timeout=30
)

print(f"Status: {result['status']}")  # "initialized"
print(f"Cached: {result['cached']}")  # False
print(f"Duration: {result['duration_ms']}ms")

# Second call - returns cached result
result2 = initialize_implementation()

print(f"Status: {result2['status']}")  # "already_initialized"
print(f"Cached: {result2['cached']}")  # True
print(f"Uptime: {result2['uptime_seconds']}s")
```

---

### get_config_implementation()

Get initialization configuration.

**Signature:**
```python
def get_config_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Copy of configuration dictionary
- Empty dict if not initialized or rate limited

**Example:**
```python
from initialization.initialization_core import (
    initialize_implementation,
    get_config_implementation
)

# Initialize with config
initialize_implementation(
    debug_mode=True,
    timeout=30,
    region='us-east-1'
)

# Get config
config = get_config_implementation()

print(f"Debug mode: {config['debug_mode']}")  # True
print(f"Timeout: {config['timeout']}")  # 30
print(f"Region: {config['region']}")  # "us-east-1"
```

---

### is_initialized_implementation()

Check if Lambda environment is initialized.

**Signature:**
```python
def is_initialized_implementation(
    correlation_id: str = None,
    **kwargs
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `bool`: True if initialized, False otherwise

**Example:**
```python
from initialization.initialization_core import (
    is_initialized_implementation,
    initialize_implementation
)

# Check before initialization
if not is_initialized_implementation():
    print("Not initialized, initializing...")
    initialize_implementation()

# Check after initialization
if is_initialized_implementation():
    print("Ready to process requests")
```

---

### reset_implementation()

Reset initialization state (lifecycle management).

**Signature:**
```python
def reset_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Reset status dictionary:
  - `status`: 'reset' or 'rate_limited'
  - `was_initialized`: Boolean indicating previous state
  - `timestamp`: Unix timestamp of reset

**Behavior:**
- Clears initialization flag
- Clears all configuration
- Clears all flags
- Resets rate limiter
- Allows re-initialization

**Example:**
```python
from initialization.initialization_core import reset_implementation

# Reset for testing or container reuse
result = reset_implementation()

print(f"Status: {result['status']}")  # "reset"
print(f"Was initialized: {result['was_initialized']}")  # True/False
print(f"Timestamp: {result['timestamp']}")
```

---

### get_status_implementation()

Get comprehensive initialization status.

**Signature:**
```python
def get_status_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Comprehensive status dictionary

**Response Fields:**
- `initialized`: Boolean initialization state
- `config`: Configuration dictionary (copy)
- `flags`: Flags dictionary (copy)
- `init_timestamp`: Unix timestamp of initialization
- `init_duration_ms`: Initialization duration
- `uptime_seconds`: Time since initialization
- `flag_count`: Number of flags set
- `config_keys`: List of configuration keys
- `rate_limited_count`: Number of rate-limited operations

**Example:**
```python
from initialization.initialization_core import get_status_implementation

status = get_status_implementation()

print(f"Initialized: {status['initialized']}")
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Flags: {status['flag_count']}")
print(f"Config keys: {status['config_keys']}")
print(f"Rate limited: {status['rate_limited_count']}")
```

---

### get_stats_implementation()

Get initialization statistics.

**Signature:**
```python
def get_stats_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Statistics dictionary (same as get_status)

**Note:** This is an alias for get_status_implementation()

**Example:**
```python
from initialization.initialization_core import get_stats_implementation

stats = get_stats_implementation()

# Build dashboard
dashboard = {
    'health': 'healthy' if stats['initialized'] else 'not_ready',
    'uptime': f"{stats['uptime_seconds']:.0f}s" if stats['uptime_seconds'] else 'N/A',
    'performance': f"{stats['init_duration_ms']:.2f}ms init" if stats['init_duration_ms'] else 'N/A',
    'flags': stats['flag_count'],
    'rate_limited': stats['rate_limited_count']
}
```

---

### set_flag_implementation()

Set an initialization flag.

**Signature:**
```python
def set_flag_implementation(
    flag_name: str,
    value: Any,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `flag_name` (str): Flag name (required, non-empty)
- `value` (Any): Flag value to set
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Set flag result dictionary

**Response Fields (success):**
- `success`: True
- `flag_name`: Name of flag
- `value`: New value
- `old_value`: Previous value (if existed)
- `was_new`: Boolean indicating if flag was newly created

**Response Fields (failure):**
- `success`: False
- `error`: Error message

**Raises:**
- `ValueError`: If flag_name is missing

**Example:**
```python
from initialization.initialization_core import set_flag_implementation, get_flag_implementation

# Set feature flags
result = set_flag_implementation('use_cache', True)
print(f"Success: {result['success']}")  # True
print(f"Was new: {result['was_new']}")  # True

# Update existing flag
result = set_flag_implementation('use_cache', False)
print(f"Old value: {result['old_value']}")  # True
print(f"New value: {result['value']}")  # False
```

---

### get_flag_implementation()

Get initialization flag value.

**Signature:**
```python
def get_flag_implementation(
    flag_name: str,
    default: Any = None,
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `flag_name` (str): Flag name (required, non-empty)
- `default` (Any): Default value if flag doesn't exist
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Any`: Flag value or default

**Raises:**
- `ValueError`: If flag_name is missing

**Example:**
```python
from initialization.initialization_core import set_flag_implementation, get_flag_implementation

# Set flag
set_flag_implementation('debug_level', 'verbose')

# Get flag
level = get_flag_implementation('debug_level')
print(f"Debug level: {level}")  # "verbose"

# Get non-existent flag with default
cache_enabled = get_flag_implementation('cache_enabled', default=True)
print(f"Cache: {cache_enabled}")  # True (default)
```

---

## DEBUG INTEGRATION

All functions include debug integration:

**Automatic Correlation IDs:**
```python
# If not provided, correlation_id is auto-generated
status = is_initialized_implementation()
# Generates: correlation_id='init_1234567890'
```

**Debug Logging:**
```python
# All operations logged with:
# - correlation_id
# - Operation name
# - Key parameters
# - Results

debug_log(correlation_id, "INIT",
         "initialize_implementation called",
         kwargs_count=len(kwargs))
```

**CloudWatch Traces:**
```
[correlation_id=init_abc123] INIT: initialize_implementation called
  kwargs_count=3
[correlation_id=init_abc123] INIT: Initialization complete
  config_keys=['debug_mode', 'timeout', 'region']
  duration_ms=12.5
```

---

## USAGE PATTERNS

### Pattern 1: Lambda Handler Initialization

```python
from initialization.initialization_core import (
    is_initialized_implementation,
    initialize_implementation,
    get_config_implementation
)

def lambda_handler(event, context):
    # Initialize on cold start
    if not is_initialized_implementation():
        initialize_implementation(
            debug_mode=True,
            timeout=30,
            region='us-east-1'
        )
    
    # Get config for request
    config = get_config_implementation()
    
    # Process request with config
    return process_request(event, config)
```

---

### Pattern 2: Feature Flags

```python
from initialization.initialization_core import (
    initialize_implementation,
    set_flag_implementation,
    get_flag_implementation
)

# Initialize with feature flags
initialize_implementation()

# Enable features
set_flag_implementation('use_cache', True)
set_flag_implementation('enable_metrics', True)
set_flag_implementation('debug_level', 'verbose')

# Use feature flags
if get_flag_implementation('use_cache', default=False):
    result = cache.get(key)
else:
    result = compute(key)

debug_level = get_flag_implementation('debug_level', default='info')
logger.setLevel(debug_level.upper())
```

---

### Pattern 3: Health Monitoring

```python
from initialization.initialization_core import get_status_implementation

def health_check():
    status = get_status_implementation()
    
    return {
        'healthy': status['initialized'],
        'uptime': status['uptime_seconds'],
        'init_time': status['init_duration_ms'],
        'flags': status['flag_count'],
        'rate_limited': status['rate_limited_count']
    }
```

---

### Pattern 4: Testing and Reset

```python
from initialization.initialization_core import (
    reset_implementation,
    initialize_implementation,
    is_initialized_implementation
)

# Test setup
def setup_test():
    # Reset any previous state
    reset_implementation()
    
    # Initialize with test config
    initialize_implementation(
        test_mode=True,
        mock_services=True
    )

# Test teardown
def teardown_test():
    # Clean state for next test
    reset_implementation()
```

---

## EXPORTS

```python
__all__ = [
    'execute_initialization_operation',
    'initialize_implementation',
    'get_config_implementation',
    'is_initialized_implementation',
    'reset_implementation',
    'get_status_implementation',
    'get_stats_implementation',
    'set_flag_implementation',
    'get_flag_implementation',
]
```

---

## RELATED DOCUMENTATION

- **initialization_manager.md**: Manager singleton and core logic
- **interface_initialization.md**: Interface layer
- **LESS-18**: SINGLETON pattern lessons
- **LESS-21**: Rate limiting lessons

---

**END OF DOCUMENTATION**

**Module:** initialization/initialization_core.py  
**Functions:** 9  
**Pattern:** SUGA Core Implementation  
**Debug:** Fully Integrated
