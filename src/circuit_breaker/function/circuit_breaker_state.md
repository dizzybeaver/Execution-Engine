# circuit_breaker_state.md

**Version:** 2025-12-13_1  
**Purpose:** Circuit breaker state and individual breaker implementation  
**Module:** circuit_breaker/circuit_breaker_state.py  
**Type:** State Machine Implementation

---

## OVERVIEW

Implements individual circuit breaker instances with state machine logic. Each breaker tracks failures, manages state transitions, and enforces the circuit breaker pattern.

**Key Features:**
- Three-state machine (CLOSED → OPEN → HALF_OPEN)
- Automatic state transitions
- Comprehensive statistics
- Debug integration
- Lambda-safe (no threading)

---

## ARCHITECTURE COMPLIANCE

**Patterns:**
- State Machine: Three states with automatic transitions
- Statistics Tracking: Per-breaker call metrics
- Lambda-Safe: No threading primitives

**Constraints:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-21: Rate limiting via manager callback

---

## ENUMS

### CircuitState

Circuit breaker states enum.

**Values:**
```python
class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Rejecting calls
    HALF_OPEN = "half_open"  # Testing recovery
```

**State Meanings:**
- **CLOSED**: Breaker is working normally, all calls pass through
- **OPEN**: Breaker has tripped, all calls are rejected
- **HALF_OPEN**: Breaker is testing if service recovered, allowing trial calls

**State Transitions:**
```
CLOSED --[failures >= threshold]--> OPEN
OPEN --[timeout expired]--> HALF_OPEN
HALF_OPEN --[success]--> CLOSED
HALF_OPEN --[failure]--> OPEN
```

---

## CLASSES

### CircuitBreaker

Single circuit breaker instance with state machine logic.

**Purpose:**
- Track failure counts
- Manage state transitions
- Execute protected calls
- Collect statistics

**Initialization:**
```python
def __init__(
    self,
    name: str,
    failure_threshold: int = 5,
    timeout: int = 60
)
```

**Parameters:**
- `name` (str): Unique breaker identifier
- `failure_threshold` (int): Failures before opening (default: 5)
- `timeout` (int): Seconds before recovery attempt (default: 60)

**Instance State:**
- `name`: Breaker identifier
- `failure_threshold`: Configured threshold
- `timeout`: Configured timeout
- `state`: Current CircuitState
- `failures`: Current failure count
- `last_failure_time`: Timestamp of last failure

**Statistics:**
- `_total_calls`: All call attempts
- `_successful_calls`: Successful executions
- `_failed_calls`: Failed executions
- `_rejected_calls`: Calls rejected when OPEN

---

## METHODS

### call()

Execute function with circuit breaker protection.

**Signature:**
```python
def call(
    self,
    func: Callable,
    rate_limit_check: Callable,
    correlation_id: str,
    *args,
    **kwargs
) -> Any
```

**Parameters:**
- `func` (Callable): Function to execute
- `rate_limit_check` (Callable): Manager's rate limit checker
- `correlation_id` (str): Correlation ID for debug tracking
- `*args`: Positional arguments for func
- `**kwargs`: Keyword arguments for func

**Returns:**
- `Any`: Result from func() execution

**Raises:**
- `Exception`: If rate limit exceeded
- `Exception`: If circuit is OPEN (and timeout not expired)
- `Exception`: If func() raises exception

**State Machine Logic:**

**1. Rate Limit Check:**
```python
if not rate_limit_check():
    raise Exception("Rate limit exceeded")
```

**2. Circuit State Check:**
```python
if self.state == CircuitState.OPEN:
    if time.time() - self.last_failure_time > self.timeout:
        # Timeout expired, try recovery
        self.state = CircuitState.HALF_OPEN
    else:
        # Still in timeout, reject call
        self._rejected_calls += 1
        raise Exception(f"Circuit breaker '{self.name}' is OPEN")
```

**3. Execute Function:**
```python
try:
    result = func(*args, **kwargs)
    self._on_success(correlation_id)
    return result
except Exception as e:
    self._on_failure(correlation_id, e)
    raise
```

**Example:**
```python
breaker = CircuitBreaker(
    name='ha_api',
    failure_threshold=3,
    timeout=30
)

def ha_call():
    return ha_client.get_state('light.living_room')

# Execute with protection
try:
    result = breaker.call(
        func=ha_call,
        rate_limit_check=manager._check_rate_limit,
        correlation_id='abc123'
    )
    print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {e}")
```

---

### _on_success()

**Private method** - Handle successful call.

**Signature:**
```python
def _on_success(self, correlation_id: str)
```

**Behavior:**
1. Increment successful calls counter
2. Reset failure count to 0
3. If state is HALF_OPEN, transition to CLOSED
4. Log success with debug_log

**State Transitions:**
```python
HALF_OPEN --[_on_success]--> CLOSED
CLOSED --[_on_success]--> CLOSED (no change)
```

**Example Flow:**
```
State: HALF_OPEN
Call succeeds
→ failures = 0
→ state = CLOSED
→ Log: "Success in HALF_OPEN - closing circuit"
```

---

### _on_failure()

**Private method** - Handle failed call.

**Signature:**
```python
def _on_failure(self, correlation_id: str, error: Exception)
```

**Parameters:**
- `correlation_id` (str): Correlation ID for debug tracking
- `error` (Exception): The exception that occurred

**Behavior:**
1. Increment failed calls counter
2. Increment failure count
3. Record current time as last_failure_time
4. If failures >= threshold, transition to OPEN
5. Log failure details

**State Transitions:**
```python
CLOSED --[failures >= threshold]--> OPEN
HALF_OPEN --[any failure]--> OPEN
```

**Example Flow:**
```
State: CLOSED
Threshold: 3
Current failures: 2

Call fails
→ failures = 3
→ state = OPEN
→ last_failure_time = now
→ Log: "Threshold exceeded - opening circuit"
```

---

### reset()

Reset circuit breaker to initial state.

**Signature:**
```python
def reset(self)
```

**Returns:**
- None

**Behavior:**
- Set state to CLOSED
- Clear failure count (0)
- Clear last_failure_time (None)
- Does NOT clear statistics

**Example:**
```python
breaker = CircuitBreaker('ha_api')

# After maintenance
breaker.reset()

print(f"State: {breaker.state.value}")  # "closed"
print(f"Failures: {breaker.failures}")  # 0
```

---

### get_state()

Get current circuit breaker state snapshot.

**Signature:**
```python
def get_state(self) -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: State dictionary

**Response Structure:**
```python
{
    'name': 'ha_api',
    'state': 'closed',  # or 'open' or 'half_open'
    'failures': 0,
    'threshold': 5,
    'timeout': 60,
    'last_failure': None,  # or timestamp
    'statistics': {
        'total_calls': 100,
        'successful_calls': 95,
        'failed_calls': 3,
        'rejected_calls': 2
    }
}
```

**Example:**
```python
breaker = CircuitBreaker('ha_api', failure_threshold=3)

state = breaker.get_state()

print(f"Breaker: {state['name']}")
print(f"State: {state['state']}")
print(f"Health: {state['failures']}/{state['threshold']}")
print(f"Success rate: {state['statistics']['successful_calls']}/{state['statistics']['total_calls']}")
```

---

## STATE MACHINE

### States Overview

**CLOSED (Normal Operation):**
- All calls pass through to func()
- Failures increment counter
- When failures >= threshold → OPEN

**OPEN (Circuit Tripped):**
- All calls immediately rejected
- No func() execution
- After timeout seconds → HALF_OPEN

**HALF_OPEN (Testing Recovery):**
- Allow trial calls through
- Success → CLOSED
- Failure → OPEN

### State Diagram

```
┌─────────┐
│ CLOSED  │ <───────────────┐
└─────────┘                  │
     │                       │
     │ failures >= threshold │
     ▼                       │
┌─────────┐                  │ success
│  OPEN   │                  │
└─────────┘                  │
     │                       │
     │ timeout expired       │
     ▼                       │
┌─────────┐                  │
│HALF_OPEN│ ─────────────────┘
└─────────┘
     │
     │ failure
     ▼
┌─────────┐
│  OPEN   │
└─────────┘
```

### Transition Examples

**Example 1: Normal Operation**
```
Initial: CLOSED, failures=0
Call 1: Success → CLOSED, failures=0
Call 2: Success → CLOSED, failures=0
Call 3: Success → CLOSED, failures=0
```

**Example 2: Trip Circuit**
```
Initial: CLOSED, failures=0, threshold=3
Call 1: Fail → CLOSED, failures=1
Call 2: Fail → CLOSED, failures=2
Call 3: Fail → OPEN, failures=3
Call 4: Rejected (circuit OPEN)
Call 5: Rejected (circuit OPEN)
```

**Example 3: Recovery Success**
```
Initial: OPEN, failures=3, timeout=30s
... wait 30 seconds ...
Call 1: Success → HALF_OPEN → CLOSED, failures=0
Call 2: Success → CLOSED, failures=0
```

**Example 4: Recovery Failure**
```
Initial: OPEN, failures=3, timeout=30s
... wait 30 seconds ...
Call 1: Fail → HALF_OPEN → OPEN, failures=3
... wait 30 seconds ...
Call 2: Success → HALF_OPEN → CLOSED, failures=0
```

---

## METRICS INTEGRATION

### CloudWatch Metrics

**Success Metrics:**
```python
from gateway import execute_operation, GatewayInterface

execute_operation(
    GatewayInterface.METRICS,
    'record_metric',
    name='circuit_breaker_call_success',
    value=1,
    tags={
        'breaker': self.name,
        'correlation_id': correlation_id
    }
)
```

**Failure Metrics:**
```python
execute_operation(
    GatewayInterface.METRICS,
    'record_metric',
    name='circuit_breaker_call_failure',
    value=1,
    tags={
        'breaker': self.name,
        'correlation_id': correlation_id
    }
)
```

**Metrics Fallback:**
- Metrics integration is optional
- Failures are caught and ignored
- Breaker continues to function without metrics

---

## DEBUG INTEGRATION

### Debug Logging

**Call Execution:**
```python
debug_log(correlation_id, "CIRCUIT_BREAKER",
         f"Executing protected call",
         breaker=self.name, state=self.state.value)
```

**State Transitions:**
```python
debug_log(correlation_id, "CIRCUIT_BREAKER",
         f"Transitioning to HALF_OPEN", breaker=self.name)
```

**Failures:**
```python
debug_log(correlation_id, "CIRCUIT_BREAKER",
         f"Call failed - failures: {self.failures}/{self.failure_threshold}",
         breaker=self.name, error=str(error))
```

### Timing

**Execution Timing:**
```python
with debug_timing(correlation_id, "CIRCUIT_BREAKER", f"call:{self.name}"):
    result = func(*args, **kwargs)
```

**CloudWatch Output:**
```
[correlation_id=abc123] CIRCUIT_BREAKER: Executing protected call
  breaker=ha_api state=closed
[correlation_id=abc123] CIRCUIT_BREAKER: call:ha_api duration=45ms
```

---

## STATISTICS

### Tracked Metrics

**Per-Breaker Statistics:**
- `total_calls`: All call attempts (includes rejected)
- `successful_calls`: Calls that succeeded
- `failed_calls`: Calls that failed
- `rejected_calls`: Calls rejected when OPEN

**Calculated Metrics:**
```python
state = breaker.get_state()
stats = state['statistics']

success_rate = stats['successful_calls'] / stats['total_calls']
failure_rate = stats['failed_calls'] / stats['total_calls']
rejection_rate = stats['rejected_calls'] / stats['total_calls']
```

**Health Indicators:**
```python
# Breaker is healthy if:
health_ok = (
    state['state'] == 'closed' and
    state['failures'] == 0 and
    success_rate > 0.95
)
```

---

## USAGE PATTERNS

### Pattern 1: Basic Protection

```python
from circuit_breaker.circuit_breaker_state import CircuitBreaker

breaker = CircuitBreaker(
    name='external_api',
    failure_threshold=5,
    timeout=60
)

def protected_call():
    return external_api.get_data()

# Execute with protection
result = breaker.call(
    func=protected_call,
    rate_limit_check=lambda: True,  # Manager provides this
    correlation_id='abc123'
)
```

---

### Pattern 2: Monitor Health

```python
breaker = CircuitBreaker('ha_api')

# Check health
state = breaker.get_state()

if state['state'] == 'open':
    print(f"⚠️  Circuit OPEN")
    print(f"Failures: {state['failures']}/{state['threshold']}")
    
    # Calculate time until retry
    if state['last_failure']:
        elapsed = time.time() - state['last_failure']
        remaining = state['timeout'] - elapsed
        print(f"Retry in {remaining:.0f}s")
        
elif state['state'] == 'half_open':
    print(f"⚡ Testing recovery...")
    
else:
    print(f"✓ Circuit healthy")
    print(f"Success rate: {state['statistics']['successful_calls']}/{state['statistics']['total_calls']}")
```

---

### Pattern 3: Reset After Maintenance

```python
breaker = CircuitBreaker('ha_api')

# System maintenance completed
print("Maintenance complete, resetting circuit breaker")

breaker.reset()

state = breaker.get_state()
print(f"State: {state['state']}")  # "closed"
print(f"Failures: {state['failures']}")  # 0
print(f"Ready for traffic")
```

---

## CONFIGURATION GUIDELINES

### Failure Threshold

**Recommendations:**
- **Critical services**: 3-5 failures
- **Non-critical services**: 5-10 failures
- **Flaky services**: 10-20 failures

**LEE Defaults:**
- Home Assistant API: 5 failures
- Alexa API: 5 failures
- Device control: 3 failures

### Timeout

**Recommendations:**
- **Fast recovery**: 30-60 seconds
- **Normal recovery**: 60-120 seconds
- **Slow recovery**: 120-300 seconds

**LEE Defaults:**
- Home Assistant API: 60 seconds
- Alexa API: 60 seconds
- Device control: 30 seconds

### Tuning Guidelines

**Too Sensitive (False Positives):**
- Increase failure_threshold
- Increase timeout
- Monitor success_rate

**Too Lenient (Slow Protection):**
- Decrease failure_threshold
- Decrease timeout
- Monitor failed_calls

---

## EXPORTS

```python
__all__ = [
    'CircuitState',
    'CircuitBreaker'
]
```

---

## RELATED DOCUMENTATION

- **circuit_breaker_manager.md**: Manager and singleton pattern
- **circuit_breaker_core.md**: Gateway implementation functions
- **interface_circuit_breaker.md**: Interface layer
- **AP-08**: No threading locks anti-pattern
- **DEC-04**: Lambda single-threaded decision
- **LESS-21**: Rate limiting lessons

---

**END OF DOCUMENTATION**

**Module:** circuit_breaker/circuit_breaker_state.py  
**Classes:** 2 (CircuitState, CircuitBreaker)  
**Pattern:** State Machine with Statistics
