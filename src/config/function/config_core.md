# config_core.py

**Version:** 2025-12-09_1  
**Module:** Config  
**Layer:** Core  
**Lines:** 140

---

## Purpose

Core configuration management class with singleton pattern, rate limiting, and statistics tracking. Provides centralized configuration state management for LEE.

---

## Classes

### ConfigurationCore

**Purpose:** Main configuration management class

**Attributes:**
- `_config: Dict[str, Any]` - Configuration storage
- `_state: ConfigurationState` - State tracking
- `_validator: ConfigurationValidator` - Validator instance
- `_cache_prefix: str` - Cache key prefix
- `_initialized: bool` - Initialization flag
- `_use_parameter_store: bool` - SSM enabled flag
- `_parameter_prefix: str` - SSM parameter prefix
- `_rate_limiter: deque` - Rate limiting queue (maxlen=1000)
- `_rate_limit_window_ms: int` - Rate limit window (1000ms)
- `_rate_limited_count: int` - Rate limit hit counter

**Initialization:**
```python
manager = ConfigurationCore()
```

**Design:**
- Single-threaded (Lambda compliant)
- Rate limiting instead of locks (AP-08 compliance)
- Statistics tracking for monitoring
- Gateway debug integration

---

### Methods

#### __init__()

**Purpose:** Initialize configuration manager

**Signature:**
```python
def __init__(self) -> None
```

**Behavior:**
1. Create empty config dict
2. Initialize ConfigurationState
3. Create ConfigurationValidator
4. Set default values
5. Initialize rate limiter (deque maxlen=1000)

**Performance:** ~10μs

**Usage:**
```python
manager = ConfigurationCore()
```

---

#### _check_rate_limit()

**Purpose:** Check if operation should be rate limited

**Signature:**
```python
def _check_rate_limit(self) -> bool
```

**Returns:**
- `bool` - True if rate limited, False if allowed

**Behavior:**
1. Get current time in milliseconds
2. Remove entries older than window (1000ms)
3. Check if queue full (1000 entries)
4. If full: increment counter, log, return True
5. If not full: add entry, return False

**Performance:** ~5μs per call

**Rate Limit:** 1000 operations per second

**Usage:**
```python
if manager._check_rate_limit():
    # Operation rate limited
    return default_value
# Proceed with operation
```

**Debug Output:**
```python
# When rate limited:
gateway.debug_log("CONFIG", "CONFIG", "Rate limit exceeded", 
                count=self._rate_limited_count)
```

---

#### reset()

**Purpose:** Reset configuration state

**Signature:**
```python
def reset(self) -> bool
```

**Returns:**
- `bool` - True if reset successful, False on error

**Behavior:**
1. Clear all configuration data
2. Create new ConfigurationState
3. Reset initialization flag
4. Clear rate limiter queue
5. Reset rate limit counter
6. Log reset action

**Performance:** ~50μs

**Debug Integration:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "reset"):
    # Reset operations
    gateway.debug_log("CONFIG", "CONFIG", "Configuration reset")
```

**Usage:**
```python
success = manager.reset()
if success:
    print("Configuration reset")
else:
    print("Reset failed")
```

**Error Handling:**
- Catches all exceptions
- Logs errors via gateway.log_error()
- Returns False on failure

**Error Scenarios:**
- Exception during clear → Logged, returns False
- Gateway not available → Logged, returns False

---

#### get_stats()

**Purpose:** Get configuration statistics

**Signature:**
```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    'initialized': bool,           # Initialization status
    'parameter_count': int,        # Number of parameters
    'use_parameter_store': bool,   # SSM enabled
    'rate_limited_count': int,     # Rate limit hits
    'rate_limiter_size': int       # Current queue size
}
```

**Behavior:**
1. Collect current statistics
2. Return stats dictionary

**Performance:** ~2μs

**Usage:**
```python
stats = manager.get_stats()
print(f"Parameters: {stats['parameter_count']}")
print(f"Rate limited: {stats['rate_limited_count']} times")
```

---

## Functions

### get_config_manager()

**Purpose:** Get configuration manager singleton

**Signature:**
```python
def get_config_manager() -> ConfigurationCore
```

**Returns:**
- `ConfigurationCore` - Singleton instance

**Behavior:**
1. Try gateway singleton registry first
2. Check if 'config_manager' registered
3. If not registered: create new, register, return
4. If registered: return existing
5. On ImportError: fall back to module-level singleton
6. Create module singleton if needed

**Performance:** 
- First call: ~100μs (registration)
- Subsequent: ~5μs (lookup)

**Usage:**
```python
manager = get_config_manager()
value = manager.get_parameter('key')
```

**Singleton Pattern:**
```python
# Gateway registration (preferred)
import gateway
manager = gateway.singleton_get('config_manager')

# Module-level fallback
_config_core = ConfigurationCore()
```

**Error Handling:**
- ImportError (gateway) → Module singleton
- Any exception → Module singleton

---

## Architecture

### SUGA Compliance

**Layer:** Core  
**Access:** Via interface only  
**Pattern:** Singleton via gateway

**Import Flow:**
```
gateway.config_get_parameter()
    ↓
interface_config.execute_config_operation()
    ↓
config.config_parameters.get_parameter()
    ↓
config.config_core.get_config_manager()
```

---

### Rate Limiting Design

**Purpose:** Prevent DoS without threading locks

**Why Not Locks:**
- Lambda is single-threaded (AP-08)
- Locks add overhead (~50ns per operation)
- False sense of thread safety
- Rate limiting more appropriate

**Implementation:**
```python
# Sliding window (1000ms)
self._rate_limiter = deque(maxlen=1000)

# O(1) check
if len(self._rate_limiter) >= 1000:
    return True  # Rate limited

# O(1) add
self._rate_limiter.append(current_time_ms)
```

**Benefits:**
- No threading primitives (AP-08 compliant)
- Fast: ~5μs per check
- Effective DoS prevention
- Statistics tracking

---

### Singleton Pattern

**Gateway Registry (Preferred):**
```python
import gateway
manager = gateway.singleton_get('config_manager')
if manager is None:
    manager = ConfigurationCore()
    gateway.singleton_register('config_manager', manager)
```

**Module-Level Fallback:**
```python
_config_core = None

def get_config_manager():
    global _config_core
    if _config_core is None:
        _config_core = ConfigurationCore()
    return _config_core
```

**Why Two Approaches:**
1. Gateway registry is preferred (centralized)
2. Module-level fallback for early bootstrap
3. Handles circular import scenarios
4. Ensures single instance

---

## Debug Integration

### Debug Logging

**Scope:** CONFIG  
**Operations:** All operations logged when enabled

**Example:**
```python
gateway.debug_log("CONFIG", "CONFIG", "Configuration reset")
gateway.debug_log("CONFIG", "CONFIG", "Rate limit exceeded", 
                count=self._rate_limited_count)
```

### Timing Measurements

**Enabled via:** `CONFIG_DEBUG_TIMING=true`

**Example:**
```python
with gateway.debug_timing("CONFIG", "CONFIG", "reset"):
    # Reset operations
    pass
```

**Environment Variables:**
```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Enable logging
CONFIG_DEBUG_TIMING=true         # Enable timing
```

---

## Performance

### Operation Timing

| Operation | Time | Notes |
|-----------|------|-------|
| `__init__()` | ~10μs | First initialization |
| `_check_rate_limit()` | ~5μs | Per operation |
| `reset()` | ~50μs | Includes logging |
| `get_stats()` | ~2μs | Dictionary creation |
| `get_config_manager()` | ~5μs | After registration |
| `get_config_manager()` (first) | ~100μs | Registration overhead |

### Memory Usage

- Empty manager: ~8KB
- Per parameter: ~200 bytes
- Rate limiter: ~8KB (1000 entries)
- Total (100 params): ~28KB

---

## Error Scenarios

### Rate Limiting

**Scenario:** More than 1000 operations in 1 second

**Behavior:**
- Operation blocked
- Counter incremented
- Debug logged (if enabled)
- Returns False or default value

**Recovery:** Automatic after 1 second

### Initialization Failure

**Scenario:** Exception during reset()

**Behavior:**
- Exception caught
- Error logged
- Returns False
- State partially reset

**Recovery:** Manual reset() call

### Gateway Unavailable

**Scenario:** Gateway import fails

**Behavior:**
- Falls back to module-level singleton
- Continues operation
- No error thrown

**Recovery:** Automatic fallback

---

## Dependencies

**Internal:**
- `config.config_state` - ConfigurationState, ConfigurationVersion
- `config.config_validator` - ConfigurationValidator

**Gateway:**
- `gateway.debug_log()` - Debug logging
- `gateway.debug_timing()` - Timing context
- `gateway.log_error()` - Error logging
- `gateway.singleton_get()` - Registry lookup
- `gateway.singleton_register()` - Registry registration

---

## Changelog

### 2025-12-09_1
- Refactored into config module
- Added debug integration
- Removed threading lock (AP-08 compliance)
- Added rate limiting (1000 ops/sec)
- Added get_stats() method
- Simplified to core functionality only

### 2025-10-22_1 (Previous)
- Added SINGLETON pattern
- Removed threading.Lock
- Added rate limiting
- Added reset() operation

---

**END OF DOCUMENTATION**
