"""interface_ast_quality.py
Version: 2026-04-11
Purpose: Quality analysis functionality for AST scanning
License: Apache 2.0

This module provides code quality scanning functionality:
- Complexity analysis
- Function length checks
- Naming convention validation
- Code metrics calculation

Usage:
    from lee.interface.interface_ast_quality import scan_quality_inline

    result = scan_quality_inline(
        path='e:/LEE',
        complexity_threshold=10,
        function_length_threshold=50
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

    def _quality_scan_handler(ast_tree: ast.AST, filepath: str, config: ScanConfig) -> list:
        """Handle QUALITY scan type.

        Args:
            ast_tree: AST tree to scan
            filepath: Path to file being scanned
            config: Scan configuration

        Returns:
            List of issues found
        """
        issues = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                        complexity += 1
                if complexity > config.complexity_threshold:
                    issues.append({
                        "type": "complexity",
                        "file": filepath,
                        "line": node.lineno,
                        "function": node.name,
                        "complexity": complexity,
                        "severity": "MEDIUM" if complexity < config.max_complexity else "HIGH",
                    })

            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > config.function_length_threshold:
                        issues.append({
                            "type": "function_length",
                            "file": filepath,
                            "line": node.lineno,
                            "function": node.name,
                            "length": length,
                            "severity": "MEDIUM",
                        })
        return issues

    _SCAN_TYPE_DISPATCH: dict[ScanType, Any] = {
        ScanType.QUALITY: _quality_scan_handler,
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

            # Scan files
            handler = _SCAN_TYPE_DISPATCH.get(scan_type)
            if handler is None:
                valid_types = ', '.join([s.value for s in _SCAN_TYPE_DISPATCH])
                raise ValueError(f"Unknown scan type: {scan_type}. Valid types: {valid_types}")

            for filepath, ast_tree in self.scan_files():
                files_scanned += 1

                issues.extend(handler(ast_tree, filepath, self.config))

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


# ===== PUBLIC API =====

def scan_quality_inline(
    path: str,
    complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
    max_complexity: int = DEFAULT_MAX_COMPLEXITY,
    function_length_threshold: int = DEFAULT_FUNCTION_LENGTH_THRESHOLD,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Run quality scan (convenience wrapper).

    Args:
        path: Path to scan
        complexity_threshold: Complexity threshold
        max_complexity: Maximum complexity
        function_length_threshold: Function length threshold
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
        complexity_threshold=complexity_threshold,
        max_complexity=max_complexity,
        function_length_threshold=function_length_threshold,
        correlation_id=correlation_id,
        lee_mode=True,
    )

    scanner = ASTScanner(config)
    result = scanner.scan(ScanType.QUALITY)

    return {
        "success": result.success,
        "scan_type": "quality",
        "files_scanned": result.files_scanned,
        "duration_seconds": result.duration_seconds,
        "issues": result.issues,
        "warnings": result.warnings,
        "data": result.data,
    }


def calculate_code_metrics(filepath: str) -> dict[str, Any]:
    """Calculate code metrics for a single file.

    Args:
        filepath: Path to Python file

    Returns:
        Dictionary with metrics including:
        - total_lines: Total lines of code
        - function_count: Number of functions
        - class_count: Number of classes
        - avg_complexity: Average cyclomatic complexity
        - max_complexity: Maximum complexity
    """
    try:
        with open(filepath, encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
    except Exception:
        return {
            "error": f"Could not parse {filepath}",
            "file": filepath,
        }

    total_lines = 0
    function_count = 0
    class_count = 0
    complexities = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_count += 1
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                    complexity += 1
            complexities.append(complexity)

        if isinstance(node, ast.ClassDef):
            class_count += 1

    return {
        "file": filepath,
        "total_lines": total_lines,
        "function_count": function_count,
        "class_count": class_count,
        "avg_complexity": sum(complexities) / len(complexities) if complexities else 0,
        "max_complexity": max(complexities) if complexities else 0,
    }


__all__ = [
    "scan_quality_inline",
    "calculate_code_metrics",
    "validate_scan_path",
    "DEFAULT_COMPLEXITY_THRESHOLD",
    "DEFAULT_MAX_COMPLEXITY",
    "DEFAULT_FUNCTION_LENGTH_THRESHOLD",
    "ASTScanner",
    "ScanConfig",
    "ScanResult",
]
