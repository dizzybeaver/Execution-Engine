# circuit_breaker/ Directory

**Version:** 2025-12-13_1  
**Purpose:** Circuit breaker pattern implementation with hierarchical debug support  
**Module:** Circuit Breaker (CIRCUIT_BREAKER interface)

---

## Files

### __init__.py (30 lines)
Module initialization - exports all public circuit breaker functions

**Exports:**
- CircuitState, CircuitBreaker (from circuit_breaker_state)
- CircuitBreakerCore, get_circuit_breaker_manager (from circuit_breaker_manager)
- Implementation functions (from circuit_breaker_core)

---

### circuit_breaker_state.py (217 lines)
Circuit breaker state enum and individual breaker implementation

**Classes:**
- CircuitState - Enum (CLOSED, OPEN, HALF_OPEN)
- CircuitBreaker - Individual circuit breaker instance

**Features:**
- State management (closed → open → half_open → closed)
- Failure tracking and threshold enforcement
- Statistics collection
- Debug integration (CIRCUIT_BREAKER scope)
- Timing measurement for protected calls
- Gateway integration for metrics

**Key Methods:**
- call() - Execute function with circuit breaker protection
- reset() - Reset circuit breaker state
- get_state() - Get current state and statistics

---

### circuit_breaker_manager.py (263 lines)
Circuit breaker manager with singleton pattern and rate limiting

**Classes:**
- CircuitBreakerCore - Manager for multiple circuit breakers

**Functions:**
- get_circuit_breaker_manager() - Singleton instance accessor

**Features:**
- Manages multiple named circuit breakers
- Rate limiting (1000 ops/sec)
- SINGLETON pattern (LESS-18)
- Debug integration (CIRCUIT_BREAKER scope)
- Statistics aggregation
- Gateway SINGLETON registry integration

**Key Methods:**
- get() - Get or create circuit breaker by name
- call() - Execute with circuit breaker protection
- get_all_states() - Get all breaker states
- reset_all() - Reset all breakers
- get_stats() - Get manager statistics
- reset() - Reset manager state

**Compliance:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

### circuit_breaker_core.py (195 lines)
Gateway implementation functions for circuit breaker interface

**Functions:**
- get_breaker_implementation() - Get circuit breaker state
- execute_with_breaker_implementation() - Execute with protection
- get_all_states_implementation() - Get all states
- reset_all_implementation() - Reset all breakers
- get_stats_implementation() - Get statistics
- reset_implementation() - Reset manager

**Features:**
- Gateway-facing implementation layer
- Debug integration with correlation ID support
- SINGLETON manager usage
- Success/error response formatting

---

## Architecture

### SUGA Pattern Compliance
```
Gateway Layer (gateway/wrappers/gateway_wrappers_circuit_breaker.py)
    ↓
Interface Layer (interface/interface_circuit_breaker.py)
    ↓
Implementation Layer (circuit_breaker/circuit_breaker_core.py)
    ↓
Manager Layer (circuit_breaker/circuit_breaker_manager.py)
    ↓
State Layer (circuit_breaker/circuit_breaker_state.py)
```

### Import Patterns

**Public (from other modules):**
```python
import circuit_breaker

# Access public functions
circuit_breaker.get_breaker_implementation(...)
circuit_breaker.execute_with_breaker_implementation(...)
```

**Private (within circuit_breaker module):**
```python
from circuit_breaker.circuit_breaker_state import CircuitBreaker
from circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager
```

---

## Debug Integration

### Hierarchical Debug Control

**Master Switch:**
- DEBUG_MODE - Enables all debugging

**Scope Switches:**
- CIRCUIT_BREAKER_DEBUG_MODE - Circuit breaker debug logging
- CIRCUIT_BREAKER_DEBUG_TIMING - Circuit breaker timing measurements

**Debug Points:**
- Circuit state transitions (CLOSED → OPEN → HALF_OPEN)
- Rate limit enforcement
- Protected call execution
- Failure threshold tracking
- Manager operations (get, call, reset)
- Statistics gathering

### Debug Output Examples

```
[abc123] [CIRCUIT_BREAKER-DEBUG] Creating new circuit breaker (breaker=api_calls, threshold=5, timeout=60)
[abc123] [CIRCUIT_BREAKER-DEBUG] Executing protected call (breaker=api_calls, state=closed)
[abc123] [CIRCUIT_BREAKER-TIMING] call:api_calls: 45.23ms
[abc123] [CIRCUIT_BREAKER-DEBUG] Call failed - failures: 3/5 (breaker=api_calls, error=Connection timeout)
[abc123] [CIRCUIT_BREAKER-DEBUG] Threshold exceeded - opening circuit (breaker=api_calls)
[abc123] [CIRCUIT_BREAKER-DEBUG] Circuit OPEN - rejecting call (breaker=api_calls, failures=5)
[abc123] [CIRCUIT_BREAKER-DEBUG] Transitioning to HALF_OPEN (breaker=api_calls)
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import execute_with_circuit_breaker, get_circuit_breaker_state

# Execute protected function
result = execute_with_circuit_breaker('api_calls', my_function, args=(param1,))

# Check breaker state
state = get_circuit_breaker_state('api_calls')
if state['state'] == 'open':
    print("Circuit is open!")
```

### Direct (Testing Only)
```python
import circuit_breaker

# Get breaker state
state = circuit_breaker.get_breaker_implementation(
    name='api_calls',
    failure_threshold=5,
    timeout=60
)

# Execute with protection
result = circuit_breaker.execute_with_breaker_implementation(
    name='api_calls',
    func=my_function,
    args=(param1,)
)
```

---

## Statistics

### Per-Breaker Statistics
- total_calls - Total calls attempted
- successful_calls - Successful executions
- failed_calls - Failed executions
- rejected_calls - Rejected due to open circuit

### Manager Statistics
- total_operations - Total manager operations
- breakers_count - Number of circuit breakers
- rate_limited_count - Rate limit hits
- current_rate_limit_size - Current window size
- max_rate_limit - Maximum operations per window

---

## Related Files

**Interface:**
- interface/interface_circuit_breaker.py - Interface router

**Gateway:**
- gateway/wrappers/gateway_wrappers_circuit_breaker.py - Gateway wrappers

**Debug:**
- debug/debug_config.py - Debug configuration
- debug/debug_core.py - Debug logging and timing

---

## File Size Summary

| File | Lines | Status |
|------|-------|--------|
| __init__.py | 30 | ✓ Well under limit |
| circuit_breaker_state.py | 217 | ✓ Under 250 target |
| circuit_breaker_manager.py | 263 | ✓ Under 300 target |
| circuit_breaker_core.py | 195 | ✓ Well under limit |
| **Total** | **705** | **4 files** |

---

## Changelog

### 2025-12-13_1
- Split monolithic circuit_breaker_core.py into 4 logical files
- Added hierarchical debug integration (CIRCUIT_BREAKER scope)
- Integrated debug_log() and debug_timing() throughout
- Added correlation ID support for debug tracking
- Created module __init__.py for clean imports
- Updated interface to use module import pattern
- All files under 300-line target (max 263 lines)
