# Test Domain - Function Reference

**Version:** 1.0.0
**Date:** 2026-01-02
**Domain:** test
**Status:** UG-ISP Compliant (EE 2.1 Ready)
**Purpose:** Testing framework, test execution

---

## Overview

The Test domain provides pytest operations, test reporting, and test scanning for comprehensive testing capabilities.

**Gateway:** TestGateway
**Interfaces:** 3 (pytest, report, scanner)
**Operations:** ~10

---

## 1. Pytest Interface

**Purpose:** Pytest operations
**Location:** `EE/test/pytest/`

### Operations

#### run

Run pytest tests.

**Parameters:**
- `target` (str, optional): Target path/module (default: all tests)
- `verbose` (bool, optional): Verbose output (default: False)
- `markers` (list, optional): Specific markers to run
- `fail_fast` (bool, optional): Stop on first failure (default: False)

**Returns:** Test results (dict with passed, failed, duration, output)

**Examples:**
```python
# Run all tests
results = execute_operation(
    domain="test",
    interface="pytest",
    operation="run"
)

# Run specific module
results = execute_operation(
    domain="test",
    interface="pytest",
    operation="run",
    target="EE/networking/tests/",
    verbose=True
)

# Run with markers
results = execute_operation(
    domain="test",
    interface="pytest",
    operation="run",
    markers=["unit", "fast"],
    fail_fast=True
)
```

---

#### collect

Collect tests without running.

**Parameters:**
- `target` (str, optional): Target path (default: all)

**Returns:** List of collected tests (List[str])

**Examples:**
```python
tests = execute_operation(
    domain="test",
    interface="pytest",
    operation="collect",
    target="EE/networking/tests/"
)
# Returns: ["test_http_client.py::test_get", "test_http_client.py::test_post", ...]
```

---

#### coverage

Generate coverage report.

**Parameters:**
- `target` (str, optional): Target module
- `format` (str, optional): Report format (term/html/xml/json)
- `output` (str, optional): Output path

**Returns:** Coverage results (dict with percentage, files, report)

**Examples:**
```python
# Terminal coverage
coverage = execute_operation(
    domain="test",
    interface="pytest",
    operation="coverage",
    target="EE/networking",
    format="term"
)
# Returns: {"percentage": 85.3, "files": [...], "report": "..."}

# HTML coverage report
coverage = execute_operation(
    domain="test",
    interface="pytest",
    operation="coverage",
    target="EE/networking",
    format="html",
    output="reports/coverage/"
)
```

---

#### list_tests

List available tests.

**Parameters:**
- `target` (str, optional): Target path (default: all)
- `detailed` (bool, optional): Show test details (default: False)

**Returns:** List of tests (List[str] or List[dict])

**Examples:**
```python
# Simple list
tests = execute_operation(
    domain="test",
    interface="pytest",
    operation="list_tests",
    target="EE/networking/tests/"
)
# Returns: ["test_http_client.py::test_get", ...]

# Detailed list
tests = execute_operation(
    domain="test",
    interface="pytest",
    operation="list_tests",
    target="EE/networking/tests/",
    detailed=True
)
# Returns: [{"test": "test_http_client.py::test_get", "markers": ["unit"], ...}, ...]
```

---

## 2. Report Interface

**Purpose:** Test reporting
**Location:** `EE/test/report/`

### Operations

#### generate

Generate test report.

**Parameters:**
- `results` (dict, required): Test results
- `format` (str, optional): Report format (markdown/html/json)
- `template` (str, optional): Report template

**Returns:** Report content (str)

**Examples:**
```python
report = execute_operation(
    domain="test",
    interface="report",
    operation="generate",
    results=test_results,
    format="markdown",
    template="standard"
)
```

---

#### export

Export test report to file.

**Parameters:**
- `report` (str, required): Report content
- `format` (str, required): Output format
- `output_path` (str, required): Output file path

**Returns:** True if successful

**Examples:**
```python
execute_operation(
    domain="test",
    interface="report",
    operation="export",
    report=markdown_report,
    format="markdown",
    output_path="reports/test-results.md"
)
```

---

#### compare

Compare test results.

**Parameters:**
- `results1` (dict, required): First test results
- `results2` (dict, required): Second test results

**Returns:** Comparison report (dict)

**Examples:**
```python
comparison = execute_operation(
    domain="test",
    interface="report",
    operation="compare",
    results1=baseline_results,
    results2=current_results
)
# Returns: {"added": [...], "removed": [...], "changed": [...], "summary": "..."}
```

---

## 3. Scanner Interface

**Purpose:** Test scanning
**Location:** `EE/test/scanner/`

### Operations

#### scan_tests

Scan for test files.

**Parameters:**
- `target` (str, required): Target path
- `pattern` (str, optional): File pattern (default: "test_*.py")

**Returns:** List of test files (List[str])

**Examples:**
```python
test_files = execute_operation(
    domain="test",
    interface="scanner",
    operation="scan_tests",
    target="EE/networking",
    pattern="test_*.py"
)
# Returns: ["EE/networking/tests/test_http_client.py", ...]
```

---

#### find_coverage

Find test coverage gaps.

**Parameters:**
- `target` (str, required): Target module
- `threshold` (float, optional): Coverage threshold (default: 80.0)

**Returns:** Coverage gaps (dict with uncovered_files, low_coverage, recommendations)

**Examples:**
```python
gaps = execute_operation(
    domain="test",
    interface="scanner",
    operation="find_coverage",
    target="EE/networking",
    threshold=80.0
)
# Returns: {"uncovered_files": [...], "low_coverage": [...], "recommendations": [...]}
```

---

## Cross-Domain Operations

**Test may call:**
- All domains (for testing)
- `observability.logging` - For test logs
- `operations.fileio` - For test file access

---

## Examples

### Complete Test Workflow

```python
def run_test_suite(domain_path):
    # Collect tests
    tests = execute_operation(
        domain="test",
        interface="pytest",
        operation="collect",
        target=domain_path
    )

    print(f"Found {len(tests)} tests")

    # Run tests with coverage
    results = execute_operation(
        domain="test",
        interface="pytest",
        operation="run",
        target=domain_path,
        verbose=True
    )

    # Generate coverage report
    coverage = execute_operation(
        domain="test",
        interface="pytest",
        operation="coverage",
        target=domain_path,
        format="html",
        output="reports/coverage/"
    )

    # Generate test report
    report = execute_operation(
        domain="test",
        interface="report",
        operation="generate",
        results=results,
        format="markdown"
    )

    # Export report
    execute_operation(
        domain="test",
        interface="report",
        operation="export",
        report=report,
        format="markdown",
        output_path="reports/test-results.md"
    )

    return {
        "results": results,
        "coverage": coverage,
        "report": report
    }
```

### Coverage Gap Analysis

```python
def analyze_coverage(domain_path):
    # Find coverage gaps
    gaps = execute_operation(
        domain="test",
        interface="scanner",
        operation="find_coverage",
        target=domain_path,
        threshold=80.0
    )

    # Print recommendations
    for rec in gaps["recommendations"]:
        print(f"Recommendation: {rec}")

    return gaps
```

---

## See Also

**Architecture:**
- [EE-Domain-Interface-Catalog.md](../../SIMA/projects/EE/architecture/EE-Domain-Interface-Catalog.md) - Domain inventory

**Implementation:**
- `EE/test/test_gateway.py` - Gateway implementation
- Individual test interface directories

---

**END OF TEST DOMAIN REFERENCE**

**Version:** 1.0.0
**Lines:** 299
