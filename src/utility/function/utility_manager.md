# utility_manager.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_manager.py  
**Module:** Utility manager core

---

## Overview

Core utility manager with rate limiting, metrics tracking, and performance optimization. Implements SINGLETON pattern for resource management.

**File:** `utility/utility_manager.py`  
**Lines:** 295  
**Pattern:** SINGLETON (LESS-18)

---

## Classes

### SharedUtilityCore

**Purpose:** Core utility manager with data operations and performance tracking  
**Pattern:** SINGLETON via `get_utility_manager()`

**Compliance:**
- AP-08: NO threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting (1000 ops/sec)

**State:**
```python
{
    '_metrics': {},  # Operation metrics by type
    '_cache_enabled': True,
    '_cache_ttl': 300,
    '_id_pool': [],  # Pre-generated UUIDs
    '_json_cache': {},  # Parsed JSON cache
    '_json_cache_order': [],  # LRU tracking
    '_stats': {  # Overall statistics
        'template_hits': 0,
        'template_fallbacks': 0,
        'cache_optimizations': 0,
        'id_pool_reuse': 0,
        'lugs_integrations': 0,
        'templates_rendered': 0,
        'configs_retrieved': 0
    },
    '_rate_limiter': deque(maxlen=1000),  # Rate limit tracking
    '_rate_limit_window_ms': 1000,
    '_rate_limited_count': 0
}
```

---

## Methods

### Rate Limiting

#### _check_rate_limit()

**Purpose:** Check if operation is within rate limit  
**Access:** Private  
**Returns:** bool (True if allowed)

**Rate Limit:** 1000 operations/second

**Implementation:**
```python
def _check_rate_limit(self) -> bool:
    """Check rate limit (1000 ops/sec)."""
    now = time.time() * 1000
    
    # Remove old entries
    while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
        self._rate_limiter.popleft()
    
    # Check limit
    if len(self._rate_limiter) >= 1000:
        self._rate_limited_count += 1
        return False
    
    self._rate_limiter.append(now)
    return True
```

---

### Operation Tracking

#### _start_operation_tracking()

**Purpose:** Start tracking an operation  
**Access:** Private

**Parameters:**
- `operation_type` (str): Operation name

**Usage:**
```python
manager._start_operation_tracking('parse_json')
```

**Creates:** UtilityMetrics instance if not exists

---

#### _complete_operation_tracking()

**Purpose:** Complete tracking for an operation  
**Access:** Private

**Parameters:**
- `operation_type` (str): Operation name
- `duration_ms` (float): Operation duration
- `success` (bool, default=True): Operation succeeded
- `cache_hit` (bool, default=False): Cache was hit
- `used_template` (bool, default=False): Template was used

**Usage:**
```python
start = time.time()
result = parse_json(data)
duration = (time.time() - start) * 1000
manager._complete_operation_tracking('parse_json', duration, True, True)
```

**Updates:**
- Call count
- Average duration
- Error count
- Cache hit/miss counts
- Template usage

---

### UUID and Timestamp

#### generate_uuid()

**Purpose:** Generate UUID with pool optimization  
**Returns:** str (UUID)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Pool Optimization:**
- Reuses pre-generated UUIDs from pool
- Tracks pool reuse in statistics
- Falls back to `uuid.uuid4()` if pool empty

**Usage:**
```python
manager = get_utility_manager()
uuid_val = manager.generate_uuid()
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] UUID from pool (pool_size=15)
[abc123] [UTILITY-DEBUG] UUID generated (new_uuid=True)
```

---

#### get_timestamp()

**Purpose:** Get current timestamp as ISO string  
**Returns:** str (ISO timestamp)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Format:** `YYYY-MM-DDTHH:MM:SSZ`

**Usage:**
```python
manager = get_utility_manager()
timestamp = manager.get_timestamp()
# Result: "2025-12-13T14:30:00Z"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Timestamp generated (timestamp=2025-12-13T14:30:00Z)
```

---

#### generate_correlation_id_impl()

**Purpose:** Generate correlation ID with optional prefix  
**Returns:** str (correlation ID)

**Parameters:**
- `prefix` (str, optional): Prefix for ID
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
manager = get_utility_manager()
corr_id = manager.generate_correlation_id_impl(prefix='req')
# Result: "req_550e8400-e29b-41d4-a716-446655440000"
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Correlation ID with prefix (prefix=req, result_length=41)
```

---

### Template Rendering

#### render_template_impl()

**Purpose:** Render template with {placeholder} substitution  
**Returns:** dict (rendered template)

**Parameters:**
- `template` (dict): Template with {placeholder} strings
- `data` (dict): Substitution data
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs`: Additional parameters (ignored)

**Features:**
- JSON serialization for nested values
- Auto-inject message_id if missing
- Template string replacement
- JSON parse result

**Usage:**
```python
manager = get_utility_manager()
template = {
    'message': 'Hello {name}',
    'user_id': '{user_id}',
    'nested': {
        'value': '{nested_value}'
    }
}
data = {
    'name': 'Alice',
    'user_id': '123',
    'nested_value': 'test'
}
result = manager.render_template_impl(template, data)
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Rendering template (placeholder_count=3)
[abc123] [UTILITY-TIMING] render_template: 1.23ms
[abc123] [UTILITY-DEBUG] Template rendered successfully
```

**Error Handling:**
- Returns original template on error
- Logs error details
- Increments template_fallbacks stat

---

### Config Retrieval

#### config_get_impl()

**Purpose:** Get typed configuration value from environment  
**Returns:** Any (typed value)

**Parameters:**
- `key` (str): Environment variable key
- `default` (Any, optional): Default value (determines type)
- `correlation_id` (str, optional): Debug correlation ID
- `**kwargs**: Additional parameters (ignored)

**Type Conversion:**

Based on default value type:
- `bool`: Converts 'true', '1', 'yes', 'on' → True
- `int`: Converts to integer
- `float`: Converts to float
- `None` or other: Returns as string

**Usage:**
```python
manager = get_utility_manager()

# Boolean
debug = manager.config_get_impl('DEBUG_MODE', False)

# Integer
timeout = manager.config_get_impl('TIMEOUT', 30)

# Float
threshold = manager.config_get_impl('THRESHOLD', 0.5)

# String
api_key = manager.config_get_impl('API_KEY', None)
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Config retrieved and converted (key=DEBUG_MODE, result_type=bool)
[abc123] [UTILITY-DEBUG] Config not found, using default (key=API_KEY, has_default=True)
[abc123] [UTILITY-DEBUG] Config conversion failed, using default (key=TIMEOUT, error=...)
```

**Error Handling:**
- Returns default on missing key
- Returns default on conversion error
- Logs debug info on failure

---

### Performance and Stats

#### get_stats()

**Purpose:** Get utility statistics  
**Returns:** dict (statistics)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
manager = get_utility_manager()
stats = manager.get_stats()
```

**Returns:** Same as `get_performance_stats()`

---

#### get_performance_stats()

**Purpose:** Get comprehensive utility performance statistics  
**Returns:** dict (performance stats)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Usage:**
```python
manager = get_utility_manager()
stats = manager.get_performance_stats()
```

**Returns:**
```python
{
    'overall_stats': {
        'template_hits': 150,
        'template_fallbacks': 2,
        'cache_optimizations': 5,
        'id_pool_reuse': 75,
        'lugs_integrations': 3,
        'templates_rendered': 150,
        'configs_retrieved': 50
    },
    'operation_stats': {
        'parse_json': {
            'call_count': 100,
            'avg_duration_ms': 1.25,
            'cache_hit_rate_percent': 75.0,
            'error_rate_percent': 2.0,
            'template_usage_percent': 0.0,
            'cache_hits': 75,
            'cache_misses': 25,
            'error_count': 2,
            'template_usage': 0
        },
        'render_template': {
            'call_count': 150,
            'avg_duration_ms': 2.50,
            'cache_hit_rate_percent': 0.0,
            'error_rate_percent': 1.33,
            'template_usage_percent': 100.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'error_count': 2,
            'template_usage': 150
        }
    },
    'id_pool_size': 15,
    'json_cache_size': 45,
    'json_cache_limit': 100,
    'cache_enabled': True,
    'rate_limited_count': 0
}
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Performance statistics retrieved (operation_count=5)
```

---

#### reset()

**Purpose:** Reset utility manager state  
**Returns:** bool (True if successful)

**Parameters:**
- `correlation_id` (str, optional): Debug correlation ID

**Resets:**
- All metrics (`_metrics`)
- All statistics (`_stats`)
- JSON cache (`_json_cache`, `_json_cache_order`)
- UUID pool (`_id_pool`)
- Rate limiter (`_rate_limiter`, `_rate_limited_count`)

**Usage:**
```python
manager = get_utility_manager()
success = manager.reset()
# Result: True
```

**Debug Output:**
```
[abc123] [UTILITY-DEBUG] Resetting utility manager state
[abc123] [UTILITY-DEBUG] Utility manager reset complete
```

**Error Handling:**
- Returns False on error
- Logs debug error details

---

## Functions

### get_utility_manager()

**Purpose:** Get utility manager SINGLETON instance  
**Returns:** SharedUtilityCore

**Pattern:** SINGLETON (LESS-18)

**Implementation:**
```python
def get_utility_manager() -> SharedUtilityCore:
    """
    Get the utility manager instance (SINGLETON pattern).
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        SharedUtilityCore instance
    """
    global _manager_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('utility_manager')
        if manager is None:
            if _manager_core is None:
                _manager_core = SharedUtilityCore()
            singleton_register('utility_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        if _manager_core is None:
            _manager_core = SharedUtilityCore()
        return _manager_core
```

**Usage:**
```python
from utility.utility_manager import get_utility_manager

manager = get_utility_manager()
uuid = manager.generate_uuid()
```

**Features:**
- Lazy initialization
- Gateway SINGLETON registry integration
- Fallback to module-level instance
- Thread-safe (Lambda is single-threaded)

---

## Usage Patterns

### Initialization
```python
from utility.utility_manager import get_utility_manager

# Get manager instance
manager = get_utility_manager()
```

### UUID Generation
```python
# Generate UUID
uuid = manager.generate_uuid()

# With debug correlation
uuid = manager.generate_uuid(correlation_id='req123')
```

### Template Rendering
```python
template = {'message': 'Hello {name}'}
data = {'name': 'Alice'}
result = manager.render_template_impl(template, data)
```

### Config Retrieval
```python
# Boolean
debug = manager.config_get_impl('DEBUG_MODE', False)

# Integer with fallback
timeout = manager.config_get_impl('TIMEOUT', 30)
```

### Performance Monitoring
```python
# Get statistics
stats = manager.get_performance_stats()

# Check cache performance
json_cache_size = stats['json_cache_size']
id_pool_size = stats['id_pool_size']

# Check rate limiting
rate_limited = stats['rate_limited_count']
```

### Reset State
```python
# Reset between tests
manager.reset()
```

---

## Debug Integration

**Master Switch:**
- `DEBUG_MODE` - Enables all debugging

**Scope Switches:**
- `UTILITY_DEBUG_MODE` - Utility debug logging
- `UTILITY_DEBUG_TIMING` - Utility timing measurements

**Correlation ID:**
- All methods accept optional `correlation_id` parameter
- Auto-generated if not provided
- Used for tracking related operations

---

## Performance Characteristics

### Rate Limiting
- **Limit:** 1000 operations/second
- **Window:** 1 second sliding window
- **Tracking:** Deque with maxlen=1000
- **Enforcement:** Returns False when limit exceeded

### UUID Pool
- **Purpose:** Reduce uuid.uuid4() overhead
- **Reuse:** Tracked in statistics
- **Refill:** Manual via optimization

### JSON Cache
- **Size:** 100 items (DEFAULT_MAX_JSON_CACHE_SIZE)
- **Eviction:** LRU (oldest first)
- **Tracking:** Cache order list
- **Hit Rate:** Tracked per operation

### Template Rendering
- **Method:** String replacement via JSON serialization
- **Fallback:** Original template on error
- **Tracking:** Template hits/fallbacks

---

## Related Files

- **Types:** `utility/utility_types.py` (UtilityMetrics)
- **Interface:** `interface/interface_utility.py`
- **Operations:** `utility/utility_data.py`, `utility/utility_validation.py`, `utility/utility_sanitize.py`
- **Core:** `utility/utility_core.py`

---

**END OF DOCUMENTATION**
