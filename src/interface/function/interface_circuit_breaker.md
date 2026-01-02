# interface_circuit_breaker.py

**Version:** 2025-12-13_1  
**Module:** CIRCUIT_BREAKER  
**Layer:** Interface  
**Interface:** INT-09  
**Lines:** ~100

---

## Purpose

Circuit breaker interface router with import protection and parameter validation.

---

## Main Function

### execute_circuit_breaker_operation()

**Signature:**
```python
def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any
```

**Purpose:** Route circuit breaker operations to internal implementations

**Parameters:**
- `operation` (str) - Operation name to execute
- `**kwargs` - Operation-specific parameters

**Returns:** Operation result (type varies by operation)

**Operations:**
- `get` - Get or create circuit breaker by name
- `call` - Execute function with circuit breaker protection
- `get_all_states` - Get states of all circuit breakers
- `reset_all` - Reset all circuit breakers
- `get_stats` - Get circuit breaker statistics
- `reset` - Reset circuit breaker state

**Raises:**
- `RuntimeError` - If Circuit Breaker interface unavailable
- `ValueError` - If operation unknown or parameters invalid
- `TypeError` - If parameter types incorrect

---

## Operations

### get

**Purpose:** Get or create circuit breaker instance by name

**Parameters:**
- `name` (str, required) - Circuit breaker name

**Returns:** CircuitBreaker instance

**Validation:**
- `name` must be provided
- `name` must be string type

**Usage:**
```python
breaker = execute_circuit_breaker_operation('get', name='api_service')
```

---

### call

**Purpose:** Execute function with circuit breaker protection

**Parameters:**
- `name` (str, required) - Circuit breaker name
- `func` (callable, required) - Function to execute
- `*args` - Positional arguments for function
- `**kwargs` - Keyword arguments for function

**Returns:** Function result

**Validation:**
- `name` must be provided and be string
- `func` must be provided and be callable

**Usage:**
```python
result = execute_circuit_breaker_operation(
    'call',
    name='external_api',
    func=api_request,
    url='https://api.example.com'
)
```

**Behavior:**
- Checks circuit breaker state (CLOSED, OPEN, HALF_OPEN)
- Executes function if allowed
- Records success/failure
- Updates circuit breaker state
- Raises CircuitBreakerError if circuit open

---

### get_all_states

**Purpose:** Get states of all circuit breakers

**Parameters:** None

**Returns:** Dict mapping breaker names to states

**Usage:**
```python
states = execute_circuit_breaker_operation('get_all_states')
# {'api_service': 'CLOSED', 'database': 'HALF_OPEN'}
```

---

### reset_all

**Purpose:** Reset all circuit breakers to initial state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_circuit_breaker_operation('reset_all')
```

---

### get_stats

**Purpose:** Get circuit breaker statistics

**Parameters:** None

**Returns:** Dict with statistics

**Fields:**
- `total_breakers` - Number of circuit breakers
- `states` - Count by state (CLOSED, OPEN, HALF_OPEN)
- `success_count` - Total successful calls
- `failure_count` - Total failed calls
- `circuit_open_count` - Times circuits opened

**Usage:**
```python
stats = execute_circuit_breaker_operation('get_stats')
```

---

### reset

**Purpose:** Reset circuit breaker interface state

**Parameters:** None

**Returns:** bool (True on success)

**Usage:**
```python
execute_circuit_breaker_operation('reset')
```

---

## Import Protection

**Pattern:**
```python
try:
    import circuit_breaker
    _CIRCUIT_BREAKER_AVAILABLE = True
except ImportError as e:
    _CIRCUIT_BREAKER_AVAILABLE = False
    _CIRCUIT_BREAKER_IMPORT_ERROR = str(e)
```

**Error Handling:**
- Checks availability before every operation
- Raises RuntimeError with import error details
- Allows graceful degradation

---

## Validation

**Type Checks:**
- `name` parameters validated as strings
- `func` parameters validated as callable
- Type mismatches raise TypeError

**Required Parameters:**
- Missing required parameters raise ValueError
- Clear error messages indicate which parameter needed

---

## Architecture Compliance

✅ **SUGA Pattern:** Gateway → Interface → Core  
✅ **Import Protection:** Graceful import failure handling  
✅ **Parameter Validation:** Type and presence checks  
✅ **Error Messages:** Clear, actionable error descriptions  
✅ **No Circular Imports:** Clean dependency flow

---

## Related Files

- `/circuit_breaker/` - Circuit breaker implementation
- `/gateway/wrappers/gateway_wrappers_circuit_breaker.py` - Gateway wrappers
- `/circuit_breaker/circuit_breaker_DIRECTORY.md` - Directory structure

---

## Valid Operations List

```python
_VALID_CIRCUIT_BREAKER_OPERATIONS = [
    'get', 'call', 'get_all_states', 'reset_all', 'get_stats', 'reset'
]
```

---

**END OF DOCUMENTATION**
