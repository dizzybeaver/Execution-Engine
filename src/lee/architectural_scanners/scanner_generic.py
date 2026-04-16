"""scanner_generic.py
Version: 2026-03-22
Purpose: Generic architectural violation scanners
License: Apache 2.0
"""

import ast
from pathlib import Path
from typing import Any, Optional

# File content cache to avoid re-reading files multiple times
_file_content_cache: dict[Path, list[str]] = {}
_file_ast_cache: dict[Path, ast.AST] = {}


def _get_file_lines(file_path: Path) -> list[str]:
    """Get file lines from cache or read from disk.

    Args:
        file_path: Path to Python file

    Returns:
        List of lines in the file

    Performance: O(1) cache hit, O(n) cache miss where n = file size
    """
    if file_path not in _file_content_cache:
        try:
            with open(file_path, encoding="utf-8") as f:
                _file_content_cache[file_path] = f.readlines()
        except (OSError, UnicodeDecodeError):
            _file_content_cache[file_path] = []
    return _file_content_cache[file_path]


def _get_file_ast(file_path: Path) -> Optional[ast.AST]:
    """Get file AST from cache or parse from disk.

    Args:
        file_path: Path to Python file

    Returns:
        Parsed AST or None if parsing fails

    Performance: O(1) cache hit, O(n) cache miss where n = file size
    """
    if file_path not in _file_ast_cache:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            _file_ast_cache[file_path] = ast.parse(content, filename=str(file_path))
        except (OSError, UnicodeDecodeError, SyntaxError):
            _file_ast_cache[file_path] = None
    return _file_ast_cache[file_path]


def clear_caches() -> None:
    """Clear file content and AST caches.

    Call this between independent scan operations to free memory.
    """
    _file_content_cache.clear()
    _file_ast_cache.clear()


def _build_forbidden_wrapper_patterns() -> list[str]:
    """Build dynamic list of forbidden wrapper import patterns.

    Returns:
        List of pattern strings that should not appear in import statements
    """
    base_patterns = [
        "interface.wrappers",
        "home_assistant.interface.wrappers",
        "gateway.wrappers",
    ]

    prefixes = ["from ", "import "]
    variations = []

    for base in base_patterns:
        for prefix in prefixes:
            variations.append(f"{prefix}{base}")

    legacy_patterns = [
        "from LEE.interface.wrappers",
        "from LEE.home_assistant.interface.wrappers",
    ]

    return variations + legacy_patterns


def _is_wrapper_module(file_path: Path) -> bool:
    """Check if file is part of wrapper module system (allowed to import
    other wrappers).

    Args:
        file_path: Path to Python file

    Returns:
        True if file is in a wrapper directory (allowed to import wrappers)
    """
    path_parts = file_path.parts

    for i, part in enumerate(path_parts):
        if part == "wrappers":
            if i > 0:
                previous_part = path_parts[i - 1]
                if previous_part in {"interface", "gateway"}:
                    return True
                if previous_part == "home_assistant":
                    return True
            if i < len(path_parts) - 1:
                next_part = path_parts[i + 1]
                if next_part == "interface":
                    return True

    return False


def _is_wrapper_import_violation(line: str, forbidden_patterns: list[str]) -> bool:
    """Check if line contains a forbidden wrapper import pattern.

    Args:
        line: Source code line to check
        forbidden_patterns: List of forbidden patterns

    Returns:
        True if line contains wrapper import pattern
    """
    line_stripped = line.strip()

    if not (line_stripped.startswith("from ") or line_stripped.startswith("import ")):
        return False

    for pattern in forbidden_patterns:
        if pattern in line_stripped:
            return True

    return False


def scan_direct_wrapper_import(path: str) -> dict[str, Any]:
    """Detect forbidden direct imports from interface wrapper modules."""
    results = []
    root_path = Path(path)
    forbidden_patterns = _build_forbidden_wrapper_patterns()

    all_python_files = list(root_path.rglob("*.py"))
    files_count = len(all_python_files)

    for py_file in all_python_files:
        try:
            lines = _get_file_lines(py_file)
            if not lines:
                continue
        except (OSError, UnicodeDecodeError):
            continue

        # Early continuation if wrapper module (allowed to import wrappers)
        if _is_wrapper_module(py_file):
            continue

        for line_num, line in enumerate(lines, start=1):
            if not _is_wrapper_import_violation(line, forbidden_patterns):
                continue

            results.append({
                "type": "direct_wrapper_import",
                "file": str(py_file),
                "line": line_num,
                "severity": "CRITICAL",
                "message": "Direct import from wrapper module bypasses gateway",
                "forbidden_import": line.strip(),
                "suggestion": "Use gateway pattern: execute_operation(GatewayInterface.*, 'operation', ...)",
            })

    return {
        "success": True,
        "scan_type": "direct_wrapper_import",
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_relative_import(path: str) -> dict[str, Any]:
    """Detect relative imports that violate absolute import preference."""
    results = []
    root_path = Path(path)

    all_python_files = list(root_path.rglob("*.py"))
    files_count = len(all_python_files)

    for py_file in all_python_files:
        try:
            lines = _get_file_lines(py_file)
            if not lines:
                continue
            for line_num, line in enumerate(lines, start=1):
                line_stripped = line.strip()
                if line_stripped.startswith("from .") or line_stripped.startswith("from .."):
                    results.append({
                        "type": "relative_import",
                        "file": str(py_file),
                        "line": line_num,
                        "severity": "MEDIUM",
                        "message": "Relative import should be absolute",
                        "import_statement": line_stripped,
                        "suggestion": "Use absolute imports: 'from package.module import name'",
                    })
        except (OSError, UnicodeDecodeError):
            continue

    return {
        "success": True,
        "scan_type": "relative_import",
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_security_bypass(path: str) -> dict[str, Any]:
    """Detect security module bypasses and unsafe practices."""
    results = []
    root_path = Path(path)

    for py_file in root_path.rglob("*.py"):
        try:
            tree = _get_file_ast(py_file)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "pickle":
                            results.append({
                                "type": "security_bypass",
                                "file": str(py_file),
                                "line": node.lineno,
                                "severity": "CRITICAL",
                                "message": "Direct pickle import bypasses lee_security safe serialization",
                                "issue": "unsafe_pickle_import",
                                "suggestion": "Use 'from lee.lee_security import safe_loads, safe_dumps' for RCE-safe serialization",
                            })
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ["environ", "getenv"]:
                            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                                results.append({
                                    "type": "security_bypass",
                                    "file": str(py_file),
                                    "line": node.lineno,
                                    "severity": "MEDIUM",
                                    "message": "Direct os.environ access bypasses gateway config layer",
                                    "issue": "config_layer_bypass",
                                    "suggestion": "Use gateway config: execute_operation(GatewayInterface.CONFIG, 'get', name='...')",
                                })
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue

    return {
        "success": True,
        "scan_type": "security_bypass",
        "files_scanned": len(list(root_path.rglob("*.py"))),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_completeness_compliance(path: str) -> dict[str, Any]:
    """Detect incomplete implementations (TODO, FIXME, NotImplementedError)."""
    results = []
    root_path = Path(path)

    all_python_files = list(root_path.rglob("*.py"))
    files_count = len(all_python_files)

    for py_file in all_python_files:
        results.extend(_check_file_completeness(py_file))

    return {
        "success": True,
        "scan_type": "completeness_compliance",
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _check_file_completeness(py_file: Path) -> list[dict[str, Any]]:
    """Check a single file for incomplete implementations.

    Args:
        py_file: Path to Python file

    Returns:
        List of completeness issues found
    """
    results = []
    try:
        with open(py_file, encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                issue = _check_function_completeness(node, py_file)
                if issue:
                    results.append(issue)
    except (OSError, UnicodeDecodeError, SyntaxError):
        pass

    return results


def _check_function_completeness(node: ast.FunctionDef, py_file: Path) -> Optional[dict[str, Any]]:
    """Check a function for incomplete implementation markers.

    Args:
        node: AST FunctionDef node
        py_file: File being scanned

    Returns:
        Issue dict if incomplete, None otherwise
    """
    has_todo = _has_todo_comment(node)
    has_not_implemented = _has_not_implemented_error(node)

    if has_todo or has_not_implemented:
        severity = "HIGH" if has_not_implemented else "MEDIUM"
        issue_type = "not_implemented_error" if has_not_implemented else "incomplete_implementation"
        return {
            "type": "completeness_compliance",
            "file": str(py_file),
            "line": node.lineno,
            "function": node.name,
            "severity": severity,
            "message": f"Function '{node.name}' has incomplete implementation",
            "issue": issue_type,
            "suggestion": "Complete implementation or remove stub function",
        }
    return None


def _has_not_implemented_error(node: ast.FunctionDef) -> bool:
    """Check if function raises NotImplementedError.

    Args:
        node: AST FunctionDef node

    Returns:
        True if function raises NotImplementedError
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Raise):
            if isinstance(child.exc, ast.Name) and child.exc.id == "NotImplementedError":
                return True
    return False


def _has_todo_comment(node: ast.FunctionDef) -> bool:
    """Check if function contains TODO or FIXME comments.

    Args:
        node: AST FunctionDef node

    Returns:
        True if function contains TODO/FIXME
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Constant):
            if isinstance(child.value, str):
                value_upper = child.value.upper()
                if "TODO" in value_upper or "FIXME" in value_upper:
                    return True
    return False
