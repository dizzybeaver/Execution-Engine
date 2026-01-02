#!/usr/bin/env python3
# ee_scanner_scanner.py
# Version: 1.0.0
# Date: 2025-12-31
# Purpose: Scanner that validates ee_ug_isp_scanner.py code quality
# Type: Code Quality Validation Tool

"""
Scanner-Scanner: Validates EE UG Scanner Code Quality

This scanner ONLY scans ee_ug_isp_scanner.py and intelligently filters out:
- Pattern definitions (regex patterns like r'pattern')
- Help text and documentation
- String literals containing anti-patterns for detection
- Pattern database entries
- Comments explaining violations

It validates REAL code quality issues:
- Actual imports (not pattern definitions)
- Code structure and organization
- Encoding compliance
- File size limits
- Actual function/class implementations
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class ScanResult:
    """Results from scanning the scanner."""
    file_path: str = ""
    total_lines: int = 0
    code_lines: int = 0
    skipped_lines: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)


class ScannerScanner:
    """
    Scanner that validates ee_ug_isp_scanner.py code quality.

    Intelligently filters out pattern definitions, help text, and
    string literals to focus on actual code quality issues.
    """

    def __init__(self, target_file: str = None):
        """
        Initialize the scanner-scanner.

        Args:
            target_file: Path to ee_ug_isp_scanner.py (default: auto-detect)
        """
        if target_file is None:
            # Auto-detect the scanner file
            self_dir = Path(__file__).parent
            self.target_file = str(self_dir / "ee_ug_isp_scanner.py")
        else:
            self.target_file = target_file

        self.results = ScanResult()

    def scan_scanner(self) -> ScanResult:
        """
        Scan the scanner and validate code quality.

        Returns:
            ScanResult with violations, warnings, and statistics
        """
        if not os.path.exists(self.target_file):
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "FILE_NOT_FOUND",
                "message": f"Target file not found: {self.target_file}"
            })
            return self.results

        # Read the file
        with open(self.target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.results.file_path = self.target_file
        self.results.total_lines = len(lines)

        # Check file encoding (already using UTF-8)
        self._check_file_encoding()

        # Check file size (should be <= 400 lines, target <= 350)
        self._check_file_size(len(lines))

        # Check file header
        self._check_file_header(lines)

        # Scan each line for violations (with filtering)
        self._scan_lines(lines)

        # Check code structure
        self._check_code_structure(lines)

        # Calculate statistics
        self._calculate_statistics()

        return self.results

    def _should_skip_line(self, line: str, line_number: int, context: str) -> Tuple[bool, str]:
        """
        Determine if a line should be skipped (not scanned for violations).

        Args:
            line: The line content
            line_number: Line number (1-indexed)
            context: Context information (e.g., function name)

        Returns:
            Tuple of (should_skip, reason)
        """
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            return True, "empty_line"

        # Skip comment-only lines (they're documentation)
        if stripped.startswith('#'):
            # But still check for TODO/FIXME in comments
            if 'TODO' in stripped or 'FIXME' in stripped or 'HACK' in stripped:
                return False, "todo_found"
            return True, "comment"

        # Skip regex pattern definitions (r'...' or r"...")
        if "r'" in line or 'r"' in line:
            return True, "regex_pattern"

        # Skip pattern database entries
        if any(key in line for key in [
            "'patterns':", '"patterns":',
            "'name':", '"name":',
            "'description':", '"description":',
            "'severity':", '"severity":',
            "'category':", '"category":'
        ]):
            return True, "pattern_database"

        # Skip string literals that contain anti-patterns (they're for detection)
        # Only skip if they're standalone string assignments or dict values
        if (stripped.startswith('"') or stripped.startswith("'")) and '=' in stripped:
            # Check if it's a simple string assignment
            if re.match(r'^\w+\s*=\s*["\'].*["\']', stripped):
                return True, "string_literal"

        # Skip help/docstring text inside triple quotes
        if '"""' in line or "'''" in line:
            return True, "docstring"

        return False, "code"

    def _scan_lines(self, lines: List[str]) -> None:
        """Scan lines for code quality violations with intelligent filtering."""
        for idx, line in enumerate(lines, start=1):
            # Check if we should skip this line
            should_skip, reason = self._should_skip_line(line, idx, "")
            if should_skip:
                self.results.skipped_lines += 1
                continue

            # This is actual code - scan it
            self.results.code_lines += 1
            self._scan_line(line, idx)

    def _scan_line(self, line: str, line_number: int) -> None:
        """Scan a single line for code quality violations."""
        stripped = line.strip()

        # Check for bare except
        if re.search(r'except\s*:', line) and 'except:' not in line.lower():
            # False positive check: only real bare except
            if not any(x in line for x in ['#', '"', "'"]):
                self.results.violations.append({
                    "line": line_number,
                    "type": "CRITICAL",
                    "rule": "BARE_EXCEPT",
                    "message": "Bare except clause detected",
                    "code": stripped[:50]
                })

        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', line):
            # Skip if it's in a comment
            if not stripped.startswith('#'):
                self.results.violations.append({
                    "line": line_number,
                    "type": "WARNING",
                    "rule": "PRINT_STATEMENT",
                    "message": "Print statement found (should use logging)",
                    "code": stripped[:50]
                })

        # Check for hardcoded paths
        if re.search(r'[A-Za-z]:\\', line) and 'r"' not in line and "r'" not in line:
            # Skip if it's just a comment or docstring
            if not stripped.startswith('#'):
                self.results.violations.append({
                    "line": line_number,
                    "type": "WARNING",
                    "rule": "HARDCODED_PATH",
                    "message": "Hardcoded Windows path detected",
                    "code": stripped[:50]
                })

        # Check for long lines (>120 characters)
        if len(line) > 120:
            self.results.violations.append({
                "line": line_number,
                "type": "WARNING",
                "rule": "LONG_LINE",
                "message": f"Line too long ({len(line)} > 120 characters)",
                "code": stripped[:50] + "..."
            })

        # Check for multiple imports on one line
        if re.search(r'^import\s+\w+,\s*\w+', line):
            self.results.violations.append({
                "line": line_number,
                "type": "WARNING",
                "rule": "MULTIPLE_IMPORTS",
                "message": "Multiple imports on one line",
                "code": stripped[:50]
            })

        # Check for wildcard imports
        if re.search(r'^from\s+\w+\s+import\s+\*', line):
            self.results.violations.append({
                "line": line_number,
                "type": "CRITICAL",
                "rule": "WILDCARD_IMPORT",
                "message": "Wildcard import detected",
                "code": stripped[:50]
            })

    def _check_file_encoding(self) -> None:
        """Check file encoding (should be UTF-8)."""
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "ENCODING",
                "message": "File is not UTF-8 encoded"
            })

    def _check_file_size(self, line_count: int) -> None:
        """Check file size limits."""
        if line_count > 400:
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "FILE_SIZE",
                "message": f"File too large: {line_count} lines (max: 400)"
            })
        elif line_count > 350:
            self.results.warnings.append({
                "line": 0,
                "type": "WARNING",
                "rule": "FILE_SIZE",
                "message": f"File exceeds target size: {line_count} lines (target: <= 350)"
            })

    def _check_file_header(self, lines: List[str]) -> None:
        """Check file has proper header."""
        if len(lines) < 6:
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "FILE_HEADER",
                "message": "File header missing or incomplete"
            })
            return

        # Check for required header fields
        header = ''.join(lines[:6])
        required_fields = ['# Version:', '# Date:', '# Purpose:', '# Type:']
        missing_fields = [field for field in required_fields if field not in header]

        if missing_fields:
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "FILE_HEADER",
                "message": f"Missing header fields: {', '.join(missing_fields)}"
            })

    def _check_code_structure(self, lines: List[str]) -> None:
        """Check overall code structure."""
        # Check for main guard
        has_main_guard = False
        for line in lines:
            if '__name__' in line and '__main__' in line:
                has_main_guard = True
                break

        if not has_main_guard:
            self.results.warnings.append({
                "line": 0,
                "type": "INFO",
                "rule": "MAIN_GUARD",
                "message": "No if __name__ == '__main__' guard found"
            })

        # Check for class definition
        has_class = any('class ' in line for line in lines)
        if not has_class:
            self.results.violations.append({
                "line": 0,
                "type": "CRITICAL",
                "rule": "CLASS_DEFINITION",
                "message": "No class definition found"
            })

    def _calculate_statistics(self) -> None:
        """Calculate scan statistics."""
        self.results.stats = {
            "total_lines": self.results.total_lines,
            "code_lines": self.results.code_lines,
            "skipped_lines": self.results.skipped_lines,
            "violations_found": len(self.results.violations),
            "warnings_found": len(self.results.warnings),
            "skip_percentage": round(
                (self.results.skipped_lines / self.results.total_lines * 100) if self.results.total_lines > 0 else 0,
                1
            )
        }

    def print_results(self, results: ScanResult) -> None:
        """Print scan results in a clean, formatted report."""
        print("=" * 80)
        print("SCANNER-SCANNER RESULTS")
        print("=" * 80)
        print(f"\nTarget File: {results.file_path}")
        print(f"\n--- Statistics ---")
        print(f"Total Lines:        {results.stats.get('total_lines', 0)}")
        print(f"Code Lines:         {results.stats.get('code_lines', 0)}")
        print(f"Skipped Lines:      {results.stats.get('skipped_lines', 0)} ({results.stats.get('skip_percentage', 0)}%)")
        print(f"Violations Found:   {results.stats.get('violations_found', 0)}")
        print(f"Warnings Found:     {results.stats.get('warnings_found', 0)}")

        # Print violations
        if results.violations:
            print(f"\n--- VIOLATIONS ({len(results.violations)}) ---")
            for v in results.violations:
                severity = v.get('type', 'UNKNOWN')
                rule = v.get('rule', 'UNKNOWN')
                line = v.get('line', 0)
                message = v.get('message', 'No message')
                code = v.get('code', '')

                print(f"\n[{severity}] {rule} (Line {line})")
                print(f"  {message}")
                if code:
                    print(f"  Code: {code}")
        else:
            print(f"\n--- VIOLATIONS ---")
            print("None - Scanner is compliant!")

        # Print warnings
        if results.warnings:
            print(f"\n--- WARNINGS ({len(results.warnings)}) ---")
            for w in results.warnings:
                severity = w.get('type', 'UNKNOWN')
                rule = w.get('rule', 'UNKNOWN')
                line = w.get('line', 0)
                message = w.get('message', 'No message')

                print(f"\n[{severity}] {rule} (Line {line})")
                print(f"  {message}")
        else:
            print(f"\n--- WARNINGS ---")
            print("None")

        # Final verdict
        print("\n" + "=" * 80)
        critical_count = sum(1 for v in results.violations if v.get('type') == 'CRITICAL')
        if critical_count == 0:
            print("VERDICT: PASS - Scanner code quality is compliant")
        else:
            print(f"VERDICT: FAIL - {critical_count} critical violations found")
        print("=" * 80)


def main():
    """Main entry point for the scanner-scanner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scanner-Scanner: Validate EE UG Scanner code quality"
    )
    parser.add_argument(
        '--target',
        type=str,
        default=None,
        help='Path to ee_ug_isp_scanner.py (default: auto-detect)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Create scanner and run scan
    scanner = ScannerScanner(target_file=args.target)
    results = scanner.scan_scanner()
    scanner.print_results(results)

    # Exit with appropriate code
    critical_count = sum(1 for v in results.violations if v.get('type') == 'CRITICAL')
    sys.exit(0 if critical_count == 0 else 1)


if __name__ == "__main__":
    main()
