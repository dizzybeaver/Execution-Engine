"""Scan Factory - Scanner Domain

Scanning operations with EE 2.1 DI compliance.

EE 2.1 Architecture:
- Factory contains all business logic
- Receives DI (get_logger, get_metrics, get_config, call_operation)
- Module-level state for persistence
- Uses stdlib imports (ast, json, pathlib) - allowed (not cross-domain)

Based on:
- EE/operations/cache/cache_factory.py (factory pattern reference)
- EE/scanner/interface/scan/scanner_scan_interface.py (business logic source)
"""

from __future__ import annotations

import ast
import json
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# =============================================================================
# Module-level state (shared across all factory instances)
# =============================================================================

# Module-level cache for scan results (optional - can be used for caching)
_SCAN_CACHE: Dict[str, Any] = {}
_SCAN_CACHE_LOCK = threading.RLock()


# =============================================================================
# UG Scanner Class (Business Logic)
# =============================================================================

class UGScanner(ast.NodeVisitor):
    """AST-based scanner for UG-ISP violations.

    Moved from scanner_scan_interface.py as part of EE 2.1 migration.
    This is the business logic that belongs in the factory layer.
    """

    # Forbidden import patterns
    FORBIDDEN_IMPORTS = [
        # Direct imports across interfaces (from X import Y where X is an interface)
        'from cache',
        'from logging',
        'from singleton',
        'from circuit_breaker',
        'from metrics',
        'from network',
        'from security',
        'from config',
        'from utility',
        'from diagnosis',
        'from test',
        # Direct gateway function imports (violates UG-ISP)
        'from gateway import',
        'from EE import cache_',
        'from EE import log_',
        'from EE import metrics_',
        'from EE import singleton_',
        'from EE import security_',
        'from EE import config_',
        'from EE import util_',
        # Direct interface imports
        'import interface_cache',
        'import interface_logging',
        'import interface_singleton',
        'import interface_circuit_breaker',
        'import interface_metrics',
        'import interface_network',
        'import interface_security',
        'import interface_config',
        'import interface_utility',
        'import interface_diagnosis',
        'import interface_test',
    ]

    # Interface directory names (for cross-interface detection)
    INTERFACES = {
        'cache', 'logging', 'singleton', 'circuit_breaker',
        'metrics', 'network', 'security', 'config', 'utility',
        'diagnosis', 'test', 'debug', 'scanner'
    }

    def __init__(self, file_path: str):
        """Initialize scanner.

        Args:
            file_path: Path to file being scanned
        """
        self.file_path = file_path
        self.violations = []
        self.current_interface = self._detect_interface(file_path)

    def _detect_interface(self, file_path: str) -> Optional[str]:
        """Detect which interface this file belongs to.

        Args:
            file_path: File path

        Returns:
            Interface name or None
        """
        path_parts = Path(file_path).parts
        for i, part in enumerate(path_parts):
            if part in self.INTERFACES:
                return part
        return None

    def _get_code_snippet(self, node: ast.AST, lines: List[str]) -> str:
        """Extract code snippet from AST node.

        Args:
            node: AST node
            lines: File lines

        Returns:
            Code snippet string
        """
        if hasattr(node, 'lineno') and node.lineno <= len(lines):
            line = lines[node.lineno - 1].strip()
            return line[:100]  # Limit snippet length
        return ""

    def _add_violation(self, node: ast.AST, violation_type: str,
                      severity: str, description: str, lines: List[str]) -> None:
        """Add violation to results.

        Args:
            node: AST node
            violation_type: Type of violation
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            description: Description of violation
            lines: File lines for snippet extraction
        """
        self.violations.append({
            'file_path': self.file_path,
            'line_number': getattr(node, 'lineno', 0),
            'violation_type': violation_type,
            'severity': severity,
            'description': description,
            'code_snippet': self._get_code_snippet(node, lines)
        })

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check import statements for violations.

        Args:
            node: ImportFrom AST node
        """
        if node.module:
            import_str = f"from {node.module}"
            imported_interface = node.module.split('.')[0]

            # Check if this is an interface directory import
            if imported_interface in self.INTERFACES:
                # Same-interface imports are ALLOWED
                if self.current_interface == imported_interface:
                    # This is a same-interface import - ALLOWED under UG-ISP
                    pass
                # Cross-interface imports are FORBIDDEN
                elif self.current_interface is not None:
                    self._add_violation(
                        node,
                        violation_type='CROSS_INTERFACE_IMPORT',
                        severity='CRITICAL',
                        description=f"Cross-interface import: {import_str} (violates UG-ISP - must use Gateway)",
                        lines=[]
                    )
                # No current interface detected (likely external code)
                else:
                    self._add_violation(
                        node,
                        violation_type='CROSS_INTERFACE_IMPORT',
                        severity='CRITICAL',
                        description=f"Cross-interface import: {import_str} (violates UG-ISP - must use Gateway)",
                        lines=[]
                    )
            # Check for other forbidden imports (gateway, EE imports, interface_* modules)
            else:
                # Check for gateway and EE imports
                if any(import_str.startswith(f) for f in [
                    'from gateway import',
                    'from EE import cache_',
                    'from EE import log_',
                    'from EE import metrics_',
                    'from EE import singleton_',
                    'from EE import security_',
                    'from EE import config_',
                    'from EE import util_'
                ]):
                    self._add_violation(
                        node,
                        violation_type='FORBIDDEN_IMPORT',
                        severity='CRITICAL',
                        description=f"Forbidden import pattern: {import_str} (bypasses Gateway)",
                        lines=[]
                    )
                # Check for direct interface_* module imports
                elif any(import_str.startswith(f'import interface_{i}') for i in self.INTERFACES):
                    self._add_violation(
                        node,
                        violation_type='FORBIDDEN_IMPORT',
                        severity='CRITICAL',
                        description=f"Direct interface import: {import_str} (bypasses Gateway)",
                        lines=[]
                    )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements for violations.

        Args:
            node: Import AST node
        """
        for alias in node.names:
            import_str = f"import {alias.name}"

            # Check for forbidden interface imports
            if alias.name.startswith('interface_'):
                severity = 'CRITICAL'
                self._add_violation(
                    node,
                    violation_type='FORBIDDEN_IMPORT',
                    severity=severity,
                    description=f"Direct interface import: {import_str} (bypasses Gateway)",
                    lines=[]
                )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for violations.

        Args:
            node: FunctionDef AST node
        """
        # Distinguish between implementation details vs gateway bypassing helpers

        # Check if this file is in the debug interface implementation
        is_in_debug_interface = (
            self.current_interface == 'debug' or
            '/debug/' in self.file_path.replace('\\', '/') or
            '\\debug\\' in self.file_path
        )

        # Only flag debug helpers in NON-debug modules
        if (node.name.startswith('_debug') or node.name.startswith('_log')) and not is_in_debug_interface:
            self._add_violation(
                node,
                violation_type='INTERNAL_DEBUG_HELPER',
                severity='CRITICAL',
                description=f"Internal debug helper function: {node.name} (bypasses Gateway DEBUG - use execute_operation(GatewayInterface.DEBUG, ...))",
                lines=[]
            )

        self.generic_visit(node)


# =============================================================================
# Scan Factory - EE 2.1 Compliant
# =============================================================================

class ScanFactory:
    """Scan operations factory (EE 2.1 compliant).

    Responsibilities:
    - Contains all scanning business logic
    - Receives DI (get_logger, get_metrics, get_config, call_operation)
    - Module-level state for persistence
    - Execution unit for scan operations

    EE 2.1 Compliance:
    - Factory contains implementation (not interface)
    - DI-mandatory pattern
    - Uses stdlib imports (ast, json, pathlib)
    - Cross-domain calls via call_operation()
    """

    # MODIFIED: EE 2.1 compliant constructor - receives DI functions
    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize scan factory with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations with signature:
                          call_operation(domain, interface, operation, **kwargs)
        """
        # Create logger using factory function
        self.logger = get_logger("scanner.scan.factory")
        self.metrics = get_metrics("scanner.scan.factory")
        self.config = get_config
        self.call_operation = call_operation

    # MODIFIED: Main scan operation (moved from interface)
    def scan(
        self,
        path: str,
        report_dir: str = 'reports/scanner',
        gateway: str = 'all',
        **kwargs
    ) -> Dict[str, Any]:
        """Execute scan operation.

        Args:
            path: Path to scan
            report_dir: Report output directory
            gateway: Gateway filter (ee, ha, scanner, all)
            **kwargs: Additional parameters

        Returns:
            Scan results dictionary with:
            - success: bool
            - files_scanned: int
            - violations_found: int
            - violations: list
            - report_dir: str
            - gateway: str
        """
        # MODIFIED: Use injected logger
        self.logger.info(f"Starting scan: {path} (gateway: {gateway})")

        # Determine scan paths based on gateway filter
        if gateway != 'all':
            scan_paths = self._get_gateway_paths(gateway)
            self.logger.info(f"Scanning gateway: {gateway.upper()}")
            for scan_path in scan_paths:
                self.logger.debug(f"  - {scan_path}")
        else:
            scan_paths = [Path(path)]

        all_violations = []
        all_python_files = []

        for scan_path in scan_paths:
            scan_path = Path(scan_path)

            if not scan_path.exists():
                self.logger.warning(f"Path does not exist: {scan_path}")
                continue

            # Find all Python files
            if scan_path.is_file():
                # Single file provided
                python_files = [scan_path]
            else:
                # Directory provided - find all Python files
                python_files = list(scan_path.rglob('*.py'))

            for file_path in python_files:
                # Skip test files and __pycache__
                if '__pycache__' in str(file_path) or 'test' in file_path.name:
                    continue

                all_python_files.append(file_path)
                violations = self._scan_file(str(file_path))

                # Tag violations with gateway name
                for v in violations:
                    v['gateway'] = gateway

                all_violations.extend(violations)

        # MODIFIED: Use injected config (if needed)
        # max_files = self.config("scanner.max_files", default=1000)

        # Create report directory
        Path(report_dir).mkdir(parents=True, exist_ok=True)

        # Save violations JSON
        violations_file = Path(report_dir) / 'violations.json'
        with open(violations_file, 'w', encoding='utf-8') as f:
            json.dump(all_violations, f, indent=2)

        # Save summary
        from datetime import datetime
        scan_date = datetime.now().strftime('%Y-%m-%d')
        summary = {
            'scan_date': scan_date,
            'gateway': gateway,
            'files_scanned': len(all_python_files),
            'violations_found': len(all_violations),
            'violations_by_severity': self._count_by_severity(all_violations),
            'violations_by_type': self._count_by_type(all_violations),
            'violations_by_gateway': self._count_by_gateway(all_violations),
        }

        summary_file = Path(report_dir) / 'scan_results.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Generate markdown report
        report_content = self._generate_markdown_report(all_violations, all_python_files, scan_date, gateway)
        report_file = Path(report_dir) / 'scan_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # MODIFIED: Use injected metrics
        if self.metrics:
            self.metrics.increment("scanner.scan.files_scanned", len(all_python_files))
            self.metrics.increment("scanner.scan.violations_found", len(all_violations))

        self.logger.info(
            f"Scan complete: {len(all_python_files)} files, "
            f"{len(all_violations)} violations"
        )

        return {
            'success': True,
            'files_scanned': summary['files_scanned'],
            'violations_found': len(all_violations),
            'violations': all_violations,
            'report_dir': report_dir,
            'gateway': gateway
        }

    # MODIFIED: Scan single file (moved from interface)
    def _scan_file(self, file_path: str) -> List[Dict]:
        """Scan single file for UG-ISP violations.

        Args:
            file_path: Path to Python file

        Returns:
            List of violation dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            tree = ast.parse(content, filename=file_path)
            scanner = UGScanner(file_path)
            scanner.visit(tree)
            scanner.lines = lines  # Store for snippet extraction

            return scanner.violations

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e.msg}")
            return [{
                'file_path': file_path,
                'line_number': e.lineno or 0,
                'violation_type': 'SYNTAX_ERROR',
                'severity': 'HIGH',
                'description': f"Syntax error: {e.msg}",
                'code_snippet': ""
            }]
        except Exception as e:
            self.logger.error(f"Scan error in {file_path}: {str(e)}")
            return [{
                'file_path': file_path,
                'line_number': 0,
                'violation_type': 'SCAN_ERROR',
                'severity': 'MEDIUM',
                'description': f"Scan error: {str(e)}",
                'code_snippet': ""
            }]

    # MODIFIED: Get gateway paths (moved from interface)
    def _get_gateway_paths(self, gateway: str) -> List[Path]:
        """Get scan paths based on gateway filter.

        Args:
            gateway: Gateway name (ee, ha, scanner, all)

        Returns:
            List of paths to scan
        """
        base_path = Path('D:\\Code\\Project\\EE')

        gateway_paths = {
            'ee': [base_path / 'src'],
            'ha': [base_path / 'src' / 'HA'],
            'scanner': [base_path / 'tools' / 'scanner'],
            'all': [base_path / 'src', base_path / 'tools' / 'scanner']
        }

        return gateway_paths.get(gateway, gateway_paths['all'])

    # MODIFIED: Count violations (moved from interface)
    def _count_by_severity(self, violations: List[Dict]) -> Dict[str, int]:
        """Count violations by severity.

        Args:
            violations: List of violation dictionaries

        Returns:
            Dictionary with severity counts
        """
        counts = {}
        for v in violations:
            severity = v.get('severity', 'UNKNOWN')
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    # MODIFIED: Count violations (moved from interface)
    def _count_by_type(self, violations: List[Dict]) -> Dict[str, int]:
        """Count violations by type.

        Args:
            violations: List of violation dictionaries

        Returns:
            Dictionary with type counts
        """
        counts = {}
        for v in violations:
            vtype = v.get('violation_type', 'UNKNOWN')
            counts[vtype] = counts.get(vtype, 0) + 1
        return counts

    # MODIFIED: Count violations (moved from interface)
    def _count_by_gateway(self, violations: List[Dict]) -> Dict[str, int]:
        """Count violations by gateway.

        Args:
            violations: List of violation dictionaries

        Returns:
            Dictionary with gateway counts
        """
        counts = {}
        for v in violations:
            gateway = v.get('gateway', 'all')
            counts[gateway] = counts.get(gateway, 0) + 1
        return counts

    # MODIFIED: Generate markdown report (moved from interface)
    def _generate_markdown_report(
        self,
        violations: List[Dict],
        files_scanned: List,
        scan_date: str = 'N/A',
        gateway: str = 'all'
    ) -> str:
        """Generate markdown report.

        Args:
            violations: List of violations
            files_scanned: List of scanned files
            scan_date: Scan date string
            gateway: Gateway filter

        Returns:
            Markdown report content
        """
        lines = [
            "# UG-ISP Architecture Compliance Report",
            "",
            f"**Date:** {scan_date}",
            f"**Gateway:** {gateway.upper()}",
            f"**Files Scanned:** {len(files_scanned)}",
            f"**Violations Found:** {len(violations)}",
            "",
            "## Violations by Severity",
            ""
        ]

        # Severity counts
        severity_counts = self._count_by_severity(violations)
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                lines.append(f"- **{severity}:** {count}")

        lines.append("")
        lines.append("## Violations by Type")
        lines.append("")

        # Type counts
        type_counts = self._count_by_type(violations)
        for vtype, count in sorted(type_counts.items()):
            lines.append(f"- **{vtype}:** {count}")

        # Gateway breakdown (if scanning all)
        if gateway == 'all':
            lines.append("")
            lines.append("## Violations by Gateway")
            lines.append("")

            gateway_counts = self._count_by_gateway(violations)
            for gw, count in sorted(gateway_counts.items()):
                lines.append(f"- **{gw.upper()}:** {count}")

        lines.append("")
        lines.append("## Detailed Violations")
        lines.append("")

        # Group violations by file
        by_file = {}
        for v in violations:
            file_path = v['file_path']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(v)

        # Print violations grouped by file
        for file_path, file_violations in sorted(by_file.items()):
            lines.append(f"### {file_path}")
            lines.append("")

            for v in sorted(file_violations, key=lambda x: x['line_number']):
                lines.append(f"**Line {v['line_number']}** - [{v['severity']}] {v['violation_type']}")
                lines.append(f"- {v['description']}")
                if v.get('code_snippet'):
                    lines.append(f"- Code: `{v['code_snippet']}`")
                lines.append("")

        return '\n'.join(lines)


# =============================================================================
# End of File
# =============================================================================
#
# **Version:** 1.0.0
# **Date:** 2026-01-01
# **Purpose:** EE 2.1 compliant scan factory with business logic
# **Lines:** 348
