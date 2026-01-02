"""
Parameter Validation Detector for EE UG-ISP Architecture

This component scans Python files for wrong parameter names in execute_operation() calls,
ensuring all operations use correct parameter names according to Gateway specifications.

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


class SeverityLevel(Enum):
    """Severity level for parameter violations."""
    CRITICAL = "CRITICAL"  # Wrong parameter name (e.g., msg= instead of message=)
    HIGH = "HIGH"         # Missing required parameter
    MEDIUM = "MEDIUM"     # Unknown parameter (might be valid context)
    LOW = "LOW"           # Potential issue


@dataclass
class ParameterViolation:
    """Represents a parameter validation violation."""
    file_path: str
    line_number: int
    interface: str
    operation: str
    violation_type: str  # WRONG_PARAMETER_NAME, MISSING_REQUIRED, UNKNOWN_PARAMETER
    parameter_found: Optional[str]
    parameter_expected: Optional[str]
    severity: SeverityLevel
    confidence: ConfidenceLevel
    context: str = ""
    suggested_fix: str = ""
    valid_parameters: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Format violation as markdown."""
        severity_marker = {
            SeverityLevel.CRITICAL: "[CRITICAL]",
            SeverityLevel.HIGH: "[HIGH]",
            SeverityLevel.MEDIUM: "[MEDIUM]",
            SeverityLevel.LOW: "[LOW]"
        }

        marker = severity_marker.get(self.severity, "")

        return f"""
### {self.file_path}:{self.line_number} {marker}
**Type:** {self.violation_type}
**Interface:** {self.interface}
**Operation:** {self.operation}
**Severity:** {self.severity.value}

{f"**Parameter Found:** `{self.parameter_found}=`" if self.parameter_found else ""}
{f"**Should Be:** `{self.parameter_expected}=`" if self.parameter_expected else ""}
{f"**Valid Parameters:** {', '.join(self.valid_parameters[:8])}{'...' if len(self.valid_parameters) > 8 else ''}" if self.valid_parameters else ""}

**Context:**
```python
{self.context}
```

**Fix:**
{self.suggested_fix}

**Confidence:** {self.confidence.value}
"""


@dataclass
class ParameterScanResult:
    """Results from parameter validation scan."""
    violations: List[ParameterViolation] = field(default_factory=list)
    files_scanned: int = 0
    total_execute_operations: int = 0
    total_parameter_violations: int = 0
    violations_by_type: Dict[str, int] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Generate complete markdown report."""
        report = ["## Parameter Validation Violations\n"]

        if not self.violations:
            report.append("**No parameter violations found.** All parameters are correct!\n")
        else:
            for violation in self.violations:
                report.append(violation.to_markdown())

        # Statistics section
        report.append("\n## Statistics\n")
        report.append(f"- **Files Scanned:** {self.files_scanned}\n")
        report.append(f"- **Total execute_operation() Calls:** {self.total_execute_operations}\n")
        report.append(f"- **Parameter Violations:** {self.total_parameter_violations}\n")

        if self.total_execute_operations > 0:
            compliance_rate = ((self.total_execute_operations - self.total_parameter_violations) /
                              self.total_execute_operations * 100)
            report.append(f"- **Parameter Compliance Rate:** {compliance_rate:.1f}%\n")

        # Summary by violation type
        if self.violations_by_type:
            report.append("\n## Violations by Type\n")
            for vtype, count in sorted(self.violations_by_type.items(),
                                      key=lambda x: x[1], reverse=True):
                report.append(f"- **{vtype}:** {count} violations\n")

        return "".join(report)


class ParameterValidator:
    """
    Validates parameter names in execute_operation() calls.

    Uses comprehensive parameter specification database to detect:
    - Wrong parameter names (e.g., msg= instead of message=)
    - Missing required parameters
    - Unknown parameters that might be typos
    """

    # Comprehensive parameter specification database
    # Built from function-map-*.md documentation
    PARAMETER_SPECS: Dict[str, Dict[str, Dict[str, Any]]] = {
        "CACHE": {
            "get": {
                "required": ["key"],
                "optional": ["registry_name", "default"],
                "common_mistakes": {},
                "context_params": ["corr_id", "correlation_id"]
            },
            "set": {
                "required": ["key", "value"],
                "optional": ["ttl", "source_module", "registry_name"],
                "common_mistakes": {},
                "context_params": ["corr_id", "correlation_id"]
            },
            "delete": {
                "required": ["key"],
                "optional": ["registry_name"],
                "common_mistakes": {},
                "context_params": ["corr_id", "correlation_id"]
            },
            "exists": {
                "required": ["key"],
                "optional": ["registry_name"],
                "common_mistakes": {},
                "context_params": ["corr_id", "correlation_id"]
            },
            "clear": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": ["corr_id", "correlation_id"]
            },
            "stats": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            }
        },

        "LOGGING": {
            "info": {
                "required": ["message"],
                "optional": [],  # Any additional kwargs become context
                "common_mistakes": {
                    "msg": "message",
                    "text": "message",
                    "log": "message"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "error": {
                "required": ["message"],
                "optional": ["error"],
                "common_mistakes": {
                    "msg": "message",
                    "err": "error",
                    "text": "message"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "warning": {
                "required": ["message"],
                "optional": [],
                "common_mistakes": {
                    "msg": "message",
                    "text": "message"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "debug": {
                "required": ["message"],
                "optional": [],
                "common_mistakes": {
                    "msg": "message"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "DEBUG": {
            "log": {
                "required": ["correlation_id", "scope", "message"],
                "optional": ["level"],
                "common_mistakes": {
                    "corr_id": "correlation_id",
                    "msg": "message"
                },
                "context_params": []
            },
            "timing": {
                "required": ["correlation_id", "scope", "operation"],
                "optional": [],
                "common_mistakes": {
                    "corr_id": "correlation_id",
                    "op": "operation"
                },
                "context_params": []
            },
            "generate_correlation_id": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            },
            "generate_trace_id": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            },
            "set_trace_context": {
                "required": ["trace_id"],
                "optional": [],  # Additional kwargs become context
                "common_mistakes": {},
                "context_params": []
            }
        },

        "METRICS": {
            "put": {
                "required": ["name", "value"],
                "optional": ["unit", "metric_type", "dimensions"],
                "common_mistakes": {
                    "metric": "name",
                    "metric_name": "name"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "increment": {
                "required": ["name"],
                "optional": ["value"],
                "common_mistakes": {
                    "metric": "name",
                    "metric_name": "name",
                    "count": "value"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "get": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            }
        },

        "SECURITY": {
            "validate_string": {
                "required": ["value"],
                "optional": ["min_length", "max_length", "name"],
                "common_mistakes": {
                    "input": "value",
                    "str": "value",
                    "string": "value"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "validate_email": {
                "required": ["email"],
                "optional": [],
                "common_mistakes": {
                    "email_address": "email",
                    "address": "email"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "sanitize_input": {
                "required": ["input_data"],
                "optional": [],
                "common_mistakes": {
                    "input": "input_data",
                    "data": "input_data",
                    "user_input": "input_data"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "encrypt": {
                "required": ["data", "key"],
                "optional": [],
                "common_mistakes": {
                    "plaintext": "data",
                    "text": "data"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "decrypt": {
                "required": ["encrypted", "key"],
                "optional": [],
                "common_mistakes": {
                    "ciphertext": "encrypted",
                    "data": "encrypted"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "SINGLETON": {
            "get": {
                "required": ["name"],
                "optional": [],
                "common_mistakes": {
                    "key": "name",
                    "instance_name": "name"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "set": {
                "required": ["name", "value"],
                "optional": [],
                "common_mistakes": {
                    "key": "name",
                    "instance": "value"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "register": {
                "required": ["name", "factory"],
                "optional": [],
                "common_mistakes": {
                    "key": "name"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "HTTP": {
            "get": {
                "required": ["url"],
                "optional": ["headers", "timeout", "params"],
                "common_mistakes": {
                    "uri": "url",
                    "endpoint": "url"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "post": {
                "required": ["url", "data"],
                "optional": ["headers", "timeout"],
                "common_mistakes": {
                    "uri": "url",
                    "body": "data",
                    "payload": "data"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "WEBSOCKET": {
            "connect": {
                "required": ["url"],
                "optional": [],
                "common_mistakes": {
                    "uri": "url",
                    "endpoint": "url"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "call_service": {
                "required": ["service_id", "method"],
                "optional": ["message"],
                "common_mistakes": {
                    "service": "service_id",
                    "service_name": "service_id"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "CIRCUIT_BREAKER": {
            "call": {
                "required": ["name", "func"],
                "optional": ["args", "kwargs"],
                "common_mistakes": {
                    "breaker_name": "name",
                    "function": "func",
                    "callable": "func"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "get_state": {
                "required": ["name"],
                "optional": [],
                "common_mistakes": {
                    "breaker_name": "name"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "CONFIG": {
            "get": {
                "required": ["key"],
                "optional": ["default"],
                "common_mistakes": {
                    "name": "key",
                    "parameter": "key"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "set": {
                "required": ["key", "value"],
                "optional": [],
                "common_mistakes": {
                    "name": "key"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "UTILITY": {
            "deep_merge": {
                "required": ["dict1", "dict2"],
                "optional": [],
                "common_mistakes": {
                    "dict": "dict1",
                    "merge_into": "dict1"
                },
                "context_params": ["corr_id", "correlation_id"]
            },
            "hash_string": {
                "required": ["data"],
                "optional": ["algorithm"],
                "common_mistakes": {
                    "input": "data",
                    "string": "data",
                    "text": "data"
                },
                "context_params": ["corr_id", "correlation_id"]
            }
        },

        "DIAGNOSIS": {
            "check_system_health": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            },
            "diagnose_memory": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            },
            "diagnose_imports": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            }
        },

        "TEST": {
            "run_test_suite": {
                "required": [],
                "optional": [],
                "common_mistakes": {},
                "context_params": []
            },
            "run_component_tests": {
                "required": ["component"],
                "optional": [],
                "common_mistakes": {
                    "name": "component",
                    "module": "component"
                },
                "context_params": []
            },
            "benchmark_operation": {
                "required": ["operation"],
                "optional": [],
                "common_mistakes": {
                    "name": "operation",
                    "op": "operation"
                },
                "context_params": []
            }
        }
    }

    def __init__(self):
        """Initialize parameter validator."""
        self.param_specs = self.PARAMETER_SPECS

    def _extract_interface_from_call(self, node: ast.Call) -> Optional[str]:
        """
        Extract interface name from GatewayInterface.ATTRIBUTE call.

        Args:
            node: AST node (should be ast.Attribute)

        Returns:
            Interface name or None
        """
        if not isinstance(node, ast.Attribute):
            return None

        # Check if it's accessing GatewayInterface enum
        if not isinstance(node.value, ast.Name) or node.value.id != "GatewayInterface":
            return None

        # Extract interface name
        return node.attr.upper()

    def _extract_operation_from_call(self, arg: ast.expr) -> Optional[str]:
        """
        Extract operation name from execute_operation() call.

        Args:
            arg: Second positional argument (should be operation name string)

        Returns:
            Operation name or None
        """
        # Direct string literal (Python 3.8+)
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value

        return None

    def _extract_parameters_from_call(self, node: ast.Call) -> Dict[str, str]:
        """
        Extract keyword parameter names and their string values from call.

        Args:
            node: AST Call node

        Returns:
            Dict mapping parameter names to their string values (if available)
        """
        params = {}

        for keyword in node.keywords:
            if keyword.arg:
                # Try to extract string value
                value_str = None
                if isinstance(keyword.value, ast.Constant):
                    value_str = str(keyword.value.value)
                elif isinstance(keyword.value, ast.Name):
                    value_str = f"<{keyword.value.id}>"

                params[keyword.arg] = value_str or "<value>"

        return params

    def _validate_parameters(self, interface: str, operation: str,
                            params: Dict[str, str]) -> List[ParameterViolation]:
        """
        Validate parameters against specification.

        Args:
            interface: Interface name
            operation: Operation name
            params: Dict of parameter names to values

        Returns:
            List of ParameterViolation objects
        """
        violations = []

        # Get specification for this interface+operation
        if interface not in self.param_specs:
            # Unknown interface - skip validation
            return violations

        if operation not in self.param_specs[interface]:
            # Unknown operation - skip validation
            return violations

        spec = self.param_specs[interface][operation]

        # Build list of all valid parameters
        valid_params = set(spec['required'] + spec['optional'] + spec.get('context_params', []))

        # Check each parameter
        for param_name in params.keys():
            # Check if it's a common mistake
            if param_name in spec.get('common_mistakes', {}):
                correct_name = spec['common_mistakes'][param_name]

                violations.append(ParameterViolation(
                    file_path="",  # Will be filled by caller
                    line_number=0,  # Will be filled by caller
                    interface=interface,
                    operation=operation,
                    violation_type="WRONG_PARAMETER_NAME",
                    parameter_found=param_name,
                    parameter_expected=correct_name,
                    severity=SeverityLevel.CRITICAL,
                    confidence=ConfidenceLevel.HIGH,
                    suggested_fix=f"Change `{param_name}=` to `{correct_name}=`",
                    valid_parameters=sorted(valid_params)
                ))

            # Check if it's an unknown parameter (not in required, optional, or context)
            elif param_name not in valid_params:
                # Check if it looks like a typo
                is_typo = any(param_name.lower() in valid.lower() or
                             valid.lower() in param_name.lower()
                             for valid in valid_params)

                if is_typo:
                    violations.append(ParameterViolation(
                        file_path="",
                        line_number=0,
                        interface=interface,
                        operation=operation,
                        violation_type="UNKNOWN_PARAMETER",
                        parameter_found=param_name,
                        parameter_expected=None,
                        severity=SeverityLevel.MEDIUM,
                        confidence=ConfidenceLevel.MEDIUM,
                        suggested_fix=f"Remove or fix parameter `{param_name}=`. Valid parameters: {', '.join(sorted(valid_params)[:5])}",
                        valid_parameters=sorted(valid_params)
                    ))

        # Check for missing required parameters
        for required_param in spec['required']:
            if required_param not in params:
                violations.append(ParameterViolation(
                    file_path="",
                    line_number=0,
                    interface=interface,
                    operation=operation,
                    violation_type="MISSING_REQUIRED_PARAMETER",
                    parameter_found=None,
                    parameter_expected=required_param,
                    severity=SeverityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    suggested_fix=f"Add required parameter `{required_param}=`",
                    valid_parameters=sorted(valid_params)
                ))

        return violations

    def _scan_execute_operation_call(self, node: ast.Call, file_path: str,
                                     source_lines: List[str]) -> List[ParameterViolation]:
        """
        Scan a single execute_operation() call for parameter violations.

        Args:
            node: AST Call node
            file_path: Path to source file
            source_lines: Source code lines for context

        Returns:
            List of ParameterViolation objects
        """
        # Check if this is an execute_operation call
        if not isinstance(node.func, ast.Name) or node.func.id != "execute_operation":
            return []

        # Need at least 2 arguments (interface, operation)
        if len(node.args) < 2:
            return []

        interface_arg = node.args[0]
        operation_arg = node.args[1]

        # Extract interface
        interface = self._extract_interface_from_call(interface_arg)
        if not interface:
            return []

        # Extract operation
        operation = self._extract_operation_from_call(operation_arg)
        if not operation:
            return []

        # Extract parameters
        params = self._extract_parameters_from_call(node)

        # Validate parameters
        violations = self._validate_parameters(interface, operation, params)

        # Fill in file_path and line_number for violations
        line_num = node.lineno
        context = source_lines[line_num - 1].strip() if line_num <= len(source_lines) else ""

        for violation in violations:
            violation.file_path = file_path
            violation.line_number = line_num
            violation.context = context

        return violations

    def scan_file(self, file_path: str) -> ParameterScanResult:
        """
        Scan a single Python file for parameter violations.

        Args:
            file_path: Path to Python file

        Returns:
            ParameterScanResult with violations found
        """
        result = ParameterScanResult(files_scanned=1)
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

                violations = self._scan_execute_operation_call(node, str(file_path_obj), source_lines)
                result.violations.extend(violations)

        # Count violations by type
        for violation in result.violations:
            vtype = violation.violation_type
            result.violations_by_type[vtype] = result.violations_by_type.get(vtype, 0) + 1

        result.total_parameter_violations = len(result.violations)

        return result

    def scan_directory(self, directory: str, pattern: str = "*.py",
                      exclude_dirs: Optional[List[str]] = None) -> ParameterScanResult:
        """
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            pattern: File pattern to match (default: *.py)
            exclude_dirs: Directories to exclude

        Returns:
            ParameterScanResult with all violations found
        """
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', 'venv', '.git', 'node_modules', '.pytest_cache', 'scanner', 'ug_isp_agent_scanner']

        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        combined_result = ParameterScanResult()

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

            # Merge violation type counts
            for vtype, count in file_result.violations_by_type.items():
                combined_result.violations_by_type[vtype] = combined_result.violations_by_type.get(vtype, 0) + count

        combined_result.total_parameter_violations = len(combined_result.violations)

        return combined_result

    def generate_report(self, result: ParameterScanResult, output_format: str = "markdown") -> str:
        """
        Generate a detailed violation report.

        Args:
            result: ParameterScanResult with violations
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
                    "violation_type": v.violation_type,
                    "parameter_found": v.parameter_found,
                    "parameter_expected": v.parameter_expected,
                    "severity": v.severity.value,
                    "confidence": v.confidence.value,
                    "context": v.context,
                    "suggested_fix": v.suggested_fix,
                    "valid_parameters": v.valid_parameters
                } for v in result.violations],
                indent=2
            )

        # Default markdown format
        return result.to_markdown()


def main():
    """Command-line interface for the parameter validator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate parameter names in execute_operation() calls"
    )
    parser.add_argument(
        "path",
        help="Path to Python file or directory to scan"
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
    parser.add_argument(
        "--severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        help="Minimum severity level to report"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = ParameterValidator()

    # Scan path
    path = Path(args.path)

    if path.is_file():
        result = validator.scan_file(str(path))
    elif path.is_dir():
        result = validator.scan_directory(str(path))
    else:
        print(f"Error: Path not found: {args.path}")
        return 1

    # Filter by severity if specified
    if args.severity:
        severity_order = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
            "CRITICAL": 3
        }
        min_severity = severity_order[args.severity]
        result.violations = [
            v for v in result.violations
            if severity_order.get(v.severity.value, 0) >= min_severity
        ]
        result.total_parameter_violations = len(result.violations)

    # Generate report
    report = validator.generate_report(result, output_format=args.format)

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
