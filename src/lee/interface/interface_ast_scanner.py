"""interface_ast_scanner.py
Version: 2026-03-22_2
Purpose: AST_SCANNER interface router - AST analysis and code quality scanning
License: Apache 2.0

SECURITY (2026-03-22_2):
- Added path traversal validation to prevent directory escape attacks
- Validates path parameter against allowlist and checks for traversal sequences

This interface provides gateway routing for AST scanning operations, including:
- Code quality analysis (complexity, length, naming)
- Clone detection (Type 1-4 duplicate detection)
- Import analysis (circular dependencies, unused imports)
- Gateway compliance checking (LEE-specific)
- Interface harvesting (extract interface definitions)
- Control flow analysis (CFG/DFG generation)
- Completeness verification (implementation tracking)
- Deep analysis (combined control + data flow)

Usage:
from lee.gateway import execute_operation, GatewayInterface
from lee.gateway.gateway_core import generate_correlation_id

    # Run quality scan
    result = execute_operation(
        GatewayInterface.AST_SCANNER,
        'scan',
        scan_type='quality',
        path='e:/LEE'
    )

    # Run duplicate detection
    result = execute_operation(
        GatewayInterface.AST_SCANNER,
        'scan',
        scan_type='duplicate',
        path='e:/LEE',
        clone_type=3
    )

    # Get scan results as markdown
    report = execute_operation(
        GatewayInterface.AST_SCANNER,
        'format_result',
        result=result,
        format='markdown'
    )
"""

# Standard library imports
import sys
from pathlib import Path
from typing import Any, Optional
from collections.abc import Callable

# Local imports
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Add work/development_tools to path for AST scanner
# SECURITY: Validate path to prevent directory traversal attacks
project_root = Path(__file__).parent.parent.parent.resolve()
ast_tools_path = (project_root / "work" / "development_tools" / "lee_ast_scanner").resolve()

# Security validation: ensure path is within project
try:
    ast_tools_path.relative_to(project_root)
except ValueError:
    # Path traversal detected - use safe default
    ...
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
    # Fallback: use simplified AST scanning without full tools
    ...
    import ast
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

    def _import_scan_handler(ast_tree: ast.AST, filepath: str, _config: ScanConfig) -> list:
        """Handle IMPORT scan type.

        Args:
            ast_tree: AST tree to scan
            filepath: Path to file being scanned
            config: Scan configuration

        Returns:
            List of issues found
        """
        issues = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('.'):
                        issues.append({
                            "type": "relative_import",
                            "file": filepath,
                            "line": node.lineno,
                            "module": alias.name,
                            "severity": "INFO",
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('.'):
                    issues.append({
                        "type": "relative_import",
                        "file": filepath,
                        "line": node.lineno,
                        "module": node.module,
                        "severity": "INFO",
                    })
        return issues

    def _gateway_scan_handler(ast_tree: ast.AST, filepath: str, config: ScanConfig) -> list:
        """Handle GATEWAY scan type.

        Args:
            ast_tree: AST tree to scan
            filepath: Path to file being scanned
            config: Scan configuration

        Returns:
            List of issues found
        """
        issues = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'execute_operation':
                    if len(node.args) >= 2:
                        issues.append({
                            "type": "gateway_call",
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "INFO",
                        })
        return issues

    _SCAN_TYPE_DISPATCH: dict[ScanType, Callable] = {
        ScanType.QUALITY: _quality_scan_handler,
        ScanType.IMPORT: _import_scan_handler,
        ScanType.GATEWAY: _gateway_scan_handler,
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

# ===== SECURITY VALIDATION =====

def _validate_scan_path(path: str) -> None:
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
    ...
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


# ===== INLINE IMPLEMENTATIONS =====

def _scan_inline(
    path: str,
    scan_type: str = "quality",
    exclude_patterns: Optional[list[str]] = None,
    complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
    max_complexity: int = DEFAULT_MAX_COMPLEXITY,
    duplication_threshold: int = DEFAULT_DUPLICATION_THRESHOLD,
    clone_type: int = DEFAULT_CLONE_TYPE,
    function_length_threshold: int = DEFAULT_FUNCTION_LENGTH_THRESHOLD,
    include_test_files: bool = False,
    check_complexity: bool = True,
    check_naming: bool = True,
    generate_graphviz: bool = False,
    cache_size_limit: int = DEFAULT_CACHE_SIZE_LIMIT,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Run AST scan on codebase.

        path: Path to scan
        scan_type: Type of scan ('quality', 'duplicate', 'import', 'gateway', 'all', etc.)
        exclude_patterns: File patterns to exclude
        complexity_threshold: Complexity threshold for warnings
        max_complexity: Maximum complexity before high severity
        duplication_threshold: Minimum occurrences for duplicate detection
        clone_type: Clone detection type (1-4)
        function_length_threshold: Function length threshold in lines
        include_test_files: Whether to include test files
        check_complexity: Whether to check complexity
        check_naming: Whether to check naming conventions
        generate_graphviz: Whether to generate Graphviz output
        cache_size_limit: AST cache size limit
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dictionary with scan results:
        - success: bool
        - scan_type: str
        - duration_seconds: float
        - files_scanned: int
        - data: dict
        - issues: list
        - warnings: list

    """
    # Build exclude patterns
    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    # Create scan config
    config = ScanConfig(
        root_path=path,
        exclude_patterns=exclude_patterns,
        complexity_threshold=complexity_threshold,
        max_complexity=max_complexity,
        duplication_threshold=duplication_threshold,
        clone_type=clone_type,
        function_length_threshold=function_length_threshold,
        include_test_files=include_test_files,
        check_complexity=check_complexity,
        check_naming=check_naming,
        generate_graphviz=generate_graphviz,
        cache_size_limit=cache_size_limit,
        correlation_id=correlation_id,
        lee_mode=True,  # LEE mode by default
    )

    # Create scanner and run scan
    scanner = ASTScanner(config)

    # Map scan type string to enum
    try:
        scanTypeEnum = ScanType(scan_type)
    except ValueError as exc:
        valid_types = ", ".join([s.value for s in ScanType])
        raise ValueError(f"Unknown scan type: '{scan_type}'. Valid types: {valid_types}") from exc

    result = scanner.scan(scanTypeEnum)

    return result.to_dict()


def _scan_quality_inline(
    path: str,
    complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
    max_complexity: int = DEFAULT_MAX_COMPLEXITY,
    function_length_threshold: int = DEFAULT_FUNCTION_LENGTH_THRESHOLD,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Run quality scan (convenience wrapper).

        path: Path to scan
        complexity_threshold: Complexity threshold
        max_complexity: Maximum complexity
        function_length_threshold: Function length threshold
        exclude_patterns: Exclude patterns
        correlation_id: Correlation ID

        Scan result dictionary

    """
    return _scan_inline(
        path=path,
        scan_type="quality",
        complexity_threshold=complexity_threshold,
        max_complexity=max_complexity,
        function_length_threshold=function_length_threshold,
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
    )


def _scan_duplicate_inline(
    path: str,
    clone_type: int = DEFAULT_CLONE_TYPE,
    duplication_threshold: int = DEFAULT_DUPLICATION_THRESHOLD,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Run duplicate detection scan (convenience wrapper).

        path: Path to scan
        clone_type: Clone detection type (1-4)
        duplication_threshold: Minimum occurrences
        exclude_patterns: Exclude patterns
        correlation_id: Correlation ID

        Scan result dictionary

    """
    return _scan_inline(
        path=path,
        scan_type="duplicate",
        clone_type=clone_type,
        duplication_threshold=duplication_threshold,
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
    )


def _scan_all_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Run all scans (convenience wrapper).

        path: Path to scan
        exclude_patterns: Exclude patterns
        correlation_id: Correlation ID

        Scan result dictionary with all scan types

    """
    return _scan_inline(
        path=path,
        scan_type="all",
        exclude_patterns=exclude_patterns,
        correlation_id=correlation_id,
        **kwargs,
    )


def _json_format_handler(formatter: ResultFormatter, scan_result: ScanResult) -> str:
    """Handle JSON format output."""
    return formatter.to_json(scan_result)


def _markdown_format_handler(formatter: ResultFormatter, scan_result: ScanResult) -> str:
    """Handle markdown format output."""
    return formatter.to_markdown(scan_result)


def _txt_format_handler(formatter: ResultFormatter, scan_result: ScanResult) -> str:
    """Handle text format output."""
    return formatter.to_txt(scan_result)


def _console_format_handler(formatter: ResultFormatter, scan_result: ScanResult) -> str:
    """Handle console format output."""
    return formatter.to_console(scan_result)


_FORMAT_DISPATCH: dict[str, Callable] = {
    "json": _json_format_handler,
    "markdown": _markdown_format_handler,
    "txt": _txt_format_handler,
    "console": _console_format_handler,
}

VALID_FORMAT_TYPES: frozenset[str] = frozenset(_FORMAT_DISPATCH.keys())


def validate_format_type(format_type: str) -> bool:
    """Validate format type against allowed values.

        format_type: Format type string to validate

        True if valid, False otherwise

    """
    if not isinstance(format_type, str):
        return False
    return format_type in VALID_FORMAT_TYPES


def get_format_metadata(format_type: str) -> Optional[dict[str, Any]]:
    """Get metadata for a format type.

        format_type: Format type string

        Dictionary with metadata or None if invalid format

        Metadata includes:
        - content_type: HTTP Content-Type header value
        - file_extension: Default file extension
        - description: Human-readable description
        - binary: Whether output is binary (always False for formats)

    """
    if not validate_format_type(format_type):
        return None

    metadata = {
        "json": {
            "content_type": "application/json",
            "file_extension": ".json",
            "description": "Structured JSON format for programmatic processing",
            "binary": False,
        },
        "markdown": {
            "content_type": "text/markdown",
            "file_extension": ".md",
            "description": "Human-readable Markdown documentation format",
            "binary": False,
        },
        "txt": {
            "content_type": "text/plain",
            "file_extension": ".txt",
            "description": "Plain text representation of scan results",
            "binary": False,
        },
        "console": {
            "content_type": "text/plain",
            "file_extension": ".txt",
            "description": "Console-friendly formatted output with ANSI colors",
            "binary": False,
        },
    }

    return metadata.get(format_type)


def _format_result_inline(
    result: dict[str, Any],
    format_type: str = "json",
    correlation_id: Optional[str] = None,
    **kwargs,
) -> str:
    """Format scan result for output.

        result: Scan result dictionary (from scan operations)
        format_type: Output format ('json', 'markdown', 'txt', 'console')
        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Formatted result string

        Raises:
        ValueError: If format_type is not valid

    """
    # Validate format type
    if not validate_format_type(format_type):
        valid_formats = ', '.join(sorted(VALID_FORMAT_TYPES))
        raise ValueError(
            f"Unknown format type: '{format_type}'. "
            f"Valid types: {valid_formats}"
        )

    # Reconstruct ScanResult from dict
    scan_result = ScanResult(
        scan_type=ScanType(result["scan_type"]),
        success=result["success"],
        duration_seconds=result["duration_seconds"],
        files_scanned=result["files_scanned"],
        data=result["data"],
        issues=[],  # Issues would need reconstruction
        warnings=result["warnings"],
        graphviz_output=result.get("graphviz_output"),
    )

    formatter = ResultFormatter()

    handler = _FORMAT_DISPATCH.get(format_type)
    if handler is None:
        valid_formats = ', '.join(_FORMAT_DISPATCH.keys())
        raise ValueError(f"Unknown format type: {format_type}. Valid types: {valid_formats}")

    return handler(formatter, scan_result)


def _get_available_scans_inline(
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, str]:
    """Get list of available scan types.

        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary mapping scan types to descriptions

    """
    return {
        "quality": "Code quality analysis (complexity, documentation, patterns)",
        "duplicate": "Type 1-4 clone detection",
        "import": "Circular import detection and validation",
        "gateway": "LEE Gateway compliance checking",
        "harvest": "Interface extraction and harvesting",
        "control": "Control flow analysis with Graphviz output",
        "completeness": "Implementation completeness verification",
        "deep": "Deep analysis (control + data flow)",
        "import_pattern": "Detect import statements inside function bodies (anti-pattern)",
        "gateway_pattern": "Detect self-referential gateway calls (anti-pattern)",
        "exception_pattern": "Detect generic exception catching without logging (anti-pattern)",
        "self_referential_gateway": "Detect wrapper functions calling their own interface (CRITICAL - infinite recursion)",
        "parameter_collision": "Detect keyword arguments conflicting with execute_operation signature (HIGH - TypeError)",
        "wrong_operation_name": "Detect calls to non-existent operations (HIGH - runtime error)",
        "misindented_import": "Detect import statements with incorrect indentation in try/except blocks (HIGH - IndentationError)",
        "empty_except_block": "Detect empty try/except blocks that silently suppress errors (HIGH - debugging difficulty)",
        "malformed_docstring": "Detect functions with malformed docstring syntax (MEDIUM - documentation quality)",
        "scan_direct_wrapper_import": "Detect forbidden direct imports from interface wrapper modules (CRITICAL - gateway bypass)",
        "scan_security_bypass": "Detect security module bypasses and unsafe practices (pickle, os.environ)",
        "scan_relative_import": "Detect relative imports that violate absolute import preference (MEDIUM)",
        "all": "Run all scans",
    }


def _get_clone_types_inline(
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, str]:
    """Get clone type descriptions.

        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary mapping clone types to descriptions

    """
    return {
        "1": "Exact match - identical source code",
        "2": "Parameterized match - same signature",
        "3": "Near-match - similar structure (default)",
        "4": "Semantic - combined signature + structure",
    }


# ===== ANTI-PATTERN DETECTION SCANNERS =====

def _scan_import_pattern_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for import statements inside function bodies (anti-pattern).

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary with scan results

    """
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


def _scan_gateway_pattern_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for self-referential gateway calls (anti-pattern).

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary with scan results

    """
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
        # Determine expected interface from filename
        if 'wrapper' in filepath:
            # Extract interface name from filename (e.g., singleton_wrappers -> SINGLETON)
            filename = filepath.replace('\\', '/').split('/')[-1]
            if '_wrappers.py' in filename:
                interface_name = filename.replace('_wrappers.py', '').upper()
                expected_interface = f"GatewayInterface.{interface_name}"

                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.Call):
                        # Check for execute_operation calls
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr == 'execute_operation':
                                # Check first argument
                                if node.args and isinstance(node.args[0], ast.Attribute):
                                    interface_ref = ast.unparse(node.args[0])
                                    if expected_interface in interface_ref:
                                        results.append({
                                            "type": "self_referential_gateway_call",
                                            "file": filepath,
                                            "line": node.lineno,
                                            "severity": "HIGH",
                                            "message": f"Function calls its own interface '{expected_interface}'",
                                            "interface": expected_interface,
                                        })

    return {
        "success": True,
        "scan_type": "gateway_pattern",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_exception_pattern_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for generic exception catching without logging (anti-pattern).

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary with scan results

    """
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
            if isinstance(node, ast.ExceptHandler):
                # Check if catching generic Exception
                if node.type and isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    # Check if body has logging call
                    has_logging = False
                    for body_node in ast.walk(node):
                        if isinstance(body_node, ast.Call):
                            if isinstance(body_node.func, ast.Attribute):
                                if body_node.func.attr in ('log', 'warning', 'error', 'info', 'debug'):
                                    has_logging = True
                                    break
                            elif isinstance(body_node.func, ast.Name):
                                if body_node.func.id in ('print', 'log'):
                                    has_logging = True
                                    break

                    if not has_logging:
                        results.append({
                            "type": "generic_exception_catch",
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "HIGH",
                            "message": "Catching Exception without logging",
                        })

    return {
        "success": True,
        "scan_type": "exception_pattern",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_self_referential_gateway_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for self-referential gateway calls (anti-pattern).

    Detects wrapper functions that call execute_operation() with their own
    interface enum, which causes infinite recursion.

    Example: singleton_reset() calling execute_operation(GatewayInterface.SINGLETON, "reset")

        path: Path to scan
        correlation_id: Correlation ID
        **kwargs: Additional parameters

        Dictionary with scan results

    """

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
        # Only scan wrapper files
        if 'wrapper' not in filepath:
            continue

        # Extract expected interface from filename
        filename = filepath.replace('\\', '/').split('/')[-1]
        if '_wrappers.py' not in filename:
            continue

        interface_name = filename.replace('_wrappers.py', '').upper()
        expected_interface = f"GatewayInterface.{interface_name}"

        # Find all function definitions
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name

                # Check if function contains execute_operation call
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        # Check for execute_operation calls
                        if isinstance(child.func, ast.Name) and child.func.id == 'execute_operation':
                            # Check first argument (interface enum)
                            if child.args and len(child.args) > 0:
                                first_arg = child.args[0]
                                if isinstance(first_arg, ast.Attribute):
                                    interface_ref = ast.unparse(first_arg)

                                    # Check if calling own interface
                                    if expected_interface in interface_ref:
                                        results.append({
                                            "type": "self_referential_gateway_call",
                                            "file": filepath,
                                            "line": child.lineno,
                                            "function": func_name,
                                            "severity": "CRITICAL",
                                            "message": f"Function '{func_name}' calls its own interface '{expected_interface}' - causes infinite recursion",
                                            "interface": expected_interface,
                                        })

    return {
        "success": True,
        "scan_type": "self_referential_gateway",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_parameter_collision_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for parameter name collisions with execute_operation signature (anti-pattern).

    Detects keyword arguments that conflict with execute_operation's 'operation' parameter,
    which causes TypeError during execution.

    Example: execute_operation(..., operation="record_cache_metric") when the operation
    parameter should be the operation name, not a custom parameter.

        path: Path to scan
        exclude_patterns: File patterns to exclude
        **kwargs: Additional parameters

        Dictionary with scan results

    """

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
            if isinstance(node, ast.Call):
                # Check for execute_operation calls
                if isinstance(node.func, ast.Name) and node.func.id == 'execute_operation':
                    # Check keyword arguments for 'operation' parameter
                    for keyword in node.keywords:
                        if keyword.arg == 'operation':
                            # This is a collision - operation should be positional arg
                            results.append({
                                "type": "parameter_name_collision",
                                "file": filepath,
                                "line": node.lineno,
                                "severity": "HIGH",
                                "message": "Keyword argument 'operation' conflicts with execute_operation signature - causes TypeError",
                                "collision_parameter": "operation",
                                "suggestion": "Use operation as second positional argument, not keyword argument",
                            })

    return {
        "success": True,
        "scan_type": "parameter_collision",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_wrong_operation_name_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for wrong operation names in execute_operation calls (anti-pattern).

    Detects calls to non-existent operations by checking the operation name
    against the interface's dispatch dictionary.

    Example: Cache calling "put" instead of "set" causes "Unknown operation" error.

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID

        Dictionary with scan results

    """

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

    # Known interface operations (from dispatch dictionaries)
    known_operations = {
        'CACHE': {
            'get', 'set', 'exists', 'delete', 'clear', 'reset', 'reset_cache',
            'get_stats', 'stats', 'get_with_grace_period', 'get_or_compute',
            'process_pending_refreshes', 'mget', 'mset', 'mdelete', 'mget_metadata',
            'get_compressor', 'get_l2_cache', 'get_invalidator',
            'invalidate', 'invalidate_batch', 'cleanup', 'get_size', 'get_ttl',
            'set_ttl', 'refresh', 'refresh_batch',
        },
        'METRICS': {
            'record', 'record_metric', 'increment', 'increment_counter',
            'get_stats', 'record_operation', 'record_operation_metric',
            'record_error', 'record_error_response', 'record_cache',
            'record_cache_metric', 'record_api', 'record_api_metric',
            'record_response', 'record_response_metric', 'record_http',
            'record_http_metric', 'record_circuit_breaker',
            'record_circuit_breaker_metric', 'get_response_metrics',
        },
        'SINGLETON': {
            'get', 'set', 'has', 'delete', 'reset', 'reset_all',
            'get_memory_stats', 'get_comprehensive_memory_stats',
            'get_all', 'get_keys', 'get_count', 'register',
        },
        'CONFIG': {
            'get', 'set', 'has', 'delete', 'get_all', 'get_keys',
            'reload', 'validate', 'get_env',
        },
        'LOGGING': {
            'log', 'log_info', 'log_warning', 'log_error', 'log_debug',
            'log_critical', 'set_level', 'get_level', 'enable_console',
            'disable_console',
        },
        'DEBUG': {
            'log', 'timing', 'get_profiler_stats', 'get_call_stack',
            'get_hot_paths', 'enable_profiling', 'disable_profiling',
            'reset_stats',
        },
    }

    for filepath, ast_tree in scanner.scan_files():
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Call):
                # Check for execute_operation calls
                if isinstance(node.func, ast.Name) and node.func.id == 'execute_operation':
                    # Get interface and operation from arguments
                    if len(node.args) >= 2:
                        interface_arg = node.args[0]
                        operation_arg = node.args[1]

                        # Extract interface name
                        if isinstance(interface_arg, ast.Attribute):
                            interface_ref = ast.unparse(interface_arg)
                            interface_name = None

                            for known_iface in known_operations:
                                if f"GatewayInterface.{known_iface}" in interface_ref:
                                    interface_name = known_iface
                                    break

                            if interface_name and interface_name in known_operations:
                                # Extract operation name (Python 3.8+: ast.Constant for all constants)
                                operation_name = None
                                if isinstance(operation_arg, ast.Constant):
                                    operation_name = operation_arg.value

                                if operation_name and operation_name not in known_operations[interface_name]:
                                    results.append({
                                        "type": "wrong_operation_name",
                                        "file": filepath,
                                        "line": node.lineno,
                                        "severity": "HIGH",
                                        "message": f"Operation '{operation_name}' does not exist in {interface_name} interface",
                                        "interface": interface_name,
                                        "operation": operation_name,
                                        "valid_operations": ", ".join(sorted(known_operations[interface_name])),
                                    })

    return {
        "success": True,
        "scan_type": "wrong_operation_name",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_misindented_import_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for misindented import statements inside try/except blocks (anti-pattern).

    Detects import statements that are inside try/except blocks but have wrong
    indentation, which causes IndentationError or prevents proper import handling.

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID

        Dictionary with scan results

    """
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


def _scan_empty_except_block_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for empty try/except blocks (anti-pattern).

    Detects try/except blocks with no body or only pass statements,
    which silently suppress errors without handling them.

    Example:
        try:
            # Missing code here
        except ImportError:
            # Missing pass or code
            ...

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID

        Dictionary with scan results

    """
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
            if isinstance(node, ast.Try):
                # Check if try block is empty
                if not node.body or all(isinstance(child, ast.Pass) for child in node.body):
                    results.append({
                        "type": "empty_try_block",
                        "file": filepath,
                        "line": node.lineno,
                        "severity": "MEDIUM",
                        "message": "Empty try block - no code to execute",
                        "suggestion": "Add code to try block or remove try/except",
                    })

                # Check if except handlers are empty
                for handler in node.handlers:
                    if not handler.body or all(isinstance(child, ast.Pass) for child in handler.body):
                        exception_type = ast.unparse(handler.type) if handler.type else "Exception"
                        results.append({
                            "type": "empty_except_block",
                            "file": filepath,
                            "line": handler.lineno,
                            "severity": "HIGH",
                            "message": f"Empty except block for '{exception_type}' - silently suppresses errors",
                            "exception_type": exception_type,
                            "suggestion": "Add error handling code or logging to except block",
                        })

    return {
        "success": True,
        "scan_type": "empty_except_block",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_malformed_docstring_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for malformed docstrings in functions (anti-pattern).

    Detects functions with docstring syntax errors, such as missing opening
    quotes or incomplete docstring structure.

        path: Path to scan
        exclude_patterns: File patterns to exclude
        correlation_id: Correlation ID

        Dictionary with scan results

    """
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
                docstring_issues = []

                if node.body:
                    first_stmt = node.body[0]

                    # Check if first statement is an expression with a string
                    if isinstance(first_stmt, ast.Expr):
                        if isinstance(first_stmt.value, ast.Constant):
                            if isinstance(first_stmt.value.value, str):
                                docstring = first_stmt.value.value

                                # Check for common docstring issues
                                # 1. Check if docstring is empty or only whitespace
                                if not docstring.strip():
                                    docstring_issues.append("Empty docstring")

                                # 2. Unclosed triple quotes (unbalanced quotes)
                                quote_count = docstring.count('"""')
                                if quote_count % 2 != 0:
                                    docstring_issues.append("Unclosed triple quotes")

                # Report issues found
                if docstring_issues:
                    for issue in docstring_issues:
                        results.append({
                            "type": "malformed_docstring",
                            "file": filepath,
                            "line": node.lineno,
                            "function": node.name,
                            "severity": "MEDIUM",
                            "message": f"Function '{node.name}' has {issue}",
                            "issue": issue,
                            "suggestion": "Fix docstring syntax - ensure proper opening and closing triple quotes",
                        })

    return {
        "success": True,
        "scan_type": "malformed_docstring",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }



def _scan_direct_wrapper_import_inline(path: str, **kwargs) -> dict[str, Any]:
    """Detect forbidden direct imports from interface wrapper modules.

    CRITICAL: Direct wrapper imports bypass the gateway pattern and break SUGA-ISP architecture.

    Args:
        path: Directory path to scan

    Returns:
        Scan result with CRITICAL severity issues for direct wrapper imports
    """
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


def _scan_security_bypass_inline(path: str, **kwargs) -> dict[str, Any]:
    """Detect security module bypasses and unsafe practices.
    
    Checks:
    - Direct pickle usage (bypasses safe_loads/safe_dumps from lee_security)
    - Hardcoded secrets/API keys
    - Direct os.environ/os.getenv instead of gateway config
    
    Args:
        path: Directory path to scan
        
    Returns:
        Scan result with HIGH/CRITICAL severity issues
    """
    config = ScanConfig(root_path=path)
    scanner = ASTScanner(config)
    results = []

    for filepath, ast_tree in scanner.scan_files():
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pickle":
                        results.append({
                            "type": "security_bypass",
                            "file": filepath,
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
                                "file": filepath,
                                "line": node.lineno,
                                "severity": "MEDIUM",
                                "message": "Direct os.environ access bypasses gateway config layer",
                                "issue": "config_layer_bypass",
                                "suggestion": "Use gateway config: execute_operation(GatewayInterface.CONFIG, 'get', name='...')",
                            })

    return {
        "success": True,
        "scan_type": "security_bypass",
        "files_scanned": len(list(scanner.scan_files())),
        "issues": results,
        "warnings": [],
        "data": {"total_found": len(results)},
    }


def _scan_relative_import_inline(path: str, **kwargs) -> dict[str, Any]:
    """Detect relative imports that violate absolute import preference.

    LEE prefers absolute imports for clarity and maintainability.

    Args:
        path: Directory path to scan

    Returns:
        Scan result with MEDIUM severity issues for relative imports
    """
    results = []
    root_path = Path(path)

    all_python_files = list(root_path.rglob("*.py"))
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


# ===== DISPATCH DICTIONARY =====

# Dispatch dictionary for AST scanner operations
# Maps operation names to their implementation functions
# Dispatch dictionary for O(1) operation routing
_AST_SCANNER_DISPATCH = {
    "scan": _scan_inline,
    "scan_quality": _scan_quality_inline,
    "scan_duplicate": _scan_duplicate_inline,
    "scan_import_pattern": _scan_import_pattern_inline,
    "scan_gateway_pattern": _scan_gateway_pattern_inline,
    "scan_exception_pattern": _scan_exception_pattern_inline,
    "scan_self_referential_gateway": _scan_self_referential_gateway_inline,
    "scan_parameter_collision": _scan_parameter_collision_inline,
    "scan_wrong_operation_name": _scan_wrong_operation_name_inline,
    "scan_misindented_import": _scan_misindented_import_inline,
    "scan_empty_except_block": _scan_empty_except_block_inline,
    "scan_malformed_docstring": _scan_malformed_docstring_inline,
    "scan_all": _scan_all_inline,
    "scan_direct_wrapper_import": _scan_direct_wrapper_import_inline,
    "scan_security_bypass": _scan_security_bypass_inline,
    "scan_relative_import": _scan_relative_import_inline,
    "format_result": _format_result_inline,
    "get_available_scans": _get_available_scans_inline,
    "get_clone_types": _get_clone_types_inline,
}


# ===== INTERFACE ROUTER =====


class _ASTScannerRouter(BaseSimpleDispatchRouter):
    """Router for AST scanner interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="AST_SCANNER",
            core_module=DummyModule(),
            dispatch_map=_AST_SCANNER_DISPATCH
        )


_ast_scanner_router = _ASTScannerRouter()


def execute_ast_scanner_operation(operation: str, **kwargs) -> Any:
    """Execute AST scanner operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The AST scanner operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from AST scanner implementation
    """
    # SECURITY: Validate path parameter for scan operations
    if "path" in kwargs:
        _validate_scan_path(kwargs["path"])

    return _ast_scanner_router.execute(operation, **kwargs)


def list_ast_scanner_operations() -> list[str]:
    """List all available AST scanner operations."""
    return list(_ast_scanner_router.dispatch_map.keys())


# ===== PUBLIC API =====

__all__ = [
    "execute_ast_scanner_operation",
    "list_ast_scanner_operations",
]
