# utility/ Directory

**Version:** 2025-12-13_1  
**Purpose:** Utility operations with hierarchical debug support  
**Module:** Utility (UTILITY interface)

---

## Files

### __init__.py (96 lines)
Module initialization - exports all public utility functions

**Exports:**
- UtilityOperation, UtilityMetrics, constants (from utility_types)
- SharedUtilityCore, get_utility_manager (from utility_manager)
- ResponseFormatter, response functions (from utility_response)
- All implementation functions (from utility_core)

---

### utility_types.py (111 lines)
Utility type definitions and enums

**Classes:**
- UtilityOperation - Enum of all utility operations
- UtilityMetrics - Metrics tracking dataclass

**Constants:**
- DEFAULT_USE_TEMPLATES, DEFAULT_USE_GENERIC_OPERATIONS, DEFAULT_MAX_JSON_CACHE_SIZE
- Response templates (SUCCESS_TEMPLATE, ERROR_TEMPLATE, etc.)
- Default headers (DEFAULT_HEADERS_JSON, DEFAULT_HEADERS_DICT)

---

### utility_manager.py (295 lines)
Core utility manager with rate limiting and metrics

**Classes:**
- SharedUtilityCore - Core utility manager

**Functions:**
- get_utility_manager() - Singleton instance accessor

**Features:**
- UUID generation with pool optimization
- Timestamp generation
- Correlation ID generation
- Template rendering with {placeholder} substitution
- Typed config retrieval from environment
- Performance metrics tracking
- Rate limiting (1000 ops/sec)
- SINGLETON pattern (LESS-18)
- Debug integration (UTILITY scope)

**Key Methods:**
- generate_uuid() - UUID with pool optimization
- get_timestamp() - ISO timestamp
- generate_correlation_id_impl() - Correlation ID with optional prefix
- render_template_impl() - Template rendering
- config_get_impl() - Typed config retrieval
- get_performance_stats() - Comprehensive statistics
- reset() - Reset manager state

**Compliance:**
- AP-08: No threading locks (Lambda single-threaded)
- DEC-04: Lambda single-threaded model
- LESS-18: SINGLETON pattern
- LESS-21: Rate limiting for DoS protection

---

### utility_data.py (273 lines)
Data operations for parsing, merging, and formatting

**Classes:**
- UtilityDataOperations - Data operation methods

**Methods:**
- parse_json() - Parse JSON string
- parse_json_safely() - Parse with caching and error handling
- deep_merge() - Deep merge dictionaries
- safe_get() - Safely get nested dict value (dot notation)
- format_bytes() - Human-readable byte formatting
- merge_dictionaries() - Merge multiple dicts
- format_data_for_response() - Format data for API response
- cleanup_cache() - Clean up JSON cache
- optimize_performance() - Optimize based on usage patterns
- configure_caching() - Configure cache settings

**Features:**
- JSON parsing with cache (100 item limit)
- Nested dictionary operations
- Performance optimization
- Debug integration

---

### utility_validation.py (116 lines)
Validation operations for data integrity

**Classes:**
- UtilityValidationOperations - Validation methods

**Methods:**
- validate_string() - String length and content validation
- validate_data_structure() - Type and field validation
- validate_operation_parameters() - Generic parameter validation

**Features:**
- Comprehensive validation with detailed error messages
- Debug integration
- Type checking
- Required field verification

---

### utility_sanitize.py (116 lines)
Sanitization operations for data cleaning

**Classes:**
- UtilitySanitizeOperations - Sanitization methods

**Methods:**
- sanitize_data() - Remove sensitive fields from dicts
- safe_string_conversion() - Safe string conversion with length limits
- extract_error_details() - Extract error info with stack trace

**Features:**
- PII protection (password, secret, token, api_key, private_key)
- Safe string conversion with truncation
- Detailed error extraction
- Debug integration

---

### utility_response.py (243 lines)
Response formatting utilities (preserved)

**Classes:**
- ResponseFormatter - Response formatting methods

**Functions:**
- format_response_fast() - Fast Lambda response with templates
- format_response() - Standard Lambda response formatting
- create_success_response() - Success response with optional correlation ID
- create_error_response() - Error response with optional correlation ID

**Features:**
- Template-based fast path
- Recursion protection
- JSON sanitization for problematic data
- Debug integration

---

### utility_core.py (197 lines)
Gateway implementation functions for utility interface

**Functions:**
- 21 implementation functions covering all utility operations
- Debug integration with correlation ID support
- Lazy initialization of operation classes

**Implementation Functions:**
- UUID/Timestamp: generate_uuid, get_timestamp, generate_correlation_id
- Template/Config: render_template, config_get
- Data: parse_json, parse_json_safely, deep_merge, safe_get, format_bytes
- Validation: validate_string, validate_data_structure, validate_operation_parameters
- Sanitization: sanitize_data, safe_string_conversion, extract_error_details
- Performance: cleanup_cache, optimize_performance, configure_caching, get_stats, reset

---

## Architecture

### SUGA Pattern Compliance
```
Gateway Layer (gateway/wrappers/gateway_wrappers_utility.py)
    ↓
Interface Layer (interface/interface_utility.py)
    ↓
Implementation Layer (utility/utility_core.py)
    ↓
Manager Layer (utility/utility_manager.py)
    ↓
Operations (utility_data.py, utility_validation.py, utility_sanitize.py)
```

### Import Patterns

**Public (from other modules):**
```python
import utility

# Access public functions
utility.generate_uuid_implementation()
utility.parse_json_implementation(data)
```

**Private (within utility module):**
```python
from utility.utility_manager import get_utility_manager
from utility.utility_data import UtilityDataOperations
```

---

## Debug Integration

### Hierarchical Debug Control

**Master Switch:**
- DEBUG_MODE - Enables all debugging

**Scope Switches:**
- UTILITY_DEBUG_MODE - Utility debug logging
- UTILITY_DEBUG_TIMING - Utility timing measurements

**Debug Points:**
- UUID generation (pool vs new)
- Timestamp generation
- Template rendering
- Config retrieval and type conversion
- JSON parsing (cache hit/miss)
- Data operations (merge, safe_get, etc.)
- Validation operations
- Sanitization operations
- Cache cleanup
- Performance optimization
- Statistics gathering

### Debug Output Examples

```
[abc123] [UTILITY-DEBUG] UUID from pool (pool_size=15)
[abc123] [UTILITY-DEBUG] Timestamp generated (timestamp=2025-12-13T14:30:00Z)
[abc123] [UTILITY-DEBUG] Rendering template (placeholder_count=5)
[abc123] [UTILITY-TIMING] render_template: 12.34ms
[abc123] [UTILITY-DEBUG] Template rendered successfully
[abc123] [UTILITY-DEBUG] Config retrieved and converted (key=DEBUG_MODE, result_type=bool)
[abc123] [UTILITY-DEBUG] JSON parse cache hit
[abc123] [UTILITY-DEBUG] Dictionaries merged (dict1_keys=10, dict2_keys=5, result_keys=12)
[abc123] [UTILITY-DEBUG] String validation passed (length=256)
[abc123] [UTILITY-DEBUG] Data sanitized (redacted_count=3, total_keys=20)
```

---

## Usage Patterns

### Via Gateway (Recommended)
```python
from gateway import generate_uuid, parse_json, render_template

# Generate UUID
uuid_val = generate_uuid()

# Parse JSON
data = parse_json('{"key": "value"}')

# Render template
result = render_template(
    template={'message': '{msg}', 'user': '{user}'},
    data={'msg': 'Hello', 'user': 'Alice'}
)
```

### Direct (Testing Only)
```python
import utility

# Generate correlation ID
corr_id = utility.generate_correlation_id_implementation(prefix='req')

# Parse JSON safely with caching
data = utility.parse_json_safely_implementation('{"key": "value"}')

# Validate string
result = utility.validate_string_implementation('test', min_length=1, max_length=100)
```

---

## Key Features

### UUID Pool Optimization
- Pre-generated UUID pool
- Reduces uuid.uuid4() calls
- Automatic pool replenishment
- Tracks pool reuse in statistics

### Template Rendering
- {placeholder} substitution
- Nested dict/list support
- Auto correlation ID injection
- JSON-safe rendering

### Typed Config Retrieval
- Auto type conversion based on default
- Boolean, int, float, string support
- Environment variable reading
- Fallback to default on error

### JSON Caching
- 100-item LRU cache
- Cache hit/miss tracking
- Automatic eviction
- Performance metrics

### Data Sanitization
- Sensitive field removal (password, secret, token, api_key, private_key)
- Recursive dict processing
- PII protection
- Debug tracking

---

## Statistics

### Overall Stats
- template_hits - Template usage count
- template_fallbacks - Template fallback count
- cache_optimizations - Cache optimization count
- id_pool_reuse - UUID pool reuse count
- lugs_integrations - LUGS integration count
- templates_rendered - Total templates rendered
- configs_retrieved - Total configs retrieved

### Operation Stats (per operation)
- call_count - Total operation calls
- avg_duration_ms - Average duration
- cache_hit_rate_percent - Cache hit percentage
- error_rate_percent - Error percentage
- template_usage_percent - Template usage percentage
- cache_hits, cache_misses - Cache statistics
- error_count - Total errors
- template_usage - Template use count

---

## Related Files

**Interface:**
- interface/interface_utility.py - Interface router

**Gateway:**
- gateway/wrappers/gateway_wrappers_utility.py - Gateway wrappers

**Debug:**
- debug/debug_config.py - Debug configuration
- debug/debug_core.py - Debug logging and timing

---

## File Size Summary

| File | Lines | Status |
|------|-------|--------|
| __init__.py | 96 | ✓ Well under limit |
| utility_types.py | 111 | ✓ Well under limit |
| utility_manager.py | 295 | ✓ Under 300 target |
| utility_data.py | 273 | ✓ Well under limit |
| utility_validation.py | 116 | ✓ Well under limit |
| utility_sanitize.py | 116 | ✓ Well under limit |
| utility_response.py | 243 | ✓ Well under limit |
| utility_core.py | 197 | ✓ Well under limit |
| **Total** | **1,447** | **8 files** |

---

## Changelog

### 2025-12-13_1
- Split monolithic utility_core.py (535 lines) into modular structure
- Added hierarchical debug integration (UTILITY scope)
- Integrated debug_log() and debug_timing() throughout
- Added correlation ID support for debug tracking
- Created module __init__.py for clean imports
- Updated interface to use module import pattern
- All files under 300-line target (max 295 lines)
- Preserved all existing functionality
- Maintained rate limiting and SINGLETON pattern
- Kept utility_types.py and utility_response.py as-is
- Created logical separation: manager, data, validation, sanitize
