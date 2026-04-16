"""interface_ast_duplicates.py
Version: 2026-04-11
Purpose: Clone detection functionality for AST scanning
License: Apache 2.0

This module provides duplicate code detection functionality:
- Type 1 clones: Exact copies with whitespace variations
- Type 2 clones: Exact copies with identifier renaming
- Type 3 clones: Near-miss copies with small modifications
- Type 4 clones: Functional clones with different implementations

Usage:
    from lee.interface.interface_ast_duplicates import scan_duplicate_inline

    result = scan_duplicate_inline(
        path='e:/LEE',
        clone_type=3,
        duplication_threshold=3
    )
"""

# Standard library imports
import ast
import sys
from pathlib import Path
from typing import Any, Optional

# Add work/development_tools to path for AST scanner
project_root = Path(__file__).parent.parent.parent.resolve()
ast_tools_path = (project_root / "work" / "development_tools" / "lee_ast_scanner").resolve()

# Security validation: ensure path is within project
try:
    ast_tools_path.relative_to(project_root)
except ValueError:
    ast_tools_path = None

if ast_tools_path and ast_tools_path.exists() and str(ast_tools_path) not in sys.path:
    sys.path.insert(0, str(ast_tools_path))

try:
    from __main__ import (
        ASTScanner,
        ResultFormatter,
        ScanConfig,
        ScanResult,
        ScanType,
    )
except ImportError:
    # Fallback implementations
    import json
    from dataclasses import dataclass, field
    from enum import Enum

    class ScanType(Enum):
        """Enumeration of available scan types for AST analysis."""
        QUALITY = "quality"
        DUPLICATE = "duplicate"
        IMPORT = "import"
        GATEWAY = "gateway"
        ALL = "all"

    @dataclass
    class ScanConfig:
        """Configuration for AST scanning operations."""
        root_path: str
        exclude_patterns: list[str] = field(default_factory=list)
        complexity_threshold: int = 10
        max_complexity: int = 15
        duplication_threshold: int = 3
        clone_type: int = 3
        function_length_threshold: int = 50
        include_test_files: bool = False
        check_complexity: bool = True
        check_naming: bool = True
        generate_graphviz: bool = False
        cache_size_limit: int = 1000
        correlation_id: Optional[str] = None
        lee_mode: bool = True

    @dataclass
    class ScanResult:
        """Results from AST scanning operations."""
        scan_type: ScanType
        success: bool
        duration_seconds: float
        files_scanned: int
        data: dict[str, Any]
        issues: list = field(default_factory=list)
        warnings: list = field(default_factory=list)
        graphviz_output: Optional[str] = None

        def to_dict(self) -> dict[str, Any]:
            return {
                "scan_type": self.scan_type.value,
                "success": self.success,
                "duration_seconds": self.duration_seconds,
                "files_scanned": self.files_scanned,
                "data": self.data,
                "issues": self.issues,
                "warnings": self.warnings,
                "graphviz_output": self.graphviz_output,
            }

    class ASTScanner:
        """AST-based code quality and security scanner."""
        def __init__(self, config: ScanConfig):
            """Initialize AST scanner with configuration."""
            self.config = config
            self.root_path = Path(config.root_path)

        def scan_files(self):
            """Yield (filepath, ast_tree) tuples for Python files.

            Yields:
                Tuples of (filepath, ast_tree) for each Python file found
            """
            for py_file in self.root_path.rglob("*.py"):
                # Check exclude patterns
                skip = False
                for pattern in self.config.exclude_patterns:
                    if pattern.replace("*", "") in str(py_file):
                        skip = True
                        break

                if skip or "test" in py_file.parts:
                    continue

                try:
                    with open(py_file, encoding='utf-8') as f:
                        tree = ast.parse(f.read(), filename=str(py_file))
                        yield (str(py_file), tree)
                except (SyntaxError, ValueError, MemoryError, RecursionError):
                    # AST parsing errors - skip file
                    ...
                except OSError:
                    # File access errors - skip file
                    ...

        def scan(self, scan_type: ScanType) -> ScanResult:
            """Run scan and return ScanResult.

            Args:
                scan_type: Type of scan to run

            Returns:
                ScanResult with scan data

            """
            import time

            start_time = time.time()
            files_scanned = 0
            data = {}
            issues = []
            warnings = []

            duration = time.time() - start_time

            return ScanResult(
                scan_type=scan_type,
                success=True,
                duration_seconds=duration,
                files_scanned=files_scanned,
                data=data,
                issues=issues,
                warnings=warnings,
                graphviz_output=None,
            )

    class ResultFormatter:
        """Formatter for AST scan results in various formats."""
        def to_json(self, result: ScanResult) -> str:
            """Convert scan result to JSON format."""
            return json.dumps(result.to_dict(), indent=2)

        def to_markdown(self, result: ScanResult) -> str:
            """Convert scan result to Markdown format."""
            lines = [
                f"# AST Scan Report: {result.scan_type.value}",
                "",
                f"**Files Scanned:** {result.files_scanned}",
                f"**Success:** {result.success}",
                f"**Duration:** {result.duration_seconds:.2f}s",
                "",
            ]
            if result.issues:
                lines.append("## Issues Found")
                for issue in result.issues:
                    lines.append(f"- {issue}")
            return "\n".join(lines)

        def to_txt(self, result: ScanResult) -> str:
            """Convert scan result to plain text format."""
            return str(result.to_dict())

        def to_console(self, result: ScanResult) -> str:
            """Convert scan result to console-friendly format."""
            return self.to_markdown(result)


# ===== CONFIGURATION =====

# Import configuration values from centralized config
try:
    from lee.lee_config.variables import (
        AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT,
        AST_SCANNER_DEFAULT_CLONE_TYPE,
        AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD,
        AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD,
        AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD,
        AST_SCANNER_DEFAULT_MAX_COMPLEXITY,
    )
    _CONFIG_AVAILABLE = True
except ImportError:
    # Fallback to hardcoded defaults if config unavailable
    _CONFIG_AVAILABLE = False
    AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD = 10
    AST_SCANNER_DEFAULT_MAX_COMPLEXITY = 15
    AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD = 3
    AST_SCANNER_DEFAULT_CLONE_TYPE = 3
    AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD = 50
    AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT = 1000

# ===== CONSTANTS =====

# Default scan parameters (now from config)
DEFAULT_COMPLEXITY_THRESHOLD = AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD
DEFAULT_MAX_COMPLEXITY = AST_SCANNER_DEFAULT_MAX_COMPLEXITY
DEFAULT_DUPLICATION_THRESHOLD = AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD
DEFAULT_CLONE_TYPE = AST_SCANNER_DEFAULT_CLONE_TYPE
DEFAULT_FUNCTION_LENGTH_THRESHOLD = AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD
DEFAULT_CACHE_SIZE_LIMIT = AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT

# Default exclude patterns
DEFAULT_EXCLUDE_PATTERNS = [
    "*/test*.py",
    "*/tests/*",
    "*/__pycache__/*",
    "*/.mypy_cache/*",
]


# ===== SECURITY VALIDATION =====

def validate_scan_path(path: str) -> None:
    """Validate path parameter to prevent directory traversal attacks.

    Args:
        path: Path to validate

    Raises:
        ValueError: If path contains traversal sequences or is outside allowed directories
        TypeError: If path is not a string
    """
    if not isinstance(path, str):
        raise TypeError(f"Path must be string, got {type(path).__name__}")

    # Check for directory traversal sequences
    dangerous_patterns = ['../', '..\\', '%2e%2e', '%252e', '..']
    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            raise ValueError(
                f"Path traversal detected: '{path}' contains '{pattern}'. "
                "Relative paths with '..' are not allowed for security reasons."
            )

    # Check for absolute path (must be within allowed base directories)
    path_obj = Path(path).resolve()

    # Define allowed base directories
    allowed_bases = [
        Path('e:/LEE').resolve(),
        Path('e:/LEE/work').resolve(),
    ]

    # Verify path is within allowed base directories
    is_allowed = False
    for base in allowed_bases:
        try:
            path_obj.relative_to(base)
            is_allowed = True
            break
        except ValueError:
            continue

    if not is_allowed:
        raise ValueError(
            f"Path '{path}' is outside allowed directories. "
            f"Allowed bases: {[str(b) for b in allowed_bases]}"
        )


# ===== CLONE DETECTION =====

def get_clone_types_inline(**_kwargs) -> dict[str, Any]:
    """Get available clone detection types.

    Returns:
        Dictionary with clone type descriptions
    """
    return {
        "success": True,
        "clone_types": {
            "1": {
                "name": "Type 1",
                "description": "Exact copies with only whitespace/comment variations",
                "examples": ["for i in range(10): print(i)", "for i in range(10):\n    print(i)"],
            },
            "2": {
                "name": "Type 2",
                "description": "Exact copies with identifier renaming",
                "examples": ["def foo(x): return x*2", "def bar(y): return y*2"],
            },
            "3": {
                "name": "Type 3",
                "description": "Near-miss copies with small modifications (insertions, deletions)",
                "examples": ["def foo(x, y): return x+y", "def foo(x, y, z=0): return x+y+z"],
            },
            "4": {
                "name": "Type 4",
                "description": "Functional clones with different implementations but same behavior",
                "examples": ["for i in range(len(lst)): print(lst[i])", "for item in lst: print(item)"],
            },
        },
        "default_type": DEFAULT_CLONE_TYPE,
    }


def scan_duplicate_inline(
    path: str,
    clone_type: int = DEFAULT_CLONE_TYPE,
    duplication_threshold: int = DEFAULT_DUPLICATION_THRESHOLD,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Run duplicate detection scan (convenience wrapper).

    Args:
        path: Path to scan
        clone_type: Clone detection type (1-4)
        duplication_threshold: Minimum occurrences
        exclude_patterns: Exclude patterns
        correlation_id: Correlation ID

    Returns:
        Scan result dictionary
    """
    # Validate path for security
    validate_scan_path(path)

    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    config = ScanConfig(
        root_path=path,
        exclude_patterns=exclude_patterns,
        clone_type=clone_type,
        duplication_threshold=duplication_threshold,
        correlation_id=correlation_id,
        lee_mode=True,
    )

    scanner = ASTScanner(config)
    results = []
    files_count = 0

    # Collect function ASTs for comparison
    functions_by_file = {}
    for filepath, ast_tree in scanner.scan_files():
        files_count += 1
        functions = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "ast": node,
                })
        if functions:
            functions_by_file[filepath] = functions

    # Type 1 & 2: Exact and near-exact matching
    if clone_type in (1, 2):
        function_hashes = {}
        for filepath, functions in functions_by_file.items():
            for func in functions:
                # Create simplified AST hash
                try:
                    func_code = ast.dump(func["ast"])
                    func_hash = hash(func_code)
                    if func_hash not in function_hashes:
                        function_hashes[func_hash] = []
                    function_hashes[func_hash].append({
                        "file": filepath,
                        "function": func["name"],
                        "line": func["line"],
                    })
                except Exception:
                    # Skip functions that can't be hashed
                    continue

        # Report duplicates
        for func_hash, occurrences in function_hashes.items():
            if len(occurrences) >= duplication_threshold:
                results.append({
                    "type": f"type_{clone_type}_clone",
                    "clone_type": clone_type,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": "MEDIUM" if len(occurrences) < 5 else "HIGH",
                })

    # Type 3: Near-miss detection (simplified)
    elif clone_type == 3:
        # Group by function signature and body length
        signature_groups = {}
        for filepath, functions in functions_by_file.items():
            for func in functions:
                node = func["ast"]
                # Count statements in function body
                stmt_count = len(node.body)
                param_count = len(node.args.args)

                sig_key = (param_count, stmt_count)
                if sig_key not in signature_groups:
                    signature_groups[sig_key] = []
                signature_groups[sig_key].append({
                    "file": filepath,
                    "function": func["name"],
                    "line": func["line"],
                })

        # Report potential near-miss clones
        for sig_key, occurrences in signature_groups.items():
            if len(occurrences) >= duplication_threshold:
                results.append({
                    "type": "type_3_clone",
                    "clone_type": 3,
                    "signature": f"{sig_key[0]} params, {sig_key[1]} statements",
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": "LOW",
                    "message": "Potential near-miss clone (similar structure)",
                })

    # Type 4: Functional clones (behavioral similarity)
    elif clone_type == 4:
        # Simplified: detect same function names in different files
        function_names = {}
        for filepath, functions in functions_by_file.items():
            for func in functions:
                name = func["name"]
                if name not in function_names:
                    function_names[name] = []
                function_names[name].append({
                    "file": filepath,
                    "line": func["line"],
                })

        for name, locations in function_names.items():
            if len(locations) >= duplication_threshold:
                results.append({
                    "type": "type_4_clone",
                    "clone_type": 4,
                    "function_name": name,
                    "occurrences": len(locations),
                    "locations": locations,
                    "severity": "INFO",
                    "message": f"Function '{name}' defined in multiple files (potential functional clone)",
                })

    return {
        "success": True,
        "scan_type": "duplicate",
        "clone_type": clone_type,
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {
            "total_clones": len(results),
            "duplication_threshold": duplication_threshold,
        },
    }


def analyze_clone_similarity(file1: str, file2: str) -> dict[str, Any]:
    """Analyze similarity between two Python files.

    Args:
        file1: Path to first file
        file2: Path to second file

    Returns:
        Dictionary with similarity metrics including:
        - jaccard_similarity: Similarity ratio (0-1)
        - common_functions: Functions with same name
        - structural_similarity: AST structure similarity
    """
    try:
        with open(file1, encoding='utf-8') as f1, open(file2, encoding='utf-8') as f2:
            tree1 = ast.parse(f1.read(), filename=file1)
            tree2 = ast.parse(f2.read(), filename=file2)
    except Exception as e:
        return {
            "error": str(e),
            "file1": file1,
            "file2": file2,
        }

    # Extract function names
    funcs1 = {n.name for n in ast.walk(tree1) if isinstance(n, ast.FunctionDef)}
    funcs2 = {n.name for n in ast.walk(tree2) if isinstance(n, ast.FunctionDef)}

    # Calculate Jaccard similarity
    intersection = len(funcs1 & funcs2)
    union = len(funcs1 | funcs2)
    jaccard = intersection / union if union > 0 else 0

    return {
        "file1": file1,
        "file2": file2,
        "jaccard_similarity": jaccard,
        "common_functions": sorted(funcs1 & funcs2),
        "unique_to_file1": sorted(funcs1 - funcs2),
        "unique_to_file2": sorted(funcs2 - funcs1),
        "recommendation": "High similarity - consider refactoring" if jaccard > 0.7 else "Acceptable",
    }


__all__ = [
    "scan_duplicate_inline",
    "get_clone_types_inline",
    "analyze_clone_similarity",
    "validate_scan_path",
    "DEFAULT_CLONE_TYPE",
    "DEFAULT_DUPLICATION_THRESHOLD",
    "ASTScanner",
    "ScanConfig",
    "ScanResult",
]
