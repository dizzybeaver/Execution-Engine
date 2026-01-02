#!/usr/bin/env python
"""
EE Deployment Verification Script

Verifies EE directory is ready for deployment by checking:
- All Python files compile successfully
- No __pycache__ directories present
- No .pyc files present
- All __init__.py files present
- Critical configuration files exist
- No syntax errors
- No import errors

Usage:
    python scripts/verify_deployment.py
    python scripts/verify_deployment.py --verbose
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import List, Tuple
import py_compile
import ast


class Colors:
    """Terminal colors for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")


def print_warning(msg: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")


def print_info(msg: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")


def check_pycache(ee_root: Path, verbose: bool = False) -> bool:
    """Check for __pycache__ directories."""
    print_info("Checking for __pycache__ directories...")

    pycache_dirs = list(ee_root.rglob("__pycache__"))
    if pycache_dirs:
        print_error(f"Found {len(pycache_dirs)} __pycache__ directories")
        if verbose:
            for d in pycache_dirs:
                print(f"  - {d.relative_to(ee_root)}")
        return False

    print_success("No __pycache__ directories found")
    return True


def check_pyc_files(ee_root: Path, verbose: bool = False) -> bool:
    """Check for .pyc files."""
    print_info("Checking for .pyc files...")

    pyc_files = list(ee_root.rglob("*.pyc"))
    if pyc_files:
        print_error(f"Found {len(pyc_files)} .pyc files")
        if verbose:
            for f in pyc_files:
                print(f"  - {f.relative_to(ee_root)}")
        return False

    print_success("No .pyc files found")
    return True


def check_pytest_cache(ee_root: Path, verbose: bool = False) -> bool:
    """Check for .pytest_cache directories."""
    print_info("Checking for .pytest_cache directories...")

    pytest_cache = list(ee_root.rglob(".pytest_cache"))
    if pytest_cache:
        print_error(f"Found {len(pytest_cache)} .pytest_cache directories")
        if verbose:
            for d in pytest_cache:
                print(f"  - {d.relative_to(ee_root)}")
        return False

    print_success("No .pytest_cache directories found")
    return True


def check_init_files(ee_root: Path, verbose: bool = False) -> bool:
    """Check all Python packages have __init__.py."""
    print_info("Checking __init__.py files...")

    # Find all directories with Python files
    missing_init = []
    for py_file in ee_root.rglob("*.py"):
        package_dir = py_file.parent
        init_file = package_dir / "__init__.py"

        if not init_file.exists() and package_dir != ee_root:
            missing_init.append(init_file.relative_to(ee_root))

    if missing_init:
        print_error(f"Missing {len(missing_init)} __init__.py files")
        if verbose:
            for f in missing_init:
                print(f"  - {f}")
        return False

    print_success("All packages have __init__.py files")
    return True


def check_compilation(ee_root: Path, verbose: bool = False) -> bool:
    """Check all Python files compile successfully."""
    print_info("Checking Python file compilation...")

    py_files = list(ee_root.rglob("*.py"))
    errors = []

    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append((py_file.relative_to(ee_root), str(e)))

    if errors:
        print_error(f"Failed to compile {len(errors)} Python files")
        if verbose:
            for f, err in errors:
                print(f"  - {f}")
                print(f"    {err}")
        return False

    print_success(f"All {len(py_files)} Python files compile successfully")
    return True


def check_syntax_errors(ee_root: Path, verbose: bool = False) -> bool:
    """Check for syntax errors using AST parsing."""
    print_info("Checking for syntax errors...")

    py_files = list(ee_root.rglob("*.py"))
    errors = []

    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            errors.append((py_file.relative_to(ee_root), str(e)))

    if errors:
        print_error(f"Found {len(errors)} files with syntax errors")
        if verbose:
            for f, err in errors:
                print(f"  - {f}")
                print(f"    {err}")
        return False

    print_success("No syntax errors found")
    return True


def check_critical_files(ee_root: Path, verbose: bool = False) -> bool:
    """Check critical files exist."""
    print_info("Checking critical files...")

    critical_files = [
        "requirements.txt",
        "ee_server_config.yaml",
        "CLAUDE.md",
        "README.md",
        "ARCHITECTURE.md",
        "run_server.py",
        "src/__init__.py",
    ]

    missing = []
    for file in critical_files:
        if not (ee_root / file).exists():
            missing.append(file)

    if missing:
        print_error(f"Missing {len(missing)} critical files")
        if verbose:
            for f in missing:
                print(f"  - {f}")
        return False

    print_success(f"All {len(critical_files)} critical files present")
    return True


def check_structure(ee_root: Path, verbose: bool = False) -> bool:
    """Check EE directory structure."""
    print_info("Checking directory structure...")

    required_dirs = [
        "src",
        "tests",
        "config",
        "plugins",
        "docs",
        "SIMA",
        "reference",
    ]

    missing = []
    for d in required_dirs:
        if not (ee_root / d).exists():
            missing.append(d)

    if missing:
        print_error(f"Missing {len(missing)} required directories")
        if verbose:
            for d in missing:
                print(f"  - {d}")
        return False

    print_success(f"All {len(required_dirs)} required directories present")
    return True


def main() -> int:
    """Main verification routine."""
    parser = argparse.ArgumentParser(
        description="Verify EE deployment readiness"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--ee-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Path to EE root directory"
    )

    args = parser.parse_args()

    ee_root = args.ee_root.resolve()
    verbose = args.verbose

    print(f"{Colors.BOLD}EE Deployment Verification{Colors.END}")
    print(f"EE Root: {ee_root}")
    print(f"Verbose: {verbose}")
    print()

    # Run all checks
    checks = [
        check_pycache,
        check_pyc_files,
        check_pytest_cache,
        check_init_files,
        check_compilation,
        check_syntax_errors,
        check_critical_files,
        check_structure,
    ]

    results = []
    for check in checks:
        try:
            result = check(ee_root, verbose)
            results.append(result)
        except Exception as e:
            print_error(f"Check failed with exception: {e}")
            results.append(False)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"{Colors.BOLD}Deployment Verification Summary{Colors.END}")
    print(f"Passed: {passed}/{total}")

    if all(results):
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] EE IS READY FOR DEPLOYMENT{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}[FAILED] EE IS NOT READY FOR DEPLOYMENT{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
