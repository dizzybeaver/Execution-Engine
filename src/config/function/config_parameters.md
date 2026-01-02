# config_parameters.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 180

---

## Purpose

Configuration parameter operations with SSM-first priority. Handles getting and setting parameters with proper fallback chain: SSM → Environment → Default.

---

## Functions

### initialize_config()

**Purpose:** Initialize configuration system

**Signature:**
```python
def initialize_config() -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,                 # Initialization result
    'use_parameter_store': bool,     # SSM enabled
    'parameter_count': int           # Parameters loaded
}
# Or on error:
{
    'success': False,
    'error': str                     # Error message
}
```

**Behavior:**
1. Get configuration manager singleton
2. Check USE_PARAMETER_STORE environment variable
3. Set SSM enabled flag
4. Load environment configuration
5. Update config storage
6. Set initialized flag
7. Return success result

**Performance:** ~500μs (includes environment load)

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "initialize"):
    gateway.debug_log("CONFIG", "CONFIG", "Initializing config",
                    use_ssm=use_ssm, prefix=manager._parameter_prefix)
```

**Usage:**
```python
result = initialize_config()
if result['success']:
    print(f"Loaded {result['parameter_count']} parameters")
else:
    print(f"Failed: {result['error']}")
```

**Environment Variables:**
- `USE_PARAMETER_STORE` - Enable SSM (true/false)

**Error Handling:**
- Catches all exceptions
- Logs via gateway.log_error()
- Returns error dict

---

### get_parameter()

**Purpose:** Get configuration parameter with SSM-first priority

**Signature:**
```python
def get_parameter(key: str, default: Any = None) -> Any
```

**Parameters:**
- `key: str` - Parameter key
- `default: Any` - Default value if not found

**Returns:**
- `Any` - Parameter value or default

**Priority Order:**
1. **SSM Parameter Store** (if USE_PARAMETER_STORE=true)
2. **Environment variable**
3. **Default value**

**Behavior:**
```python
# 1. Check rate limit
if rate_limited:
    log warning, return default

# 2. Check cache
if key in cache and valid:
    return cached_value

# 3. Check SSM (if enabled)
if use_parameter_store:
    ssm_value = get_ssm_parameter(f"{prefix}/{key}")
    if ssm_value:
        cache it, return ssm_value

# 4. Check environment
env_value = os.getenv(key)
if env_value:
    cache it, return env_value

# 5. Return default
return default
```

**Performance:**
- Cache hit: ~3μs
- SSM lookup: ~50-100ms (first call)
- Environment: ~5μs
- With rate limit: +5μs

**Debug Integration:**
```python
gateway.debug_log("CONFIG", "CONFIG", "Getting parameter", key=key)
gateway.debug_log("CONFIG", "CONFIG", "Cache hit", key=key)
gateway.debug_log("CONFIG", "CONFIG", "Checking SSM", ssm_key=ssm_key)
gateway.debug_log("CONFIG", "CONFIG", "SSM hit", key=key)
gateway.debug_log("CONFIG", "CONFIG", "Environment hit", key=key)
gateway.debug_log("CONFIG", "CONFIG", "Using default", key=key, default=default)
```

**Usage:**
```python
# Basic usage
value = get_parameter('database.host', 'localhost')

# SSM priority
# If USE_PARAMETER_STORE=true:
#   1. Checks SSM: /lambda-execution-engine/database.host
#   2. Falls back to env: database.host
#   3. Falls back to default: 'localhost'

# Cache behavior
value1 = get_parameter('key')  # May hit SSM/env
value2 = get_parameter('key')  # Cache hit (fast)
```

**Rate Limiting:**
```python
# If rate limit exceeded
gateway.log_warning(f"Config get_parameter rate limited: {key}")
return default
```

**Error Scenarios:**
- Rate limited → Warning logged, returns default
- SSM unavailable → Falls back to environment
- SSM error → Warning logged, falls back
- Key not found anywhere → Returns default

---

### set_parameter()

**Purpose:** Set configuration parameter

**Signature:**
```python
def set_parameter(key: str, value: Any) -> bool
```

**Parameters:**
- `key: str` - Parameter key
- `value: Any` - Parameter value

**Returns:**
- `bool` - True if set successfully, False on error

**Behavior:**
1. Get configuration manager
2. Check rate limit
3. Log operation (if debug enabled)
4. Set parameter in config storage
5. Return success

**Performance:** ~10μs (includes rate check)

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "set_parameter"):
    gateway.debug_log("CONFIG", "CONFIG", "Setting parameter", 
                    key=key, value_type=type(value).__name__)
```

**Usage:**
```python
success = set_parameter('cache.ttl', 300)
if success:
    print("Parameter set")
else:
    print("Failed to set parameter")

# Set complex values
set_parameter('config.dict', {'key': 'value'})
set_parameter('config.list', [1, 2, 3])
```

**Rate Limiting:**
```python
if manager._check_rate_limit():
    gateway.log_warning(f"Config set_parameter rate limited: {key}")
    return False
```

**Error Handling:**
- Rate limited → Warning logged, returns False
- Exception during set → Error logged, returns False

---

### get_category_config()

**Purpose:** Get configuration for a category

**Signature:**
```python
def get_category_config(category: str) -> Dict[str, Any]
```

**Parameters:**
- `category: str` - Category name (e.g., 'cache', 'logging')

**Returns:**
```python
{
    'key1': value1,  # Category prefix removed
    'key2': value2,
    ...
}
```

**Behavior:**
1. Get configuration manager
2. Create category prefix (e.g., 'cache.')
3. Filter config keys by prefix
4. Remove prefix from keys
5. Return category config dict

**Performance:** ~20μs for 100 parameters

**Debug Integration:**
```python
gateway.debug_log("CONFIG", "CONFIG", "Getting category config", 
                category=category)
gateway.debug_log("CONFIG", "CONFIG", "Category config retrieved",
                category=category, key_count=len(category_config))
```

**Usage:**
```python
# Get cache category
cache_config = get_category_config('cache')
# Returns: {'enabled': true, 'ttl': 300, ...}
# From keys: cache.enabled, cache.ttl, ...

# Get logging category
logging_config = get_category_config('logging')
# Returns: {'level': 'INFO', 'format': '...'}
```

**Example:**
```python
# Config storage:
{
    'cache.enabled': 'true',
    'cache.ttl': '300',
    'logging.level': 'INFO',
    'database.host': 'localhost'
}

# get_category_config('cache') returns:
{
    'enabled': 'true',
    'ttl': '300'
}
```

---

### get_state()

**Purpose:** Get configuration state

**Signature:**
```python
def get_state() -> Dict[str, Any]
```

**Returns:**
```python
{
    'initialized': bool,              # Initialization status
    'use_parameter_store': bool,      # SSM enabled
    'parameter_prefix': str,          # SSM prefix
    'config_keys': List[str],         # All parameter keys
    'rate_limited_count': int         # Rate limit hits
}
```

**Behavior:**
1. Get configuration manager
2. Collect state information
3. Return state dict

**Performance:** ~5μs

**Usage:**
```python
state = get_state()
print(f"Initialized: {state['initialized']}")
print(f"Parameters: {len(state['config_keys'])}")
print(f"Rate limited: {state['rate_limited_count']} times")

# Check SSM usage
if state['use_parameter_store']:
    print(f"Using SSM: {state['parameter_prefix']}")
```

---

### _get_ssm_parameter() (Internal)

**Purpose:** Get parameter from SSM Parameter Store

**Signature:**
```python
def _get_ssm_parameter(key: str) -> Optional[Any]
```

**Parameters:**
- `key: str` - SSM parameter key (full path)

**Returns:**
- `Any` - Parameter value
- `None` - If not found or error

**Behavior:**
1. Import boto3 SSM client
2. Call get_parameter() with decryption
3. Extract parameter value
4. Return value
5. On any exception: return None

**Performance:** ~50-100ms (AWS API call)

**Usage:**
```python
# Internal use only
value = _get_ssm_parameter('/lambda-execution-engine/database.host')
```

**AWS API:**
```python
ssm_client = boto3.client('ssm')
response = ssm_client.get_parameter(
    Name=key,
    WithDecryption=True
)
return response['Parameter']['Value']
```

**Error Handling:**
- Catches all exceptions
- Returns None on error
- No logging (handled by caller)

---

## Priority Chain

### SSM-First Design

**Rationale:**
When USE_PARAMETER_STORE=true, SSM is the authoritative source. Environment variables should only serve as fallback when SSM is unavailable.

**Priority:**
```
1. SSM Parameter Store (if enabled)
   └─ Authoritative source
   └─ Secure, encrypted
   └─ Centralized management

2. Environment Variable
   └─ Fallback when SSM fails
   └─ Local development
   └─ Testing

3. Default Value
   └─ Fallback of last resort
   └─ Prevents crashes
   └─ Development convenience
```

**Example Flow:**
```python
# Configuration: USE_PARAMETER_STORE=true
# Environment: DATABASE_HOST=localhost
# SSM: /lambda-execution-engine/DATABASE_HOST=prod-db

value = get_parameter('DATABASE_HOST', 'default')

# Flow:
# 1. Check SSM: /lambda-execution-engine/DATABASE_HOST
#    → Found: 'prod-db'
# 2. Return 'prod-db' (environment ignored)

# If SSM fails:
# 1. Check SSM: (fails)
# 2. Check environment: DATABASE_HOST
#    → Found: 'localhost'
# 3. Return 'localhost'
```

---

## Debug Integration

### Scope

**Scope Name:** CONFIG  
**Operations:** All parameter operations

### Environment Variables

```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Enable config debug
CONFIG_DEBUG_TIMING=true         # Enable timing
```

### Debug Output

**Getting Parameter:**
```
[corr-id] [CONFIG-DEBUG] Getting parameter (key=database.host)
[corr-id] [CONFIG-DEBUG] Checking SSM (ssm_key=/lee/database.host)
[corr-id] [CONFIG-DEBUG] SSM hit (key=database.host)
```

**Setting Parameter:**
```
[corr-id] [CONFIG-DEBUG] Setting parameter (key=cache.ttl, value_type=int)
[corr-id] [CONFIG-TIMING] set_parameter: 8.42ms
```

---

## Performance

### Operation Timing

| Operation | Cache Hit | SSM Hit | Env Hit | Miss |
|-----------|-----------|---------|---------|------|
| get_parameter | ~3μs | ~50ms | ~5μs | ~5μs |
| set_parameter | ~10μs | N/A | N/A | N/A |
| get_category_config | ~20μs | N/A | N/A | N/A |
| get_state | ~5μs | N/A | N/A | N/A |

### Optimization Tips

1. **Cache frequently accessed parameters:**
```python
# First call: SSM lookup (~50ms)
host = get_parameter('database.host')

# Subsequent calls: cache hit (~3μs)
host = get_parameter('database.host')
```

2. **Batch initialization:**
```python
# Initialize once, loads all environment
initialize_config()

# Then access without overhead
value1 = get_parameter('key1')
value2 = get_parameter('key2')
```

---

## Dependencies

**Internal:**
- `config.config_core` - get_config_manager()
- `config.config_loader` - load_from_environment()

**External:**
- `boto3` - SSM Parameter Store access (optional)

**Gateway:**
- `gateway.debug_log()` - Debug logging
- `gateway.debug_timing()` - Timing context
- `gateway.log_error()` - Error logging
- `gateway.log_warning()` - Warning logging

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Added debug integration throughout
- Improved SSM-first documentation
- Added comprehensive error handling
- Simplified function signatures

---

**END OF DOCUMENTATION**
