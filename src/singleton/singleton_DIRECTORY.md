# singleton/ Directory

**Version:** 2025-12-13_1  
**Purpose:** Singleton instance management with hierarchical debug support  
**Module:** Singleton (SINGLETON interface)

---

## Files

### __init__.py (39 lines)
Module initialization - exports all public singleton functions

**Exports:**
- SingletonOperation, SingletonCore, get_singleton_manager (from singleton_manager)
- Implementation functions (from singleton_core)

---

### singleton_manager.py (300 lines)
Singleton instance manager with rate limiting and lifecycle management

**Classes:**
- SingletonOperation - Enum of all operations
- SingletonCore - Singleton instance manager

**Functions:**
- get_singleton_manager() - Singleton instance accessor (ironic!)

**Features:**
- Manages object instances (classes, managers, services)
- Factory pattern support for lazy initialization
- Rate limiting (1000 ops/sec)
- SINGLETON pattern (LESS-18)
- Debug integration (SINGLETON scope)
- Statistics tracking
- Access count monitoring
- Creation time tracking
- Memory estimation

**Key Methods:**
- get() - Get or create singleton instance with optional factory
- set() - Set singleton instance
- has() - Check if singleton exists
- delete() - Delete singleton instance
- clear() - Clear all singleton instances
- get_stats() - Get comprehensive statistics
- reset() - Reset manager state
- reset_all() - Legacy clear operation
- exists() - Legacy has operation

**SINGLETON vs CACHE Distinction:**
- SINGLETON: Object instances (managers, classes, services)
- CACHE: Data values (strings, dicts, with TTL/LRU)

**Compliance:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern (ironic self-reference!)
- LESS-21: Rate limiting for DoS protection

---

### singleton_core.py (242 lines)
Gateway implementation functions for singleton interface

**Functions:**
- execute_singleton_operation() - Universal operation executor
- get_implementation() - Get or create singleton
- set_implementation() - Set singleton
- has_implementation() - Check existence
- delete_implementation() - Delete singleton
- clear_implementation() - Clear all
- get_stats_implementation() - Get statistics
- reset_implementation() - Reset manager

**Features:**
- Gateway-facing implementation layer
- Debug integration with correlation ID support
- SINGLETON manager usage
- Parameter validation
- Error handling and exception propagation

---

### singleton_convenience.py (171 lines)
Convenience accessor functions for common singletons

**Functions:**
- get_named_singleton() - Universal singleton accessor
- get_cost_protection() - Cost protection singleton
- get_cache_manager() - Cache manager singleton
- get_security_validator() - Security validator singleton
- get_unified_validator() - Unified validator singleton
- get_config_manager() - Config manager singleton
- get_memory_manager() - Memory manager singleton
- get_lambda_cache() - Lambda cache singleton
- get_response_cache() - Response cache singleton
- get_circuit_breaker_manager() - Circuit breaker manager singleton
- get_response_processor() - Response processor singleton
- get_lambda_optimizer() - Lambda optimizer singleton
- get_response_metrics_manager() - Response metrics manager singleton
- has_singleton() - Check singleton existence
- delete_singleton() - Delete singleton
- clear_all_singletons() - Clear all singletons
- get_singleton_stats() - Get statistics

**Purpose:**
Provides semantic named accessors for commonly-used singletons, eliminating the need to remember exact singleton keys.

---

### singleton_memory.py (260 lines)
Memory monitoring and optimization utilities

**Functions:**
- get_memory_stats() - Get current memory statistics
- get_comprehensive_memory_stats() - Comprehensive memory + GC stats
- check_lambda_memory_compliance() - Check 128MB compliance
- force_memory_cleanup() - Force aggressive cleanup
- optimize_memory() - Multi-strategy optimization
- force_comprehensive_memory_cleanup() - All cleanup strategies
- emergency_memory_preserve() - Emergency preservation mode

**Features:**
- Lambda 128MB compliance checking
- Garbage collection statistics
- Memory pressure detection
- Multi-level cleanup strategies
- Emergency mode for critical situations
- Standardized response handlers

**Purpose:**
Provides comprehensive memory monitoring and cleanup capabilities essential for staying within Lambda's 128MB limit.

---

## Architecture

### SUGA Pattern Compliance
```
Gateway Layer (gateway/wrappers/gateway_wrappers_singleton.py)
    ↓
Interface Layer (interface/interface_singleton.py)
    ↓
Implementation Layer (singleton/singleton_core.py)
    ↓
Manager Layer (singleton/singleton_manager.py)
```

### Import Patterns

**Public (from other modules):**
```python
import singleton

# Access public functions
singleton.get_implementation(name='cache_manager')
singleton.set_implementation(name='config', instance=config_obj)
```

**Private (within singleton module):**
```python
from singleton.singleton_manager import get_singleton_manager
```

**Convenience (recommended):**
```python
from singleton.singleton_convenience import get_cache_manager, get_config_manager

# Semantic accessors
cache = get_cache_manager()
config = get_config_manager()
```

---

## Debug Integration

### Hierarchical Debug Control

**Master Switch:**
- DEBUG_MODE - Enables all debugging

**Scope Switches:**
- SINGLETON_DEBUG_MODE - Singleton debug logging
- SINGLETON_DEBUG_TIMING - Singleton timing measurements

**Debug Points:**
- Instance creation (factory calls)
- Instance retrieval
- Instance deletion
- Clear operations
- Existence checks
- Statistics gathering
- Rate limit enforcement
- Access count tracking

### Debug Output Examples

```
[abc123] [SINGLETON-DEBUG] Creating new instance (name=cache_manager, has_factory=True)
[abc123] [SINGLETON-TIMING] factory:cache_manager: 5.67ms
[abc123] [SINGLETON-DEBUG] Instance created (name=cache_manager, instance_type=CacheManager)
[abc123] [SINGLETON-DEBUG] Instance retrieved (name=cache_manager, access_count=5)
[abc123] [SINGLETON-DEBUG] Setting instance (name=config_manager, instance_type=ConfigManager)
[abc123] [SINGLETON-DEBUG] Instance set successfully (name=config_manager)
[abc123] [SINGLETON-DEBUG] Existence check (name=security_validator, exists=True)
[abc123] [SINGLETON-DEBUG] Deleting instance (name=temp_cache)
[abc123] [SINGLETON-DEBUG] Instance deleted (name=temp_cache)
[abc123] [SINGLETON-DEBUG] Clearing all instances (count=12)
[abc123] [SINGLETON-DEBUG] All instances cleared
[abc123] [SINGLETON-DEBUG] Getting statistics (total_singletons=12, total_memory_kb=45.3)
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import singleton_get, singleton_set, singleton_has

# Get or create with factory
cache = singleton_get('cache_manager', factory_func=CacheManager)

# Set directly
singleton_set('config', config_instance)

# Check existence
if singleton_has('security_validator'):
    validator = singleton_get('security_validator')
```

### Via Convenience Functions (Recommended)
```python
from singleton.singleton_convenience import (
    get_cache_manager,
    get_config_manager,
    get_security_validator
)

# Semantic accessors
cache = get_cache_manager()
config = get_config_manager()
validator = get_security_validator()
```

### Direct (Testing Only)
```python
import singleton

# Get or create
instance = singleton.get_implementation(
    name='my_manager',
    factory_func=lambda: MyManager()
)

# Set
singleton.set_implementation(name='config', instance=config_obj)

# Check existence
exists = singleton.has_implementation(name='my_manager')
```

---

## Factory Pattern

### Lazy Initialization

```python
from gateway import singleton_get

def create_expensive_manager():
    """Factory function for expensive initialization."""
    manager = ExpensiveManager()
    manager.load_large_dataset()
    manager.initialize_connections()
    return manager

# First call - creates instance (slow)
manager = singleton_get('expensive_manager', factory_func=create_expensive_manager)

# Subsequent calls - returns cached instance (fast)
manager = singleton_get('expensive_manager')  # No factory needed
```

**Benefits:**
- Defers expensive initialization until first use
- Ensures only one instance exists
- Subsequent access is fast (no recreation)
- Thread-safe in Lambda's single-threaded environment

---

## Statistics

### Singleton Statistics
- total_singletons - Number of managed instances
- singleton_names - List of all singleton names
- singleton_types - Type of each singleton
- creation_times - When each singleton was created
- access_counts - How many times each accessed
- estimated_memory_bytes - Total memory (shallow)
- estimated_memory_kb - Memory in KB
- estimated_memory_mb - Memory in MB
- rate_limited_count - Rate limit hits
- timestamp - When stats were collected

### Memory Statistics
- rss_mb - Resident set size in MB
- available_mb - Memory available (128 - used)
- percent_used - Percentage of Lambda limit used
- compliant - Whether within 128MB limit
- gc_collections - Garbage collection counts
- tracked_objects - Number of GC-tracked objects
- pressure_level - 'normal' or 'high'

---

## SINGLETON vs CACHE

### When to Use SINGLETON

**Use SINGLETON for:**
- Manager instances (CacheManager, ConfigManager)
- Service objects (SecurityValidator, CircuitBreaker)
- Resource pools (ConnectionPool, ThreadPool)
- Stateful controllers (RateLimiter, LoadBalancer)
- Complex objects with initialization logic

**Example:**
```python
singleton_set('cache_manager', CacheManager())
singleton_set('config', ConfigLoader().load())
```

### When to Use CACHE

**Use CACHE for:**
- API response data
- Computed values
- Temporary data with TTL
- Frequently accessed primitives
- Data that should expire

**Example:**
```python
cache_set('user:123', user_data, ttl=300)
cache_set('api_response', response, ttl=60)
```

---

## Lifecycle Management

### Reset for Testing

```python
from gateway import singleton_reset, singleton_clear

# Clear all instances
count = singleton_clear()
print(f"Cleared {count} singletons")

# Reset manager state (rate limiting)
success = singleton_reset()
```

**Use Cases:**
- Unit test isolation
- Integration test setup
- Memory pressure relief
- Hot reload scenarios

---

## Related Files

**Interface:**
- interface/interface_singleton.py - Interface router

**Gateway:**
- gateway/wrappers/gateway_wrappers_singleton.py - Gateway wrappers

**Debug:**
- debug/debug_config.py - Debug configuration
- debug/debug_core.py - Debug logging and timing

---

## File Size Summary

| File | Lines | Status |
|------|-------|--------|
| __init__.py | 39 | ✓ Well under limit |
| singleton_manager.py | 300 | ✓ At 300 target |
| singleton_core.py | 242 | ✓ Well under limit |
| singleton_convenience.py | 171 | ✓ Well under limit |
| singleton_memory.py | 260 | ✓ Well under limit |
| **Total** | **1,012** | **5 files** |

---

## Changelog

### 2025-12-13_1
- Split monolithic singleton_core.py into modular structure
- Added hierarchical debug integration (SINGLETON scope)
- Integrated debug_log() and debug_timing() throughout
- Added correlation ID support for debug tracking
- Created module __init__.py for clean imports
- Updated interface to use module import pattern
- All files under 300-line target (max 300 lines)
- Preserved factory pattern and lazy initialization
- Maintained backward compatibility with legacy operations
- Clarified SINGLETON vs CACHE distinction
- Kept singleton_convenience.py and singleton_memory.py as utility files
