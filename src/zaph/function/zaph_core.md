# zaph_core.py

**Version:** 2025-12-14_1  
**Module:** ZAPH Core  
**Layer:** Core  
**Lines:** 420

---

## Purpose

ZAPH (Zero-Abstraction Path for Hot operations) core implementation. Provides intelligent operation heat tracking, LRU caching, LUGS module protection, and Lambda cold start optimization.

---

## Architecture

**ZAPH Pattern:**
```
Gateway → Interface → zaph_core.py (LUGSAwareFastPath)
```

**Heat-Based Optimization:**
- COLD: <5 calls - no optimization
- WARM: 5-19 calls - eligible for caching
- HOT: 20-99 calls - auto-cached, module protected
- CRITICAL: 100+ calls - always protected

---

## Classes

### OperationHeatLevel

**Purpose:** Enum for operation heat levels

**Signature:**
```python
class OperationHeatLevel(Enum):
    COLD = "cold"         # <5 calls
    WARM = "warm"         # 5-19 calls
    HOT = "hot"           # 20-99 calls
    CRITICAL = "critical" # 100+ calls
```

**Usage:**
```python
heat = track_operation('cache_get', 15.5)
if heat == OperationHeatLevel.HOT:
    # Operation is hot, protect module
```

**Keywords:** enum, heat-level, classification, threshold

---

### OperationMetrics

**Purpose:** Dataclass for operation tracking metrics

**Signature:**
```python
@dataclass
class OperationMetrics:
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    last_call_time: float = 0.0
    last_access_time: float = 0.0
    heat_level: OperationHeatLevel = OperationHeatLevel.COLD
    source_module: Optional[str] = None
```

**Fields:**
- `call_count` - Total times operation called
- `total_duration_ms` - Cumulative execution time
- `avg_duration_ms` - Average execution time per call
- `last_call_time` - Timestamp of last execution
- `last_access_time` - Timestamp of last access (for LRU)
- `heat_level` - Current heat classification
- `source_module` - Module name for LUGS protection

**Keywords:** dataclass, metrics, tracking, statistics, LRU

---

### LUGSAwareFastPath

**Purpose:** Core fast path system with heat detection, LRU eviction, LUGS protection

**Signature:**
```python
class LUGSAwareFastPath:
    def __init__(self):
        # Thread-safe operation tracking
        # LRU cache for hot operations
        # LUGS module protection
        # Configurable thresholds
```

**Features:**
- Thread-safe operation tracking
- Automatic heat-based caching
- LRU eviction when cache full
- LUGS module protection for hot operations
- Prewarming for cold starts
- Comprehensive statistics

**Configuration Defaults:**
```python
enabled: True
cache_size_limit: 100
warm_threshold: 5
hot_threshold: 20
critical_threshold: 100
```

**Keywords:** fast-path, LUGS, LRU, heat-detection, cache, optimization, thread-safe

---

## Functions

### \_\_init\_\_()

**Purpose:** Initialize fast path system with defaults

**Signature:**
```python
def __init__(self):
```

**Behavior:**
1. Creates thread lock for safety
2. Initializes operation metrics dict
3. Initializes hot paths cache
4. Sets protected modules set
5. Configures default thresholds
6. Resets statistics

**Thread Safety:** Yes (creates lock)

**Performance:** <1ms initialization

**Usage:**
```python
# Via singleton (recommended)
from zaph import _get_instance
fast_path = _get_instance()

# Direct (not recommended)
from zaph.zaph_core import LUGSAwareFastPath
fast_path = LUGSAwareFastPath()
```

**Keywords:** initialization, constructor, configuration, thread-safe

---

### track_operation()

**Purpose:** Track operation execution and update heat level

**Signature:**
```python
def track_operation(
    operation_key: str,
    duration_ms: float,
    source_module: Optional[str] = None
) -> OperationHeatLevel:
```

**Parameters:**
- `operation_key` - Unique operation identifier (e.g., 'cache_get')
- `duration_ms` - Execution time in milliseconds
- `source_module` - Module name for LUGS protection (optional)

**Returns:**
`OperationHeatLevel` - Updated heat level (COLD, WARM, HOT, CRITICAL)

**Behavior:**
1. Increments call count for operation
2. Updates metrics (duration, avg, timestamps)
3. Calculates new heat level based on call count
4. Protects module if operation becomes HOT/CRITICAL
5. Records heat promotion in statistics
6. Returns new heat level

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms per call

**Usage:**
```python
from gateway import zaph_track_operation

# Track cache operation
heat = zaph_track_operation('cache_get', 15.5, 'cache.cache_core')

if heat == OperationHeatLevel.HOT:
    print("Operation is hot!")
```

**Side Effects:**
- Updates `_operation_metrics`
- Updates `_call_counts`
- Updates `_stats['total_operations']`
- Updates `_stats['heat_promotions']` (on promotion)
- Adds module to `_protected_modules` (if HOT/CRITICAL)

**Keywords:** tracking, heat-detection, metrics, LUGS-protection, monitoring

---

### execute_fast_path()

**Purpose:** Execute operation with automatic fast-path optimization and LRU caching

**Signature:**
```python
def execute_fast_path(
    operation_key: str,
    func: Callable,
    *args,
    **kwargs
) -> Any:
```

**Parameters:**
- `operation_key` - Unique operation identifier
- `func` - Function to execute
- `*args` - Positional arguments for function
- `**kwargs` - Keyword arguments for function

**Returns:**
`Any` - Result from function execution

**Behavior:**
1. Checks if fast path enabled
2. Checks if operation in hot paths cache
3. Updates LRU access time if cached
4. Executes function (outside lock for performance)
5. Tracks execution time
6. Auto-caches if operation becomes warm (≥5 calls)
7. Estimates time saved for cached operations
8. Returns function result

**Thread Safety:** Yes (minimal locking)

**Performance:**
- Cached: ~25ns overhead (ZAPH optimization)
- Uncached: ~130ns overhead
- Auto-caches when call_count ≥ warm_threshold

**Usage:**
```python
from gateway import zaph_execute

# Execute with fast-path optimization
def slow_operation(x, y):
    return x + y

result = zaph_execute('add_numbers', slow_operation, 5, 10)
# After 5 calls, automatically cached
```

**Side Effects:**
- Updates `_call_counts`
- Updates `_operation_metrics`
- Updates `_stats['fast_path_hits']` or `_stats['fast_path_misses']`
- May add to `_hot_paths` (auto-cache)
- May trigger LRU eviction (if cache full)
- Updates `_stats['time_saved_ms']` (if cached)

**Keywords:** execution, fast-path, auto-cache, LRU, performance, optimization

---

### _add_to_hot_paths()

**Purpose:** Add operation to hot paths cache with LRU eviction (private, called within lock)

**Signature:**
```python
def _add_to_hot_paths(self, operation_key: str, func: Callable) -> None:
```

**Parameters:**
- `operation_key` - Operation identifier
- `func` - Function to cache

**Returns:** None

**Behavior:**
1. Checks if cache at capacity
2. If full, finds least recently accessed operation
3. Evicts LRU operation from cache
4. Adds new operation to cache
5. Increments eviction counter

**Thread Safety:** Caller must hold lock

**Performance:** O(n) for LRU search (n = cache size)

**LRU Algorithm:**
Uses `last_access_time` from metrics to find least recently used operation.

**Usage:**
```python
# Internal use only - called by execute_fast_path()
# Do not call directly
```

**Keywords:** private, LRU, eviction, cache-management, internal

---

### _calculate_heat_level()

**Purpose:** Calculate heat level based on call count (private)

**Signature:**
```python
def _calculate_heat_level(self, call_count: int) -> OperationHeatLevel:
```

**Parameters:**
- `call_count` - Number of times operation called

**Returns:**
`OperationHeatLevel` - Calculated heat level

**Behavior:**
Compares call_count against thresholds:
- ≥100: CRITICAL
- ≥20: HOT
- ≥5: WARM
- <5: COLD

**Thread Safety:** No locking needed (pure calculation)

**Performance:** <0.1ms (simple comparison)

**Thresholds (configurable):**
```python
WARM: 5 calls
HOT: 20 calls
CRITICAL: 100 calls
```

**Usage:**
```python
# Internal use only
# Do not call directly
```

**Keywords:** private, calculation, threshold, classification, heat-level

---

### _protect_module()

**Purpose:** Protect hot module from LUGS unloading (private)

**Signature:**
```python
def _protect_module(self, module_name: Optional[str]) -> None:
```

**Parameters:**
- `module_name` - Name of module to protect (optional)

**Returns:** None

**Behavior:**
1. Checks if module_name provided
2. Checks if already protected (no duplicate protection)
3. Adds module to protected set
4. Increments protection counter

**Thread Safety:** Caller must hold lock

**Performance:** O(1) set lookup and addition

**Usage:**
```python
# Internal use only - called by track_operation()
# Do not call directly
```

**Side Effects:**
- Adds to `_protected_modules`
- Updates `_stats['hot_modules_protected']`

**Keywords:** private, LUGS, module-protection, hot-operations, internal

---

### register_fast_path()

**Purpose:** Manually register fast path for operation (pre-optimization)

**Signature:**
```python
def register_fast_path(
    operation_key: str,
    fast_func: Callable,
    source_module: Optional[str] = None
) -> None:
```

**Parameters:**
- `operation_key` - Operation identifier
- `fast_func` - Optimized function to register
- `source_module` - Module name for LUGS protection (optional)

**Returns:** None

**Behavior:**
1. Adds function to hot paths cache
2. Creates metrics entry if doesn't exist
3. Sets heat level to HOT
4. Protects module if provided
5. Updates access time for LRU

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms

**Usage:**
```python
from gateway import zaph_register

# Pre-register known hot operation
def fast_cache_get(key):
    # Optimized implementation
    return cache[key]

zaph_register('cache_get', fast_cache_get, 'cache.cache_core')
```

**Use Cases:**
- Pre-register known hot operations
- Lambda cold start optimization
- Manual fast-path definition

**Keywords:** registration, manual, pre-optimization, hot-path, LUGS-protection

---

### get_fast_path()

**Purpose:** Get fast path function if available

**Signature:**
```python
def get_fast_path(self, operation_key: str) -> Optional[Callable]:
```

**Parameters:**
- `operation_key` - Operation identifier

**Returns:**
- `Callable` if fast path exists
- `None` if not cached

**Behavior:**
1. Checks if operation in hot paths
2. Updates LRU access time if found
3. Increments hit counter
4. Returns cached function or None

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms (dict lookup)

**Usage:**
```python
from gateway import zaph_get

# Check if fast path available
fast_func = zaph_get('cache_get')
if fast_func:
    result = fast_func(key)
else:
    result = slow_func(key)
```

**Keywords:** retrieval, lookup, fast-path, cache-access, LRU-update

---

### is_hot_operation()

**Purpose:** Check if operation is hot (HOT or CRITICAL)

**Signature:**
```python
def is_hot_operation(self, operation_key: str) -> bool:
```

**Parameters:**
- `operation_key` - Operation identifier

**Returns:**
- `True` if HOT or CRITICAL
- `False` if COLD, WARM, or not tracked

**Behavior:**
1. Checks if operation has metrics
2. Retrieves heat level
3. Returns True if HOT or CRITICAL

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms

**Usage:**
```python
from gateway import zaph_is_hot

if zaph_is_hot('cache_get'):
    print("Cache get is hot operation")
```

**Keywords:** check, hot-operation, heat-level, query

---

### should_protect_module()

**Purpose:** Check if module is protected from LUGS unloading

**Signature:**
```python
def should_protect_module(self, module_name: str) -> bool:
```

**Parameters:**
- `module_name` - Module name to check

**Returns:**
- `True` if protected
- `False` if not protected

**Behavior:**
1. Checks if module in protected set
2. Returns boolean result

**Thread Safety:** Yes (uses lock)

**Performance:** O(1) set lookup

**Usage:**
```python
from gateway import zaph_should_protect

if zaph_should_protect('cache.cache_core'):
    print("Cache core is protected from unloading")
```

**Integration:**
Used by LUGS to determine which modules to keep loaded.

**Keywords:** check, LUGS, module-protection, query, unloading

---

### get_heat_level()

**Purpose:** Get operation heat level

**Signature:**
```python
def get_heat_level(self, operation_key: str) -> OperationHeatLevel:
```

**Parameters:**
- `operation_key` - Operation identifier

**Returns:**
`OperationHeatLevel` - COLD, WARM, HOT, or CRITICAL

**Behavior:**
1. Checks if operation has metrics
2. Returns heat level (defaults to COLD if not found)

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms

**Usage:**
```python
from gateway import zaph_heat_level

heat = zaph_heat_level('cache_get')
print(f"Cache get heat: {heat.value}")
```

**Keywords:** query, heat-level, status, monitoring

---

### get_stats()

**Purpose:** Get comprehensive fast path statistics

**Signature:**
```python
def get_stats(self) -> Dict[str, Any]:
```

**Parameters:** None

**Returns:**
```python
{
    'total_operations': int,
    'fast_path_hits': int,
    'fast_path_misses': int,
    'cache_evictions': int,
    'hot_modules_protected': int,
    'heat_promotions': int,
    'time_saved_ms': float,
    'total_tracked_operations': int,
    'registered_fast_paths': int,
    'protected_modules': int,
    'cold_operations': int,
    'warm_operations': int,
    'hot_operations': int,
    'critical_operations': int,
    'hit_rate_percent': float,
    'avg_time_saved_ms': float,
    'cache_size_limit': int,
    'enabled': bool
}
```

**Behavior:**
1. Copies current statistics
2. Calculates heat level distribution
3. Calculates hit rate percentage
4. Calculates average time saved
5. Returns comprehensive stats dict

**Thread Safety:** Yes (uses lock)

**Performance:** O(n) where n = tracked operations

**Usage:**
```python
from gateway import zaph_stats

stats = zaph_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
print(f"Hot operations: {stats['hot_operations']}")
print(f"Time saved: {stats['time_saved_ms']:.2f}ms")
```

**Keywords:** statistics, monitoring, metrics, performance, hit-rate, diagnostics

---

### get_hot_operations()

**Purpose:** Get most frequently called operations

**Signature:**
```python
def get_hot_operations(self, limit: int = 10) -> list:
```

**Parameters:**
- `limit` - Maximum number of operations to return (default: 10)

**Returns:**
```python
[
    ('operation_key', call_count),
    ...
]
```

**Behavior:**
1. Sorts operations by call count (descending)
2. Returns top N operations with counts

**Thread Safety:** Yes (uses lock)

**Performance:** O(n log n) for sorting

**Usage:**
```python
from gateway import zaph_hot_operations

hot_ops = zaph_hot_operations(limit=5)
for op, count in hot_ops:
    print(f"{op}: {count} calls")
```

**Keywords:** query, hot-operations, ranking, frequency, monitoring

---

### get_cached_operations()

**Purpose:** Get list of operations in hot path cache

**Signature:**
```python
def get_cached_operations(self) -> list:
```

**Parameters:** None

**Returns:**
`list` - List of cached operation keys

**Behavior:**
Returns keys from hot paths dictionary.

**Thread Safety:** Yes (uses lock)

**Performance:** O(n) where n = cache size

**Usage:**
```python
from gateway import zaph_cached_operations

cached = zaph_cached_operations()
print(f"Cached operations: {cached}")
```

**Keywords:** query, cache, operations, monitoring

---

### configure()

**Purpose:** Configure fast path system parameters

**Signature:**
```python
def configure(
    enabled: Optional[bool] = None,
    cache_size: Optional[int] = None,
    warm_threshold: Optional[int] = None,
    hot_threshold: Optional[int] = None,
    critical_threshold: Optional[int] = None
) -> Dict[str, Any]:
```

**Parameters:**
- `enabled` - Enable/disable fast path (optional)
- `cache_size` - Maximum cache size (optional)
- `warm_threshold` - Calls needed for WARM (optional)
- `hot_threshold` - Calls needed for HOT (optional)
- `critical_threshold` - Calls needed for CRITICAL (optional)

**Returns:**
Current configuration dict (from `get_config()`)

**Behavior:**
1. Updates enabled flag (clears cache if disabling)
2. Updates cache size (trims if needed)
3. Updates heat thresholds
4. Returns current configuration

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms (O(n) if trimming cache)

**Usage:**
```python
from gateway import zaph_configure

# Increase cache size
config = zaph_configure(cache_size=200)

# Adjust thresholds
config = zaph_configure(warm_threshold=10, hot_threshold=50)

# Disable fast path
config = zaph_configure(enabled=False)
```

**Keywords:** configuration, settings, thresholds, cache-size, enable-disable

---

### get_config()

**Purpose:** Get current fast path configuration

**Signature:**
```python
def get_config(self) -> Dict[str, Any]:
```

**Parameters:** None

**Returns:**
```python
{
    'enabled': bool,
    'cache_size_limit': int,
    'warm_threshold': int,
    'hot_threshold': int,
    'critical_threshold': int
}
```

**Behavior:**
Returns current configuration values.

**Thread Safety:** Yes (uses lock)

**Performance:** <1ms

**Usage:**
```python
from gateway import zaph_config

config = zaph_config()
print(f"Enabled: {config['enabled']}")
print(f"Cache size: {config['cache_size_limit']}")
```

**Keywords:** configuration, query, settings, parameters

---

### prewarm()

**Purpose:** Prewarm cache with operation keys (for Lambda cold starts)

**Signature:**
```python
def prewarm(self, operation_keys: list) -> int:
```

**Parameters:**
- `operation_keys` - List of operation keys to prewarm

**Returns:**
`int` - Number of operations prewarmed

**Behavior:**
1. Iterates through operation keys
2. Creates metrics entry for each (if space available)
3. Sets heat level to WARM
4. Counts successful prewarms

**Thread Safety:** Yes (uses lock)

**Performance:** O(n) where n = len(operation_keys)

**Usage:**
```python
from gateway import zaph_prewarm

# Prewarm common operations
ops = ['cache_get', 'cache_set', 'log_info']
count = zaph_prewarm(ops)
print(f"Prewarmed {count} operations")
```

**Use Cases:**
- Lambda cold start optimization
- Initialize cache before traffic
- Reduce initial latency

**Keywords:** prewarming, cold-start, initialization, optimization, Lambda

---

### prewarm_common()

**Purpose:** Prewarm with predefined common operations

**Signature:**
```python
def prewarm_common(self) -> int:
```

**Parameters:** None

**Returns:**
`int` - Number of operations prewarmed

**Behavior:**
Prewarms these operations:
- cache_get
- cache_set
- logging_log_info
- logging_log_error
- metrics_record_metric
- security_generate_correlation_id
- config_get_state

**Thread Safety:** Yes (uses lock via prewarm())

**Performance:** <10ms (7 operations)

**Usage:**
```python
from gateway import zaph_prewarm_common

# Prewarm during Lambda initialization
count = zaph_prewarm_common()
print(f"Prewarmed {count} common operations")
```

**Integration:**
Called automatically if `ZAPH_PREWARM_ON_COLD_START=true` environment variable set.

**Keywords:** prewarming, common-operations, cold-start, initialization, Lambda

---

### clear_cache()

**Purpose:** Clear hot path cache

**Signature:**
```python
def clear_cache(self) -> None:
```

**Parameters:** None

**Returns:** None

**Behavior:**
Clears all entries from hot paths cache.

**Thread Safety:** Yes (uses lock)

**Performance:** O(1)

**Usage:**
```python
from gateway import zaph_clear

# Clear cache (for testing or reset)
zaph_clear()
```

**Use Cases:**
- Testing
- Manual cache invalidation
- System reset

**Keywords:** cache, clear, reset, invalidation

---

### reset_call_counts()

**Purpose:** Reset operation call counts

**Signature:**
```python
def reset_call_counts(self) -> None:
```

**Parameters:** None

**Returns:** None

**Behavior:**
Clears all call count tracking.

**Thread Safety:** Yes (uses lock)

**Performance:** O(1)

**Usage:**
```python
from gateway import zaph_reset_counts

# Reset counts (for testing)
zaph_reset_counts()
```

**Use Cases:**
- Testing
- Periodic reset for fresh tracking
- Debugging

**Keywords:** reset, call-counts, tracking, testing

---

### reset_stats()

**Purpose:** Reset all statistics

**Signature:**
```python
def reset_stats(self) -> None:
```

**Parameters:** None

**Returns:** None

**Behavior:**
Resets all statistics to initial values (0 or 0.0).

**Thread Safety:** Yes (uses lock)

**Performance:** O(1)

**Usage:**
```python
from gateway import zaph_reset_stats

# Reset statistics
zaph_reset_stats()
```

**Use Cases:**
- Testing
- Periodic stats reset
- Fresh monitoring period

**Keywords:** reset, statistics, monitoring, testing

---

### optimize()

**Purpose:** Run optimization cycle - remove stale operations

**Signature:**
```python
def optimize(self) -> Dict[str, Any]:
```

**Parameters:** None

**Returns:**
```python
{
    'optimizations': int,
    'stale_removed': int
}
```

**Behavior:**
1. Finds COLD operations not called in 5 minutes
2. Removes from metrics and call counts
3. Does NOT remove from hot paths (may be prewarmed)
4. Returns count of optimizations

**Thread Safety:** Yes (uses lock)

**Performance:** O(n) where n = tracked operations

**Stale Criteria:**
- Last call >300 seconds ago
- Heat level is COLD
- Not in hot paths cache

**Usage:**
```python
from gateway import zaph_optimize

# Run optimization
result = zaph_optimize()
print(f"Removed {result['stale_removed']} stale operations")
```

**Use Cases:**
- Periodic cleanup
- Memory management
- Remove obsolete operations

**Keywords:** optimization, cleanup, stale-operations, memory-management, maintenance

---

## Patterns

### Heat-Based Auto-Caching

**Pattern:**
```python
# Automatic caching based on call frequency
for i in range(25):
    result = zaph_execute('my_op', expensive_func, arg)

# After 5 calls: Auto-cached (WARM threshold)
# After 20 calls: Hot operation (HOT threshold)
# After 100 calls: Critical operation (CRITICAL threshold)
```

**Benefits:**
- No manual cache management
- Adapts to usage patterns
- Protects hot operations

---

### Manual Fast Path Registration

**Pattern:**
```python
# Pre-register known hot operation
def optimized_cache_get(key):
    # Fast implementation
    return cache[key]

zaph_register('cache_get', optimized_cache_get, 'cache.cache_core')
```

**Use Cases:**
- Known hot operations
- Cold start optimization
- Manual performance tuning

---

### LUGS Integration

**Pattern:**
```python
# Track operation with module
heat = zaph_track_operation('cache_get', 10.5, 'cache.cache_core')

# Module protected when operation becomes HOT
if heat in [OperationHeatLevel.HOT, OperationHeatLevel.CRITICAL]:
    # Module 'cache.cache_core' protected from LUGS unloading
```

**Benefits:**
- Automatic module protection
- Prevents hot module unloading
- Maintains performance

---

### Lambda Cold Start Prewarming

**Pattern:**
```python
# In lambda_preload.py
if os.environ.get('ZAPH_PREWARM_ON_COLD_START', 'true') == 'true':
    from gateway import zaph_prewarm_common
    count = zaph_prewarm_common()
    print(f"Prewarmed {count} operations")
```

**Benefits:**
- Reduced initial latency
- Faster first requests
- Predictable performance

---

## Configuration

**Via user_config.py:**
```python
"zaph": {
    "enabled": True,
    "cache_size_limit": 100,
    "warm_threshold": 5,
    "hot_threshold": 20,
    "critical_threshold": 100,
    "prewarm_on_cold_start": True,
    "prewarm_common_operations": True,
    "track_heat_metrics": True,
    "protect_hot_modules_from_unload": True,
    "auto_optimize_interval_seconds": 300,
    "stale_operation_timeout_seconds": 300
}
```

**Via Environment Variables:**
- `DEBUG_MODE=true` - Enable master debug
- `ZAPH_DEBUG_MODE=true` - Enable ZAPH-specific debug
- `ZAPH_PREWARM_ON_COLD_START=true` - Prewarm on Lambda init

---

## Performance Characteristics

**Operation Tracking:** <1ms overhead  
**Fast Path Execution (cached):** ~25ns overhead  
**Fast Path Execution (uncached):** ~130ns overhead  
**LRU Eviction:** O(n) where n = cache size  
**Heat Calculation:** <0.1ms  
**Statistics Generation:** O(n) where n = tracked operations

**Memory Usage:**
- Per operation: ~200 bytes (metrics)
- Per cached function: ~100 bytes (reference)
- Total: ~30KB for 100 operations

---

## Thread Safety

All public methods are thread-safe using a single lock (`threading.Lock`).

**Lock Strategy:**
- Acquire lock for data structure access
- Execute operations outside lock when possible
- Minimize lock hold time for performance

---

## Related Files

**Interface:**
- interface_zaph.py - ZAPH interface router

**Gateway:**
- gateway_wrappers_zaph.py - Gateway wrappers (18 functions)
- gateway.py - Exports all zaph_* functions

**Public Interface:**
- __init__.py - Public API with debug tracing

---

## Integration Points

**LUGS:**
- Provides module protection via `should_protect_module()`
- Prevents unloading of hot modules

**Metrics:**
- Reports heat levels and cache stats
- Tracks fast path hit rates

**Lambda Preload:**
- Optional prewarming via `ZAPH_PREWARM_ON_COLD_START`
- Reduces cold start latency

---

## Changelog

### 2025-12-14_1
- Initial ZAPH core implementation
- LUGSAwareFastPath class with 25 methods
- Heat-based auto-caching (COLD/WARM/HOT/CRITICAL)
- LRU eviction for cache management
- LUGS module protection
- Prewarming support for cold starts
- Comprehensive statistics tracking
- Thread-safe operations
- Configurable thresholds

---

**END OF ZAPH_CORE DOCUMENTATION**

**Total Classes:** 3  
**Total Methods:** 25  
**Keywords:** ZAPH, fast-path, heat-detection, LRU, LUGS, optimization, Lambda, cold-start, caching, performance, thread-safe
