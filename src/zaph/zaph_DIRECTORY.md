# ZAPH Interface Directory

**Interface ID:** INT-16  
**Version:** 2025-12-14_1  
**Purpose:** Zero-Abstraction Path for Hot operations

---

## Overview

The ZAPH (Zero-Abstraction Path for Hot operations) interface provides high-performance operation routing with intelligent heat detection, LRU caching, and LUGS integration for Lambda-optimized execution.

## Directory Structure

```
zaph/
├── __init__.py              - Public interface with debug tracing
├── zaph_core.py            - Core implementation (LUGSAwareFastPath)
└── function/               - Function documentation (to be created)
```

## Key Features

1. **Heat-Based Operation Tracking**
   - COLD: <5 calls
   - WARM: 5-19 calls
   - HOT: 20-99 calls
   - CRITICAL: 100+ calls

2. **LRU Cache with Eviction**
   - Configurable cache size (default: 100)
   - Least recently used eviction
   - Auto-caching for warm operations

3. **LUGS Integration**
   - Protects hot modules from unloading
   - Tracks module dependencies
   - Memory-aware operation

4. **Debug Tracing**
   - Hierarchical control via ZAPH_DEBUG_MODE
   - Correlation ID support
   - Timing measurements

## Public Functions

All functions exported via gateway with `zaph_` prefix:

- `zaph_track_operation()` - Track operation heat
- `zaph_execute()` - Execute with fast path
- `zaph_register()` - Register fast path
- `zaph_get()` - Get fast path function
- `zaph_is_hot()` - Check if operation is hot
- `zaph_should_protect()` - Check module protection
- `zaph_heat_level()` - Get heat level
- `zaph_stats()` - Get statistics
- `zaph_hot_operations()` - Get hot ops list
- `zaph_cached_operations()` - Get cached ops
- `zaph_configure()` - Configure system
- `zaph_config()` - Get configuration
- `zaph_prewarm()` - Prewarm cache
- `zaph_prewarm_common()` - Prewarm common ops
- `zaph_clear()` - Clear cache
- `zaph_reset_counts()` - Reset call counts
- `zaph_reset_stats()` - Reset statistics
- `zaph_optimize()` - Run optimization

## Configuration

Via `user_config.py`:

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

## Environment Variables

- `DEBUG_MODE=true` - Enable master debug
- `ZAPH_DEBUG_MODE=true` - Enable ZAPH-specific debug
- `ZAPH_PREWARM_ON_COLD_START=true` - Prewarm on Lambda init

## Usage Examples

### Via Gateway (Recommended)

```python
from gateway import (
    zaph_track_operation,
    zaph_execute,
    zaph_register,
    zaph_stats
)

# Track operation
heat = zaph_track_operation('cache_get', 15.5, 'cache.cache_core')

# Execute with fast path
result = zaph_execute('cache_get', get_func, key='user_123')

# Register fast path
zaph_register('cache_get', fast_get_func, 'cache.cache_core')

# Get stats
stats = zaph_stats()
```

### Direct Import (Not Recommended - Use Gateway)

```python
from zaph import (
    track_operation,
    execute_fast_path,
    register_fast_path
)

# Same functions without zaph_ prefix
heat = track_operation('op_key', 10.0)
```

## Architecture Compliance

- ✅ SUGA: All cross-interface via gateway
- ✅ LMMS: Lazy import in __init__.py
- ✅ DD-1: Dispatch dictionary in interface
- ✅ Debug: Hierarchical with correlation IDs
- ✅ File Size: All files <350 lines

## Performance Targets

- **Hot Path Execution:** <5ms overhead
- **Cache Lookup:** O(1)
- **Heat Detection:** <1ms per operation
- **Prewarm Time:** <50ms for 10 operations

## Integration Points

### Lambda Preload
- Optional prewarming via `ZAPH_PREWARM_ON_COLD_START`
- Loads common operations during INIT phase

### Cache Interface
- Can protect cache operations from eviction
- Tracks cache access patterns

### Metrics Interface
- Reports heat levels and cache stats
- Tracks fast path hit rates

### Singleton Interface  
- Coordinates with LUGS module protection
- Prevents unloading of hot modules

## Testing

Use TEST interface via gateway:

```python
from gateway import test_component_operation

# Test ZAPH operations
result = test_component_operation(
    component='zaph',
    operation='track_operation',
    scenario='valid',
    operation_key='test_op',
    duration_ms=10.0
)
```

## Maintenance

- Review heat thresholds quarterly
- Monitor cache hit rates
- Adjust cache size based on usage patterns
- Optimize stale operation cleanup

---

**Version:** 2025-12-14_1  
**Interface:** INT-16 (ZAPH)  
**Status:** Active  
**Files:** 2 (core, __init__)
