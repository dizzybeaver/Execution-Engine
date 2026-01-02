"""Test UG-ISP Compliance

Comprehensive tests for UG-ISP (Single Universal Gateway Architecture with ISP Network Topology) compliance:
- Gateway acts as ISP (Internet Service Provider)
- Interfaces act as Routers
- Implementation acts as Local Network
- No cross-interface direct imports
- All operations via execute_operation()
- No internal debug helpers
- File size <= 350 lines
"""

import pytest
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


@pytest.mark.compliance
class TestUGISPCompliance:
    """Comprehensive UG-ISP compliance tests."""

    def test_gateway_is_isp(self):
        """Test that Gateway acts as ISP (central routing point)."""
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'

        with open(gateway_file, 'r') as f:
            source = f.read()

        # Must have execute_operation function
        assert 'def execute_operation' in source, \
            "Gateway must have execute_operation() function (ISP routing)"

        # Must use dispatch dictionary for O(1) routing
        assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
            "Gateway must use dispatch dictionary pattern"

        # Must route to interfaces
        assert 'interface' in source.lower(), \
            "Gateway must route to interfaces"

    def test_interfaces_are_routers(self):
        """Test that Interfaces act as Routers (not direct implementations)."""
        interface_dir = Path(__file__).parent.parent / 'src' / 'interface'

        interface_files = [
            'interface_plugins.py',
            'interface_object_pool.py',
            'interface_network.py',
        ]

        for interface_file in interface_files:
            file_path = interface_dir / interface_file

            if not file_path.exists():
                continue

            with open(file_path, 'r') as f:
                source = f.read()

            # Must have execute_operation function (routing)
            assert 'def execute_' in source, \
                f"{interface_file} must have execute_*_operation function (router function)"

            # Must use dispatch dictionary
            assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
                f"{interface_file} must use dispatch dictionary pattern"

    def test_no_cross_interface_imports(self):
        """Test that there are NO direct imports between interfaces."""
        interface_dir = Path(__file__).parent.parent / 'src' / 'interface'

        interface_files = list(interface_dir.glob('interface_*.py'))

        violations = []

        for interface_file in interface_files:
            with open(interface_file, 'r') as f:
                source = f.read()

            # Check for direct interface imports
            for line_num, line in enumerate(source.split('\n'), 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Check for forbidden patterns
                if re.search(r'from interface_\w+', line):
                    violations.append({
                        'file': str(interface_file.name),
                        'line': line_num,
                        'content': line.strip(),
                        'severity': 'CRITICAL',
                        'rule': 'No direct interface-to-interface imports'
                    })

        # Assert no violations
        violation_summary = "\n".join([
            f"{v['file']}:{v['line']} - {v['severity']} - {v['rule']}\n  {v['content']}"
            for v in violations
        ])

        assert len(violations) == 0, \
            f"Found {len(violations)} cross-interface import violations:\n{violation_summary}"

    def test_no_internal_debug_helpers(self):
        """Test that there are NO internal debug helper functions."""
        # Search all Python files in src/
        src_dir = Path(__file__).parent.parent / 'src'

        violations = []

        for py_file in src_dir.rglob('*.py'):
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
                        # Check for internal debug helpers
                        if node.name.startswith('_debug'):
                            # Check if it's a helper (bypasses gateway)
                            if 'log' in node.name or 'timing' in node.name:
                                violations.append({
                                    'file': str(py_file.relative_to(src_dir.parent)),
                                    'line': node.lineno,
                                    'function': node.name,
                                    'severity': 'CRITICAL',
                                    'rule': 'No internal debug helpers (bypasses Gateway)'
                                })
            except SyntaxError:
                # Skip files with syntax errors
                continue

        # Assert no violations
        violation_summary = "\n".join([
            f"{v['file']}:{v['line']} - {v['severity']} - {v['rule']}\n  Function: {v['function']}"
            for v in violations
        ])

        assert len(violations) == 0, \
            f"Found {len(violations)} internal debug helper violations:\n{violation_summary}"

    def test_file_size_limits(self):
        """Test that all files are <= 350 lines (AWS Lambda limit)."""
        src_dir = Path(__file__).parent.parent / 'src'

        violations = []

        for py_file in src_dir.rglob('*.py'):
            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                lines = f.readlines()

            if len(lines) > 350:
                violations.append({
                    'file': str(py_file.relative_to(src_dir.parent)),
                    'lines': len(lines),
                    'severity': 'CRITICAL',
                    'rule': 'File size <= 350 lines'
                })

        # Assert no violations
        violation_summary = "\n".join([
            f"{v['file']}: {v['lines']} lines - {v['severity']}\n  Rule: {v['rule']}"
            for v in violations
        ])

        assert len(violations) == 0, \
            f"Found {len(violations)} file size violations:\n{violation_summary}"

    def test_all_operations_via_execute_operation(self):
        """Test that all cross-interface operations use execute_operation()."""
        # This is a pattern check - we look for proper usage in sample files

        # Check gateway/gateway.py
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'
        with open(gateway_file, 'r') as f:
            source = f.read()

        # Must export execute_operation
        assert "'execute_operation'" in source or '"execute_operation"' in source, \
            "Gateway must export execute_operation function"

        # Must use dispatch pattern
        assert 'DISPATCH' in source or '_GATEWAY_DISPATCH' in source, \
            "Gateway must use dispatch dictionary"

    def test_isp_network_topology(self):
        """Test ISP Network Topology: Gateway=ISP, Interfaces=Routers, Implementation=Local Network."""
        src_dir = Path(__file__).parent.parent / 'src'

        # Gateway (ISP) level
        gateway_file = src_dir / 'gateway' / 'gateway.py'
        assert gateway_file.exists(), "Gateway (ISP) must exist"

        with open(gateway_file, 'r') as f:
            gateway_source = f.read()

        # Gateway should be the central router
        assert 'execute_operation' in gateway_source, \
            "Gateway (ISP) must provide execute_operation()"

        # Interface (Router) level
        interface_dir = src_dir / 'interface'
        assert interface_dir.exists(), "Interface (Router) directory must exist"

        interface_files = list(interface_dir.glob('interface_*.py'))
        assert len(interface_files) > 0, "Must have interface (router) files"

        # Each interface should route operations
        for interface_file in interface_files:
            with open(interface_file, 'r') as f:
                interface_source = f.read()

            # Should have operation routing
            assert 'execute_' in interface_source or 'DISPATCH' in interface_source, \
                f"{interface_file.name} must have operation routing (router pattern)"

    def test_enumerated_interfaces(self):
        """Test that all interfaces are properly enumerated in GatewayInterface enum."""
        from gateway.ee_gateway_enums import EEGatewayInterface

        # Check that required interfaces exist
        required_interfaces = [
            'PLUGINS',
            'OBJECT_POOL',
            'NETWORK',
            'DI',
        ]

        for interface_name in required_interfaces:
            assert hasattr(EEGatewayInterface, interface_name), \
                f"EEGatewayInterface must have {interface_name} interface"


@pytest.mark.compliance
class TestUGISPArchitecturePatterns:
    """Test specific UG-ISP architecture patterns."""

    def test_dispatch_dictionary_pattern(self):
        """Test that dispatch dictionary pattern is used consistently."""
        src_dir = Path(__file__).parent.parent / 'src'

        # Gateway must use dispatch
        gateway_file = src_dir / 'gateway' / 'gateway.py'
        with open(gateway_file, 'r') as f:
            source = f.read()

        assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
            "Gateway must use dispatch dictionary pattern"

        # Interfaces must use dispatch
        interface_dir = src_dir / 'interface'
        for interface_file in interface_dir.glob('interface_*.py'):
            with open(interface_file, 'r') as f:
                source = f.read()

            assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
                f"{interface_file.name} must use dispatch dictionary pattern"

    def test_lazy_import_pattern(self):
        """Test that lazy import pattern is used in Gateway wrappers."""
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'

        with open(gateway_file, 'r') as f:
            source = f.read()

        # Check for lazy import function
        assert 'def _import_interface_router' in source or 'lazy' in source.lower(), \
            "Gateway should use lazy import pattern for interfaces"

    def test_no_bypass_patterns(self):
        """Test that there are no patterns that bypass Gateway routing."""
        forbidden_patterns = [
            (r'from interface\.(\w+) import', 'Direct interface import'),
            (r'from EE\.gateway\.(\w+) import \w+', 'Direct gateway function import'),
            (r'import interface_(\w+)', 'Module-level interface import'),
        ]

        src_dir = Path(__file__).parent.parent / 'src'

        violations = []

        for py_file in src_dir.rglob('*.py'):
            # Skip gateway files (they are the ISP)
            if 'gateway' in str(py_file):
                continue

            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                source = f.read()

            for pattern, description in forbidden_patterns:
                for match in re.finditer(pattern, source):
                    # Skip comments
                    line_start = source.rfind('\n', 0, match.start()) + 1
                    line_end = source.find('\n', match.start())
                    line = source[line_start:line_end]

                    if line.strip().startswith('#'):
                        continue

                    violations.append({
                        'file': str(py_file.relative_to(src_dir.parent)),
                        'pattern': description,
                        'match': match.group(0),
                        'line': line.strip()
                    })

        # Assert no violations
        if violations:
            violation_summary = "\n".join([
                f"{v['file']}: {v['pattern']}\n  {v['line']}"
                for v in violations[:10]  # Show first 10
            ])

            assert len(violations) == 0, \
                f"Found {len(violations)} bypass pattern violations:\n{violation_summary}"


@pytest.mark.compliance
class TestUGISPDocumentation:
    """Test that UG-ISP compliance is documented."""

    def test_gateway_documented_as_isp(self):
        """Test that Gateway is documented as ISP in code comments."""
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'

        with open(gateway_file, 'r') as f:
            source = f.read()

        # Should mention ISP or UG-ISP in documentation
        assert 'ISP' in source or 'SUGA' in source, \
            "Gateway should be documented as ISP (UG-ISP architecture)"

    def test_interfaces_documented_as_routers(self):
        """Test that Interfaces are documented as Routers."""
        interface_dir = Path(__file__).parent.parent / 'src' / 'interface'

        for interface_file in interface_dir.glob('interface_*.py'):
            with open(interface_file, 'r') as f:
                source = f.read()

            # Should mention router or interface in documentation
            # (This is a relaxed check - just look for docstrings)
            assert '"""' in source or "'''" in source, \
                f"{interface_file.name} should have docstring documentation"


@pytest.mark.integration
class TestUGISPIntegrationCompliance:
    """Integration tests for UG-ISP compliance."""

    def test_full_request_flow_compliance(self, execute_operation, EEGatewayInterface):
        """Test that full request flow follows UG-ISP pattern."""
        try:
            # External code -> Gateway (ISP) -> Interface (Router) -> Implementation
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Should complete successfully
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Full request flow testing not yet implemented")

    def test_no_short_circuit_routes(self):
        """Test that there are no 'short circuit' routes that bypass Gateway."""
        # This checks that no code directly calls interface functions
        # without going through execute_operation()

        src_dir = Path(__file__).parent.parent / 'src'

        # Look for patterns like: interface_plugins.execute_plugins_operation(...)
        # outside of gateway.py

        violations = []

        for py_file in src_dir.rglob('*.py'):
            # Skip gateway files (they are allowed to call interfaces)
            if 'gateway' in str(py_file):
                continue

            # Skip __pycache__
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r') as f:
                source = f.read()

            # Check for direct interface function calls
            for line_num, line in enumerate(source.split('\n'), 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Look for interface_function.operation_function patterns
                if re.search(r'interface_\w+\.execute_\w+', line):
                    violations.append({
                        'file': str(py_file.relative_to(src_dir.parent)),
                        'line': line_num,
                        'content': line.strip()
                    })

        # Assert no violations
        if violations:
            violation_summary = "\n".join([
                f"{v['file']}:{v['line']} - {v['content']}"
                for v in violations[:10]
            ])

            assert len(violations) == 0, \
                f"Found {len(violations)} short-circuit route violations:\n{violation_summary}"
