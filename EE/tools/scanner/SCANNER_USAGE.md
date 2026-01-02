# EE UG Scanner - Usage Guide

**Version:** 1.0.0
**Date:** 2025-12-29
**Purpose:** Guide for using EE UG Architecture Compliance Scanner

---

## Quick Start

### Installation

Scanner is included in EE tools directory:
```bash
cd D:\Code\LEE\EE
python tools/scanner/ee_ug_scanner.py
```

### Basic Usage

```bash
# Scan entire EE source directory
python tools/scanner/ee_ug_scanner.py src markdown

# Scan specific file
python tools/scanner/ee_ug_scanner.py src/interface/interface_plugins.py markdown

# Generate JSON report
python tools/scanner/ee_ug_scanner.py src json > results.json

# Save markdown report
python tools/scanner/ee_ug_scanner.py src markdown > report.md
```

---

## Scanner Features

### Violation Detection

The scanner detects 20+ EE-specific UG violation patterns:

**CRITICAL Violations:**
- Internal debug helper functions (bypass Gateway)
- Cross-interface direct imports
- Wrong Gateway import patterns
- EE Gateway Factory bypass
- Direct plugin/pool/DI imports

**HIGH Violations:**
- Custom plugin/pool implementations
- Direct pool/protocol usage
- DI decorator/AOP imports
- Direct logging calls
- Direct HTTP operations

**MEDIUM Violations:**
- Manual JSON/hash operations
- Direct config access
- Flask direct routes

### Report Formats

**Markdown Format:**
```bash
python tools/scanner/ee_ug_scanner.py src markdown
```

Output includes:
- Total violation count
- Violations grouped by severity
- File path and line number for each violation
- Pattern name and description
- Fix suggestions with code examples
- Context lines (surrounding code)

**JSON Format:**
```bash
python tools/scanner/ee_ug_scanner.py src json > results.json
```

JSON structure:
```json
[
  {
    "file_path": "src/interface/interface_plugins.py",
    "line_number": 26,
    "pattern_name": "Custom Plugin Implementation",
    "severity": "HIGH",
    "found_code": "class PluginState(Enum):",
    "gateway_interface": "PLUGINS",
    "gateway_operation": "load",
    "fix_pattern": "Use Gateway PLUGINS interface operations",
    "description": "Custom plugin implementation..."
  }
]
```

---

## Violation Patterns

### INT-16 PLUGINS Interface Violations

**Pattern:** `plugin_direct_import` (CRITICAL)
```python
# VIOLATION:
from plugins.plugin_core import PluginCore
from plugins.plugin_loader import load_plugin

# CORRECT:
from EE import execute_operation, EEGatewayInterface
plugin = execute_operation(
    EEGatewayInterface.PLUGINS,
    'load',
    name='my_plugin',
    path='./plugins/my_plugin/'
)
```

**Pattern:** `plugin_missing_base_class` (HIGH)
```python
# VIOLATION:
class MyPlugin:
    pass

# CORRECT:
from plugins.plugin_core import EEPlugin
class MyPlugin(EEPlugin):
    pass
```

### INT-18 OBJECT_POOL Interface Violations

**Pattern:** `pool_direct_import` (CRITICAL)
```python
# VIOLATION:
from object_pool.pool_core import ObjectPool
from object_pool.pool_factory import PoolFactory

# CORRECT:
from EE import execute_operation, EEGatewayInterface

# Create pool
execute_operation(
    EEGatewayInterface.OBJECT_POOL,
    'create',
    name='connections',
    factory_func=lambda: Connection(),
    max_size=10
)

# Acquire object
conn = execute_operation(
    EEGatewayInterface.OBJECT_POOL,
    'acquire',
    name='connections'
)

# Release object
execute_operation(
    EEGatewayInterface.OBJECT_POOL,
    'release',
    name='connections',
    obj=conn
)
```

### INT-17 NETWORK Interface Violations

**Pattern:** `network_protocol_direct_import` (HIGH)
```python
# VIOLATION:
from protocols.protocol_redis import RedisProtocol
from protocols.protocol_mqtt import MQTTProtocol

# CORRECT:
from EE import execute_operation, EEGatewayInterface

# Redis operations
value = execute_operation(
    EEGatewayInterface.NETWORK,
    'redis_get',
    key='mykey',
    host='localhost',
    port=6379
)

# MQTT operations
execute_operation(
    EEGatewayInterface.NETWORK,
    'mqtt_publish',
    topic='sensors/temperature',
    payload='22.5',
    host='mqtt.example.com',
    port=1883
)
```

### DI Gateway Violations

**Pattern:** `di_container_direct_import` (CRITICAL)
```python
# VIOLATION:
from operations.di.di_core import DIContainer
from operations.di.di_decorators import singleton, inject

# CORRECT:
from EE import execute_operation, EEGatewayInterface

# Create container
container = execute_operation(
    EEGatewayInterface.DI,
    'CONTAINER_CREATE'
)

# Register service
execute_operation(
    EEGatewayInterface.DI,
    'CONTAINER_REGISTER_SINGLETON',
    service_type=MyService,
    implementation=MyServiceImpl,
    container=container
)

# Resolve service
service = execute_operation(
    EEGatewayInterface.DI,
    'CONTAINER_RESOLVE',
    service_type=MyService,
    container=container
)
```

### EE Gateway Factory Violations

**Pattern:** `wrong_gateway_import` (CRITICAL)
```python
# VIOLATION:
from EE.gateway import execute_operation, GatewayInterface
from gateway.gateway import execute_operation

# CORRECT:
from EE import execute_operation, EEGatewayInterface

# Use Gateway
result = execute_operation(
    EEGatewayInterface.CACHE,
    'get',
    key='test'
)
```

### Internal Debug Helper Violations

**Pattern:** `internal_debug_helper` (CRITICAL)
```python
# VIOLATION:
def _debug_log(corr_id, message, **context):
    print(f"[{corr_id}] {message}")

def _generate_correlation_id():
    return f"id_{int(time.time() * 1000)}"

# CORRECT:
from EE import execute_operation, EEGatewayInterface
import time, random

def my_function():
    # Inline correlation ID generation
    corr_id = f"mod_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    # Debug via Gateway
    execute_operation(
        EEGatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="MODULE_NAME",
        message="Operation started"
    )
```

---

## Interpretation of Results

### Severity Levels

**CRITICAL:** Violates UG architecture, breaks network topology
- Must fix immediately
- Blocks deployment
- Breaks architecture compliance

**HIGH:** Bypasses Gateway services, creates technical debt
- Should fix soon
- Impacts performance and maintainability
- Violates best practices

**MEDIUM:** Inconsistent patterns, potential issues
- Fix when possible
- Code quality improvement
- Standardization needed

**LOW:** Style and consistency issues
- Fix for code quality
- No immediate impact
- Nice to have improvements

### Interface Categories

**EE_GATEWAY_FACTORY:** Gateway Factory violations
- Wrong import patterns
- Bypassing factory pattern

**PLUGINS:** INT-16 Plugin System violations
- Direct plugin imports
- Custom implementations
- Missing base classes

**OBJECT_POOL:** INT-18 Object Pool violations
- Direct pool imports
- Custom pool implementations
- Direct pool usage

**NETWORK:** INT-17 Network Protocol violations
- Direct protocol imports
- Direct client usage

**DI:** Dependency Injection violations
- Direct DI imports
- Direct decorator/AOP usage

**DEBUG:** Debug system violations
- Internal debug helpers
- Missing correlation IDs

---

## Integration with Development Workflow

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running EE UG scanner..."

# Run scanner
python EE/tools/scanner/ee_ug_scanner.py EE/src json > ee_scan.json

# Check for CRITICAL violations
CRITICAL=$(grep -o '"severity": "CRITICAL"' ee_scan.json | wc -l)
if [ $CRITICAL -gt 0 ]; then
    echo "ERROR: $CRITICAL CRITICAL UG violations detected!"
    echo "Run: python EE/tools/scanner/ee_ug_scanner.py EE/src markdown"
    exit 1
fi

echo "UG scan passed: No CRITICAL violations"
```

### VS Code Task

Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Scan EE UG",
            "type": "shell",
            "command": "python EE/tools/scanner/ee_ug_scanner.py EE/src markdown",
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```

### GitHub Actions Workflow

Create `.github/workflows/ee-suga-isp-scan.yml`:
```yaml
name: EE UG Compliance

on:
  push:
    paths:
      - 'EE/src/**'
  pull_request:
    paths:
      - 'EE/src/**'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Run EE Scanner
        run: |
          python EE/tools/scanner/ee_ug_scanner.py EE/src json > results.json

      - name: Check CRITICAL Violations
        run: |
          CRITICAL=$(grep -o '"severity": "CRITICAL"' results.json | wc -l)
          if [ $CRITICAL -gt 0 ]; then
            echo "::error::Found $CRITICAL CRITICAL UG violations"
            cat results.json
            exit 1
          fi

      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: ee-scan-results
          path: results.json
```

---

## Common Issues and Solutions

### Issue: False Positive - Enum Definitions

**Problem:** Scanner flags `class PluginState(Enum):` as custom implementation violation.

**Solution:** This is a known false positive. Enum definitions are allowed in EE codebase.

**Action:** Ignore these violations or filter them from reports.

### Issue: Interface Router Files Flagged

**Problem:** `interface_object_pool.py` flagged for importing from `object_pool.pool_core`.

**Solution:** This is NOT a false positive. Interface routers should not import implementation modules directly.

**Fix:** Use Gateway routing for all cross-interface communication.

### Issue: Test Files Flagged

**Problem:** Test files have violations for testing purposes.

**Solution:** Scanner excludes `test/` and `tests/` directories by default.

**Action:** If using different test directory names, update scanner exclude list.

---

## Advanced Usage

### Custom Pattern Matching

```python
from ee_ug_scanner import EESUGAISPPatternMatcher

# Create matcher
matcher = EESUGAISPPatternMatcher()

# Scan single file
violations = matcher.scan_file('src/interface/interface_plugins.py')

# Filter by severity
critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]

# Filter by interface
pool_violations = [v for v in violations if v.gateway_interface == 'OBJECT_POOL']

# Generate custom report
for v in critical_violations:
    print(f"{v.file_path}:{v.line_number} - {v.pattern_name}")
    print(f"Fix: {v.fix_pattern}")
    print()
```

### Batch Processing

```python
from ee_ug_scanner import scan_ee_directory

# Scan multiple directories
directories = [
    'D:/Code/LEE/EE/src/interface',
    'D:/Code/LEE/EE/src/operations',
    'D:/Code/LEE/EE/src/protocols'
]

all_violations = []
for directory in directories:
    violations = scan_ee_directory(directory)
    all_violations.extend(violations)

# Generate summary
matcher = EESUGAISPPatternMatcher()
summary = matcher.get_violation_summary(all_violations)
print(f"Total violations: {summary['total_violations']}")
print(f"By severity: {summary['by_severity']}")
```

---

## Support and Documentation

**Scanner Location:** `D:\Code\LEE\EE\tools\scanner\ee_ug_scanner.py`
**Report Location:** `D:\Code\LEE\EE\tools\scanner\ee_scan_*.md/json`
**Planning Report:** `D:\Code\LEE\reports\Planning\2025-12-28-Plan\1-ee-scanner-updates/README.md`

**Related Documentation:**
- EE README: `EE/README.md`
- UG Architecture: `reference/LEE-Import-Rules.md`
- LEE Scanner: `src/LEE/test/scanner/core/custom_impl_patterns.py`

---

**Scanner Version:** 1.0.0
**Last Updated:** 2025-12-29
