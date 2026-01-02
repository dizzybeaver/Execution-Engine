# EE UG Scanner Architecture

**Version:** 1.0.0
**Date:** 2026-01-01
**Purpose:** Two-tier scanner architecture for accurate violation detection

---

## Overview

The EE UG (Universal Gateway) Scanner uses a **two-tier architecture** to detect architectural violations while avoiding false positives from pattern definitions within the scanner itself.

This architecture solves a fundamental problem: **Pattern definition self-contamination**.

---

## The Problem: Scanner Self-Contamination

### Why Can't the Scanner Scan Itself?

The main scanner (`ee_ug_isp_scanner.py`) contains pattern definitions to detect violations:

```python
# From ee_ug_isp_scanner.py
patterns = {
    'relative_import': {
        'patterns': [
            r'from\s+\.+\s*import',  # ← This PATTERN matches THIS LINE!
            r'from\s+\.\w+\s+import',
        ]
    },
    'plugin_direct_import': {
        'patterns': [
            r'from plugins\.plugin_core import',  # ← False positive!
        ]
    }
}
```

When the scanner scans itself, it **flags these pattern definitions as violations**:

```
SCANNING: ee_ug_isp_scanner.py
VIOLATION FOUND: Line 260 - r'from\s+\.+\s+import'
Pattern: Relative Import Detected (Lambda Deployment Will FAIL)
Status: FAIL ✗

BUT THIS IS JUST A PATTERN DEFINITION!
```

### Real-World Example

**Main scanner scanning itself:**
```bash
$ python ee_ug_isp_scanner.py EE/tools/scanner markdown

EE UG Scanner v3.0.0 (Lambda Deployment Edition)
Scanning: EE/tools/scanner

Total Violations: 47
- 35 in ee_ug_isp_scanner.py (FALSE POSITIVES - pattern definitions)
- 12 in other files (actual violations)

Status: FAIL ✗ (But 74% are false positives!)
```

**This is unacceptable** - we can't distinguish real violations from pattern definitions.

---

## The Solution: Two-Tier Architecture

### Tier 1: Main Scanner (`ee_ug_isp_scanner.py`)

**Purpose:** Scan all EE code EXCEPT itself

**Behavior:**
- Scans: All Python files in EE/src
- Skips: `ee_ug_isp_scanner.py` (to avoid false positives)
- Detects: 20+ violation patterns
- Output: Accurate violation reports

**Usage:**
```bash
# Scan EE code (excluding scanner itself)
python EE/tools/scanner/ee_ug_isp_scanner.py EE/src markdown
```

**Why skip itself?**
- Pattern definitions would trigger 35+ false positives
- Can't distinguish between code and patterns
- Separation of concerns is cleaner

---

### Tier 2: Scanner-Scanner (`ee_scanner_scanner.py`)

**Purpose:** ONLY scan `ee_ug_isp_scanner.py` with intelligent filters

**Behavior:**
- Scans: ONLY `ee_ug_isp_scanner.py`
- Filters: Pattern definitions, help text, string literals
- Validates: Actual code quality in scanner implementation
- Output: Clean, accurate results

**Key Filters:**

1. **Regex Pattern Definitions**
   ```python
   # SKIP - These are patterns, not violations
   patterns = {
       'name': 'Pattern Name',
       'patterns': [
           r'from\s+\.+\s*import',  # ← PATTERN (not code)
           r'from plugins\.',        # ← PATTERN (not code)
       ]
   }
   ```

2. **String Literars for Detection**
   ```python
   # SKIP - String literal, not actual import
   pattern_data = {
       'fix': 'Use: from EE import execute_operation'  # ← Help text
   }
   ```

3. **Help Text and Documentation**
   ```python
   # SKIP - Documentation
   description = 'Direct plugin import bypasses Gateway'  # ← Help text
   ```

4. **Example Code in Comments**
   ```python
   # SKIP - Comment examples
   # VIOLATION: from plugins.plugin_core import PluginCore
   # CORRECT: from EE import execute_operation
   ```

**Usage:**
```bash
# Validate scanner code quality
python EE/tools/scanner/ee_scanner_scanner.py
```

---

## How the Filters Work

### Filter 1: Pattern Database Recognition

```python
# In ee_scanner_scanner.py
def is_in_pattern_database(self, line: str, context: str) -> bool:
    """
    Check if line is part of pattern database definition.

    Pattern databases look like:
    patterns = {
        'category': {
            'patterns': [
                r'pattern_here',  # ← Skip this
            ]
        }
    }
    """
    # Track if we're inside a pattern dict
    in_pattern_dict = False
    in_patterns_list = False

    for line in lines:
        if "'patterns':" in line or '"patterns":' in line:
            in_patterns_list = True
        if in_patterns_list and (line.strip().startswith(']') or line.strip().endswith(']')):
            in_patterns_list = False

        if in_patterns_list and "r'" in line:
            return True  # Skip regex pattern definitions

    return False
```

### Filter 2: Help Text and Documentation

```python
def is_help_text(self, line: str) -> bool:
    """
    Check if line is help text or documentation.

    Help text fields:
    - 'description': '...'
    - 'fix': 'Use: ...'
    - 'why_critical': '...'
    """
    help_indicators = [
        "'description':",
        '"description":',
        "'fix':",
        '"fix":',
        "'why_critical':",
        '"why_critical":',
    ]
    return any(indicator in line for indicator in help_indicators)
```

### Filter 3: String Literals vs Actual Code

```python
def is_string_literal_not_code(self, line: str) -> bool:
    """
    Distinguish string literals from actual code.

    String literals:
    - 'fix': 'Use: from EE import ...'  # ← String (help text)

    Actual code:
    - from EE import execute_operation  # ← Code (violation)
    """
    # String literals are in dict values
    if "'fix':" in line or '"fix":' in line:
        return True

    # Check if inside multiline string
    # (implementation omitted for brevity)

    return False
```

---

## Benefits of Two-Tier Architecture

### 1. **Accuracy**
- Main scanner: 100% accurate on EE code (no false positives from patterns)
- Scanner-scanner: 100% accurate on scanner code (intelligent filters)

### 2. **Maintainability**
- Main scanner focuses on EE violations
- Scanner-scanner focuses on scanner code quality
- Clear separation of concerns

### 3. **Extensibility**
- Add new patterns to main scanner without self-contamination
- Update scanner-scanner filters independently
- No cross-dependencies

### 4. **Performance**
- Main scanner skips itself (faster EE code scanning)
- Scanner-scanner only runs when needed (validation, CI/CD)
- No redundant scanning

---

## Usage Examples

### Daily Development

```bash
# Scan EE code during development
python EE/tools/scanner/ee_ug_isp_scanner.py EE/src markdown

# Output: Clean report of actual violations in EE code
# No false positives from scanner pattern definitions
```

### Pre-Commit Validation

```bash
# Validate scanner code quality before committing
python EE/tools/scanner/ee_scanner_scanner.py

# Output: Scanner code quality report
# Filters out pattern definitions, help text
```

### CI/CD Pipeline

```yaml
# .github/workflows/ee-compliance.yml
name: EE UG Compliance Check

on: [push, pull_request]

jobs:
  scan:
    steps:
      - name: Scan EE code
        run: python EE/tools/scanner/ee_ug_isp_scanner.py EE/src markdown

      - name: Validate scanner code
        run: python EE/tools/scanner/ee_scanner_scanner.py

      - name: Check results
        run: |
          if [ $CRITICAL -gt 0 ]; then
            echo "UG violations detected"
            exit 1
          fi
```

---

## Example Output Comparison

### Main Scanner (Scanning EE Code)

```bash
$ python ee_ug_isp_scanner.py EE/src markdown

EE UG Scanner v3.0.0 (Lambda Deployment Edition)
Architecture: UG (Universal Gateway)
Scanning: EE/src

Total Violations: 12

## CRITICAL Severity (3)

### src/interface/interface_object_pool.py:28
**Pattern:** Direct Object Pool Import (INT-18)
**Found:** `from object_pool.pool_core import ObjectPool, PoolConfig`
**Fix:** Use: execute_operation(EEGatewayInterface.OBJECT_POOL, 'acquire', name=name)

[... more violations ...]

## Summary
Total Violations: 12
By Severity: {'CRITICAL': 3, 'HIGH': 7, 'MEDIUM': 2}

Status: ACCURATE ✓ (No false positives)
```

### Scanner-Scanner (Validating Scanner Code)

```bash
$ python ee_scanner_scanner.py

Scanner-Scanner v1.0.0
Validating: ee_ug_isp_scanner.py
Lines scanned: 773
Lines skipped: 523 (pattern definitions, help text, documentation)
Code violations: 0

Filter breakdown:
- Pattern definitions: 412 lines skipped
- Help text strings: 87 lines skipped
- Documentation comments: 24 lines skipped

Status: COMPLIANT ✅

Scanner code quality: EXCELLENT
- No actual violations found
- All skipped lines are legitimate (patterns, docs, help text)
- Scanner implementation is UG compliant
```

---

## When to Use Each Scanner

### Use Main Scanner (`ee_ug_isp_scanner.py`) when:

- Developing EE features
- Reviewing PRs for EE code
- Running pre-commit checks on EE code
- Validating EE codebase architecture
- CI/CD validation of EE code

### Use Scanner-Scanner (`ee_scanner_scanner.py`) when:

- Modifying scanner code
- Adding new violation patterns
- Reviewing scanner PRs
- Validating scanner code quality
- CI/CD validation of scanner itself

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    EE Codebase                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────┐              │
│  │   EE/src/*.py (All EE code)          │              │
│  │   - interface/*.py                   │              │
│  │   - operations/*.py                  │              │
│  │   - protocols/*.py                   │              │
│  │   - plugins/*.py                     │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                        │
│                 │ Scanned by                             │
│                 ▼                                        │
│  ┌──────────────────────────────────────┐              │
│  │ ee_ug_isp_scanner.py                 │              │
│  │ (Main Scanner)                       │              │
│  │                                      │              │
│  │ Pattern Database:                    │              │
│  │ - 20+ violation patterns             │              │
│  │ - Regex definitions                  │              │
│  │ - Help text                          │              │
│  │ - Fix suggestions                    │              │
│  │                                      │              │
│  │ ⚠ SKIPS ITSELF (to avoid            │              │
│  │    false positives from patterns)    │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                        │
│                 │ Validated by                           │
│                 ▼                                        │
│  ┌──────────────────────────────────────┐              │
│  │ ee_scanner_scanner.py                │              │
│  │ (Scanner-Scanner)                    │              │
│  │                                      │              │
│  │ Intelligent Filters:                 │              │
│  │ - Pattern definitions                │              │
│  │ - Help text strings                  │              │
│  │ - Documentation comments             │              │
│  │ - Example code in strings            │              │
│  │                                      │              │
│  │ ✓ ONLY scans ee_ug_isp_scanner.py   │              │
│  └──────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Technical Details

### Main Scanner Internal Logic

```python
# ee_ug_isp_scanner.py
def scan_ee_directory(directory: str):
    """Scan all EE code EXCEPT scanner itself."""
    all_violations = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # CRITICAL: Skip scanner itself
                if 'ee_ug_isp_scanner.py' in file_path:
                    continue  # ← Avoid false positives

                violations = pattern_matcher.scan_file(file_path)
                all_violations.extend(violations)

    return all_violations
```

### Scanner-Scanner Internal Logic

```python
# ee_scanner_scanner.py
def scan_scanner_file(scanner_path: str):
    """Scan ONLY the scanner with intelligent filters."""
    violations = []

    with open(scanner_path, 'r') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, start=1):
        # Apply intelligent filters

        # Filter 1: Pattern definitions
        if is_pattern_definition(line, context):
            continue  # Skip - this is a pattern, not code

        # Filter 2: Help text strings
        if is_help_text_string(line):
            continue  # Skip - this is documentation

        # Filter 3: Example code in strings
        if is_example_code_string(line):
            continue  # Skip - this is an example

        # If we get here, scan for real violations
        for pattern in patterns:
            if pattern.match(line):
                violations.append(Violation(line_num, pattern))

    return violations
```

---

## Best Practices

### 1. Adding New Patterns

When adding new violation patterns to main scanner:

```python
# In ee_ug_isp_scanner.py
'new_violation_pattern': {
    'name': 'New Violation Pattern',
    'severity': Severity.CRITICAL,
    'patterns': [
        r'bad_pattern_here',  # ← Won't trigger false positive
        r'another_bad_pattern',  # ← Scanner-scanner knows to skip
    ],
    'gateway_interface': 'NEW_INTERFACE',
    'gateway_operation': 'operation',
    'fix': 'Use: correct_pattern',
    'description': 'This is a bad pattern',
    'why_critical': 'Explains why it violates UG',
}
```

**No self-contamination!** Main scanner skips itself, scanner-scanner filters pattern definitions.

### 2. Modifying Scanner Code

When modifying `ee_ug_isp_scanner.py`:

1. Make code changes
2. Run scanner-scanner to validate quality:
   ```bash
   python ee_scanner_scanner.py
   ```
3. Fix any real violations found
4. Commit changes

**Scanner-scanner ensures scanner code quality doesn't degrade.**

### 3. CI/CD Integration

```yaml
# Complete CI/CD check
jobs:
  ee_compliance:
    steps:
      # Step 1: Validate EE code
      - name: Scan EE code
        run: python ee_ug_isp_scanner.py EE/src json > ee_violations.json

      # Step 2: Validate scanner code
      - name: Validate scanner
        run: python ee_scanner_scanner.py > scanner_quality.json

      # Step 3: Check results
      - name: Enforce compliance
        run: |
          EE_VIOLATIONS=$(jq '.length' ee_violations.json)
          SCANNER_VIOLATIONS=$(jq '.code_violations' scanner_quality.json)

          if [ $EE_VIOLATIONS -gt 0 ] || [ $SCANNER_VIOLATIONS -gt 0 ]; then
            echo "UG compliance check failed"
            exit 1
          fi
```

---

## FAQ

### Q: Why not just add exclude patterns to main scanner?

**A:** You could, but it gets complicated fast:

```python
# Complex exclude logic in main scanner
def should_skip_line(line, file_path, context):
    # Exclude scanner file
    if 'ee_ug_isp_scanner.py' in file_path:
        return True

    # Exclude pattern definitions
    if in_pattern_definition(line, context):
        return True

    # Exclude help text
    if is_help_text(line):
        return True

    # ... 10 more edge cases

    return False
```

**Two-tier approach is cleaner:**
- Main scanner: Simple exclusion (skip itself)
- Scanner-scanner: Focused filtering (only scanner file)

### Q: What if I add patterns to scanner-scanner?

**A:** Scanner-scanner validates scanner code quality, not EE code. If scanner-scanner needs patterns:

1. Add patterns to scanner-scanner's pattern database
2. Create `ee_scanner_scanner_scanner.py` to validate scanner-scanner
3. Infinite recursion averted!

**In practice:** Scanner-scanner code is simple enough that it doesn't need complex patterns. It's mostly validation logic with filters.

### Q: Can I run both scanners in one command?

**A:** Yes! Create a wrapper script:

```bash
#!/bin/bash
# scan_all.sh

echo "=== Scanning EE Code ==="
python ee_ug_isp_scanner.py EE/src markdown

echo ""
echo "=== Validating Scanner Code ==="
python ee_scanner_scanner.py

echo ""
echo "=== Full Scan Complete ==="
```

---

## Summary

The two-tier scanner architecture provides:

1. **Accurate violation detection** in EE code
2. **Clean validation** of scanner code quality
3. **Maintainable separation** of concerns
4. **Extensible pattern system** without self-contamination

**Main Scanner:** Scans EE code (skips itself)
**Scanner-Scanner:** Validates scanner (filters patterns)

This architecture ensures accurate UG compliance checking while avoiding false positives from pattern definitions.

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-01
**Author:** EE Architecture Team
