# circuit_breaker_core.md

**Version:** 2025-12-13_1  
**Purpose:** Gateway implementation functions for circuit breaker interface  
**Module:** circuit_breaker/circuit_breaker_core.py  
**Type:** Core Implementation Functions

---

## OVERVIEW

Provides gateway-accessible implementation functions for circuit breaker operations. All functions delegate to the singleton CircuitBreakerManager and include debug integration for comprehensive tracking.

**Pattern:** Gateway → Interface → Core (SUGA)  
**Singleton:** All operations use get_circuit_breaker_manager()  
**Debug:** All functions integrate correlation_id tracking

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SUGA: Gateway implementation layer
- SINGLETON: Uses get_circuit_breaker_manager() (LESS-18)
- Debug Integration: All functions support correlation_id

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-21: Rate limiting (1000 ops/sec)

---

## FUNCTIONS

### get_breaker_implementation()

Get circuit breaker state using SINGLETON manager.

**Signature:**
```python
def get_breaker_implementation(
    name: str,
    failure_threshold: int = 5,
    timeout: int = 60,
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `name` (str): Circuit breaker name
- `failure_threshold` (int): Number of failures before opening (default: 5)
- `timeout` (int): Seconds before attempting recovery (default: 60)
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Any]`: Circuit breaker state dictionary containing:
  - `name`: Breaker name
  - `state`: Current state (closed/open/half_open)
  - `failures`: Current failure count
  - `threshold`: Configured failure threshold
  - `timeout`: Configured timeout
  - `last_failure`: Timestamp of last failure
  - `statistics`: Call statistics

**Behavior:**
1. Generates correlation_id if not provided
2. Logs debug information
3. Gets singleton manager instance
4. Gets or creates circuit breaker
5. Returns current state

**Example:**
```python
from circuit_breaker.circuit_breaker_core import get_breaker_implementation

# Get state of Home Assistant API breaker
state = get_breaker_implementation(
    name='ha_api',
    failure_threshold=3,
    timeout=30
)

print(f"State: {state['state']}")
print(f"Failures: {state['failures']}/{state['threshold']}")
```

---

### execute_with_breaker_implementation()

Execute function call with circuit breaker protection using SINGLETON manager.

**Signature:**
```python
def execute_with_breaker_implementation(
    name: str,
    func: Callable,
    args: tuple = (),
    correlation_id: str = None,
    **kwargs
) -> Any
```

**Parameters:**
- `name` (str): Circuit breaker name
- `func` (Callable): Function to execute with protection
- `args` (tuple): Positional arguments for func (default: ())
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Keyword arguments for func

**Returns:**
- `Any`: Result of func() execution

**Raises:**
- `Exception`: If circuit is OPEN
- `Exception`: If rate limit exceeded
- `Exception`: If func() raises an exception

**Behavior:**
1. Generates correlation_id if not provided
2. Logs debug information
3. Gets singleton manager instance
4. Executes func with circuit breaker protection
5. Updates circuit state based on success/failure

**Example:**
```python
from circuit_breaker.circuit_breaker_core import execute_with_breaker_implementation

def call_ha_api():
    return ha_client.get_state('light.living_room')

# Execute with protection
try:
    result = execute_with_breaker_implementation(
        name='ha_api',
        func=call_ha_api
    )
    print(f"Success: {result}")
except Exception as e:
    print(f"Circuit breaker prevented call: {e}")
```

---

### get_all_states_implementation()

Get states of all circuit breakers using SINGLETON manager.

**Signature:**
```python
def get_all_states_implementation(
    correlation_id: str = None,
    **kwargs
) -> Dict[str, Dict[str, Any]]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- `Dict[str, Dict[str, Any]]`: Mapping of breaker names to their states

**Example:**
```python
from circuit_breaker.circuit_breaker_core import get_all_states_implementation

# Get all breaker states
all_states = get_all_states_implementation()

for name, state in all_states.items():
    print(f"{name}: {state['state']} ({state['failures']}/{state['threshold']})")
```

**Output Example:**
```
ha_api: closed (0/3)
alexa_api: open (5/5)
device_control: half_open (2/5)
```

---

### reset_all_implementation()

Reset all circuit breakers using SINGLETON manager.

**Signature:**
```python
def reset_all_implementation(
    correlation_id: str = None,
    **kwargs
)
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking
- `**kwargs`: Additional arguments (ignored)

**Returns:**
- None

**Behavior:**
- Resets all circuit breakers to CLOSED state
- Clears all failure counts
- Does NOT clear statistics

**Example:**
```python
from circuit_breaker.circuit_breaker_core import reset_all_implementation

# Reset all breakers after maintenance
reset_all_implementation()
print("All circuit breakers reset to CLOSED")
```

---

### get_stats_implementation()

Get circuit breaker manager statistics using SINGLETON manager.

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
- `Dict[str, Any]`: Statistics dictionary containing:
  - `total_operations`: Total operations executed
  - `breakers_count`: Number of registered breakers
  - `rate_limited_count`: Number of rate-limited operations
  - `rate_limit_window_ms`: Rate limit window in milliseconds
  - `current_rate_limit_size`: Current rate limiter size
  - `max_rate_limit`: Maximum rate limit
  - `breakers`: Dict of all breaker states

**Example:**
```python
from circuit_breaker.circuit_breaker_core import get_stats_implementation

stats = get_stats_implementation()

print(f"Total operations: {stats['total_operations']}")
print(f"Active breakers: {stats['breakers_count']}")
print(f"Rate limited: {stats['rate_limited_count']}")
```

---

### reset_implementation()

Reset circuit breaker manager state using SINGLETON manager.

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
- `Dict[str, Any]`: Success/error response dictionary:
  - Success: `{'success': True, 'data': {'reset': True}}`
  - Failure: `{'success': False, 'error': 'RATE_LIMIT_EXCEEDED'}`

**Behavior:**
- Clears all circuit breakers
- Resets all statistics
- Clears rate limiter
- Subject to rate limiting

**Example:**
```python
from circuit_breaker.circuit_breaker_core import reset_implementation

# Complete manager reset
response = reset_implementation()

if response['success']:
    print("Manager reset successful")
else:
    print(f"Reset failed: {response['error']}")
```

---

## DEBUG INTEGRATION

All functions include debug integration:

**Automatic Correlation IDs:**
```python
# If not provided, correlation_id is auto-generated
state = get_breaker_implementation('ha_api')
# Generates: correlation_id='cb_1234567890'
```

**Debug Logging:**
```python
# All operations logged with:
# - correlation_id
# - Operation name
# - Breaker name
# - Key parameters

debug_log(correlation_id, "CIRCUIT_BREAKER",
         "get_breaker_implementation called",
         breaker=name, threshold=failure_threshold, timeout=timeout)
```

**CloudWatch Traces:**
```
[correlation_id=cb_abc123] CIRCUIT_BREAKER: get_breaker_implementation called
  breaker=ha_api threshold=3 timeout=30
```

---

## USAGE PATTERNS

### Pattern 1: Protect External API Call

```python
from circuit_breaker.circuit_breaker_core import execute_with_breaker_implementation

def ha_get_state(entity_id: str):
    # Your API call logic
    return ha_client.get_state(entity_id)

# Execute with protection
result = execute_with_breaker_implementation(
    name='ha_api',
    func=ha_get_state,
    args=('light.living_room',)
)
```

---

### Pattern 2: Monitor Circuit Health

```python
from circuit_breaker.circuit_breaker_core import get_breaker_implementation

# Check if circuit is healthy
state = get_breaker_implementation('ha_api')

if state['state'] == 'open':
    print(f"WARNING: Circuit breaker OPEN")
    print(f"Failures: {state['failures']}")
    print(f"Will retry in {state['timeout']} seconds")
elif state['state'] == 'half_open':
    print("Circuit attempting recovery...")
else:
    print("Circuit healthy")
```

---

### Pattern 3: Dashboard Statistics

```python
from circuit_breaker.circuit_breaker_core import get_stats_implementation, get_all_states_implementation

# Get manager stats
stats = get_stats_implementation()
all_states = get_all_states_implementation()

# Build health dashboard
dashboard = {
    'total_operations': stats['total_operations'],
    'healthy_breakers': sum(1 for s in all_states.values() if s['state'] == 'closed'),
    'open_breakers': sum(1 for s in all_states.values() if s['state'] == 'open'),
    'recovering_breakers': sum(1 for s in all_states.values() if s['state'] == 'half_open'),
    'total_breakers': len(all_states)
}
```

---

## EXPORTS

```python
__all__ = [
    'get_breaker_implementation',
    'execute_with_breaker_implementation',
    'get_all_states_implementation',
    'reset_all_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
```

---

**END OF DOCUMENTATION**

**Module:** circuit_breaker/circuit_breaker_core.py  
**Functions:** 6  
**Pattern:** SUGA Core Implementation  
**Debug:** Fully Integrated
