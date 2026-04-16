"""interface_ast_interfaces.py
Version: 2026-04-11
Purpose: Interface and gateway pattern analysis for AST scanning
License: Apache 2.0

This module provides interface and gateway pattern detection.
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
            """Yield (filepath, ast_tree) tuples for Python files."""
            for py_file in self.root_path.rglob("*.py"):
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
                    ...
                except OSError:
                    ...

        def scan(self, scan_type: ScanType) -> ScanResult:
            """Run scan and return ScanResult."""
            import time
            start_time = time.time()
            return ScanResult(
                scan_type=scan_type,
                success=True,
                duration_seconds=time.time() - start_time,
                files_scanned=0,
                data={},
                issues=[],
                warnings=[],
                graphviz_output=None,
            )

    class ResultFormatter:
        """Formatter for AST scan results in various formats."""
        def to_json(self, result: ScanResult) -> str:
            """Convert scan result to JSON format."""
            return json.dumps(result.to_dict(), indent=2)

        def to_markdown(self, result: ScanResult) -> str:
            """Convert scan result to Markdown format."""
            return f"# AST Scan Report: {result.scan_type.value}"

        def to_txt(self, result: ScanResult) -> str:
            """Convert scan result to plain text format."""
            return str(result.to_dict())

        def to_console(self, result: ScanResult) -> str:
            """Convert scan result to console-friendly format."""
            return self.to_markdown(result)


# ===== CONFIGURATION =====

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
    _CONFIG_AVAILABLE = False
    AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD = 10
    AST_SCANNER_DEFAULT_MAX_COMPLEXITY = 15
    AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD = 3
    AST_SCANNER_DEFAULT_CLONE_TYPE = 3
    AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD = 50
    AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT = 1000

DEFAULT_COMPLEXITY_THRESHOLD = AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD
DEFAULT_MAX_COMPLEXITY = AST_SCANNER_DEFAULT_MAX_COMPLEXITY
DEFAULT_DUPLICATION_THRESHOLD = AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD
DEFAULT_CLONE_TYPE = AST_SCANNER_DEFAULT_CLONE_TYPE
DEFAULT_FUNCTION_LENGTH_THRESHOLD = AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD
DEFAULT_CACHE_SIZE_LIMIT = AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT

DEFAULT_EXCLUDE_PATTERNS = [
    "*/test*.py",
    "*/tests/*",
    "*/__pycache__/*",
    "*/.mypy_cache/*",
]


def validate_scan_path(path: str) -> None:
    """Validate path parameter to prevent directory traversal attacks."""
    if not isinstance(path, str):
        raise TypeError(f"Path must be string, got {type(path).__name__}")
    dangerous_patterns = ['../', '..\\', '%2e%2e', '%252e', '..']
    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            raise ValueError(
                f"Path traversal detected: '{path}' contains '{pattern}'. "
                "Relative paths with '..' are not allowed for security reasons."
            )
    path_obj = Path(path).resolve()
    allowed_bases = [Path('e:/LEE').resolve(), Path('e:/LEE/work').resolve()]
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


def scan_gateway_pattern_inline(
    path: str,
    exclude_patterns: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Scan for self-referential gateway calls (anti-pattern)."""
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
        if 'wrapper' in filepath:
            filename = filepath.replace('\\', '/').split('/')[-1]
            if '_wrappers.py' in filename:
                interface_name = filename.replace('_wrappers.py', '').upper()
                expected_interface = f"GatewayInterface.{interface_name}"
                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr == 'execute_operation':
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


__all__ = [
    "scan_gateway_pattern_inline",
    "validate_scan_path",
    "ASTScanner",
    "ScanConfig",
    "ScanResult",
]
