# Scanner Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** scanner
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Security scanning, UG-ISP compliance checking

---

## Overview

The Scanner domain provides security scanning, compliance validation, test execution, report generation, and rule compilation for EE 2.1 architecture compliance.

**Gateway:** ScannerGateway
**Interfaces:** 8 (scan, validate, test, report, cache, cleanup, compile, utility)
**Operations:** ~20

---

## 1. Scan Interface

**Purpose:** Security and compliance scanning
**Location:** `EE/scanner/interface/scan/`

### Operations

#### run_scan

Run compliance scan on codebase.

**Parameters:**
- `target` (str, required): Target path or file
- `rules` (list, optional): Specific rules to check (default: all)
- `severity` (str, optional): Minimum severity (default: "warning")

**Returns:** Scan results (dict with violations, stats, summary)

**Examples:**
```python
results = execute_operation(
    domain="scanner",
    interface="scan",
    operation="run_scan",
    target="EE/networking",
    rules=["AP-EE-04", "AP-EE-06"],
    severity="error"
)
```

---

#### scan_target

Quick scan of specific target.

**Parameters:**
- `target` (str, required): File or directory path
- `quick` (bool, optional): Quick scan mode (default: False)

**Returns:** Scan summary (dict)

**Examples:**
```python
summary = execute_operation(
    domain="scanner",
    interface="scan",
    operation="scan_target",
    target="EE/networking/http_client/http_interface.py",
    quick=True
)
```

---

#### generate_report

Generate scan report.

**Parameters:**
- `results` (dict, required): Scan results
- `format` (str, optional): Report format (markdown/json/html)
- `output_path` (str, optional): Output file path

**Returns:** Report content (str) or file path (str)

**Examples:**
```python
report = execute_operation(
    domain="scanner",
    interface="scan",
    operation="generate_report",
    results=scan_results,
    format="markdown",
    output_path="reports/scan-report.md"
)
```

---

## 2. Validate Interface

**Purpose:** Compliance validation
**Location:** `EE/scanner/interface/validate/`

### Operations

#### validate_compliance

Validate EE 2.1 compliance.

**Parameters:**
- `target` (str, required): Target path
- `category` (str, optional): Category to validate (default: all)

**Returns:** Compliance results (dict with compliant, violations, score)

**Examples:**
```python
results = execute_operation(
    domain="scanner",
    interface="validate",
    operation="validate_compliance",
    target="EE/networking",
    category="ug-isp"
)
# Returns: {"compliant": false, "violations": [...], "score": 85}
```

---

#### check_rules

Check specific rules.

**Parameters:**
- `target` (str, required): Target path
- `rules` (list, required): Rules to check

**Returns:** Rule check results (dict)

**Examples:**
```python
results = execute_operation(
    domain="scanner",
    interface="validate",
    operation="check_rules",
    target="EE/networking",
    rules=["AP-EE-04", "AP-EE-06"]
)
```

---

## 3. Test Interface

**Purpose:** Test execution and coverage
**Location:** `EE/scanner/interface/test/`

### Operations

#### run_tests

Run test suite.

**Parameters:**
- `target` (str, optional): Target module (default: all)
- `coverage` (bool, optional): Generate coverage report (default: False)

**Returns:** Test results (dict with passed, failed, coverage)

**Examples:**
```python
# Run all tests
results = execute_operation(
    domain="scanner",
    interface="test",
    operation="run_tests"
)

# Run with coverage
results = execute_operation(
    domain="scanner",
    interface="test",
    operation="run_tests",
    target="EE/networking",
    coverage=True
)
```

---

#### generate_coverage

Generate coverage report.

**Parameters:**
- `target` (str, required): Target module
- `format` (str, optional): Report format (term/html/xml)

**Returns:** Coverage report (str)

**Examples:**
```python
report = execute_operation(
    domain="scanner",
    interface="test",
    operation="generate_coverage",
    target="EE/networking",
    format="html"
)
```

---

## 4. Report Interface

**Purpose:** Report generation and export
**Location:** `EE/scanner/interface/report/`

### Operations

#### generate, export, format

```python
# Generate report
report = execute_operation(
    domain="scanner",
    interface="report",
    operation="generate",
    type="compliance",
    data=results
)

# Export report
execute_operation(
    domain="scanner",
    interface="report",
    operation="export",
    report=report,
    format="pdf",
    output_path="reports/compliance.pdf"
)

# Format report
formatted = execute_operation(
    domain="scanner",
    interface="report",
    operation="format",
    report=report,
    format="markdown"
)
```

---

## 5. Cache Interface

**Purpose:** Scan result caching
**Location:** `EE/scanner/interface/cache/`

### Operations

#### get, set, invalidate

```python
# Get cached scan
cached = execute_operation(
    domain="scanner",
    interface="cache",
    operation="get",
    key="scan:EE/networking:123456"
)

# Cache scan results
execute_operation(
    domain="scanner",
    interface="cache",
    operation="set",
    key="scan:EE/networking:123456",
    value=scan_results,
    ttl=3600
)

# Invalidate cache
execute_operation(
    domain="scanner",
    interface="cache",
    operation="invalidate",
    key="scan:EE/networking"
)
```

---

## 6. Cleanup Interface

**Purpose:** Cleanup operations
**Location:** `EE/scanner/interface/cleanup/`

### Operations

#### clean_artifacts, purge_temp

```python
# Clean scan artifacts
execute_operation(
    domain="scanner",
    interface="cleanup",
    operation="clean_artifacts",
    older_than_hours=24
)

# Purge temp files
execute_operation(
    domain="scanner",
    interface="cleanup",
    operation="purge_temp"
)
```

---

## 7. Compile Interface

**Purpose:** Rule compilation
**Location:** `EE/scanner/interface/compile/`

### Operations

#### compile_rules, validate_rules

```python
# Compile rules
compiled = execute_operation(
    domain="scanner",
    interface="compile",
    operation="compile_rules",
    rules=["AP-EE-04", "AP-EE-06"],
    output_path="rules/compiled.json"
)

# Validate rules
valid = execute_operation(
    domain="scanner",
    interface="compile",
    operation="validate_rules",
    rules=["AP-EE-04", "AP-EE-06"]
)
```

---

## 8. Utility Interface

**Purpose:** Scanner utilities
**Location:** `EE/scanner/interface/utility/`

### Operations

#### parse, format, transform

```python
# Parse scan results
parsed = execute_operation(
    domain="scanner",
    interface="utility",
    operation="parse",
    data=raw_scan_data,
    format="json"
)

# Format output
formatted = execute_operation(
    domain="scanner",
    interface="utility",
    operation="format",
    data=results,
    format="table"
)

# Transform data
transformed = execute_operation(
    domain="scanner",
    interface="utility",
    operation="transform",
    data=results,
    transformation="aggregate-by-severity"
)
```

---

## Cross-Domain Operations

**Scanner may call:**
- All domains (for compliance checking)
- `observability.logging` - For scan logs
- `operations.cache` - For scan result caching

---

## Examples

### Complete Compliance Scan

```python
def run_compliance_scan(domain_path):
    # Run scan
    results = execute_operation(
        domain="scanner",
        interface="scan",
        operation="run_scan",
        target=domain_path,
        severity="warning"
    )

    # Validate compliance
    compliance = execute_operation(
        domain="scanner",
        interface="validate",
        operation="validate_compliance",
        target=domain_path
    )

    # Generate report
    report = execute_operation(
        domain="scanner",
        interface="report",
        operation="generate",
        type="compliance",
        data={
            "scan": results,
            "compliance": compliance
        }
    )

    # Export report
    execute_operation(
        domain="scanner",
        interface="report",
        operation="export",
        report=report,
        format="markdown",
        output_path="reports/compliance.md"
    )

    return report
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/scanner/gateway/scanner_gateway_21.py` - Gateway implementation
- `EE/scanner/interface/` - All scanner interfaces

---

**END OF SCANNER DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 349 (target achieved)
