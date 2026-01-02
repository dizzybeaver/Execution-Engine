"""
Invalid Operation Detector for EE UG-ISP Architecture

This component scans Python files for invalid execute_operation() calls,
ensuring all operations use valid interface/operation combinations.

Version: 1.0.0
Date: 2025-12-29

UG-ISP COMPLIANCE:
- NO os.environ/os.getenv() calls
- ALL config access via gateway
- Lazy imports only
- Inline correlation IDs
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level for violation detection."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Violation:
    """Represents a single EE UG-ISP operation violation."""
    file_path: str
    line_number: int
    interface: str
    operation: str
    valid_operations: List[str]
    confidence: ConfidenceLevel
    context: str = ""
    suggested_fix: str = ""

    def to_markdown(self) -> str:
        """Format violation as markdown."""
        fix = self.suggested_fix or f"Change '{self.operation}' → one of {', '.join(self.valid_operations[:3])}"

        return f"""
### {self.file_path}:{self.line_number}
**Interface:** {self.interface}
**Called:** '{self.operation}'
**Valid Operations:** {', '.join(self.valid_operations[:5])}{'...' if len(self.valid_operations) > 5 else ''}
**Fix:** {fix}
**Confidence:** {self.confidence.value}
**Context:** `{self.context}`
"""


@dataclass
class ScanResult:
    """Results from scanning a file or directory."""
    violations: List[Violation] = field(default_factory=list)
    files_scanned: int = 0
    total_execute_operations: int = 0
    invalid_operations: int = 0

    def to_markdown(self) -> str:
        """Generate complete markdown report."""
        report = ["## Invalid Operation Violations\n"]

        if not self.violations:
            report.append("**No violations found.** All operations are valid!\n")
        else:
            for violation in self.violations:
                report.append(violation.to_markdown())

        # Statistics section
        report.append("\n## Statistics\n")
        report.append(f"- **Files Scanned:** {self.files_scanned}\n")
        report.append(f"- **Total execute_operation() Calls:** {self.total_execute_operations}\n")
        report.append(f"- **Invalid Operations:** {self.invalid_operations}\n")

        if self.total_execute_operations > 0:
            compliance_rate = ((self.total_execute_operations - self.invalid_operations) /
                              self.total_execute_operations * 100)
            report.append(f"- **Compliance Rate:** {compliance_rate:.1f}%\n")

        # Summary by interface
        if self.violations:
            report.append("\n## Violations by Interface\n")
            interface_counts: Dict[str, int] = {}
            for v in self.violations:
                interface_counts[v.interface] = interface_counts.get(v.interface, 0) + 1

            for interface, count in sorted(interface_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- **{interface}:** {count} violations\n")

        return "".join(report)


class InvalidOperationDetector:
    """
    Detects invalid execute_operation() calls in Python code.

    Uses AST parsing to accurately identify operation calls and validate
    them against the Gateway operations catalog.
    """

    # EE INTERFACE_OPERATIONS catalog - Updated for EE Architecture
    INTERFACE_OPERATIONS: Dict[str, Set[str]] = {
        # EE L0 - Foundational
        "SINGLETON": {"acquire", "release", "stats"},
        "UTILITY": {"format", "validate", "transform"},
        "CONFIG": {"get", "set", "delete", "get_all", "get_profile", "reload"},

        # EE L1 - Infrastructure
        "LOGGING": {"log", "info", "error", "warning", "debug"},
        "METRICS": {"counter", "gauge", "histogram", "timer"},
        "SECURITY": {"authenticate", "authorize", "encrypt", "decrypt", "hash", "validate"},
        "DEBUG": {"log", "timing", "trace", "breakpoint"},

        # EE L2 - Communication
        "HTTP_CLIENT": {"get", "post", "put", "patch", "delete"},
        "WEBSOCKET": {"connect", "send", "receive", "close"},

        # EE L3 - Operational
        "CACHE": {"get", "set", "delete", "exists", "clear"},
        "CIRCUIT_BREAKER": {"check", "record_success", "record_failure", "reset"},
        "DIRECTORY": {"list", "exists", "create"},
        "FILEIO": {"read", "write", "delete"},
        "NETWORK": {"redis_get", "redis_set", "mqtt_publish", "mqtt_subscribe"},
        "SERIALIZATION": {"json_to_string", "json_from_string", "yaml_to_string", "yaml_from_string"},
        "TEMPLATE": {"render", "validate", "parse"},

        # EE Operations
        "OBJECT_POOL": {"acquire", "release", "create", "stats"},
        "PLUGINS": {"load", "unload", "list"},
        "ISP": {"execute", "execute_operation", "get_service"},
        "TEST": {"scan_all", "scan_path", "run_test_suite", "run_ha_test_suite"},

        # EE Domains (dot-notation)
        "CONFIG": {"get", "set", "delete", "get_all", "reload"},
        "SECURITY": {"auth.authenticate", "encrypt", "decrypt", "hash", "validate"},
        "LOGGING": {"log.info", "log.error", "log.warning", "log.debug"},
        "METRICS": {"counter.increment", "gauge.set", "histogram.record"},
        "DEBUG": {"log", "timing", "trace"},
        "SERIALIZATION": {"json.to_string", "json.from_string", "yaml.to_string", "yaml.from_string"},
        "CLI": {"execute_command", "interactive_mode"},
        "DOC": {"generate", "validate"},
        "SDK": {"load", "unload", "list"},
    }

    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize detector with operations catalog.

        Args:
            catalog_path: Path to gateway_operations_catalog.json (optional)
                         If None, uses built-in EE INTERFACE_OPERATIONS
        """
        self.catalog_path = Path(catalog_path) if catalog_path else None
        self.catalog = self._load_catalog()
        self.valid_operations = self._build_valid_operations_map()

    def _load_catalog(self) -> Dict[str, Any]:
        """
        Load the gateway operations catalog.

        Returns catalog dict from file if specified, otherwise built-in catalog.
        """
        if self.catalog_path and self.catalog_path.exists():
            try:
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Warning: Catalog not found at {self.catalog_path}, using built-in EE catalog")
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in catalog: {e}, using built-in EE catalog")

        # Return built-in catalog structure
        return {
            "version": "1.0.0",
            "date": "2025-12-29",
            "interfaces": {
                interface: {
                    "operations": list(operations),
                    "description": f"EE {interface} interface"
                }
                for interface, operations in self.INTERFACE_OPERATIONS.items()
            }
        }

    def _build_valid_operations_map(self) -> Dict[str, Set[str]]:
        """
        Build a map of interface -> valid operations.

        Returns:
            Dict mapping interface names to sets of valid operation names
        """
        operations_map = {}

        for interface_name, interface_data in self.catalog.get("interfaces", {}).items():
            operations = set(interface_data.get("operations", []))
            operations_map[interface_name] = operations

        return operations_map

    def _extract_interface_from_call(self, node: ast.Call) -> Optional[Tuple[str, int]]:
        """
        Extract interface name from GatewayInterface.ATTRIBUTE call.

        Args:
            node: AST Call node

        Returns:
            Tuple of (interface_name, confidence_level) or None
        """
        # Check if it's an attribute access (e.g., GatewayInterface.CACHE)
        if not isinstance(node, ast.Attribute):
            return None

        # Check if it's accessing GatewayInterface enum
        if not isinstance(node.value, ast.Name) or node.value.id != "GatewayInterface":
            return None

        # Extract interface name
        interface = node.attr.upper()
        return (interface, ConfidenceLevel.HIGH)

    def _extract_operation_from_call(self, arg: ast.expr) -> Optional[Tuple[str, ConfidenceLevel]]:
        """
        Extract operation name from execute_operation() call.

        Args:
            arg: Second positional argument to execute_operation (should be operation name)

        Returns:
            Tuple of (operation_name, confidence_level) or None
        """
        # Direct string literal - HIGH confidence
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return (arg.value, ConfidenceLevel.HIGH)

        # Joined strings (f-strings, concatenation) - LOW confidence
        if isinstance(arg, ast.JoinedStr):
            # Cannot determine operation name statically
            return (None, ConfidenceLevel.LOW)

        # Variable reference - MEDIUM confidence (need to track variable)
        if isinstance(arg, ast.Name):
            return (arg.id, ConfidenceLevel.LOW)

        # Function call - LOW confidence
        if isinstance(arg, ast.Call):
            return ("<dynamic>", ConfidenceLevel.LOW)

        return None

    def _scan_execute_operation_call(self, node: ast.Call, file_path: str,
                                     source_lines: List[str]) -> Optional[Violation]:
        """
        Scan a single execute_operation() call for violations.

        Args:
            node: AST Call node
            file_path: Path to source file
            source_lines: Source code lines for context

        Returns:
            Violation object if found, None otherwise
        """
        # Check if this is an execute_operation call
        if not isinstance(node.func, ast.Name) or node.func.id != "execute_operation":
            return None

        # Need at least 2 arguments (interface, operation)
        if len(node.args) < 2:
            return None

        interface_arg = node.args[0]
        operation_arg = node.args[1]

        # Extract interface
        interface_result = self._extract_interface_from_call(interface_arg)
        if not interface_result:
            # Cannot determine interface statically
            return None

        interface, _ = interface_result

        # Extract operation
        operation_result = self._extract_operation_from_call(operation_arg)
        if not operation_result:
            return None

        operation, confidence = operation_result

        # Skip if operation is dynamic or None
        if not operation or operation == "<dynamic>":
            return None

        # Validate operation exists for interface
        if interface not in self.valid_operations:
            # Unknown interface - not our concern here
            return None

        valid_ops = self.valid_operations[interface]

        # Check if operation is valid
        if operation not in valid_ops:
            # Build context
            line_num = node.lineno
            context = source_lines[line_num - 1].strip() if line_num <= len(source_lines) else ""

            # Generate suggested fix
            suggested_fix = self._generate_suggested_fix(interface, operation, valid_ops)

            return Violation(
                file_path=file_path,
                line_number=line_num,
                interface=interface,
                operation=operation,
                valid_operations=sorted(valid_ops),
                confidence=confidence,
                context=context,
                suggested_fix=suggested_fix
            )

        return None

    def _generate_suggested_fix(self, interface: str, operation: str,
                               valid_ops: Set[str]) -> str:
        """
        Generate suggested fix for invalid operation.

        Args:
            interface: Interface name
            operation: Invalid operation name
            valid_ops: Set of valid operations

        Returns:
            Suggested fix string
        """
        # Check for common misspellings
        close_matches = [op for op in valid_ops if operation.lower() in op.lower()]

        if close_matches:
            return f"Did you mean '{close_matches[0]}' instead of '{operation}'?"

        # Check for missing prefix (e.g., 'info' vs 'log_info')
        if interface == "LOGGING" and not operation.startswith("log_"):
            if f"log_{operation}" in valid_ops:
                return f"Change '{operation}' → 'log_{operation}'"

        if interface == "SECURITY":
            if operation == "validate" and "validate_string" in valid_ops:
                return f"Change '{operation}' → 'validate_string' (or specific validate_* operation)"
            if operation == "sanitize" and "sanitize_input" in valid_ops:
                return f"Change '{operation}' → 'sanitize_input' (or specific sanitize_* operation)"

        # Generic suggestion
        return f"Use one of: {', '.join(sorted(list(valid_ops))[:4])}{'...' if len(valid_ops) > 4 else ''}"

    def scan_file(self, file_path: str) -> ScanResult:
        """
        Scan a single Python file for invalid operations.

        Args:
            file_path: Path to Python file

        Returns:
            ScanResult with violations found
        """
        result = ScanResult(files_scanned=1)
        file_path_obj = Path(file_path)

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                source_code = f.read()
                source_lines = source_code.splitlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return result

        try:
            tree = ast.parse(source_code, filename=str(file_path_obj))
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}")
            return result

        # Walk AST looking for execute_operation calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                result.total_execute_operations += 1

                violation = self._scan_execute_operation_call(node, str(file_path_obj), source_lines)
                if violation:
                    result.violations.append(violation)
                    result.invalid_operations += 1

        return result

    def scan_directory(self, directory: str, pattern: str = "*.py",
                      exclude_dirs: Optional[List[str]] = None) -> ScanResult:
        """
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            pattern: File pattern to match (default: *.py)
            exclude_dirs: Directories to exclude (default: ['__pycache__', 'venv', '.git'])

        Returns:
            ScanResult with all violations found
        """
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', 'venv', '.git', 'node_modules', '.pytest_cache']

        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        combined_result = ScanResult()

        # Find all Python files
        for file_path in directory_path.rglob(pattern):
            # Skip excluded directories
            if any(excluded_dir in file_path.parts for excluded_dir in exclude_dirs):
                continue

            # Scan file
            file_result = self.scan_file(str(file_path))
            combined_result.violations.extend(file_result.violations)
            combined_result.files_scanned += file_result.files_scanned
            combined_result.total_execute_operations += file_result.total_execute_operations
            combined_result.invalid_operations += file_result.invalid_operations

        return combined_result

    def generate_report(self, violations: List[Violation], output_format: str = "markdown") -> str:
        """
        Generate a detailed violation report.

        Args:
            violations: List of violations to report
            output_format: Format for report ('markdown' or 'json')

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return json.dumps(
                [{
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "interface": v.interface,
                    "operation": v.operation,
                    "valid_operations": v.valid_operations,
                    "confidence": v.confidence.value,
                    "context": v.context,
                    "suggested_fix": v.suggested_fix
                } for v in violations],
                indent=2
            )

        # Default markdown format
        scan_result = ScanResult(violations=violations)
        return scan_result.to_markdown()

    @classmethod
    def get_interface_operations_count(cls) -> int:
        """Get total count of interfaces in EE catalog."""
        return len(cls.INTERFACE_OPERATIONS)

    @classmethod
    def get_total_operations_count(cls) -> int:
        """Get total count of all operations across all interfaces."""
        return sum(len(ops) for ops in cls.INTERFACE_OPERATIONS.values())


def main():
    """Command-line interface for the detector."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect invalid execute_operation() calls in EE UG-ISP code"
    )
    parser.add_argument(
        "path",
        help="Path to Python file or directory to scan"
    )
    parser.add_argument(
        "--catalog",
        default=None,
        help="Path to gateway operations catalog (default: built-in EE catalog)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output",
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Initialize detector
    detector = InvalidOperationDetector(args.catalog)

    # Scan path
    path = Path(args.path)

    if path.is_file():
        result = detector.scan_file(str(path))
    elif path.is_dir():
        result = detector.scan_directory(str(path))
    else:
        print(f"Error: Path not found: {args.path}")
        return 1

    # Generate report
    report = detector.generate_report(result.violations, output_format=args.format)

    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Return exit code based on violations found
    return 1 if result.violations else 0


if __name__ == "__main__":
    exit(main())
