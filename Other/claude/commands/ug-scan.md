---
description: Runs EE UG (Universal Gateway) architecture compliance scanner using two-tier architecture
---

You are running the EE UG (Universal Gateway) Architecture Compliance Scanner with the two-tier scanner architecture.

## TWO-TIER SCANNER ARCHITECTURE

The EE UG scanner uses a clever two-tier architecture to eliminate false positives:

### Tier 1: Main Scanner (ee_ug_isp_scanner.py)
- **Purpose:** Scans all EE code EXCEPT itself
- **Why skip itself:** The scanner contains pattern definitions (regex patterns like `r'bad_pattern'`) that would trigger false positives if scanned
- **Accuracy:** 100% (no false positives from self-contamination)

### Tier 2: Scanner-Scanner (ee_scanner_scanner.py)
- **Purpose:** ONLY scans the scanner file itself
- **Special features:** Intelligent filters that distinguish between:
  - Pattern definitions (to be ignored) vs. actual code (to be validated)
  - Help text and documentation (to be ignored) vs. implementation (to be checked)
  - String literals containing anti-patterns for detection (to be ignored)
- **Why needed:** Ensures the scanner code quality is validated without flagging its own pattern definitions as violations

## SCANNING PROCESS

### Step 1: Run Main Scanner (Scan EE Code)

Run the main EE UG scanner to detect violations in all EE code:

```bash
python EE/tools/scanner/ee_ug_isp_scanner.py EE markdown
```

**Expected behavior:**
- Scans all Python files in the EE directory
- Skips the scanner file itself (ee_ug_isp_scanner.py)
- Reports violations with file paths, line numbers, and fixes
- All violations reported are REAL violations (no false positives)

**Output format:**
- Total violation count
- Breakdown by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Each violation shows:
  - File path and line number
  - Pattern name
  - Code snippet that triggered the violation
  - Description
  - Fix recommendation with code example

### Step 2: Run Scanner-Scanner (Validate Scanner Code)

After the main scanner completes, explain that you will now validate the scanner code itself:

"Now I'll validate the scanner code quality using the specialized scanner-scanner, which intelligently filters out pattern definitions and help text to focus on actual code quality issues."

Run the scanner-scanner:

```bash
python EE/tools/scanner/ee_scanner_scanner.py
```

**Expected behavior:**
- Scans only EE/tools/scanner/ee_ug_isp_scanner.py
- Filters out pattern definitions (regex strings like `r'pattern'`)
- Filters out pattern database entries
- Filters out help text and documentation
- Validates actual scanner code quality

**Output format:**
- Statistics: total lines, code lines, skipped lines, violations
- Critical violations (if any)
- Warnings (if any)
- Clear verdict (PASS/FAIL)

## RESULT PRESENTATION

Present the results in this format:

### Main Scanner Results
```
EE UG Architecture Compliance Scan
==================================

Total Violations: [count]
By Severity: {CRITICAL: X, HIGH: Y, MEDIUM: Z, LOW: W}

Top Violations:
- [Pattern]: [count] occurrences
- [Pattern]: [count] occurrences
```

### Scanner-Scanner Results
```
Scanner Code Quality Validation
===============================

File: EE/tools/scanner/ee_ug_isp_scanner.py
Lines Scanned: [total]
Lines Skipped: [count] ([percentage]%) ← Pattern definitions filtered
Violations Found: [count]

Status: [PASS/FAIL]
```

### Summary
Provide a clear summary of:
1. EE code compliance status
2. Scanner code quality status
3. Any critical issues requiring immediate attention
4. Actionable next steps

## IMPORTANT NOTES

- The main scanner does NOT scan itself - this is by design to avoid false positives
- The scanner-scanner exists solely to validate scanner code with smart pattern filters
- Together they provide 100% accurate violation detection with zero false positives
- All violations reported by the main scanner are REAL violations requiring attention
- Pattern definitions in the scanner are NOT violations (they're detection logic)

Run both scanners and present the complete results.
