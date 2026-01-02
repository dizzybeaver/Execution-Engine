# initialization_manager.md

**Version:** 2025-12-13_1  
**Purpose:** Lambda initialization manager with singleton pattern  
**Module:** initialization/initialization_manager.py  
**Type:** Singleton Manager

---

## OVERVIEW

Manages Lambda environment initialization with idempotent initialization, configuration storage, feature flags, and comprehensive lifecycle management.

**Key Features:**
- Singleton instance per Lambda container
- Idempotent initialization (safe multiple calls)
- Configuration storage
- Feature flag management
- Rate limiting (1000 ops/sec)
- Comprehensive status tracking
- Lambda-safe (no threading)

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SINGLETON: Single instance via get_initialization_manager()
- Idempotency: Safe to call initialize() multiple times
- Rate Limiting: 1000 operations/second protection

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

## ENUMS

### InitializationOperation

Enumeration of all initialization operations.

**Values:**
```python
class InitializationOperation(Enum):
    INITIALIZE = "initialize"
    GET_CONFIG = "get_config"
    IS_INITIALIZED = "is_initialized"
    RESET = "reset"
    GET_STATUS = "get_status"
    GET_STATS = "get_stats"
    SET_FLAG = "set_flag"
    GET_FLAG = "get_flag"
```

**Usage:**
```python
from initialization.initialization_manager import InitializationOperation

# Use in execute operation
operation = InitializationOperation.INITIALIZE
result = execute_initialization_operation(operation, config={...})
```

---

## CLASSES

### InitializationCore

Main manager class for Lambda initialization with SINGLETON pattern and idempotency.

**Purpose:**
- Manage Lambda initialization lifecycle
- Store configuration and flags
- Enforce rate limits
- Track initialization state

**Initialization:**
```python
def __init__(self):
    self._initialized = False
    self._config: Dict[str, Any] = {}
    self._flags: Dict[str, Any] = {}
    self._init_timestamp: Optional[float] = None
    self._init_duration_ms: Optional[float] = None
    
    # Rate limiting
    self._rate_limiter = deque(maxlen=1000)
    self._rate_limit_window_ms = 1000
    self._rate_limited_count = 0
```

**State:**
- `_initialized`: Initialization flag
- `_config`: Configuration dictionary
- `_flags`: Feature flags dictionary
- `_init_timestamp`: Unix timestamp of initialization
- `_init_duration_ms`: Initialization duration in milliseconds
- `_rate_limiter`: Deque tracking operation timestamps
- `_rate_limit_window_ms`: Rate limit window (1000ms)
- `_rate_limited_count`: Count of rate-limited operations

---

## METHODS

### _check_rate_limit()

**Private method** - Check if operation is within rate limit.

**Signature:**
```python
def _check_rate_limit(self) -> bool
```

**Returns:**
- `bool`: True if allowed, False if rate limited

**Algorithm:**
1. Get current timestamp in milliseconds
2. Remove timestamps older than 1000ms from deque
3. If deque has 1000 entries, reject (rate limited)
4. Otherwise, append current timestamp and allow

**Rate Limit:** 1000 operations per second (sliding window)

---

### initialize()

Initialize Lambda environment with idempotency guarantee.

**Signature:**
```python
def initialize(
    self,
    config: Optional[Dict[str, Any]] = None,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `config` (Dict[str, Any]): Optional configuration dictionary
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional configuration items (merged with config)

**Returns:**
- `Dict[str, Any]`: Initialization status dictionary

**Response (First Call - Fresh Initialization):**
```python
{
    'status': 'initialized',
    'cached': False,
    'timestamp': 1702500000.123,
    'duration_ms': 12.5,
    'config_keys': ['debug_mode', 'timeout', 'region']
}
```

**Response (Subsequent Calls - Cached):**
```python
{
    'status': 'already_initialized',
    'cached': True,
    'timestamp': 1702500000.123,
    'init_duration_ms': 12.5,
    'uptime_seconds': 45.2,
    'config_keys': ['debug_mode', 'timeout', 'region']
}
```

**Idempotency Guarantee:**
- First call: Performs initialization, stores config
- Subsequent calls: Returns cached result immediately
- No re-initialization on subsequent calls
- Safe to call multiple times

**Example:**
```python
manager = get_initialization_manager()

# First call - initialize
result = manager.initialize(
    config={'debug_mode': True, 'timeout': 30},
    region='us-east-1'
)

print(f"Status: {result['status']}")  # "initialized"
print(f"Duration: {result['duration_ms']}ms")

# Second call - cached
result2 = manager.initialize()

print(f"Status: {result2['status']}")  # "already_initialized"
print(f"Uptime: {result2['uptime_seconds']}s")
```

---

### get_config()

Get initialization configuration.

**Signature:**
```python
def get_config(
    self,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Copy of configuration dictionary
- Empty dict if not initialized or rate limited

**Example:**
```python
manager = get_initialization_manager()

# Initialize with config
manager.initialize(debug_mode=True, timeout=30)

# Get config
config = manager.get_config()

print(f"Debug: {config['debug_mode']}")  # True
print(f"Timeout: {config['timeout']}")  # 30
```

---

### is_initialized()

Check if Lambda environment is initialized.

**Signature:**
```python
def is_initialized(
    self,
    correlation_id: str = None
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `bool`: True if initialized, False otherwise
- False if rate limited

**Example:**
```python
manager = get_initialization_manager()

# Check initialization state
if not manager.is_initialized():
    print("Initializing...")
    manager.initialize()

# Now ready
if manager.is_initialized():
    print("Ready to process requests")
```

---

### reset()

Reset initialization state (lifecycle management).

**Signature:**
```python
def reset(
    self,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Reset status dictionary

**Response:**
```python
{
    'status': 'reset',
    'was_initialized': True,  # or False
    'timestamp': 1702500000.456
}
```

**Behavior:**
- Sets `_initialized` to False
- Clears `_config` dictionary
- Clears `_flags` dictionary
- Resets `_init_timestamp` to None
- Resets `_init_duration_ms` to None
- Clears rate limiter deque
- Resets `_rate_limited_count` to 0

**Example:**
```python
manager = get_initialization_manager()

# Reset for testing or container reuse
result = manager.reset()

print(f"Status: {result['status']}")  # "reset"
print(f"Was initialized: {result['was_initialized']}")

# Can initialize again
manager.initialize(new_config=True)
```

---

### get_status()

Get comprehensive initialization status.

**Signature:**
```python
def get_status(
    self,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Comprehensive status dictionary

**Response:**
```python
{
    'initialized': True,
    'config': {'debug_mode': True, 'timeout': 30},
    'flags': {'use_cache': True, 'debug_level': 'verbose'},
    'init_timestamp': 1702500000.123,
    'init_duration_ms': 12.5,
    'uptime_seconds': 45.2,
    'flag_count': 2,
    'config_keys': ['debug_mode', 'timeout'],
    'rate_limited_count': 0
}
```

**Example:**
```python
manager = get_initialization_manager()

status = manager.get_status()

# Check health
if status['initialized']:
    print(f"✓ Initialized")
    print(f"  Uptime: {status['uptime_seconds']:.1f}s")
    print(f"  Init time: {status['init_duration_ms']:.2f}ms")
    print(f"  Flags: {status['flag_count']}")
    print(f"  Rate limited: {status['rate_limited_count']}")
else:
    print("✗ Not initialized")
```

---

### get_stats()

Get initialization statistics.

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
- `Dict[str, Any]`: Statistics dictionary (same as get_status())

**Note:** This is an alias for get_status()

---

### set_flag()

Set an initialization flag with validation.

**Signature:**
```python
def set_flag(
    self,
    flag_name: str,
    value: Any,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `flag_name` (str): Name of flag (required, non-empty string)
- `value` (Any): Value to set
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Any]`: Operation result dictionary

**Response (Success):**
```python
{
    'success': True,
    'flag_name': 'use_cache',
    'value': True,
    'old_value': None,  # or previous value
    'was_new': True  # or False if updating
}
```

**Response (Failure):**
```python
{
    'success': False,
    'error': 'Flag name must be a non-empty string',
    'flag_name': ''
}
```

**Validation:**
- `flag_name` must be a string
- `flag_name` must be non-empty
- `value` can be any type

**Example:**
```python
manager = get_initialization_manager()

# Set new flag
result = manager.set_flag('use_cache', True)
print(f"Success: {result['success']}")  # True
print(f"Was new: {result['was_new']}")  # True

# Update existing flag
result = manager.set_flag('use_cache', False)
print(f"Old value: {result['old_value']}")  # True
print(f"New value: {result['value']}")  # False

# Invalid flag name
result = manager.set_flag('', True)
print(f"Success: {result['success']}")  # False
print(f"Error: {result['error']}")  # "Flag name must be..."
```

---

### get_flag()

Get initialization flag value with validation.

**Signature:**
```python
def get_flag(
    self,
    flag_name: str,
    default: Any = None,
    correlation_id: str = None
) -> Any
```

**Parameters:**
- `flag_name` (str): Name of flag (required, non-empty string)
- `default` (Any): Default value if flag doesn't exist
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Any`: Flag value or default

**Behavior:**
- Returns flag value if exists
- Returns default if flag doesn't exist
- Returns default if flag_name is invalid
- Returns default if rate limited

**Example:**
```python
manager = get_initialization_manager()

# Set flag
manager.set_flag('debug_level', 'verbose')

# Get flag
level = manager.get_flag('debug_level')
print(f"Level: {level}")  # "verbose"

# Get non-existent flag
cache = manager.get_flag('use_cache', default=True)
print(f"Cache: {cache}")  # True (default)

# Invalid flag name returns default
value = manager.get_flag('', default='fallback')
print(f"Value: {value}")  # "fallback"
```

---

## SINGLETON PATTERN

### get_initialization_manager()

Get SINGLETON initialization manager instance.

**Function:** Module-level singleton factory

**Signature:**
```python
def get_initialization_manager() -> InitializationCore
```

**Returns:**
- `InitializationCore`: The singleton manager instance

**Implementation:**
```python
_manager_core = None  # Module-level singleton

def get_initialization_manager() -> InitializationCore:
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        # Try gateway SINGLETON registry first
        manager = singleton_get('initialization_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = InitializationCore()
            singleton_register('initialization_manager', _manager_core)
            manager = _manager_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _manager_core is None:
            _manager_core = InitializationCore()
        return _manager_core
```

**Singleton Strategy:**
1. **Preferred:** Gateway SINGLETON registry
2. **Fallback:** Module-level global variable

**Usage:**
```python
# Always use this function to get manager
manager = get_initialization_manager()

# Never instantiate directly
# manager = InitializationCore()  # ❌ WRONG
```

---

## IDEMPOTENCY

### Design

Initialization is idempotent - calling `initialize()` multiple times is safe:

**First Call:**
```python
result = manager.initialize(config={'debug': True})
# {'status': 'initialized', 'cached': False, 'duration_ms': 12.5}
```

**Second Call (same config):**
```python
result = manager.initialize(config={'debug': True})
# {'status': 'already_initialized', 'cached': True, 'uptime_seconds': 10.2}
```

**Why Idempotent?**
- Lambda containers may be reused
- Handler may be called multiple times
- Prevents duplicate initialization overhead
- Ensures consistent state

**Implementation:**
```python
if self._initialized:
    # Fast path - return cached result
    return {
        'status': 'already_initialized',
        'cached': True,
        'timestamp': self._init_timestamp,
        'uptime_seconds': time.time() - self._init_timestamp
    }

# Slow path - perform initialization
self._initialized = True
self._init_timestamp = time.time()
# ... initialization logic ...
```

---

## RATE LIMITING

### Design

**Limit:** 1000 operations/second  
**Window:** 1000ms sliding window  
**Implementation:** Deque with maxlen=1000

**Algorithm:**
1. Store operation timestamps in deque
2. Before each operation, remove timestamps > 1000ms old
3. If deque has 1000 entries, reject (rate limited)
4. Otherwise, append current timestamp and proceed

**Why 1000 ops/sec?**
- Infrastructure component needs high throughput
- Prevents DoS attacks
- Still allows burst traffic
- Higher than typical usage

---

## USAGE PATTERNS

### Pattern 1: Lambda Handler

```python
from initialization.initialization_manager import get_initialization_manager

def lambda_handler(event, context):
    manager = get_initialization_manager()
    
    # Initialize on cold start (idempotent)
    manager.initialize(
        debug_mode=True,
        timeout=30,
        region='us-east-1'
    )
    
    # Get config for request
    config = manager.get_config()
    
    # Process with config
    return process_request(event, config)
```

---

### Pattern 2: Feature Flags

```python
from initialization.initialization_manager import get_initialization_manager

manager = get_initialization_manager()

# Set feature flags
manager.set_flag('use_cache', True)
manager.set_flag('enable_metrics', True)
manager.set_flag('debug_level', 'verbose')

# Use feature flags
if manager.get_flag('use_cache', default=False):
    result = cache.get(key)
else:
    result = compute(key)

debug_level = manager.get_flag('debug_level', default='info')
```

---

### Pattern 3: Health Dashboard

```python
from initialization.initialization_manager import get_initialization_manager

def health_check():
    manager = get_initialization_manager()
    status = manager.get_status()
    
    return {
        'healthy': status['initialized'],
        'uptime': f"{status['uptime_seconds']:.1f}s",
        'init_time': f"{status['init_duration_ms']:.2f}ms",
        'flags': status['flag_count'],
        'rate_limited': status['rate_limited_count'],
        'config': status['config_keys']
    }
```

---

### Pattern 4: Testing

```python
from initialization.initialization_manager import get_initialization_manager

def test_setup():
    manager = get_initialization_manager()
    
    # Reset from previous tests
    manager.reset()
    
    # Initialize with test config
    manager.initialize(
        test_mode=True,
        mock_services=True
    )
    
    # Set test flags
    manager.set_flag('use_mocks', True)

def test_teardown():
    manager = get_initialization_manager()
    manager.reset()
```

---

## EXPORTS

```python
__all__ = [
    'InitializationOperation',
    'InitializationCore',
    'get_initialization_manager',
]
```

---

## RELATED DOCUMENTATION

- **initialization_core.md**: Gateway implementation functions
- **interface_initialization.md**: Interface layer
- **LESS-18**: SINGLETON pattern lessons
- **LESS-21**: Rate limiting lessons

---

**END OF DOCUMENTATION**

**Module:** initialization/initialization_manager.py  
**Classes:** 2 (InitializationOperation, InitializationCore)  
**Functions:** 1 (get_initialization_manager)  
**Pattern:** SINGLETON with Idempotency
