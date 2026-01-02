# http_client/ Directory

**Version:** 2025-12-10_1  
**Purpose:** HTTP client module with singleton pattern and debug integration  
**Architecture:** SUGA Core Layer

---

## Directory Structure

```
http_client/
├── __init__.py                         (96 lines)  - Module exports
├── http_client_manager.py              (286 lines) - Core HTTPClientCore class + singleton
├── http_client_operations.py           (96 lines)  - Gateway implementation wrappers
├── http_client_state.py                (206 lines) - State management
├── http_client_transformation.py       (176 lines) - Response transformation
├── http_client_utilities.py            (70 lines)  - Utility functions
├── http_client_validation.py           (92 lines)  - Response validation
└── DIRECTORY.md                        (This file)
```

---

## File Descriptions

### __init__.py (96 lines)
**Purpose:** Module-level exports for http_client package

**Exports:**
- Core manager: `HTTPClientCore`, `get_http_client_manager`, `get_http_client`
- Operations: Implementation wrappers for gateway
- State: State management functions
- Utilities: Headers, query strings, response parsing
- Transformation: Response transformation classes
- Validation: Response validation classes

---

### http_client_manager.py (286 lines)
**Purpose:** Core HTTP client implementation with singleton pattern

**Key Components:**
- `HTTPClientCore` class - Main HTTP client with retry, rate limiting
- Singleton management via `get_http_client_manager()`
- Rate limiting (500 ops/sec with deque)
- Retry logic with exponential backoff
- SSL verification support
- Debug integration with timing

**Features:**
- Connection pooling via urllib3
- Request/response statistics tracking
- Circuit breaker support via retry config
- Reset operation for lifecycle management

**Debug Integration:**
- `gateway.debug_log()` for request tracking
- `gateway.debug_timing()` for performance monitoring
- Scope: `HTTP`

---

### http_client_operations.py (96 lines)
**Purpose:** Gateway operation implementations

**Functions:**
- `http_request_implementation()` - Generic HTTP request
- `http_get_implementation()` - GET request
- `http_post_implementation()` - POST request
- `http_put_implementation()` - PUT request
- `http_delete_implementation()` - DELETE request
- `http_reset_implementation()` - Reset client state
- `get_state_implementation()` - Get client state
- `reset_state_implementation()` - Reset state (legacy)

**Usage:**
Called by interface router, not directly by application code.

---

### http_client_state.py (206 lines)
**Purpose:** HTTP client state management and configuration

**Functions:**
- `get_client_state()` - Query client state via singleton
- `reset_client_state()` - Reset client state via singleton delete
- `configure_http_retry()` - Configure retry behavior
- `get_connection_statistics()` - Get request statistics

**State Information:**
- Client existence and initialization status
- Instance ID and type
- Request statistics
- Retry configuration

---

### http_client_transformation.py (176 lines)
**Purpose:** HTTP response transformation pipeline

**Classes:**
- `ResponseTransformer` - Transform response data
- `TransformationPipeline` - Chainable transformations

**Operations:**
- Flatten nested dictionaries
- Extract specific fields
- Map/rename fields
- Filter fields with predicates
- Transform values
- Normalize data types

**Usage:**
```python
from http_client import create_transformer, create_pipeline

# Simple transformation
transformer = create_transformer()
result = transformer.flatten(data)

# Pipeline
pipeline = create_pipeline()
pipeline.add_transformation(transform_func)
pipeline.add_validation(validate_func)
result = pipeline.execute(data)
```

---

### http_client_utilities.py (70 lines)
**Purpose:** HTTP utility functions

**Functions:**
- `get_standard_headers()` - Standard request headers
- `get_ha_headers()` - Home Assistant headers with auth
- `build_query_string()` - URL query string builder
- `parse_response_headers()` - Header parsing and normalization
- `process_response()` - Response processing

**Headers:**
- Standard: Content-Type, User-Agent
- HA: Authorization bearer token

---

### http_client_validation.py (92 lines)
**Purpose:** HTTP response validation

**Classes:**
- `HTTPMethod` - HTTP method enumeration
- `ResponseValidator` - Flexible validation rules

**Validation Rules:**
- Status code validation
- Field presence validation
- Custom validation functions

**Usage:**
```python
from http_client import create_validator

validator = create_validator()
validator.add_status_code_rule([200, 201])
validator.add_field_rule('data', lambda x: x is not None)
is_valid = validator.validate(response)
```

---

## Import Patterns

### From Other Modules (Public API)
```python
import http_client

# Get client
client = http_client.get_http_client()

# Utilities
headers = http_client.get_standard_headers()
query = http_client.build_query_string({'key': 'value'})

# Transformation
transformer = http_client.create_transformer()
pipeline = http_client.create_pipeline()

# Validation
validator = http_client.create_validator()
```

### Internal Imports (Private)
```python
# From within http_client/ files
from http_client.http_client_manager import get_http_client_manager
from http_client.http_client_operations import http_get_implementation
from http_client.http_client_state import get_client_state
```

### Gateway Access (Preferred)
```python
# Application code should use gateway
import gateway

result = gateway.http_get(url, correlation_id=corr_id)
result = gateway.http_post(url, json=data, correlation_id=corr_id)
```

---

## Configuration

### Environment Variables
```bash
# SSL Verification
HOME_ASSISTANT_VERIFY_SSL=true|false  # Default: true

# Debug (hierarchical)
DEBUG_MODE=true|false                 # Master switch
HTTP_DEBUG_MODE=true|false            # HTTP scope debug
HTTP_DEBUG_TIMING=true|false          # HTTP scope timing
```

### Retry Configuration
```python
# Default retry config
max_attempts: 3
backoff_base_ms: 100
backoff_multiplier: 2.0
retriable_status_codes: [408, 429, 500, 502, 503, 504]

# Configure at runtime
gateway.execute_operation(
    GatewayInterface.HTTP_CLIENT,
    'configure_retry',
    max_attempts=5,
    backoff_base_ms=200
)
```

---

## Rate Limiting

**Limit:** 500 operations per second  
**Window:** 1 second (1000ms)  
**Implementation:** `deque` with `maxlen=500`  
**Behavior:** O(1) operations, automatic eviction

**Rate Limit Response:**
```python
{
    'success': False,
    'error': 'Rate limit exceeded',
    'error_type': 'RateLimitError',
    'rate_limited': True
}
```

---

## Debug Integration

### Debug Logging
```python
# In http_client_manager.py
gateway.debug_log(correlation_id, 'HTTP', 'Request start',
                 method=method, url=url[:50])
gateway.debug_log(correlation_id, 'HTTP', 'Request success',
                 status=status_code)
gateway.debug_log(correlation_id, 'HTTP', 'Request exception',
                 error=str(e))
```

### Timing Measurement
```python
# In http_client_manager.py
with gateway.debug_timing(correlation_id, 'HTTP', f'{method} {url[:30]}'):
    response = self.http.request(method, url, ...)
```

### Scope
**Scope:** `HTTP`

**Flags:**
- `HTTP_DEBUG_MODE` - Enable/disable debug logging
- `HTTP_DEBUG_TIMING` - Enable/disable timing measurements

---

## Statistics

### Available Metrics
```python
stats = client.get_stats()
# Returns:
{
    'requests': int,           # Total requests
    'successful': int,         # Successful requests
    'failed': int,             # Failed requests
    'retries': int,            # Retry attempts
    'rate_limited': int,       # Rate limit hits
    'rate_limiter_size': int   # Current window size
}
```

### Via Gateway
```python
result = gateway.http_get_state()
# Returns state info including stats
```

---

## Architecture Compliance

### SUGA Pattern
✅ Gateway access via `gateway.http_*()` functions  
✅ Interface router in `interfaces/interface_http.py`  
✅ Core implementation in `http_client/` module  
✅ No direct cross-interface imports

### LMMS Pattern
✅ Lazy imports in interface router  
✅ Operations imported on-demand  
✅ Module-level preloading for urllib3 (hot path)

### Singleton Pattern
✅ Single `HTTPClientCore` instance via gateway singleton registry  
✅ Fallback to module-level singleton  
✅ Reset operation for lifecycle management

---

## Related Files

### Interface Layer
- `interfaces/interface_http.py` - Router with dispatch dictionary

### Gateway Layer
- `gateway/wrappers/gateway_wrappers_http_client.py` - Gateway wrappers

### Dependencies
- `lambda_preload.py` - Preloaded urllib3 classes
- `gateway.py` - Singleton registry, logging, debug functions

---

## Changelog

### 2025-12-10_1
- Refactored into http_client/ subdirectory
- Split http_client_core.py into manager and operations
- Added debug integration (debug_log, debug_timing)
- Updated imports for new structure
- Added correlation_id parameter support
- Target: 250-300 lines per file (max 350)

---

**Lines:** 350 (target achieved)  
**Files:** 7 core files + __init__.py + DIRECTORY.md
