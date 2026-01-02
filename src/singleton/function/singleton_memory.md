# singleton_memory.md

**Version:** 2025-12-13_1  
**Purpose:** Memory monitoring and optimization utilities  
**Module:** singleton/singleton_memory.py  
**Type:** Memory Management Utilities

---

## OVERVIEW

Provides comprehensive memory monitoring and cleanup capabilities essential for staying within Lambda's 128MB limit. All functions return standardized gateway responses for consistent error handling and observability.

**Key Features:**
- Lambda 128MB compliance checking
- Garbage collection statistics
- Memory pressure detection
- Multi-level cleanup strategies
- Emergency preservation mode
- Standardized response format

---

## LAMBDA MEMORY CONSTRAINTS

**Hard Limit:** 128MB total memory per Lambda container  
**Target:** Stay under 100MB for safety margin  
**Warning Zone:** 100-120MB (high pressure)  
**Critical Zone:** 120-128MB (emergency cleanup needed)

**Memory Components:**
- Runtime overhead: ~40MB (Python + imports)
- Application code: ~10-20MB
- Available for data: ~60-80MB

---

## RESPONSE FORMAT

All functions return standardized gateway responses:

**Success Response:**
```python
{
    'success': True,
    'message': 'Memory statistics retrieved',
    'data': {
        'rss_mb': 85.5,
        'available_mb': 42.5,
        # ... operation-specific data
    },
    'correlation_id': 'abc123...',
    'timestamp': 1702500000.123
}
```

**Error Response:**
```python
{
    'success': False,
    'message': 'Failed to get memory statistics',
    'error_code': 'MEMORY_STATS_ERROR',
    'details': {
        'error': 'Error message'
    },
    'correlation_id': 'abc123...',
    'timestamp': 1702500000.123
}
```

---

## MONITORING FUNCTIONS

### get_memory_stats()

Get current memory statistics.

**Signature:**
```python
def get_memory_stats() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with memory stats

**Success Data Structure:**
```python
{
    'rss_mb': 85.5,           # Resident set size in MB
    'vms_mb': 85.5,           # Virtual memory size in MB
    'percent': 66.8,          # Percentage of 128MB limit used
    'available_mb': 42.5,     # Memory available (128 - used)
    'compliant': True         # Whether within 128MB limit
}
```

**Example:**
```python
from singleton.singleton_memory import get_memory_stats

response = get_memory_stats()

if response['success']:
    stats = response['data']
    print(f"Memory used: {stats['rss_mb']:.2f} MB")
    print(f"Available: {stats['available_mb']:.2f} MB")
    print(f"Compliant: {stats['compliant']}")
else:
    print(f"Error: {response['message']}")
```

---

### get_comprehensive_memory_stats()

Get comprehensive memory statistics including GC stats.

**Signature:**
```python
def get_comprehensive_memory_stats() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with comprehensive stats

**Success Data Structure:**
```python
{
    'memory': {
        'rss_mb': 85.5,
        'available_mb': 42.5,
        'percent_used': 66.8,
        'compliant': True
    },
    'gc': {
        'collections': [150, 10, 2],      # Per-generation GC counts
        'stats': [...],                    # GC statistics
        'tracked_objects': 12345           # Objects tracked by GC
    },
    'system': {
        'lambda_limit_mb': 128,
        'pressure_level': 'normal'         # 'normal' or 'high'
    }
}
```

**Pressure Levels:**
- `'normal'`: Memory < 100MB
- `'high'`: Memory >= 100MB

**Example:**
```python
from singleton.singleton_memory import get_comprehensive_memory_stats

response = get_comprehensive_memory_stats()

if response['success']:
    data = response['data']
    
    # Check memory
    memory = data['memory']
    print(f"Memory: {memory['rss_mb']:.2f} MB ({memory['percent_used']:.1f}%)")
    
    # Check GC
    gc_info = data['gc']
    print(f"GC collections: {gc_info['collections']}")
    print(f"Tracked objects: {gc_info['tracked_objects']}")
    
    # Check pressure
    pressure = data['system']['pressure_level']
    if pressure == 'high':
        print("WARNING: High memory pressure!")
```

---

### check_lambda_memory_compliance()

Check if memory usage is within Lambda 128MB limit.

**Signature:**
```python
def check_lambda_memory_compliance() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with compliance status

**Success Data Structure:**
```python
{
    'compliant': True,        # Whether within 128MB limit
    'current_mb': 85.5,       # Current memory usage
    'limit_mb': 128,          # Lambda memory limit
    'margin_mb': 42.5         # Margin before limit (128 - current)
}
```

**Example:**
```python
from singleton.singleton_memory import check_lambda_memory_compliance

response = check_lambda_memory_compliance()

if response['success']:
    data = response['data']
    
    if data['compliant']:
        print(f"Memory OK: {data['current_mb']:.2f} MB")
        print(f"Margin: {data['margin_mb']:.2f} MB")
    else:
        print(f"CRITICAL: Memory exceeds limit!")
        print(f"Current: {data['current_mb']:.2f} MB / Limit: {data['limit_mb']} MB")
        print("Run emergency_memory_preserve()")
```

---

## CLEANUP FUNCTIONS

### force_memory_cleanup()

Force aggressive garbage collection cleanup.

**Signature:**
```python
def force_memory_cleanup() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with cleanup results

**Success Data Structure:**
```python
{
    'gc_collected': 42,           # Objects collected by GC
    'memory_before_mb': 95.5,     # Memory before cleanup
    'memory_after_mb': 88.2,      # Memory after cleanup
    'memory_freed_mb': 7.3,       # Memory freed (max 0)
    'compliant': True             # Compliance status after cleanup
}
```

**Example:**
```python
from singleton.singleton_memory import force_memory_cleanup

response = force_memory_cleanup()

if response['success']:
    data = response['data']
    print(f"Collected: {data['gc_collected']} objects")
    print(f"Freed: {data['memory_freed_mb']:.2f} MB")
    print(f"Current: {data['memory_after_mb']:.2f} MB")
    
    if not data['compliant']:
        print("Still not compliant - try optimize_memory()")
```

---

### optimize_memory()

Optimize memory usage with multiple cleanup strategies.

**Signature:**
```python
def optimize_memory() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with optimization results

**Strategies Applied:**
1. Full garbage collection (all generations)
2. Per-generation GC (generations 0, 1, 2)
3. Singleton cache clearing (if memory > 100MB)

**Success Data Structure:**
```python
{
    'strategies_applied': [
        'gc_collected_42_objects',
        'gen0_collected_15_objects',
        'gen1_collected_5_objects',
        'gen2_collected_2_objects',
        'singleton_cache_cleared'    # If memory was high
    ],
    'final_memory_mb': 82.5,
    'compliant': True,
    'optimization_count': 5
}
```

**Example:**
```python
from singleton.singleton_memory import optimize_memory

response = optimize_memory()

if response['success']:
    data = response['data']
    print(f"Strategies applied: {data['optimization_count']}")
    for strategy in data['strategies_applied']:
        print(f"  - {strategy}")
    print(f"Final memory: {data['final_memory_mb']:.2f} MB")
```

---

### force_comprehensive_memory_cleanup()

Force comprehensive memory cleanup with all strategies.

**Signature:**
```python
def force_comprehensive_memory_cleanup() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with comprehensive cleanup results

**Cleanup Steps:**
1. Basic GC cleanup
2. Singleton cache clearing
3. System cleanup (string interning)
4. Final memory statistics

**Success Data Structure:**
```python
{
    'cleanup_steps': [
        ('basic_gc', {
            'gc_collected': 42,
            'memory_freed_mb': 5.2
        }),
        ('singleton_cleanup', {
            'success': True
        }),
        ('system_cleanup', {
            'intern_cleared': True
        })
    ],
    'final_memory_mb': 75.8,
    'final_compliant': True,
    'steps_completed': 3
}
```

**Example:**
```python
from singleton.singleton_memory import force_comprehensive_memory_cleanup

response = force_comprehensive_memory_cleanup()

if response['success']:
    data = response['data']
    
    print(f"Cleanup steps completed: {data['steps_completed']}")
    for step_name, step_result in data['cleanup_steps']:
        print(f"  {step_name}: {step_result}")
    
    print(f"Final memory: {data['final_memory_mb']:.2f} MB")
    print(f"Compliant: {data['final_compliant']}")
```

---

### emergency_memory_preserve()

Emergency memory preservation mode for critical situations.

**Signature:**
```python
def emergency_memory_preserve() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with emergency preservation results

**Behavior:**
1. Check if emergency mode is needed (memory > 128MB)
2. If not needed, return early
3. If needed, perform aggressive cleanup:
   - Full garbage collection
   - Clear ALL singleton instances
   - Final garbage collection

**Success Data Structure (Not Needed):**
```python
{
    'emergency_mode': False,
    'reason': 'memory_within_limits',
    'current_mb': 85.5
}
```

**Success Data Structure (Emergency Performed):**
```python
{
    'emergency_mode': True,
    'emergency_steps': [
        'gc_collected_42_objects',
        'cleared_12_singletons',
        'final_gc_collected_8_objects'
    ],
    'memory_before_mb': 125.5,
    'memory_after_mb': 78.2,
    'memory_freed_mb': 47.3,
    'now_compliant': True
}
```

**Example:**
```python
from singleton.singleton_memory import emergency_memory_preserve

response = emergency_memory_preserve()

if response['success']:
    data = response['data']
    
    if not data['emergency_mode']:
        print(f"No emergency needed: {data['current_mb']:.2f} MB")
    else:
        print("EMERGENCY MODE ACTIVATED!")
        print(f"Before: {data['memory_before_mb']:.2f} MB")
        print(f"After: {data['memory_after_mb']:.2f} MB")
        print(f"Freed: {data['memory_freed_mb']:.2f} MB")
        
        for step in data['emergency_steps']:
            print(f"  - {step}")
        
        if data['now_compliant']:
            print("Memory now compliant")
        else:
            print("CRITICAL: Still not compliant!")
```

---

## INTERNAL FUNCTIONS

### _get_singleton_memory_status_implementation()

Get singleton memory status (internal implementation).

**Signature:**
```python
def _get_singleton_memory_status_implementation() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Standardized response with singleton memory status

**Success Data Structure:**
```python
{
    'total_process_memory_mb': 85.5,
    'singleton_count': 12,
    'lambda_128mb_compliant': True,
    'memory_pressure': 'normal'    # 'normal' or 'high'
}
```

**Note:** Internal function used by interface layer. Use `get_comprehensive_memory_stats()` for public access.

---

## USAGE PATTERNS

### Pattern 1: Health Check

```python
from singleton.singleton_memory import (
    check_lambda_memory_compliance,
    get_comprehensive_memory_stats
)

def memory_health_check():
    """Check memory health."""
    # Quick compliance check
    compliance = check_lambda_memory_compliance()
    
    if not compliance['success']:
        return {'healthy': False, 'error': compliance['message']}
    
    data = compliance['data']
    
    if not data['compliant']:
        return {
            'healthy': False,
            'current_mb': data['current_mb'],
            'margin_mb': data['margin_mb'],
            'action': 'emergency_cleanup_needed'
        }
    
    # Detailed stats
    stats = get_comprehensive_memory_stats()
    
    if stats['success']:
        pressure = stats['data']['system']['pressure_level']
        
        return {
            'healthy': True,
            'current_mb': data['current_mb'],
            'margin_mb': data['margin_mb'],
            'pressure': pressure,
            'action': 'monitor' if pressure == 'normal' else 'cleanup_recommended'
        }
    
    return {'healthy': True, 'current_mb': data['current_mb']}
```

---

### Pattern 2: Proactive Cleanup

```python
from singleton.singleton_memory import (
    get_memory_stats,
    force_memory_cleanup,
    optimize_memory
)

def proactive_memory_management():
    """Proactively manage memory."""
    # Check current state
    stats = get_memory_stats()
    
    if not stats['success']:
        return
    
    current_mb = stats['data']['rss_mb']
    
    # Light cleanup at 80MB
    if current_mb > 80:
        print("Light cleanup triggered")
        force_memory_cleanup()
    
    # Aggressive cleanup at 100MB
    elif current_mb > 100:
        print("Aggressive cleanup triggered")
        optimize_memory()
```

---

### Pattern 3: Request Handler Wrapper

```python
from singleton.singleton_memory import (
    check_lambda_memory_compliance,
    emergency_memory_preserve
)

def lambda_handler(event, context):
    """Lambda handler with memory protection."""
    # Check memory before processing
    compliance = check_lambda_memory_compliance()
    
    if compliance['success'] and not compliance['data']['compliant']:
        # Emergency cleanup
        emergency = emergency_memory_preserve()
        
        if not emergency['success'] or not emergency['data'].get('now_compliant', False):
            return {
                'statusCode': 503,
                'body': 'Service unavailable - memory exhausted'
            }
    
    # Process request
    result = process_request(event)
    
    # Cleanup after processing
    force_memory_cleanup()
    
    return result
```

---

### Pattern 4: Memory Monitoring Loop

```python
from singleton.singleton_memory import get_comprehensive_memory_stats
import time

def monitor_memory_continuously():
    """Monitor memory continuously."""
    while True:
        stats = get_comprehensive_memory_stats()
        
        if stats['success']:
            data = stats['data']
            memory = data['memory']
            
            print(f"Memory: {memory['rss_mb']:.2f} MB ({memory['percent_used']:.1f}%)")
            print(f"Pressure: {data['system']['pressure_level']}")
            print(f"GC tracked: {data['gc']['tracked_objects']}")
            
            if data['system']['pressure_level'] == 'high':
                print("WARNING: High memory pressure!")
        
        time.sleep(60)  # Check every minute
```

---

### Pattern 5: Progressive Cleanup Strategy

```python
from singleton.singleton_memory import (
    get_memory_stats,
    force_memory_cleanup,
    optimize_memory,
    force_comprehensive_memory_cleanup,
    emergency_memory_preserve
)

def progressive_memory_cleanup():
    """Progressive cleanup based on memory level."""
    stats = get_memory_stats()
    
    if not stats['success']:
        return
    
    current_mb = stats['data']['rss_mb']
    
    # Level 1: Light cleanup (80-100MB)
    if 80 <= current_mb < 100:
        print("Level 1: Light cleanup")
        force_memory_cleanup()
    
    # Level 2: Aggressive cleanup (100-115MB)
    elif 100 <= current_mb < 115:
        print("Level 2: Aggressive cleanup")
        optimize_memory()
    
    # Level 3: Comprehensive cleanup (115-125MB)
    elif 115 <= current_mb < 125:
        print("Level 3: Comprehensive cleanup")
        force_comprehensive_memory_cleanup()
    
    # Level 4: Emergency mode (125MB+)
    elif current_mb >= 125:
        print("Level 4: EMERGENCY MODE")
        emergency_memory_preserve()
    
    # Check result
    final_stats = get_memory_stats()
    if final_stats['success']:
        final_mb = final_stats['data']['rss_mb']
        print(f"Final memory: {final_mb:.2f} MB")
```

---

## STANDARDIZED RESPONSES

All functions use gateway response helpers:

**Success Response Creation:**
```python
from gateway import create_success_response, generate_correlation_id

correlation_id = generate_correlation_id()
return create_success_response(
    "Memory statistics retrieved",
    {'rss_mb': 85.5, 'available_mb': 42.5},
    correlation_id
)
```

**Error Response Creation:**
```python
from gateway import create_error_response, generate_correlation_id, log_error

correlation_id = generate_correlation_id()
log_error(f"Memory stats failed: {str(e)}", e)
return create_error_response(
    "Failed to get memory statistics",
    error_code="MEMORY_STATS_ERROR",
    details={'error': str(e)},
    correlation_id=correlation_id
)
```

---

## MEMORY PRESSURE LEVELS

**Normal Pressure (< 100MB):**
- No action required
- Monitor periodically
- Proactive cleanup optional

**High Pressure (100-120MB):**
- Action recommended
- Run optimize_memory()
- Consider singleton cleanup

**Critical Pressure (120-128MB):**
- Immediate action required
- Run force_comprehensive_memory_cleanup()
- Prepare for emergency mode

**Emergency (>= 128MB):**
- Lambda may crash
- Run emergency_memory_preserve()
- Clear all non-essential singletons

---

## EXPORTS

```python
__all__ = [
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    '_get_singleton_memory_status_implementation',
]
```

---

## RELATED DOCUMENTATION

- **singleton_manager.md**: Singleton instance management
- **singleton_core.md**: Gateway implementation functions
- **singleton_convenience.md**: Convenience accessors

---

**END OF DOCUMENTATION**

**Module:** singleton/singleton_memory.py  
**Functions:** 8 (7 public + 1 internal)  
**Purpose:** Lambda 128MB compliance and memory optimization
