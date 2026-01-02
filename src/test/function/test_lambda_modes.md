# test_lambda_modes.py

**Version:** 2025-12-08_1  
**Module:** TEST Interface  
**Layer:** Core  
**Lines:** 110

---

## Purpose

Lambda mode testing. Routes special Lambda execution modes (failsafe, diagnostic, emergency) to appropriate handlers. Migrated from lambda_function.py mode routing logic.

---

## Functions

### test_lambda_mode()

**Purpose:** Test Lambda mode by routing to appropriate handler

**Signature:**
```python
def test_lambda_mode(mode: str, event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `mode` - Lambda execution mode identifier
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # HTTP status code
    'body': Dict            # Response body
}
```

**Available Modes:**
- `failsafe` - Minimal failsafe handler
- `diagnostic` - System diagnostics
- `emergency` - Emergency response
- `ha_connection_test` - HA connection testing
- `ha_discovery` - HA device discovery

**Behavior:**
1. Define mode map to handler functions
2. Look up handler for requested mode
3. Route to handler with event and context
4. Return handler response

**Performance:** Variable (depends on mode handler)

**Usage:**
```python
from test import test_lambda_mode

# Test failsafe mode
result = test_lambda_mode('failsafe', event, context)
print(f"Status: {result['statusCode']}")

# Test diagnostic mode
result = test_lambda_mode('diagnostic', event, context)
```

**Error Handling:**
Returns error response for unknown mode:
```python
{
    'statusCode': 400,
    'body': {
        'error': 'Unknown mode: invalid_mode',
        'available_modes': ['failsafe', 'diagnostic', ...]
    }
}
```

---

### test_failsafe_mode()

**Purpose:** Test failsafe mode handler

**Signature:**
```python
def test_failsafe_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # 200 if available, 503 if not
    'body': Dict            # Handler response or error
}
```

**Behavior:**
1. Try to import lambda_failsafe module
2. Call lambda_failsafe_handler(event, context)
3. Return handler response
4. Return 503 if module not available

**Purpose of Failsafe Mode:**
Provides minimal Lambda response when main handler fails. Used for debugging deployment issues.

**Performance:** ~50-100ms (minimal handler)

**Usage:**
```python
from test import test_failsafe_mode

result = test_failsafe_mode(event, context)
if result['statusCode'] == 200:
    print("Failsafe mode operational")
else:
    print(f"Failsafe unavailable: {result['body']['error']}")
```

**Error Response:**
```python
{
    'statusCode': 503,
    'body': {
        'error': 'lambda_failsafe not available',
        'mode': 'failsafe'
    }
}
```

---

### test_diagnostic_mode()

**Purpose:** Test diagnostic mode handler

**Signature:**
```python
def test_diagnostic_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # 200 if available, 503 if not
    'body': Dict            # Diagnostic results or error
}
```

**Behavior:**
1. Try to import lambda_diagnostic module
2. Call lambda_diagnostic.lambda_handler(event, context)
3. Return diagnostic results
4. Return 503 if module not available

**Purpose of Diagnostic Mode:**
Provides system health checks, import testing, configuration validation. Used for troubleshooting Lambda issues.

**Diagnostic Checks:**
- Module import status
- Configuration validation
- Memory usage
- Environment variables
- Gateway connectivity

**Performance:** ~100-500ms (comprehensive diagnostics)

**Usage:**
```python
from test import test_diagnostic_mode

result = test_diagnostic_mode(event, context)
if result['statusCode'] == 200:
    diagnostics = result['body']
    print(f"Memory: {diagnostics['memory_mb']}MB")
    print(f"Imports: {diagnostics['imports_ok']}")
```

**Error Response:**
```python
{
    'statusCode': 503,
    'body': {
        'error': 'lambda_diagnostic not available',
        'mode': 'diagnostic'
    }
}
```

---

### test_emergency_mode()

**Purpose:** Test emergency mode handler

**Signature:**
```python
def test_emergency_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # 200 if available, 503 if not
    'body': Dict            # Emergency response or error
}
```

**Behavior:**
1. Try to import lambda_emergency module
2. Call lambda_emergency.lambda_handler(event, context)
3. Return emergency response
4. Return 503 if module not available

**Purpose of Emergency Mode:**
Provides minimal response when main handler crashes. Last-resort handler for critical failures.

**Emergency Response:**
Returns basic acknowledgment without processing request. Prevents Lambda from timing out.

**Performance:** ~10-50ms (minimal processing)

**Usage:**
```python
from test import test_emergency_mode

result = test_emergency_mode(event, context)
if result['statusCode'] == 200:
    print("Emergency mode operational")
```

**Error Response:**
```python
{
    'statusCode': 503,
    'body': {
        'error': 'lambda_emergency not available',
        'mode': 'emergency'
    }
}
```

---

### test_ha_connection_mode()

**Purpose:** Test HA connection test mode

**Signature:**
```python
def test_ha_connection_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # 200 if available, 503 if not
    'body': Dict            # Connection test results or error
}
```

**Behavior:**
1. Try to import lambda_ha_connection module
2. Call lambda_ha_connection.lambda_handler(event, context)
3. Return connection test results
4. Return 503 if module not available

**Purpose of HA Connection Test:**
Tests Home Assistant WebSocket connection, authentication, and basic API access. Used for diagnosing HA integration issues.

**Connection Tests:**
- WebSocket connection establishment
- Authentication token validation
- Basic API call (get states)
- Response timing

**Performance:** ~500-2000ms (includes HA API calls)

**Usage:**
```python
from test import test_ha_connection_mode

result = test_ha_connection_mode(event, context)
if result['statusCode'] == 200:
    test_results = result['body']
    print(f"WebSocket: {test_results['websocket_ok']}")
    print(f"Auth: {test_results['auth_ok']}")
    print(f"API: {test_results['api_ok']}")
```

**Error Response:**
```python
{
    'statusCode': 503,
    'body': {
        'error': 'lambda_ha_connection not available',
        'mode': 'ha_connection_test'
    }
}
```

---

### test_ha_discovery_mode()

**Purpose:** Test HA discovery mode

**Signature:**
```python
def test_ha_discovery_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]
```

**Parameters:**
- `event` - Lambda event dict
- `context` - Lambda context object

**Returns:**
```python
{
    'statusCode': int,      # 200 if available, 503 if not
    'body': Dict            # Discovery results or error
}
```

**Behavior:**
1. Try to import debug_discovery module
2. Call debug_discovery.lambda_handler(event, context)
3. Return device discovery results
4. Return 503 if module not available

**Purpose of HA Discovery:**
Tests Home Assistant device discovery for Alexa integration. Lists discovered entities and their capabilities.

**Discovery Information:**
- Entity list by domain
- Entity capabilities
- Discovery timing
- Cache status

**Performance:** ~1000-3000ms (full discovery)

**Usage:**
```python
from test import test_ha_discovery_mode

result = test_ha_discovery_mode(event, context)
if result['statusCode'] == 200:
    discovery = result['body']
    print(f"Entities found: {discovery['entity_count']}")
    print(f"Domains: {discovery['domains']}")
```

**Error Response:**
```python
{
    'statusCode': 503,
    'body': {
        'error': 'debug_discovery not available',
        'mode': 'ha_discovery'
    }
}
```

---

## Mode Routing Pattern

**Mode Map Structure:**
```python
mode_map = {
    'failsafe': test_failsafe_mode,
    'diagnostic': test_diagnostic_mode,
    'emergency': test_emergency_mode,
    'ha_connection_test': test_ha_connection_mode,
    'ha_discovery': test_ha_discovery_mode
}
```

**Handler Lookup:**
```python
handler = mode_map.get(mode)
if not handler:
    return {
        'statusCode': 400,
        'body': {
            'error': f'Unknown mode: {mode}',
            'available_modes': list(mode_map.keys())
        }
    }
```

**Handler Invocation:**
```python
return handler(event, context)
```

---

## Lambda Mode Usage

**Trigger Mode via Event:**
```json
{
  "mode": "diagnostic",
  "parameters": {}
}
```

**Test All Modes:**
```python
from test import test_lambda_mode

modes = ['failsafe', 'diagnostic', 'emergency', 'ha_connection_test', 'ha_discovery']

for mode in modes:
    result = test_lambda_mode(mode, event, context)
    print(f"{mode}: {result['statusCode']}")
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** TEST (INT-15)  
**Gateway Access:** Direct to mode handlers

**Import Pattern:**
```python
# From test package
from test import test_lambda_mode, test_failsafe_mode

# Direct import (for testing)
from test.test_lambda_modes import test_diagnostic_mode
```

---

## Dependencies

**Internal:**
- lambda_failsafe (lazy import)
- lambda_diagnostic (lazy import)
- lambda_emergency (lazy import)
- lambda_ha_connection (lazy import)
- debug_discovery (lazy import)

**External:**
- typing (type hints)

---

## Related Files

**Lambda Handlers:**
- lambda_failsafe.py - Failsafe handler
- lambda_diagnostic.py - Diagnostic handler
- lambda_emergency.py - Emergency handler
- lambda_ha_connection.py - HA connection test
- debug_discovery.py - HA discovery test

**Test Modules:**
- test_core.py - Test orchestration
- test_scenarios.py - Error scenario tests
- test_performance.py - Performance tests

**Interface:**
- interface_test.py - TEST interface router

---

## Changelog

### 2025-12-08_1
- Initial version migrated from lambda_function.py
- test_lambda_mode() mode router
- test_failsafe_mode() handler
- test_diagnostic_mode() handler
- test_emergency_mode() handler
- test_ha_connection_mode() handler
- test_ha_discovery_mode() handler
- Lazy imports for all mode handlers
- Error responses for unavailable modes
