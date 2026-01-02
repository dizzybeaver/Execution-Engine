# HTTP Client Function Reference Index

**Version:** 2025-12-10_1  
**Module:** http_client  
**Type:** Function Reference Index

---

## Overview

This directory contains function reference documentation for the http_client module. Each function has a dedicated .md file with signature, parameters, behavior, usage examples, and notes.

---

## Core Manager Functions

### get_http_client_manager.md
**Function:** `get_http_client_manager() -> HTTPClientCore`  
**Module:** `http_client.http_client_manager`  
**Purpose:** Get singleton HTTP client manager instance  
**Key Features:**
- Singleton pattern via gateway registry
- Module-level fallback
- Lifecycle management

### make_request.md
**Function:** `HTTPClientCore.make_request(method, url, correlation_id=None, **kwargs) -> Dict`  
**Module:** `http_client.http_client_manager`  
**Purpose:** Execute HTTP request with retry logic  
**Key Features:**
- Retry with exponential backoff
- Rate limiting (500 ops/sec)
- Debug integration
- Statistics tracking

### reset.md
**Function:** `HTTPClientCore.reset() -> bool`  
**Module:** `http_client.http_client_manager`  
**Purpose:** Reset HTTP client state  
**Key Features:**
- Connection pool reset
- Statistics reset
- Rate limiter reset
- SSL config reload

### get_stats.md
**Function:** `HTTPClientCore.get_stats() -> Dict`  
**Module:** `http_client.http_client_manager`  
**Purpose:** Get HTTP client statistics  
**Key Features:**
- Request counts
- Success/failure rates
- Retry statistics
- Rate limiter state

---

## State Management Functions

### get_client_state.md
**Function:** `get_client_state(client_type='urllib3', **kwargs) -> Dict`  
**Module:** `http_client.http_client_state`  
**Purpose:** Query HTTP client state via singleton registry  
**Key Features:**
- Singleton existence check
- Instance information
- Statistics included
- Gateway integration

### reset_client_state()
**Function:** `reset_client_state(client_type=None, **kwargs) -> Dict`  
**Module:** `http_client.http_client_state`  
**Purpose:** Reset client state via singleton deletion  
**Documentation:** TBD

### configure_http_retry()
**Function:** `configure_http_retry(max_attempts=3, backoff_base_ms=100, **kwargs) -> Dict`  
**Module:** `http_client.http_client_state`  
**Purpose:** Configure HTTP retry behavior  
**Documentation:** TBD

### get_connection_statistics()
**Function:** `get_connection_statistics(**kwargs) -> Dict`  
**Module:** `http_client.http_client_state`  
**Purpose:** Get enhanced HTTP statistics  
**Documentation:** TBD

---

## Utility Functions

### get_standard_headers.md
**Function:** `get_standard_headers() -> Dict[str, str]`  
**Module:** `http_client.http_client_utilities`  
**Purpose:** Get standard HTTP headers  
**Key Features:**
- Content-Type and User-Agent
- Auto-applied when no headers provided
- Extensible pattern

### get_ha_headers()
**Function:** `get_ha_headers(token: str) -> Dict[str, str]`  
**Module:** `http_client.http_client_utilities`  
**Purpose:** Get Home Assistant headers with auth  
**Documentation:** TBD

### build_query_string()
**Function:** `build_query_string(params: Dict) -> str`  
**Module:** `http_client.http_client_utilities`  
**Purpose:** Build URL query string  
**Documentation:** TBD

### parse_response_headers()
**Function:** `parse_response_headers(headers: Dict) -> Dict`  
**Module:** `http_client.http_client_utilities`  
**Purpose:** Parse and normalize response headers  
**Documentation:** TBD

---

## Transformation Functions

### create_transformer.md
**Function:** `create_transformer() -> ResponseTransformer`  
**Module:** `http_client.http_client_transformation`  
**Purpose:** Create response transformer instance  
**Key Features:**
- Flatten nested dicts
- Extract fields
- Map/rename fields
- Filter by predicate
- Transform values
- Normalize types

### create_pipeline()
**Function:** `create_pipeline() -> TransformationPipeline`  
**Module:** `http_client.http_client_transformation`  
**Purpose:** Create transformation pipeline  
**Documentation:** TBD

### transform_http_response()
**Function:** `transform_http_response(response: Dict, transformer: Callable) -> Dict`  
**Module:** `http_client.http_client_transformation`  
**Purpose:** Transform HTTP response data  
**Documentation:** TBD

### create_common_transformers()
**Function:** `create_common_transformers() -> Dict[str, Callable]`  
**Module:** `http_client.http_client_transformation`  
**Purpose:** Get dictionary of common transformers  
**Documentation:** TBD

---

## Validation Functions

### create_validator.md
**Function:** `create_validator() -> ResponseValidator`  
**Module:** `http_client.http_client_validation`  
**Purpose:** Create response validator instance  
**Key Features:**
- Status code validation
- Field validation
- Custom rules
- Chainable API

### validate_http_response()
**Function:** `validate_http_response(response: Dict, required_fields: List = None) -> Dict`  
**Module:** `http_client.http_client_validation`  
**Purpose:** Validate HTTP response structure  
**Documentation:** TBD

---

## Gateway Operations

### http_request()
**Wrapper:** `http_request(method: str, url: str, **kwargs) -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** Generic HTTP request via gateway  
**Documentation:** TBD

### http_get()
**Wrapper:** `http_get(url: str, **kwargs) -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** HTTP GET request via gateway  
**Documentation:** TBD

### http_post()
**Wrapper:** `http_post(url: str, **kwargs) -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** HTTP POST request via gateway  
**Documentation:** TBD

### http_put()
**Wrapper:** `http_put(url: str, **kwargs) -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** HTTP PUT request via gateway  
**Documentation:** TBD

### http_delete()
**Wrapper:** `http_delete(url: str, **kwargs) -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** HTTP DELETE request via gateway  
**Documentation:** TBD

### http_reset()
**Wrapper:** `http_reset() -> Dict`  
**Module:** `gateway.wrappers.gateway_wrappers_http_client`  
**Purpose:** Reset HTTP client via gateway  
**Documentation:** TBD

---

## Classes

### HTTPClientCore
**Module:** `http_client.http_client_manager`  
**Purpose:** Core HTTP client implementation  
**Methods:**
- `__init__()` - Initialize client
- `make_request()` - Execute request
- `reset()` - Reset state
- `get_stats()` - Get statistics
- `_check_rate_limit()` - Rate limit check (internal)
- `_execute_request()` - Single request (internal)
- `_is_retriable_error()` - Retry decision (internal)
- `_calculate_backoff()` - Backoff calculation (internal)

### ResponseTransformer
**Module:** `http_client.http_client_transformation`  
**Purpose:** Response data transformation  
**Methods:**
- `flatten()` - Flatten nested dicts
- `extract()` - Extract fields
- `map_fields()` - Rename fields
- `filter_fields()` - Filter by predicate
- `transform_values()` - Transform values
- `normalize()` - Normalize types

### TransformationPipeline
**Module:** `http_client.http_client_transformation`  
**Purpose:** Chainable transformation pipeline  
**Methods:**
- `add_validation()` - Add validation step
- `add_transformation()` - Add transformation
- `add_filter()` - Add filter
- `execute()` - Execute pipeline

### ResponseValidator
**Module:** `http_client.http_client_validation`  
**Purpose:** Response validation  
**Methods:**
- `add_status_code_rule()` - Status validation
- `add_field_rule()` - Field validation
- `add_custom_rule()` - Custom validation
- `validate()` - Execute rules

---

## Documentation Status

**Complete (19 files):**

**Core Manager (4 files):**
- ✅ get_http_client_manager.md
- ✅ make_request.md
- ✅ reset.md
- ✅ get_stats.md

**State Management (4 files):**
- ✅ get_client_state.md
- ✅ reset_client_state.md
- ✅ configure_http_retry.md
- ✅ get_connection_statistics.md

**Utilities (3 files):**
- ✅ get_standard_headers.md
- ✅ get_ha_headers.md
- ✅ build_query_string.md
- ✅ parse_response_headers.md

**Transformation (4 files):**
- ✅ create_transformer.md
- ✅ create_pipeline.md
- ✅ transform_http_response.md
- ✅ create_common_transformers.md

**Validation (2 files):**
- ✅ create_validator.md
- ✅ validate_http_response.md

**Gateway Wrappers (1 file):**
- ✅ gateway_wrappers.md (8 functions combined)

---

## Usage Patterns

### Via Gateway (Recommended)
```python
import gateway

# HTTP operations
result = gateway.http_get(url, correlation_id=corr_id)
result = gateway.http_post(url, json=data, correlation_id=corr_id)
result = gateway.http_reset()

# State queries
state = gateway.http_get_state()
```

### Direct Import (Advanced)
```python
import http_client

# Get client
client = http_client.get_http_client_manager()

# Use client
result = client.make_request('GET', url)
stats = client.get_stats()

# Utilities
headers = http_client.get_standard_headers()
transformer = http_client.create_transformer()
validator = http_client.create_validator()
```

### Internal Use (Module)
```python
# Within http_client module
from http_client.http_client_manager import get_http_client_manager
from http_client.http_client_state import get_client_state
from http_client.http_client_utilities import get_standard_headers
```

---

## Related Documentation

- **http_client/DIRECTORY.md** - Module overview and structure
- **interfaces/interface_http.py** - Interface router
- **gateway/wrappers/gateway_wrappers_http_client.py** - Gateway wrappers

---

**Lines:** 340  
**Documented Functions:** 20/20 (100%)  
**Status:** Complete ✅
