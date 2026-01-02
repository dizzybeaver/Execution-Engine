# Metrics Interface - Directory Listing

**Version:** 2025-12-11_1  
**Purpose:** Metrics interface refactored structure  
**Project:** LEE

---

## Directory Structure

```
metrics/
├── __init__.py              # Module initialization, public API exports
├── metrics_core.py          # Core metrics implementation (SINGLETON)
├── metrics_helper.py        # Helper utilities (safe_divide, percentiles)
└── metrics_types.py         # Data structures (ResponseMetrics, HTTPClientMetrics)

interface_metrics.py         # Interface router (dispatch dictionary)

gateway/wrappers/
└── gateway_wrappers_metrics.py  # Gateway convenience wrappers
```

---

## File Descriptions

### metrics/__init__.py (48 lines)
- **Purpose:** Module initialization
- **Exports:** 18 public API functions
- **Pattern:** Re-exports from metrics_core
- **Usage:** `import metrics` for public functions

### metrics/metrics_core.py (299 lines)
- **Purpose:** Core metrics implementation
- **Class:** MetricsCore (SINGLETON)
- **Functions:** 18 public API functions
- **Features:** 
  - Record metrics, counters, gauges
  - Operation, cache, API metrics
  - HTTP and circuit breaker metrics
  - Dispatcher timing
  - Performance reporting

### metrics/metrics_helper.py (77 lines)
- **Purpose:** Helper utilities
- **Functions:**
  - safe_divide() - Division with zero check
  - build_dimensions() - Build dimension dictionaries
  - calculate_percentiles() - P50, P95, P99
  - format_metric_name() - Naming utilities
  - parse_metric_key() - Key parsing

### metrics/metrics_types.py (61 lines)
- **Purpose:** Type definitions
- **Classes:**
  - ResponseMetrics - Response tracking
  - HTTPClientMetrics - HTTP request tracking
  - CircuitBreakerMetrics - Circuit breaker stats

### interface_metrics.py (78 lines)
- **Purpose:** Metrics interface router
- **Pattern:** SUGA dispatch dictionary
- **Function:** execute_metrics_operation()
- **Operations:** 20+ operations supported

### gateway/wrappers/gateway_wrappers_metrics.py (147 lines)
- **Purpose:** Gateway convenience wrappers
- **Functions:** 16 wrapper functions
- **Pattern:** Call gateway.execute_operation()
- **Usage:** `from gateway import record_metric`

---

## Import Patterns

### Public API (Recommended)
```python
# Import from metrics module
import metrics

# Use public functions
metrics.record_metric('test', 1.0)
metrics.increment_counter('counter')
stats = metrics.get_stats()
```

### Interface Layer
```python
# Interface uses metrics module
import metrics

def execute_metrics_operation(operation, **kwargs):
    handler = DISPATCH[operation]
    return handler(**kwargs)
```

### Gateway Wrappers
```python
# Gateway wrappers call interface
from gateway_core import execute_operation, GatewayInterface

def record_metric(name, value, **kwargs):
    return execute_operation(GatewayInterface.METRICS, 'record', 
                            name=name, value=value, **kwargs)
```

---

## Key Features

### SINGLETON Pattern
- Single MetricsCore instance (_MANAGER)
- Lazy initialization
- Thread-safe (single-threaded Lambda)

### Operation Tracking
- Record any metric with dimensions
- Track operation duration and success
- Calculate percentiles (P50, P95, P99)

### Performance Reporting
- Comprehensive performance analysis
- Slow operation detection
- Intelligent recommendations

### Circuit Breaker Metrics
- Track circuit state changes
- Monitor failure rates
- Success/failure counts

### HTTP Metrics
- Request method tracking
- Status code distribution
- Response time analysis

---

## Usage Examples

### Recording Metrics
```python
import metrics

# Simple metric
metrics.record_metric('user.login', 1.0)

# With dimensions
metrics.record_metric('api.call', 1.0, {'endpoint': '/users', 'method': 'GET'})

# Counter
count = metrics.increment_counter('requests')
```

### Operation Tracking
```python
import metrics

# Track operation with duration
metrics.record_operation_metric(
    operation_name='process_data',
    success=True,
    duration_ms=45.2
)

# With error
metrics.record_operation_metric(
    operation_name='fetch_user',
    success=False,
    duration_ms=12.0,
    error_type='NotFound'
)
```

### Performance Report
```python
import metrics

# Get comprehensive report
report = metrics.get_performance_report(slow_threshold_ms=100.0)

print(f"Slow operations: {report['slow_operation_count']}")
for op in report['slow_operations']:
    print(f"  {op['operation']}: {op['p95_ms']}ms (p95)")
```

---

## Line Counts

| File | Lines | Target | Status |
|------|-------|--------|--------|
| __init__.py | 48 | <100 | ✓ |
| metrics_core.py | 299 | <300 | ✓ |
| metrics_helper.py | 77 | <300 | ✓ |
| metrics_types.py | 61 | <300 | ✓ |
| interface_metrics.py | 78 | <300 | ✓ |
| gateway_wrappers_metrics.py | 147 | <300 | ✓ |

**Total:** 710 lines across 6 files  
**Average:** 118 lines per file  
**All files under 300-line target** ✓

---

## Architecture Compliance

- ✓ SUGA pattern (Gateway → Interface → Core)
- ✓ Lazy imports
- ✓ SINGLETON pattern
- ✓ Dictionary dispatch (O(1) lookup)
- ✓ No direct core imports
- ✓ Under 300 lines per file

---

## Related Interfaces

- **CACHE:** Cache metrics recording
- **HTTP_CLIENT:** HTTP request metrics
- **CIRCUIT_BREAKER:** Circuit state metrics
- **LOGGING:** Operation logging
- **DEBUG:** Performance diagnostics

---

## Changelog

### 2025-12-11_1
- Initial refactoring to metrics/ subdirectory
- Split from monolithic files
- Added debug integration points
- Created gateway/wrappers structure
- All files under 300-line target
