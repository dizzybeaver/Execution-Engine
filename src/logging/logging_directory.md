# Logging Interface Directory

**Version:** 2025-12-08_1  
**Purpose:** LOGGING interface module with subdirectory structure  
**Layer:** Interface Layer (INT-03)

---

## Directory Structure

```
logging/
├── __init__.py                  # Module initialization & exports
├── logging_types.py             # Type definitions & enums (107 lines)
├── logging_manager.py           # LoggingCore class & singleton (281 lines)
├── logging_core.py              # Implementation functions (257 lines)
├── logging_operations.py        # Operation dispatcher (74 lines)
└── DIRECTORY.md                 # This file
```

---

## File Descriptions

### __init__.py (84 lines)
**Purpose:** Module initialization with exports

**Exports:**
- Types: `LogOperation`, `LogTemplate`, `ErrorLogLevel`, `ErrorEntry`, `ErrorLogEntry`
- Manager: `LoggingCore`, `get_logging_core`, `RateLimitTracker`
- Core implementations: 9 `_execute_*_implementation` functions
- Operations: `execute_logging_operation`

**Import Pattern:**
```python
# Public functions
import logging

# Private functions
from logging.logging_core import _execute_log_info_implementation
```

---

### logging_types.py (107 lines)
**Purpose:** Type definitions and enumerations

**Contains:**
- `LogOperation` - Enum of logging operations
- `LogTemplate` - Pre-formatted log templates
- `ErrorLogLevel` - Error severity levels
- `ErrorEntry` - Simple error entry dataclass
- `ErrorLogEntry` - Structured error response log entry

**Dependencies:** None (standard library only)

---

### logging_manager.py (281 lines)
**Purpose:** Core logging manager class with singleton pattern

**Key Components:**
- `RateLimitTracker` - Rate limiting for log flooding prevention
- `LoggingCore` - Main logging manager class
- `get_logging_core()` - Singleton factory function

**Features:**
- Template optimization (optional)
- Rate limiting (500 logs per invocation)
- Error tracking (100 entry deque)
- Statistics collection
- Phase 1 reset() support

**Dependencies:**
- `logging.logging_types` (ErrorLogLevel, ErrorEntry, LogTemplate)
- `gateway` (singleton_get, singleton_register) - lazy import

---

### logging_core.py (257 lines)
**Purpose:** Core implementation functions with security hardening

**Key Features:**
- Exception sanitization (CVE-LOG-004 mitigation)
- Debug integration via debug module
- Security: Removes sensitive paths, credentials
- Hierarchical debug control

**Functions:**
- `_execute_log_info_implementation()`
- `_execute_log_warning_implementation()`
- `_execute_log_error_implementation()`
- `_execute_log_debug_implementation()`
- `_execute_log_critical_implementation()`
- `_execute_log_operation_start_implementation()`
- `_execute_log_operation_success_implementation()`
- `_execute_log_operation_failure_implementation()`
- `_execute_log_reset_implementation()`

**Security Features:**
- Sanitizes file paths (removes `/var/task/`, `/opt/python/`)
- Redacts credentials (password=, token=)
- Limits error messages (500 chars)
- Optional traceback in debug mode only

**Dependencies:**
- `logging.logging_manager` (get_logging_core)
- `logging.logging_types` (ErrorLogLevel)
- `debug` (get_debug_config) - lazy import for hierarchical control

---

### logging_operations.py (74 lines)
**Purpose:** Operation dispatcher with performance monitoring

**Note:** Deprecated - retained for backward compatibility

**Function:**
- `execute_logging_operation()` - Routes through interface_logging

**Metrics:**
- Records dispatcher timing via METRICS interface
- Performance monitoring per operation

**Dependencies:**
- `logging.logging_types` (LogOperation)
- `interface_logging` (execute_logging_operation) - lazy import
- `gateway` (execute_operation, GatewayInterface) - lazy import

---

## Integration Points

### Interface Router
**Location:** `/interface_logging.py`  
**Purpose:** LOGGING interface router with security firewall  
**Lines:** 200

**Key Features:**
- Security sanitization (CVE-LOG-001/002/003)
- Parameter validation
- Operation dispatch dictionary
- Sensitive data redaction

### Gateway Wrappers
**Location:** `/gateway/wrappers/gateway_wrappers_logging.py`  
**Purpose:** Convenience wrappers for gateway access  
**Lines:** 77

**Exported Functions:**
- `log_info(message, **kwargs)`
- `log_error(message, error, **kwargs)`
- `log_warning(message, **kwargs)`
- `log_debug(message, **kwargs)`
- `log_operation_start(operation_name, **kwargs)`
- `log_operation_success(operation_name, duration_ms, **kwargs)`
- `log_operation_failure(operation_name, error, **kwargs)`

---

## Usage Patterns

### Basic Logging
```python
import gateway

gateway.log_info("Operation started", request_id="12345")
gateway.log_error("Operation failed", error=exception)
gateway.log_warning("Resource limit approaching")
gateway.log_debug("Debug trace information")
```

### Operation Logging
```python
import gateway

gateway.log_operation_start("user_authentication", user_id="user123")
gateway.log_operation_success("user_authentication", duration_ms=45.2)
gateway.log_operation_failure("user_authentication", error="Invalid credentials")
```

### Direct Interface Usage (Internal)
```python
from interface_logging import execute_logging_operation

execute_logging_operation('log_info', message="System initialized")
```

### Singleton Access (Internal)
```python
from logging.logging_manager import get_logging_core

core = get_logging_core()
stats = core.get_error_stats()
```

---

## Configuration

### Environment Variables

**Debug Control:**
```bash
DEBUG_MODE=true                 # Master switch
LOGGING_DEBUG_MODE=true         # Scope-specific debug
LOGGING_DEBUG_TIMING=true       # Scope-specific timing
```

**Rate Limiting:**
```bash
LOG_RATE_LIMIT_ENABLED=true    # Enable rate limiting (default: true)
MAX_LOGS_PER_INVOCATION=500    # Max logs per Lambda invocation
```

**Template Optimization:**
```bash
USE_LOG_TEMPLATES=false         # Enable template caching (default: false)
```

**Security:**
```bash
SANITIZE_EXCEPTIONS=true        # Exception sanitization (default: true)
LOG_LEVEL=INFO                  # Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
```

---

## Security Features

### CVE Mitigations

**CVE-LOG-001:** Message injection prevention
- Strips newlines and carriage returns
- Limits message length (500 chars)

**CVE-LOG-002:** Extra data injection prevention  
- Sanitizes all extra context parameters
- Limits extra value length (200 chars)

**CVE-LOG-003:** Sensitive data logging
- Redacts password, token, secret, api_key, auth, credential
- Replaces with `***REDACTED***`

**CVE-LOG-004:** Exception information disclosure
- Removes internal file paths
- Sanitizes AWS Lambda environment details
- Limits traceback exposure (production mode)
- Optional full traceback (debug mode only)

---

## Performance Characteristics

### Memory Usage
- LoggingCore: ~8KB base
- Error log: ~2KB (100 entry deque)
- Template cache: ~4KB (average)
- Total: ~14KB per instance

### Operation Timing
- log_info/warning/debug: <1ms
- log_error (with tracking): <2ms
- log_operation_*: <1ms
- get_*_stats: <1ms

### Rate Limiting
- Default: 500 logs per Lambda invocation
- Overhead: <0.1ms per log check
- Warning printed once when limit exceeded

---

## Dependencies

### Internal
- `gateway` - SINGLETON, METRICS interfaces (lazy import)
- `debug` - Hierarchical debug control (lazy import)
- `interface_logging` - Interface router (lazy import)

### External (Standard Library)
- `os` - Environment variable access
- `time` - Performance timing
- `logging` - Python logging framework
- `typing` - Type hints
- `collections` - deque for error log
- `datetime` - Timestamp management
- `traceback` - Exception formatting

---

## Changelog

### 2025-12-08_1
- **REFACTORED:** Moved to logging/ subdirectory
- **ADDED:** Hierarchical debug integration via debug module
- **UPDATED:** All imports for subdirectory structure
- **PRESERVED:** All existing functionality exactly
- **ADDED:** __init__.py for module exports
- **CREATED:** DIRECTORY.md documentation

### 2025-10-22_01
- Added reset() method for Phase 1 compliance
- SINGLETON pattern with gateway integration
- Rate limiting to prevent log flooding

### 2025-10-21_03
- Fixed ErrorEntry dataclass for logging_manager
- Removed LogTemplate validation

### 2025-10-18_02
- Enhanced security with CVE mitigations
- Added exception sanitization (CVE-LOG-004)

---

## Related Files

- `/interface_logging.py` - Interface router (200 lines)
- `/gateway/wrappers/gateway_wrappers_logging.py` - Gateway wrappers (77 lines)
- `/gateway_core.py` - Gateway routing
- `/debug/` - Debug module for hierarchical control

---

**Total Lines:** 719 lines (logging/ subdirectory files)  
**Average File Size:** 143 lines  
**Largest File:** logging_manager.py (281 lines)  
**Compliance:** All files under 350 line limit ✓
