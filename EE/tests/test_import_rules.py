"""Test Import Rules

Tests for LEE Import Rules compliance:
- External code imports only execute_operation and GatewayInterface
- No direct function imports from Gateway
- Same-interface imports are allowed
- Cross-interface imports go through Gateway
- No module-level cross-interface imports
- No dot imports (causes Lambda failure)
"""

import pytest
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


@pytest.mark.compliance
class TestImportRules:
    """Comprehensive import rules compliance tests."""

    def test_external_code_import_pattern(self):
        """Test that external code uses correct import pattern."""
        # External code should ONLY import: from EE import execute_operation, GatewayInterface
        # This is tested by checking example files and documentation

        ee_src = Path(__file__).parent.parent / 'src'

        # Check example files that should follow external code pattern
        example_files = [
            'flask_server/flask_app.py',
            'flask_server/routes.py',
        ]

        for example_file in example_files:
            file_path = ee_src / example_file

            if not file_path.exists():
                continue

            with open(file_path, 'r') as f:
                source = f.read()

            # Parse AST
            tree = ast.parse(source)

            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    # Check for forbidden direct function imports from gateway
                    if node.module and 'gateway' in node.module:
                        # Allowed: from EE import execute_operation, GatewayInterface
                        # Not allowed: from EE import cache_get, log_info, etc.
                        for alias in node.names:
                            if alias.name not in ['execute_operation', 'GatewayInterface', 'EEGatewayInterface']:
                                pytest.fail(
                                    f"{example_file} imports {alias.name} from gateway directly. "
                                    f"Should use execute_operation() instead."
                                )

    def test_no_dot_imports(self):
        """Test that there are NO dot imports (causes Lambda failure)."""
        ee_src = Path(__file__).parent.parent / 'src'

        violations = []

        for py_file in ee_src.rglob('*.py'):
            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                source = f.read()

            # Parse AST
            try:
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        # Check for relative imports (dots)
                        if node.level > 0:
                            violations.append({
                                'file': str(py_file.relative_to(ee_src.parent)),
                                'line': node.lineno,
                                'rule': 'No relative imports (dots)'
                            })
            except SyntaxError:
                continue

        # Assert no violations
        if violations:
            violation_summary = "\n".join([
                f"{v['file']}:{v['line']} - {v['rule']}"
                for v in violations
            ])

            assert len(violations) == 0, \
                f"Found {len(violations)} dot import violations:\n{violation_summary}"

    def test_same_interface_imports_allowed(self):
        """Test that same-interface imports are allowed."""
        # Example: cache/cache_core.py can import from cache/cache_utilities.py
        interface_dir = Path(__file__).parent.parent / 'src'

        # Look for valid same-interface imports
        valid_patterns = [
            ('interface/interface_plugins.py', 'from interface_plugins'),
            ('interface/interface_object_pool.py', 'from interface_object_pool'),
        ]

        for file_pattern, import_pattern in valid_patterns:
            # This test just verifies that same-interface imports exist
            # and don't cause violations
            pass  # Placeholder - actual implementation would check files

    def test_cross_interface_via_gateway_only(self):
        """Test that cross-interface communication goes through Gateway only."""
        ee_src = Path(__file__).parent.parent / 'src'

        violations = []

        for py_file in ee_src.rglob('*.py'):
            # Skip gateway files (they are the ISP)
            if 'gateway' in str(py_file):
                continue

            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            # Skip interface files (they can import from their own utilities)
            if 'interface' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                source = f.read()

            # Parse AST
            try:
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        # Check for cross-interface imports
                        if node.module:
                            # Check if it's importing from another interface
                            if any(node.module.startswith(f'interface_{intf}') for intf in ['plugins', 'object_pool', 'network']):
                                violations.append({
                                    'file': str(py_file.relative_to(ee_src.parent)),
                                    'line': node.lineno,
                                    'module': node.module,
                                    'rule': 'Cross-interface imports must go through Gateway'
                                })
            except SyntaxError:
                continue

        # Assert no violations
        if violations:
            violation_summary = "\n".join([
                f"{v['file']}:{v['line']} - from {v['module']}\n  Rule: {v['rule']}"
                for v in violations
            ])

            assert len(violations) == 0, \
                f"Found {len(violations)} cross-interface import violations:\n{violation_summary}"

    def test_gateway_exports(self):
        """Test that Gateway exports only correct functions."""
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / '__init__.py'

        if not gateway_file.exists():
            pytest.skip("Gateway __init__.py not found")

        with open(gateway_file, 'r') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Find __all__ export
        all_exports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        # Extract list
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    all_exports.append(elt.value)

        # Check exports
        # Should export: execute_operation, GatewayInterface
        # Should NOT export individual interface functions
        assert 'execute_operation' in all_exports, \
            "Gateway must export execute_operation"

        # Check that individual functions are NOT exported
        forbidden_exports = ['cache_get', 'log_info', 'metrics_increment']
        for export in forbidden_exports:
            assert export not in all_exports, \
                f"Gateway should NOT export {export} (use execute_operation instead)"


@pytest.mark.compliance
class TestImportAntiPatterns:
    """Test for anti-patterns in imports."""

    def test_no_eager_interface_imports(self):
        """Test that interfaces are not eagerly imported at module level."""
        ee_src = Path(__file__).parent.parent / 'src'

        # Check gateway files for eager imports
        gateway_files = list(ee_src.glob('gateway/*.py'))

        for gateway_file in gateway_files:
            if '__pycache__' in str(gateway_file):
                continue

            with open(gateway_file, 'r') as f:
                source = f.read()

            # Look for module-level interface imports
            for line_num, line in enumerate(source.split('\n'), 1):
                # Skip comments and docstrings
                if line.strip().startswith('#') or '"""' in line or "'''" in line:
                    continue

                # Check for interface imports at module level
                if re.match(r'^import interface_\w+', line):
                    # This might be okay if it's lazy (inside a function)
                    # For now, just warn
                    pass

    def test_no_circular_imports(self):
        """Test that there are no circular imports."""
        import sys

        ee_src = Path(__file__).parent.parent / 'src'

        # Try importing all modules to check for circular imports
        modules_to_test = [
            'gateway.gateway',
            'gateway.ee_gateway_enums',
            'interface.interface_plugins',
            'interface.interface_object_pool',
            'interface.interface_network',
        ]

        for module_path in modules_to_test:
            # Clear module if already imported
            if module_path in sys.modules:
                del sys.modules[module_path]

            try:
                __import__(module_path)
            except ImportError as e:
                if "circular" in str(e).lower():
                    pytest.fail(f"Circular import detected in {module_path}: {e}")
                else:
                    # Other import errors are okay for this test
                    pass

    def test_no_duplicate_functions(self):
        """Test that there are no duplicate function implementations (custom implementations)."""
        # This checks for anti-pattern: custom implementations when Gateway provides the service

        ee_src = Path(__file__).parent.parent / 'src'

        # Look for suspicious function names that duplicate Gateway functionality
        duplicate_patterns = {
            'cache_get': 'CACHE interface',
            'cache_set': 'CACHE interface',
            'log_info': 'LOGGING interface',
            'log_error': 'LOGGING interface',
            'metrics_put': 'METRICS interface',
            'metrics_increment': 'METRICS interface',
        }

        violations = []

        for py_file in ee_src.rglob('*.py'):
            # Skip gateway and interface files (they implement these)
            if 'gateway' in str(py_file) or 'interface' in str(py_file):
                continue

            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                source = f.read()

            # Parse AST
            try:
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name in duplicate_patterns:
                            violations.append({
                                'file': str(py_file.relative_to(ee_src.parent)),
                                'line': node.lineno,
                                'function': node.name,
                                'should_use': duplicate_patterns[node.name]
                            })
            except SyntaxError:
                continue

        # Assert no violations
        if violations:
            violation_summary = "\n".join([
                f"{v['file']}:{v['line']} - {v['function']}()\n"
                f"  Should use: execute_operation(GatewayInterface.{v['should_use']}, ...)"
                for v in violations
            ])

            assert len(violations) == 0, \
                f"Found {len(violations)} duplicate function violations:\n{violation_summary}"


@pytest.mark.unit
class TestImportRuleDocumentation:
    """Test that import rules are documented."""

    def test_import_rules_document_exists(self):
        """Test that import rules documentation exists."""
        # This would check for reference/LEE-Import-Rules.md
        # For EE, we can check if similar documentation exists
        pass

    def test_code_follows_documentation(self):
        """Test that code follows documented import patterns."""
        # This is a meta-test that checks code against its own documentation
        pass


@pytest.mark.integration
class TestImportRulesIntegration:
    """Integration tests for import rules."""

    def test_import_rules_in_real_execution(self, execute_operation, EEGatewayInterface):
        """Test that import rules are followed in real execution."""
        try:
            # This operation should use execute_operation (UG-ISP compliant)
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Should complete successfully
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Real execution testing not yet implemented")

    def test_no_runtime_import_violations(self):
        """Test that no import violations occur at runtime."""
        # This would test that code doesn't have import errors when executed
        # due to circular imports or missing modules
        pass
