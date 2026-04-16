"""interface_ast_imports.py
Version: 2026-04-11
Purpose: Import analysis functionality for AST scanning
License: Apache 2.0

This module provides import statement analysis functionality:
- Detect import statements inside function bodies (anti-pattern)
- Identify circular dependencies
- Find unused imports
- Check for relative import violations
- Analyze import organization and style

Usage:
    from lee.interface.interface_ast_imports import scan_import_pattern_inline

    result = scan_import_pattern_inline(path='e:/LEE')
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


# ===== IMPORT ANALYSIS FUNCTIONS =====

def scan_import_pattern_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for import statements inside function bodies (anti-pattern).

    Args:
        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID
        **kwargs: Additional parameters

    Returns:
        Dictionary with scan results
    """
    # Validate path for security
    validate_scan_path(path)

    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    config = ScanConfig(
        root_path=path,
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
        lee_mode=True,
    )

    scanner = ASTScanner(config)
    results = []

    for filepath, ast_tree in scanner.scan_files():
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        # Check if import is inside function body (direct child)
                        if child in node.body:
                            results.append({
                                "type": "import_inside_function",
                                "file": filepath,
                                "line": child.lineno,
                                "function": node.name,
                                "severity": "MEDIUM",
                                "message": f"Import statement inside function '{node.name}'",
                                "import": ast.unparse(child) if hasattr(ast, 'unparse') else 'import',
                            })

    return {
        "success": True,
        "scan_type": "import_pattern",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_misindented_import_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for misindented import statements inside try/except blocks (anti-pattern).

    Detects import statements that are inside try/except blocks but have wrong
    indentation, which causes IndentationError or prevents proper import handling.

    Args:
        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID

    Returns:
        Dictionary with scan results
    """
    # Validate path for security
    validate_scan_path(path)

    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    config = ScanConfig(
        root_path=path,
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
        lee_mode=True,
    )

    scanner = ASTScanner(config)
    results = []

    for filepath, ast_tree in scanner.scan_files():
        # Read source code to check indentation
        try:
            with open(filepath, encoding='utf-8') as f:
                source_lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            continue

        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Try):
                # Check try body for import statements
                for child in node.body:
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        # Get the line number and check indentation
                        line_num = child.lineno - 1  # 0-indexed
                        if line_num < len(source_lines):
                            line = source_lines[line_num]
                            # Check if import has proper indentation (at least 4 spaces for inside try)
                            indent = len(line) - len(line.lstrip())
                            # Accept 4, 8, 12, etc. spaces (multiples of 4, at least 4)
                            if indent < 4 or indent % 4 != 0:
                                results.append({
                                    "type": "misindented_import",
                                    "file": filepath,
                                    "line": child.lineno,
                                    "severity": "HIGH",
                                    "message": f"Import statement has incorrect indentation ({indent} spaces)",
                                    "import": ast.unparse(child) if hasattr(ast, 'unparse') else 'import',
                                    "suggestion": "Ensure import is indented by 4 spaces (one level) inside try block",
                                })

                # Check except handlers for import statements
                for handler in node.handlers:
                    for child in handler.body:
                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                            line_num = child.lineno - 1
                            if line_num < len(source_lines):
                                line = source_lines[line_num]
                                indent = len(line) - len(line.lstrip())
                                # Accept 4, 8, 12, etc. spaces (multiples of 4, at least 4)
                                if indent < 4 or indent % 4 != 0:
                                    results.append({
                                        "type": "misindented_import",
                                        "file": filepath,
                                        "line": child.lineno,
                                        "severity": "HIGH",
                                        "message": f"Import statement in except block has incorrect indentation ({indent} spaces)",
                                        "import": ast.unparse(child) if hasattr(ast, 'unparse') else 'import',
                                        "suggestion": "Ensure import is indented by 4 spaces (one level) inside except block",
                                    })

    return {
        "success": True,
        "scan_type": "misindented_import",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_direct_wrapper_import_inline(path: str, **kwargs) -> dict[str, Any]:
    """Detect forbidden direct imports from interface wrapper modules.

    CRITICAL: Direct wrapper imports bypass the gateway pattern and break SUGA-ISP architecture.

    Args:
        path: Directory path to scan

    Returns:
        Scan result with CRITICAL severity issues for direct wrapper imports
    """
    # Validate path for security
    validate_scan_path(path)

    results = []
    root_path = Path(path)

    forbidden_patterns = [
        "from interface.wrappers",
        "from home_assistant.interface.wrappers",
        "from LEE.interface.wrappers",
    ]

    all_python_files = list(root_path.rglob("*.py"))
    files_count = len(all_python_files)

    for py_file in all_python_files:
        try:
            with open(py_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f.readlines(), start=1):
                    line_stripped = line.strip()
                    if line_stripped.startswith("from ") or line_stripped.startswith("import "):
                        for pattern in forbidden_patterns:
                            if pattern in line_stripped:
                                results.append({
                                    "type": "direct_wrapper_import",
                                    "file": str(py_file),
                                    "line": line_num,
                                    "severity": "CRITICAL",
                                    "message": "Direct import from wrapper module bypasses gateway",
                                    "forbidden_import": line_stripped,
                                    "suggestion": "Use gateway pattern: execute_operation(GatewayInterface.*, 'operation', ...)",
                                })
        except (KeyError, AttributeError, TypeError):
            # Data structure errors during analysis
            continue

    return {
        "success": True,
        "scan_type": "direct_wrapper_import",
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def scan_relative_import_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for relative imports that should be absolute (LEE style guide violation).

    LEE prefers absolute imports over relative imports for clarity.

    Args:
        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID
        **kwargs: Additional parameters

    Returns:
        Dictionary with scan results
    """
    # Validate path for security
    validate_scan_path(path)

    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    config = ScanConfig(
        root_path=path,
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
        lee_mode=True,
    )

    results = []
    files_count = 0

    all_python_files = list(Path(config.root_path).rglob("*.py"))
    files_count = len(all_python_files)

    for py_file in all_python_files:
        try:
            with open(py_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f.readlines(), start=1):
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
        except (KeyError, AttributeError, TypeError):
            # Data structure errors during analysis
            continue

    return {
        "success": True,
        "scan_type": "relative_import",
        "files_scanned": files_count,
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def analyze_import_dependencies(path: str) -> dict[str, Any]:
    """Analyze import dependencies across a codebase.

    Args:
        path: Root path to analyze

    Returns:
        Dictionary with:
        - dependency_graph: Adjacency list of module dependencies
        - circular_dependencies: List of circular dependency chains
        - orphan_modules: Modules with no imports
        - import_frequency: How often each module is imported
    """
    # Validate path for security
    validate_scan_path(path)

    root_path = Path(path)
    dependency_graph = {}
    import_frequency = {}

    for py_file in root_path.rglob("*.py"):
        if "test" in py_file.parts or "__pycache__" in py_file.parts:
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            module_name = str(py_file.relative_to(root_path).with_suffix(''))
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            dependency_graph[module_name] = imports

            # Track import frequency
            for imp in imports:
                if imp not in import_frequency:
                    import_frequency[imp] = 0
                import_frequency[imp] += 1

        except Exception:
            # Skip files that can't be parsed
            continue

    # Detect circular dependencies
    circular_deps = []
    visited = set()

    def detect_cycle(module: str, path: list[str]) -> None:
        if module in path:
            cycle_start = path.index(module)
            circular_deps.append(path[cycle_start:] + [module])
            return
        if module in visited or module not in dependency_graph:
            return
        visited.add(module)
        for dep in dependency_graph[module]:
            detect_cycle(dep, path + [module])

    for module in dependency_graph:
        detect_cycle(module, [])

    return {
        "success": True,
        "dependency_graph": dependency_graph,
        "circular_dependencies": circular_deps,
        "orphan_modules": [m for m, deps in dependency_graph.items() if not deps],
        "import_frequency": dict(sorted(import_frequency.items(), key=lambda x: x[1], reverse=True)),
    }


__all__ = [
    "scan_import_pattern_inline",
    "scan_misindented_import_inline",
    "scan_direct_wrapper_import_inline",
    "scan_relative_import_inline",
    "analyze_import_dependencies",
    "validate_scan_path",
    "ASTScanner",
    "ScanConfig",
    "ScanResult",
]
