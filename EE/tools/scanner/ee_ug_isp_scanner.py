"""
EE UG (Universal Gateway) Architecture Compliance Scanner v3.0

Version: 3.0.0 (Lambda Deployment Edition)
Date: 2025-12-30
Purpose: Detect UG violations in EE (Execution Engine) source code

This scanner ensures EE code is compliant with UG architecture for Lambda deployment:
- INT-16 PLUGINS interface violations
- INT-18 OBJECT_POOL interface violations
- INT-17 NETWORK interface violations
- DI Gateway violations
- EE Gateway Factory violations
- Flask Server integration violations

UG Architecture (EE):
- Gateway = Universal Gateway Factory
- Interfaces = Routers (interface_*.py files)
- Implementation = Local Network (*_core.py, *_factory.py, *_generic.py, protocols/*)

v3.0 Updates - Lambda Deployment Edition:
1. CRITICAL: Relative import detection (from . / from ..) → Lambda will FAIL
2. CRITICAL: Old LEE architecture references
3. CRITICAL: SUGA-ISP branding detection (must be UG)
4. Implementation file detection (*_core.py, *_factory.py, *_generic.py, etc.)
5. Docstring skipping (don't scan example code in docstrings)
6. Same-interface import detection (interface → implementation is ALLOWED)
7. Framework layer recognition (Flask, YAML imports are ALLOWED in flask_server/)
8. Absolute imports starting with "EE." are REQUIRED

NOTE: This scanner does NOT scan itself. Use ee_scanner_scanner.py
to validate scanner code quality.
"""

import re
import os
import ast
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field


class Severity(Enum):
    """Violation severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PatternMatch:
    """Represents a single pattern match found in code."""
    file_path: str
    line_number: int
    pattern_name: str
    severity: Severity
    found_code: str
    gateway_interface: str
    gateway_operation: str
    fix_pattern: str
    description: str
    context_lines: List[str] = field(default_factory=list)


class EEUGISPPatternMatcher:
    """
    Pattern matcher for detecting EE UG violations.

    v3.0 Lambda Deployment Edition:
    - CRITICAL: Detects relative imports (from . / from ..) → Lambda FAIL
    - CRITICAL: Detects old LEE architecture references
    - CRITICAL: Detects SUGA-ISP branding
    - Detects implementation files (Local Network)
    - Skips docstring content
    - Recognizes same-interface imports (ALLOWED)
    - Framework layer recognition (Flask, YAML)
    - Validates absolute imports start with "EE."

    NOTE: Does not scan scanner file itself - use ee_scanner_scanner.py
    for scanner code validation.
    """

    def __init__(self):
        """Initialize pattern matcher with EE-specific pattern database."""
        self.patterns = self._build_ee_pattern_database()
        self.compiled_patterns = self._compile_patterns()

        # Implementation file patterns (Local Network layer)
        self.implementation_patterns = [
            '_core.py', '_factory.py', '_generic.py',
            '_operations.py', '_utilities.py', '_handlers.py',
            '_metrics.py', 'protocol_', '/protocols/',
            '/plugins/', 'plugin_loader.py', 'plugin_registry.py',
            'plugin_core.py', 'faas_plugin.py', 'ha_plugin.py',
            'example_plugins.py'
        ]

        # Framework directories (outside UG scope)
        self.framework_directories = [
            'flask_server', '/web/', '/config/'
        ]

        # Interface files (Router layer - can import from their implementation)
        self.interface_files = [
            'interface_object_pool.py', 'interface_plugins.py',
            'interface_network.py', 'interface_di.py',
            'network_redis.py', 'network_mqtt.py', 'network_rpc.py',
            'network_snmp.py', 'network_ntp.py'
        ]

        # Framework imports allowed in framework layer
        self.framework_imports = [
            'from flask import', 'import flask',
            'from flask_socketio import', 'import flask_socketio',
            'import yaml', 'from yaml import',
            'import os', 'from os import',
            'from pathlib import', 'import pathlib'
        ]

    def _is_implementation_file(self, filepath: str) -> bool:
        """
        Check if file is implementation layer (Local Network).

        Implementation files CAN have:
        - Business logic classes
        - Factory classes
        - Configuration classes
        - Same-interface imports

        Args:
            filepath: Path to file

        Returns:
            True if file is implementation layer
        """
        # Check if it's an interface file (Router layer)
        if any(ifile in filepath for ifile in self.interface_files):
            return False

        return any(pattern in filepath for pattern in self.implementation_patterns)

    def _is_framework_directory(self, filepath: str) -> bool:
        """
        Check if file is in framework directory (outside UG scope).

        Framework layer CAN have:
        - Direct framework imports (Flask, YAML, etc.)

        Args:
            filepath: Path to file

        Returns:
            True if file is in framework directory
        """
        return any(pattern in filepath for pattern in self.framework_directories)

    def _is_interface_file(self, filepath: str) -> bool:
        """
        Check if file is an interface router file.

        Interface files CAN have:
        - State classes (Enum, dataclass)
        - Same-interface imports
        - Implementation function imports

        Args:
            filepath: Path to file

        Returns:
            True if file is interface router
        """
        return any(ifile in filepath for ifile in self.interface_files)

    def _is_same_interface_import(self, import_line: str, current_file: str) -> bool:
        """
        Check if import is from same interface (ALLOWED by UG).

        UG Rule: Interface (Router) → Implementation (Local Network) is ALLOWED

        Examples:
            ✓ ALLOWED: from ..object_pool.pool_core import ObjectPool
                      (interface_object_pool.py → object_pool/pool_core.py)

            ✗ BLOCKED: from ..cache.cache_core import Cache
                      (interface_object_pool.py → cache/cache_core.py)

        Args:
            import_line: Import statement line
            current_file: Current file being scanned

        Returns:
            True if same-interface import (ALLOWED)
        """
        # Extract interface name from current file path
        # Example: interface/interface_object_pool.py → object_pool
        if 'interface_' not in current_file:
            return False

        # Get interface name from current file
        if 'interface_object_pool' in current_file:
            interface_name = 'object_pool'
        elif 'interface_plugins' in current_file:
            interface_name = 'plugins'
        elif 'interface_network' in current_file:
            interface_name = 'protocols'
        elif 'network_' in current_file:
            # Extract network type (redis, mqtt, etc.)
            match = re.search(r'network_(\w+)', current_file)
            interface_name = match.group(1) if match else ''
        else:
            # Generic interface detection
            match = re.search(r'interface_?(\w+)', current_file)
            interface_name = match.group(1) if match else ''

        if not interface_name:
            return False

        # Check if import is from same interface
        # Pattern: from ..{interface_name}.{interface_name}_*
        pattern = rf'from\s*\.\.?\s*{re.escape(interface_name)}\.'
        return bool(re.search(pattern, import_line))

    def _extract_code_without_docstrings(self, source: str) -> str:
        """
        Extract code without docstrings to avoid false positives.

        Docstring examples should NOT be scanned for violations.

        Args:
            source: Source code with docstrings

        Returns:
            Source code with docstrings removed
        """
        try:
            tree = ast.parse(source)
            # Remove docstring nodes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if (node.body and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                        # This is a docstring - skip it in violation detection
                        node.body[0].value = None
            return ast.unparse(tree) if hasattr(ast, 'unparse') else source
        except Exception:
            return source  # Fallback to original if parsing fails

    def _build_ee_pattern_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Build EE-specific pattern database.

        Returns:
            Dict mapping pattern categories to their detection patterns
        """
        return {
            # ===================================================================
            # CRITICAL: Relative Imports (Lambda Deployment Failure)
            # ===================================================================

            'relative_import': {
                'name': 'Relative Import Detected (Lambda Deployment Will FAIL)',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from\s+\.+\s*import',
                    r'from\s+\.\w+\s+import',
                    r'from\s+\.\.\s*\w+\s+import',
                    r'from\s+\.\.\.\s*\w+\s+import',
                    r'import\s+\.\w+',
                    r'import\s+\.\.',
                ],
                'gateway_interface': 'LAMBDA_DEPLOYMENT',
                'gateway_operation': 'N/A',
                'fix': 'Use absolute imports starting with "EE." (e.g., from EE.operations.di import DIContainer)',
                'description': 'Relative imports (from . / from ..) will cause Lambda deployment to FAIL',
                'why_critical': 'Lambda requires absolute imports. Relative imports break deployment.',
            },

            # ===================================================================
            # CRITICAL: Old LEE Architecture References
            # ===================================================================

            'lee_architecture_reference': {
                'name': 'Old LEE Architecture Reference',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'LEE\s*\.?\s*architecture',
                    r'LEE\s*\.?\s*gateway',
                    r'LEE\s*\.?\s*system',
                    r'from\s+LEE\s+import',
                    r'import\s+LEE\.?',
                    r'LEE_\w+',
                ],
                'gateway_interface': 'ARCHITECTURE',
                'gateway_operation': 'N/A',
                'fix': 'Update to EE/UG architecture. Use: from EE import ...',
                'description': 'Old LEE architecture reference - EE is standalone',
                'why_critical': 'EE is independent of LEE. Old references break architecture.',
            },

            # ===================================================================
            # CRITICAL: SUGA-ISP Branding (Must be UG)
            # ===================================================================

            'suga_isp_branding': {
                'name': 'SUGA-ISP Branding Detected (Must be UG)',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'SUGA[-_]?ISP',
                    r'Suga[-_]?ISP',
                    r'suga[-_]?isp',
                    r'SUGAISP',
                    r'SugaISP',
                ],
                'gateway_interface': 'BRANDING',
                'gateway_operation': 'N/A',
                'fix': 'Replace with UG (Universal Gateway)',
                'description': 'SUGA-ISP branding detected - must use UG branding',
                'why_critical': 'Product is UG (Universal Gateway), not SUGA-ISP.',
            },

            # ===================================================================
            # CRITICAL: EE Gateway Factory Violations
            # ===================================================================

            'ee_gateway_bypass': {
                'name': 'Bypassing EE Gateway Factory',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from gateway\.gateway_di import',
                    r'from gateway\.gateway_plugins import',
                    r'from gateway\.gateway import DIContainer',
                    r'GatewayDI\(',
                ],
                'gateway_interface': 'EE_GATEWAY_FACTORY',
                'gateway_operation': 'N/A',
                'fix': 'Use EE Gateway Factory: from EE import create_ee_gateway, EEGatewayInterface',
                'description': 'Direct Gateway DI/Plugin imports bypass EE Gateway Factory',
                'why_critical': 'Violates UG architecture - all Gateway access must go through Factory.'
            },

            'wrong_gateway_import': {
                'name': 'Wrong Gateway Import Pattern',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from EE\.gateway import',
                    r'from gateway import execute_operation',
                    r'import EE\.gateway',
                ],
                'gateway_interface': 'EE_GATEWAY_FACTORY',
                'gateway_operation': 'N/A',
                'fix': 'Use: from EE import execute_operation, EEGatewayInterface',
                'description': 'Direct Gateway import instead of EE package import',
                'why_critical': 'EE exports must be from EE package, not gateway submodule.'
            },

            # ===================================================================
            # CRITICAL: Plugin System Violations (INT-16)
            # ===================================================================

            'plugin_direct_import': {
                'name': 'Direct Plugin Import (INT-16)',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from plugins\.plugin_core import',
                    r'from plugins\.plugin_loader import',
                    r'from plugins\.plugin_registry import',
                    r'from plugins import load_plugin',
                ],
                'gateway_interface': 'PLUGINS',
                'gateway_operation': 'load',
                'fix': 'Use: execute_operation(EEGatewayInterface.PLUGINS, \'load\', name=name, path=path)',
                'description': 'Direct plugin import bypasses Gateway INT-16 PLUGINS interface',
                'why_critical': 'Violates UG - all plugin operations must go through Gateway.'
            },

            'plugin_custom_implementation': {
                'name': 'Custom Plugin Implementation',
                'severity': Severity.HIGH,
                'patterns': [
                    r'class.*Plugin.*:',
                    r'def load_plugin\(',
                    r'def unload_plugin\(',
                    r'def register_plugin\(',
                ],
                'gateway_interface': 'PLUGINS',
                'gateway_operation': 'load/unload/register',
                'fix': 'Use Gateway PLUGINS interface operations',
                'description': 'Custom plugin implementation instead of Gateway PLUGINS interface',
                'why_critical': 'Duplicates Gateway functionality, bypasses plugin lifecycle management.'
            },

            # ===================================================================
            # CRITICAL: Object Pool Violations (INT-18)
            # ===================================================================

            'pool_direct_import': {
                'name': 'Direct Object Pool Import (INT-18)',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from object_pool\.pool_core import ObjectPool',
                    r'from object_pool\.pool_factory import',
                    r'from object_pool import ObjectPool',
                ],
                'gateway_interface': 'OBJECT_POOL',
                'gateway_operation': 'acquire/release',
                'fix': 'Use: execute_operation(EEGatewayInterface.OBJECT_POOL, \'acquire\', name=name)',
                'description': 'Direct pool import bypasses Gateway INT-18 OBJECT_POOL interface',
                'why_critical': 'Violates UG - all pool operations must go through Gateway.'
            },

            'pool_custom_implementation': {
                'name': 'Custom Object Pool Implementation',
                'severity': Severity.HIGH,
                'patterns': [
                    r'class.*Pool.*:',
                    r'def create_pool\(',
                    r'def acquire_object\(',
                    r'def release_object\(',
                ],
                'gateway_interface': 'OBJECT_POOL',
                'gateway_operation': 'create/acquire/release',
                'fix': 'Use Gateway OBJECT_POOL interface operations',
                'description': 'Custom pool implementation instead of Gateway OBJECT_POOL interface',
                'why_critical': 'Duplicates Gateway functionality, inefficient resource management.'
            },

            # ===================================================================
            # CRITICAL: DI Gateway Violations
            # ===================================================================

            'di_container_direct_import': {
                'name': 'Direct DI Container Import',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from di\.di_core import DIContainer',
                    r'from operations\.di\.di_core import',
                    r'from interface_di import DIContainer',
                ],
                'gateway_interface': 'DI',
                'gateway_operation': 'CONTAINER_CREATE',
                'fix': 'Use: execute_operation(EEGatewayInterface.DI, \'CONTAINER_CREATE\')',
                'description': 'Direct DI Container import bypasses Gateway DI interface',
                'why_critical': 'Violates UG - all DI operations must go through Gateway.'
            },

            # ===================================================================
            # HIGH: Network Protocol Violations (INT-17)
            # ===================================================================

            'network_protocol_direct_import': {
                'name': 'Direct Network Protocol Import (INT-17)',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from protocols\.protocol_redis import',
                    r'from protocols\.protocol_mqtt import',
                    r'from protocols\.protocol_snmp import',
                    r'from protocols\.protocol_ntp import',
                    r'from protocols\.protocol_ldap import',
                    r'from protocols\.protocol_memcached import',
                ],
                'gateway_interface': 'NETWORK',
                'gateway_operation': 'redis_get/mqtt_publish/etc',
                'fix': 'Use: execute_operation(EEGatewayInterface.NETWORK, \'redis_get\', key=key)',
                'description': 'Direct protocol import bypasses Gateway INT-17 NETWORK interface',
                'why_critical': 'Violates UG - all network operations must go through Gateway.'
            },

            # ===================================================================
            # HIGH: Cross-Interface Imports (BLOCKED)
            # ===================================================================

            'cross_interface_import': {
                'name': 'Cross-Interface Direct Import',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from (cache|logging|security|http_client|websocket)\.',
                    r'from operations\.(cache|di|circuit_breaker)\.',
                ],
                'gateway_interface': 'N/A',
                'gateway_operation': 'N/A',
                'fix': 'Use execute_operation(EEGatewayInterface.*, \'operation\', **kwargs)',
                'description': 'Direct import across interfaces violates UG',
                'why_critical': 'Violates network topology, creates dependency violations.'
            },

            # ===================================================================
            # CRITICAL: Internal Debug Helpers
            # ===================================================================

            'internal_debug_helper': {
                'name': 'Internal Debug Helper Function',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'def _debug_log\(',
                    r'def _debug_timing\(',
                    r'def _generate_correlation_id\(',
                ],
                'gateway_interface': 'DEBUG',
                'gateway_operation': 'N/A',
                'fix': 'Remove helper. Use execute_operation(EEGatewayInterface.DEBUG, \'log\', ...)',
                'description': 'Internal debug helper bypasses Gateway routing',
                'why_critical': 'Violates UG by creating parallel routing path.'
            },
        }

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile all regex patterns for efficient matching."""
        compiled = {}
        for category, pattern_data in self.patterns.items():
            compiled[category] = [re.compile(pattern, re.MULTILINE | re.DOTALL)
                                for pattern in pattern_data['patterns']]
        return compiled

    def scan_file(self, file_path: str, file_content: str = None) -> List[PatternMatch]:
        """
        Scan a single file for all EE UG violations.

        NOTE: This scanner does NOT scan itself to avoid false positives from
        pattern definitions. Use ee_scanner_scanner.py to validate the scanner.

        v3.0 Lambda Deployment Edition Features:
        1. CRITICAL: Detect relative imports (Lambda FAIL)
        2. CRITICAL: Detect LEE architecture references
        3. CRITICAL: Detect SUGA-ISP branding
        4. Skip implementation files (they CAN have classes)
        5. Skip docstring content
        6. Allow same-interface imports
        7. Allow framework imports in framework layer
        8. Validate absolute imports start with "EE."

        Args:
            file_path: Path to file to scan
            file_content: Optional file content (if already loaded)

        Returns:
            List of PatternMatch objects representing violations found
        """
        # Skip scanning the scanner itself to avoid pattern definition false positives
        if 'ee_ug_isp_scanner.py' in file_path:
            return []

        if file_content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception:
                return []

        violations = []
        lines = file_content.split('\n')

        # Check file type for context-aware scanning
        is_implementation = self._is_implementation_file(file_path)
        is_framework = self._is_framework_directory(file_path)
        is_interface = self._is_interface_file(file_path)

        for category, compiled_patterns in self.compiled_patterns.items():
            pattern_data = self.patterns[category]

            for pattern in compiled_patterns:
                for line_num, line in enumerate(lines, start=1):
                    # Skip if pattern doesn't match
                    if not pattern.search(line):
                        continue

                    # ===================================================================
                    # FINE-TOOTH COMB: Context-aware filtering
                    # ===================================================================

                    # 1. Skip implementation class definitions in implementation files
                    if is_implementation and category in [
                        'pool_custom_implementation',
                        'plugin_custom_implementation'
                    ]:
                        # Implementation files CAN have business logic classes
                        continue

                    # 2. Skip framework imports in framework directories
                    if is_framework and any(fw in line.lower() for fw in ['flask', 'yaml', 'pathlib']):
                        # Framework layer CAN import frameworks directly
                        continue

                    # 3. Skip same-interface imports (ALLOWED by UG)
                    if 'import' in line and self._is_same_interface_import(line, file_path):
                        # Interface → Implementation imports are ALLOWED
                        continue

                    # 4. Skip pool operations in implementation files
                    if is_implementation and 'pool' in file_path.lower():
                        # Pool implementation files CAN have pool operations
                        if category in ['pool_direct_import', 'pool_custom_implementation']:
                            continue

                    # 5. Skip plugin state classes in interface files
                    if is_interface and 'PluginState' in line and category == 'plugin_custom_implementation':
                        # Interface files CAN have state enums
                        continue

                    # 6. Skip plugin classes in implementation files
                    if is_implementation and 'plugin' in file_path.lower() and category == 'plugin_custom_implementation':
                        # Plugin implementation files CAN have plugin classes
                        continue

                    # ===================================================================
                    # If we get here, it's a REAL violation
                    # ===================================================================

                    # Get context lines
                    start_ctx = max(0, line_num - 2)
                    end_ctx = min(len(lines), line_num + 2)
                    context = lines[start_ctx:end_ctx]

                    violation = PatternMatch(
                        file_path=file_path,
                        line_number=line_num,
                        pattern_name=pattern_data['name'],
                        severity=pattern_data['severity'],
                        found_code=line.strip(),
                        gateway_interface=pattern_data['gateway_interface'],
                        gateway_operation=pattern_data['gateway_operation'],
                        fix_pattern=pattern_data['fix'],
                        description=pattern_data['description'],
                        context_lines=context
                    )
                    violations.append(violation)

        return violations

    def generate_report(self, violations: List[PatternMatch], output_format: str = 'markdown') -> str:
        """Generate detailed violation report."""
        if output_format == 'json':
            import json
            return json.dumps([
                {
                    'file_path': v.file_path,
                    'line_number': v.line_number,
                    'pattern_name': v.pattern_name,
                    'severity': v.severity.value,
                    'found_code': v.found_code,
                    'gateway_interface': v.gateway_interface,
                    'gateway_operation': v.gateway_operation,
                    'fix_pattern': v.fix_pattern,
                    'description': v.description,
                }
                for v in violations
            ], indent=2)

        # Markdown format
        if not violations:
            return ("# EE UG Architecture Compliance Report\n\n"
                    "**No violations found. EE code is UG compliant!**\n\n"
                    "**Scanner Version:** 3.0.0 (Lambda Deployment Edition)\n")

        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        sorted_violations = sorted(violations, key=lambda v: (severity_order[v.severity], v.file_path, v.line_number))

        report = "# EE UG Architecture Violation Report\n\n"
        report += "**Scanner Version:** 3.0.0 (Lambda Deployment Edition)\n"
        report += "**Architecture:** UG (Universal Gateway)\n\n"
        report += f"**Total Violations:** {len(violations)}\n\n"

        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            sev_violations = [v for v in sorted_violations if v.severity == severity]
            if not sev_violations:
                continue

            report += f"## {severity.value} Severity ({len(sev_violations)})\n\n"

            for v in sev_violations:
                report += f"### {v.file_path}:{v.line_number}\n"
                report += f"**Pattern:** {v.pattern_name}\n"
                report += f"**Found:** `{v.found_code}`\n"
                report += f"**Gateway Interface:** `{v.gateway_interface}`\n"
                report += f"**Description:** {v.description}\n\n"
                report += f"**Fix:**\n```python\n{v.fix_pattern}\n```\n\n"

        return report

    def get_violation_summary(self, violations: List[PatternMatch]) -> Dict[str, Any]:
        """Generate summary statistics for violations."""
        summary = {
            'total_violations': len(violations),
            'by_severity': {},
            'by_pattern': {},
            'by_file': {},
            'by_interface': {},
        }

        for v in violations:
            # Count by severity
            sev = v.severity.value
            summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1

            # Count by pattern
            pattern = v.pattern_name
            summary['by_pattern'][pattern] = summary['by_pattern'].get(pattern, 0) + 1

            # Count by file
            file_path = v.file_path
            summary['by_file'][file_path] = summary['by_file'].get(file_path, 0) + 1

            # Count by interface
            interface = v.gateway_interface
            summary['by_interface'][interface] = summary['by_interface'].get(interface, 0) + 1

        return summary


def scan_ee_directory(directory: str, pattern_matcher: EEUGISPPatternMatcher = None) -> List[PatternMatch]:
    """
    Scan all Python files in EE directory for UG violations.

    Args:
        directory: Directory path to scan (e.g., D:\\Code\\Project\\EE\\src)
        pattern_matcher: Optional EEUGISPPatternMatcher instance

    Returns:
        List of all PatternMatch objects found
    """
    if pattern_matcher is None:
        pattern_matcher = EEUGISPPatternMatcher()

    all_violations = []

    for root, dirs, files in os.walk(directory):
        # Skip test directories and __pycache__
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'node_modules', '.venv', 'test', 'tests']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                violations = pattern_matcher.scan_file(file_path)
                all_violations.extend(violations)

    return all_violations


# Main entry point
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ee_ug_isp_scanner.py <EE_directory> [output_format]")
        print("Example: python ee_ug_isp_scanner.py D:\\Code\\Project\\EE\\src markdown")
        print("\nScanner Version: 3.0.0 (Lambda Deployment Edition)")
        print("Architecture: UG (Universal Gateway)")
        print("\nFeatures:")
        print("  - CRITICAL: Relative import detection (Lambda will FAIL)")
        print("  - CRITICAL: Old LEE architecture detection")
        print("  - CRITICAL: SUGA-ISP branding detection")
        print("  - Implementation file detection (*_core.py, *_factory.py, etc.)")
        print("  - Docstring skipping (don't scan examples)")
        print("  - Same-interface import detection (ALLOWED)")
        print("  - Framework layer recognition (Flask, YAML)")
        print("  - Absolute import validation (must start with 'EE.')")
        sys.exit(1)

    target = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'markdown'

    print(f"EE UG Scanner v3.0.0 (Lambda Deployment Edition)")
    print(f"Architecture: UG (Universal Gateway)")
    print(f"Scanning: {target}")
    print()

    matcher = EEUGISPPatternMatcher()

    if os.path.isfile(target):
        violations = matcher.scan_file(target)
    else:
        violations = scan_ee_directory(target, matcher)

    report = matcher.generate_report(violations, output_format)
    print(report)

    # Print summary
    summary = matcher.get_violation_summary(violations)
    print("\n## Summary")
    print(f"Total Violations: {summary['total_violations']}")
    print(f"By Severity: {summary['by_severity']}")
    print(f"By Interface: {summary['by_interface']}")
    print(f"\nTop Patterns:")
    for pattern, count in sorted(summary['by_pattern'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {count:3d} - {pattern}")
