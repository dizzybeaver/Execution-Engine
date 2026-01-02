# circuit_breaker_manager.md

**Version:** 2025-12-13_1  
**Purpose:** Circuit breaker manager with singleton pattern  
**Module:** circuit_breaker/circuit_breaker_manager.py  
**Type:** Singleton Manager

---

## OVERVIEW

Manages all circuit breakers in the system using the SINGLETON pattern. Provides centralized control over circuit breaker lifecycle, rate limiting, and statistics.

**Key Features:**
- Singleton instance per Lambda container
- Rate limiting (1000 ops/sec)
- Centralized statistics
- Debug integration
- Lambda-safe (no threading)

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- SINGLETON: Single instance via get_circuit_breaker_manager()
- Rate Limiting: 1000 operations/second protection
- Lambda-Safe: No threading primitives

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

## CLASSES

### CircuitBreakerCore

Main manager class for circuit breakers with SINGLETON pattern and rate limiting.

**Purpose:**
- Manage circuit breaker lifecycle
- Enforce rate limits
- Track statistics
- Provide singleton access

**Initialization:**
```python
def __init__(self):
    self._breakers: Dict[str, CircuitBreaker] = {}
    self._rate_limiter = deque(maxlen=1000)
    self._rate_limit_window_ms = 1000
    self._rate_limited_count = 0
    self._total_operations = 0
```

**State:**
- `_breakers`: Dictionary mapping names to CircuitBreaker instances
- `_rate_limiter`: Deque tracking operation timestamps (maxlen=1000)
- `_rate_limit_window_ms`: Rate limit window (1000ms)
- `_rate_limited_count`: Count of rate-limited operations
- `_total_operations`: Total operations executed

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

**Rate Limit:**
- 1000 operations per second
- Sliding window implementation
- Deque automatically discards oldest when maxlen reached

**Example:**
```python
if not self._check_rate_limit():
    self._rate_limited_count += 1
    raise Exception("Rate limit exceeded")
```

---

### get()

Get or create a circuit breaker by name.

**Signature:**
```python
def get(
    self,
    name: str,
    failure_threshold: int = 5,
    timeout: int = 60,
    correlation_id: str = None
) -> CircuitBreaker
```

**Parameters:**
- `name` (str): Circuit breaker name (unique identifier)
- `failure_threshold` (int): Failures before opening (default: 5)
- `timeout` (int): Seconds before recovery attempt (default: 60)
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `CircuitBreaker`: Existing or newly created breaker instance

**Behavior:**
1. Check rate limit (raises Exception if exceeded)
2. Increment total operations counter
3. If breaker exists, return it
4. If new, create CircuitBreaker and store
5. Log creation with debug_log

**Example:**
```python
manager = get_circuit_breaker_manager()

# Get or create 'ha_api' breaker
breaker = manager.get(
    name='ha_api',
    failure_threshold=3,
    timeout=30
)

print(f"Breaker state: {breaker.state.value}")
```

---

### call()

Execute function with circuit breaker protection.

**Signature:**
```python
def call(
    self,
    name: str,
    func: Callable,
    correlation_id: str = None,
    *args,
    **kwargs
) -> Any
```

**Parameters:**
- `name` (str): Circuit breaker name
- `func` (Callable): Function to execute
- `correlation_id` (str): Optional correlation ID for debug tracking
- `*args`: Positional arguments for func
- `**kwargs`: Keyword arguments for func

**Returns:**
- `Any`: Result from func() execution

**Raises:**
- `Exception`: If rate limit exceeded
- `Exception`: If circuit is OPEN
- `Exception`: If func() raises exception

**Behavior:**
1. Check rate limit (raises if exceeded)
2. Increment total operations counter
3. Log execution attempt
4. Get or create circuit breaker
5. Delegate to breaker.call() with timing
6. Return result or propagate exception

**Example:**
```python
manager = get_circuit_breaker_manager()

def ha_api_call():
    return ha_client.get_state('light.living_room')

# Execute with protection
result = manager.call(
    name='ha_api',
    func=ha_api_call
)
```

**Debug Timing:**
```python
with debug_timing(correlation_id, "CIRCUIT_BREAKER", f"manager.call:{name}"):
    breaker = self.get(name, correlation_id=correlation_id)
    return breaker.call(func, self._check_rate_limit, correlation_id, *args, **kwargs)
```

---

### get_all_states()

Get states of all registered circuit breakers.

**Signature:**
```python
def get_all_states(
    self,
    correlation_id: str = None
) -> Dict[str, Dict[str, Any]]
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `Dict[str, Dict[str, Any]]`: Mapping of breaker names to state dicts

**Example:**
```python
manager = get_circuit_breaker_manager()

all_states = manager.get_all_states()

# Print all breaker states
for name, state in all_states.items():
    print(f"{name}:")
    print(f"  State: {state['state']}")
    print(f"  Failures: {state['failures']}/{state['threshold']}")
    print(f"  Calls: {state['statistics']['total_calls']}")
```

---

### reset_all()

Reset all circuit breakers to CLOSED state.

**Signature:**
```python
def reset_all(
    self,
    correlation_id: str = None
)
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- None

**Behavior:**
- Calls reset() on all registered breakers
- Sets state to CLOSED
- Clears failure counts
- Does NOT clear statistics
- Does NOT remove breakers from manager

**Example:**
```python
manager = get_circuit_breaker_manager()

# After maintenance window
manager.reset_all()
print("All breakers reset to CLOSED state")
```

---

### get_stats()

Get comprehensive circuit breaker manager statistics.

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
- `Dict[str, Any]`: Statistics dictionary with gateway response wrapper

**Response Structure:**
```python
{
    'success': True,
    'message': 'Circuit breaker statistics',
    'data': {
        'total_operations': 1234,
        'breakers_count': 5,
        'rate_limited_count': 2,
        'rate_limit_window_ms': 1000,
        'current_rate_limit_size': 100,
        'max_rate_limit': 1000,
        'breakers': {
            'ha_api': {...},
            'alexa_api': {...},
            ...
        }
    }
}
```

**Example:**
```python
manager = get_circuit_breaker_manager()

response = manager.get_stats()

if response['success']:
    stats = response['data']
    print(f"Total operations: {stats['total_operations']}")
    print(f"Active breakers: {stats['breakers_count']}")
    print(f"Rate limited: {stats['rate_limited_count']}")
    print(f"Rate utilization: {stats['current_rate_limit_size']}/{stats['max_rate_limit']}")
```

---

### reset()

Reset circuit breaker manager to initial state.

**Signature:**
```python
def reset(
    self,
    correlation_id: str = None
) -> bool
```

**Parameters:**
- `correlation_id` (str): Optional correlation ID for debug tracking

**Returns:**
- `bool`: True if reset successful, False if rate limited

**Behavior:**
1. Check rate limit (returns False if exceeded)
2. Clear all breakers from registry
3. Reset total operations counter to 0
4. Clear rate limiter deque
5. Reset rate limited counter to 0
6. Log reset completion

**Example:**
```python
manager = get_circuit_breaker_manager()

# Complete manager reset
success = manager.reset()

if success:
    print("Manager reset successful")
    print("All breakers removed")
    print("All counters reset")
else:
    print("Reset failed: rate limited")
```

---

## SINGLETON PATTERN

### get_circuit_breaker_manager()

Get SINGLETON circuit breaker manager instance.

**Function:** Module-level singleton factory

**Signature:**
```python
def get_circuit_breaker_manager() -> CircuitBreakerCore
```

**Returns:**
- `CircuitBreakerCore`: The singleton manager instance

**Implementation:**
```python
_circuit_breaker_core = None  # Module-level singleton

def get_circuit_breaker_manager() -> CircuitBreakerCore:
    global _circuit_breaker_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        # Try gateway SINGLETON registry first
        manager = singleton_get('circuit_breaker_manager')
        if manager is None:
            if _circuit_breaker_core is None:
                _circuit_breaker_core = CircuitBreakerCore()
            singleton_register('circuit_breaker_manager', _circuit_breaker_core)
            manager = _circuit_breaker_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _circuit_breaker_core is None:
            _circuit_breaker_core = CircuitBreakerCore()
        return _circuit_breaker_core
```

**Singleton Strategy:**
1. **Preferred:** Gateway SINGLETON registry
   - Centralized singleton management
   - Consistent with other interfaces
2. **Fallback:** Module-level global variable
   - Works when gateway not available
   - Ensures singleton in all cases

**Usage:**
```python
# Always use this function to get manager
manager = get_circuit_breaker_manager()

# Never instantiate directly
# manager = CircuitBreakerCore()  # ❌ WRONG
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

**Properties:**
- O(1) append operation
- O(n) cleanup (but n ≤ 1000)
- Automatic old timestamp eviction
- No threading required

**Why 1000 ops/sec?**
- Higher than typical usage (protection, not throttling)
- Prevents DoS attacks
- Still allows burst traffic
- Infrastructure component needs headroom

---

## STATISTICS

### Tracked Metrics

**Manager Level:**
- `total_operations`: Total operations executed
- `breakers_count`: Number of registered breakers
- `rate_limited_count`: Number of rejected operations
- `rate_limit_window_ms`: Rate limit window
- `current_rate_limit_size`: Current deque size
- `max_rate_limit`: Maximum rate limit

**Per-Breaker Statistics:**
- See circuit_breaker_state.md for breaker-level stats

---

## USAGE PATTERNS

### Pattern 1: Get Singleton Instance

```python
from circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager

# Always use singleton factory
manager = get_circuit_breaker_manager()

# Use for all operations
breaker = manager.get('ha_api')
result = manager.call('ha_api', my_function)
```

---

### Pattern 2: Monitor Rate Limiting

```python
from circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager

manager = get_circuit_breaker_manager()

# Check rate limit health
response = manager.get_stats()
stats = response['data']

utilization = stats['current_rate_limit_size'] / stats['max_rate_limit']

if utilization > 0.8:
    print(f"WARNING: Rate limit at {utilization*100}%")
    print(f"Rate limited count: {stats['rate_limited_count']}")
```

---

### Pattern 3: Health Dashboard

```python
from circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager

manager = get_circuit_breaker_manager()

# Build comprehensive health view
response = manager.get_stats()
stats = response['data']

dashboard = {
    'manager': {
        'operations': stats['total_operations'],
        'rate_limited': stats['rate_limited_count'],
        'rate_utilization': f"{stats['current_rate_limit_size']}/{stats['max_rate_limit']}"
    },
    'breakers': {
        name: {
            'state': state['state'],
            'health': 'healthy' if state['failures'] == 0 else 'degraded'
        }
        for name, state in stats['breakers'].items()
    }
}
```

---

## EXPORTS

```python
__all__ = [
    'CircuitBreakerCore',
    'get_circuit_breaker_manager'
]
```

---

## RELATED DOCUMENTATION

- **circuit_breaker_state.md**: Individual circuit breaker implementation
- **circuit_breaker_core.md**: Gateway implementation functions
- **interface_circuit_breaker.md**: Interface layer
- **LESS-18**: SINGLETON pattern lessons
- **LESS-21**: Rate limiting lessons

---

**END OF DOCUMENTATION**

**Module:** circuit_breaker/circuit_breaker_manager.py  
**Classes:** 1 (CircuitBreakerCore)  
**Functions:** 1 (get_circuit_breaker_manager)  
**Pattern:** SINGLETON with Rate Limiting
