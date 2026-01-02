# utility_types.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_types.py  
**Module:** Utility type definitions and constants

---

## Overview

Core types, enums, and constants for the utility interface. Defines operation enums, metrics tracking, and response templates.

**File:** `utility/utility_types.py`  
**Lines:** 111  
**Pattern:** Type definitions and constants

---

## Configuration Constants

### DEFAULT_USE_TEMPLATES

**Type:** bool  
**Default:** True  
**Purpose:** Enable template-based response optimization

**Override:** Environment variable `USE_JSON_TEMPLATES`

---

### DEFAULT_USE_GENERIC_OPERATIONS

**Type:** bool  
**Default:** True  
**Purpose:** Enable generic cross-interface operations

---

### DEFAULT_MAX_JSON_CACHE_SIZE

**Type:** int  
**Default:** 100  
**Purpose:** Maximum JSON cache entries

**Behavior:**
- LRU eviction when full
- Per-manager instance limit

---

## Response Templates

### Success Templates

#### SUCCESS_TEMPLATE

**Template:** `'{"success":true,"message":"%s","timestamp":%d,"data":%s}'`

**Parameters:**
- `%s` - message (str)
- `%d` - timestamp (int)
- `%s` - data (JSON string)

**Usage:**
```python
json_str = SUCCESS_TEMPLATE % ('Operation completed', 1702480800, '{"key":"value"}')
```

---

#### SUCCESS_WITH_CORRELATION

**Template:** `'{"success":true,"message":"%s","timestamp":%d,"data":%s,"correlation_id":"%s"}'`

**Parameters:**
- `%s` - message (str)
- `%d` - timestamp (int)
- `%s` - data (JSON string)
- `%s` - correlation_id (str)

---

### Error Templates

#### ERROR_TEMPLATE

**Template:** `'{"success":false,"error":"%s","timestamp":%d}'`

**Parameters:**
- `%s` - error message (str)
- `%d` - timestamp (int)

---

#### ERROR_WITH_CODE

**Template:** `'{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s}'`

**Parameters:**
- `%s` - error message (str)
- `%s` - error_code (str)
- `%d` - timestamp (int)
- `%s` - details (JSON string)

---

#### ERROR_WITH_CORRELATION

**Template:** `'{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s,"correlation_id":"%s"}'`

**Parameters:**
- `%s` - error message (str)
- `%s` - error_code (str)
- `%d` - timestamp (int)
- `%s` - details (JSON string)
- `%s` - correlation_id (str)

---

### Lambda Response Template

#### LAMBDA_RESPONSE

**Template:** `'{"statusCode":%d,"body":%s,"headers":%s}'`

**Parameters:**
- `%d` - statusCode (int)
- `%s` - body (JSON string)
- `%s` - headers (JSON string)

---

### Header Constants

#### DEFAULT_HEADERS_JSON

**Type:** str  
**Value:** `'{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}'`

**Purpose:** Pre-formatted JSON headers for template use

---

#### DEFAULT_HEADERS_DICT

**Type:** dict  
**Value:**
```python
{
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}
```

**Purpose:** Headers dict for standard path

---

#### EMPTY_DATA

**Type:** str  
**Value:** `'{}'`

**Purpose:** Empty data placeholder for templates

---

## Enums

### UtilityOperation

**Purpose:** Enumeration of all utility operations  
**Type:** Enum

**Members:**

#### UUID and Timestamp
- `GENERATE_UUID` = "generate_uuid"
- `GET_TIMESTAMP` = "get_timestamp"
- `GENERATE_CORRELATION_ID` = "generate_correlation_id"

#### Response Formatting
- `FORMAT_RESPONSE` = "format_response"
- `FORMAT_RESPONSE_FAST` = "format_response_fast"
- `CREATE_SUCCESS_RESPONSE` = "create_success_response"
- `CREATE_ERROR_RESPONSE` = "create_error_response"

#### Data Operations
- `PARSE_JSON` = "parse_json"
- `PARSE_JSON_SAFELY` = "parse_json_safely"
- `DEEP_MERGE` = "deep_merge"
- `SAFE_GET` = "safe_get"
- `FORMAT_BYTES` = "format_bytes"

#### Validation
- `VALIDATE_STRING` = "validate_string"
- `VALIDATE_DATA_STRUCTURE` = "validate_data_structure"
- `VALIDATE_OPERATION_PARAMETERS` = "validate_operation_parameters"

#### Sanitization
- `SANITIZE_DATA` = "sanitize_data"
- `SANITIZE_RESPONSE_DATA` = "sanitize_response_data"
- `SAFE_STRING_CONVERSION` = "safe_string_conversion"

#### Utilities
- `MERGE_DICTIONARIES` = "merge_dictionaries"
- `EXTRACT_ERROR_DETAILS` = "extract_error_details"
- `FORMAT_DATA_FOR_RESPONSE` = "format_data_for_response"

#### Performance
- `CLEANUP_CACHE` = "cleanup_cache"
- `GET_PERFORMANCE_STATS` = "get_performance_stats"
- `OPTIMIZE_PERFORMANCE` = "optimize_performance"
- `CONFIGURE_CACHING` = "configure_caching"

**Usage:**
```python
from utility_types import UtilityOperation

# Access operation names
op_name = UtilityOperation.PARSE_JSON.value
# Result: "parse_json"

# Iterate operations
for op in UtilityOperation:
    print(op.value)
```

---

## Dataclasses

### UtilityMetrics

**Purpose:** Metrics tracking for utility operations  
**Type:** dataclass

**Fields:**

#### operation_type
- **Type:** str
- **Purpose:** Operation name
- **Required:** Yes

#### call_count
- **Type:** int
- **Default:** 0
- **Purpose:** Total number of calls

#### total_duration_ms
- **Type:** float
- **Default:** 0.0
- **Purpose:** Total execution time

#### avg_duration_ms
- **Type:** float
- **Default:** 0.0
- **Purpose:** Average execution time

#### cache_hits
- **Type:** int
- **Default:** 0
- **Purpose:** Cache hit count

#### cache_misses
- **Type:** int
- **Default:** 0
- **Purpose:** Cache miss count

#### error_count
- **Type:** int
- **Default:** 0
- **Purpose:** Error count

#### template_usage
- **Type:** int
- **Default:** 0
- **Purpose:** Template usage count

**Usage:**
```python
from utility_types import UtilityMetrics

# Create metrics
metrics = UtilityMetrics(operation_type='parse_json')

# Update metrics
metrics.call_count += 1
metrics.total_duration_ms += 1.5
metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
metrics.cache_hits += 1

# Calculate rates
cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
error_rate = metrics.error_count / metrics.call_count * 100
```

---

## Usage Patterns

### Import Constants
```python
from utility_types import (
    DEFAULT_MAX_JSON_CACHE_SIZE,
    DEFAULT_HEADERS_DICT,
    SUCCESS_TEMPLATE
)
```

### Use Templates
```python
from utility_types import SUCCESS_TEMPLATE
import json
import time

response = SUCCESS_TEMPLATE % (
    'Operation completed',
    int(time.time()),
    json.dumps({'key': 'value'})
)
result = json.loads(response)
```

### Use Enum
```python
from utility_types import UtilityOperation

operation = UtilityOperation.PARSE_JSON
print(operation.value)  # "parse_json"
```

### Create Metrics
```python
from utility_types import UtilityMetrics

metrics = UtilityMetrics(operation_type='parse_json')
metrics.call_count = 100
metrics.avg_duration_ms = 1.25
```

---

## Related Files

- **Manager:** `utility/utility_manager.py` (uses UtilityMetrics)
- **Response:** `utility/utility_response.py` (uses templates)
- **Core:** `utility/utility_core.py` (uses constants)

---

**END OF DOCUMENTATION**
