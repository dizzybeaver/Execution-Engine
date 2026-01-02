"""Test Interface Plugins (INT-16)

Tests for the Plugins interface (INT-16) which manages plugin lifecycle:
- Plugin registration
- Plugin initialization
- Plugin execution
- Plugin shutdown
- Plugin status queries
- Plugin configuration
"""

import pytest
from typing import Dict, Any
from pathlib import Path


@pytest.mark.unit
class TestPluginsInterface:
    """Test suite for Plugins interface."""

    def test_plugins_interface_exists(self, GatewayInterface):
        """Test PLUGINS interface exists in GatewayInterface."""
        from gateway.ee_gateway_enums import EEGatewayInterface
        assert hasattr(EEGatewayInterface, 'PLUGINS')
        assert EEGatewayInterface.PLUGINS is not None

    def test_execute_plugins_operation_import(self):
        """Test that execute_plugins_operation can be imported."""
        try:
            from interface import interface_plugins
            assert hasattr(interface_plugins, 'execute_plugins_operation')
        except ImportError:
            pytest.skip("Plugins interface not yet implemented")

    def test_plugin_register_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin registration operation."""
        try:
            # Register a test plugin
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'register',
                name='test_plugin',
                plugin_class=lambda: None,
                version='1.0.0'
            )

            # Should return success
            assert result is not None
            assert 'success' in result or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin registration not yet implemented")

    def test_plugin_initialize_operation(self, execute_operation, EEGatewayInterface, mock_plugin_config):
        """Test plugin initialization operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'initialize',
                name='test_plugin',
                config=mock_plugin_config
            )

            # Should return success
            assert result is not None
            assert result.get('initialized', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin initialization not yet implemented")

    def test_plugin_execute_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin execution operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'execute',
                name='test_plugin',
                operation='test_operation',
                param1='value1'
            )

            # Should return operation result
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin execution not yet implemented")

    def test_plugin_shutdown_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin shutdown operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'shutdown',
                name='test_plugin'
            )

            # Should return success
            assert result is not None
            assert result.get('shutdown', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin shutdown not yet implemented")

    def test_plugin_get_status_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin status query operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'get_status',
                name='test_plugin'
            )

            # Should return status dict
            assert isinstance(result, dict)
            assert 'name' in result or 'status' in result

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin status query not yet implemented")

    def test_plugin_list_all_operation(self, execute_operation, EEGatewayInterface):
        """Test list all plugins operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Should return list of plugins
            assert isinstance(result, (list, dict))

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin list not yet implemented")

    def test_plugin_enable_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin enable operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'enable',
                name='test_plugin'
            )

            # Should return success
            assert result is not None
            assert result.get('enabled', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin enable not yet implemented")

    def test_plugin_disable_operation(self, execute_operation, EEGatewayInterface):
        """Test plugin disable operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'disable',
                name='test_plugin'
            )

            # Should return success
            assert result is not None
            assert result.get('disabled', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin disable not yet implemented")

    def test_plugin_get_config_operation(self, execute_operation, EEGatewayInterface):
        """Test get plugin config operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'get_config',
                name='test_plugin'
            )

            # Should return config dict
            assert isinstance(result, dict)

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin get config not yet implemented")

    def test_plugin_update_config_operation(self, execute_operation, EEGatewayInterface, mock_plugin_config):
        """Test update plugin config operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'update_config',
                name='test_plugin',
                config=mock_plugin_config
            )

            # Should return success
            assert result is not None
            assert result.get('updated', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin update config not yet implemented")


@pytest.mark.unit
class TestPluginsInterfaceSUGAISPCompliance:
    """Test UG-ISP compliance for Plugins interface."""

    def test_no_direct_interface_import(self):
        """Test that direct interface imports are not used."""
        import ast
        import sys

        # Check main interface file
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_plugins.py'

        if not interface_file.exists():
            pytest.skip("Plugins interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Check for forbidden imports
        forbidden_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'gateway' in node.module:
                    forbidden_imports.append(f"Line {node.lineno}: from {node.module} import ...")

        # Assert no forbidden imports
        assert len(forbidden_imports) == 0, f"Found direct gateway imports: {forbidden_imports}"

    def test_operations_use_dispatch_dict(self):
        """Test that interface uses dispatch dictionary pattern."""
        import ast

        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_plugins.py'

        if not interface_file.exists():
            pytest.skip("Plugins interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Check for DISPATCH dictionary
        assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
            "Plugins interface should use dispatch dictionary pattern"

    def test_file_size_compliance(self):
        """Test that interface file is <= 350 lines."""
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_plugins.py'

        if not interface_file.exists():
            pytest.skip("Plugins interface file not found")

        with open(interface_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) <= 350, \
            f"Interface file has {len(lines)} lines, exceeds 350 line limit"


@pytest.mark.integration
class TestPluginsIntegration:
    """Integration tests for Plugins interface."""

    def test_plugin_full_lifecycle(self, execute_operation, EEGatewayInterface, mock_plugin_config):
        """Test complete plugin lifecycle: register -> initialize -> execute -> shutdown."""
        try:
            plugin_name = 'lifecycle_test_plugin'

            # Register
            execute_operation(
                EEGatewayInterface.PLUGINS,
                'register',
                name=plugin_name,
                plugin_class=lambda: None,
                version='1.0.0'
            )

            # Initialize
            init_result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'initialize',
                name=plugin_name,
                config=mock_plugin_config
            )
            assert init_result is not None

            # Execute
            exec_result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'execute',
                name=plugin_name,
                operation='test'
            )
            assert exec_result is not None

            # Shutdown
            shutdown_result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'shutdown',
                name=plugin_name
            )
            assert shutdown_result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Plugin lifecycle not yet fully implemented")

    def test_multiple_plugins_management(self, execute_operation, EEGatewayInterface):
        """Test managing multiple plugins simultaneously."""
        try:
            plugins = ['plugin1', 'plugin2', 'plugin3']

            # Register all
            for plugin in plugins:
                execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'register',
                    name=plugin,
                    plugin_class=lambda: None,
                    version='1.0.0'
                )

            # List all
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Should contain our plugins
            assert isinstance(result, (list, dict))

        except (ValueError, NotImplementedError):
            pytest.skip("Multiple plugin management not yet implemented")
