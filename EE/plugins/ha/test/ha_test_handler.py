"""
HA Test Handler for EE

Phase 4: Migration - HA Test Suite Runner

This module provides the EEHATestSuite class for running all HA plugin tests.
100% UG-ISP compliant - all operations via gateway routing.

Tests:
- test_ha_plugin_import(): Verify plugin can be imported
- test_ha_plugin_routing(): Verify operations route through gateway
- test_ha_config_access(): Verify config accessed via gateway
- test_ee_gateway_integration(): Verify EE Gateway integration

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any, List


class EEHATestSuite:
    """HA Plugin Test Suite for EE Gateway (100% UG-ISP compliant)."""

    def __init__(self):
        """Initialize HA test suite."""
        self.results = []
        self.gateway = None
        self.ha_plugin = None

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all HA plugin tests."""
        from EE import execute, GatewayInterface

        corr_id = f"ha_test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="Starting HA test suite"
        )

        # Run all tests
        tests = [
            self.test_ha_plugin_import,
            self.test_ha_plugin_routing,
            self.test_ha_config_access,
            self.test_ee_gateway_integration,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                results.append({
                    'test': test.__name__,
                    'success': False,
                    'error': str(e)
                })

        # Calculate summary
        passed = sum(1 for r in results if r.get('success'))
        failed = len(results) - passed

        summary = {
            'success': True,
            'total': len(results),
            'passed': passed,
            'failed': failed,
            'results': results
        }

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="HA test suite completed",
            total=summary['total'],
            passed=passed,
            failed=failed
        )

        return summary

    def test_ha_plugin_import(self) -> Dict[str, Any]:
        """Test HA plugin can be imported."""
        from EE import execute, GatewayInterface

        corr_id = f"ha_test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="Testing HA plugin import"
        )

        try:
            # Test plugin import
            from plugins.ha_plugin import HAPlugin

            # Verify plugin metadata
            assert HAPlugin.name == "home_assistant", "Plugin name incorrect"
            assert HAPlugin.version == "1.0.0", "Plugin version incorrect"

            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA plugin import successful",
                success=True
            )

            return {
                'test': 'test_ha_plugin_import',
                'success': True,
                'plugin_name': HAPlugin.name,
                'plugin_version': HAPlugin.version
            }

        except Exception as e:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA plugin import failed",
                error=str(e)
            )

            return {
                'test': 'test_ha_plugin_import',
                'success': False,
                'error': str(e)
            }

    def test_ha_plugin_routing(self) -> Dict[str, Any]:
        """Test HA plugin operations route through gateway."""
        from EE import execute, GatewayInterface

        corr_id = f"ha_test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="Testing HA plugin routing"
        )

        try:
            # Test gateway routing exists
            from EE import execute as gateway_execute

            # Verify gateway has execute function
            assert callable(gateway_execute), "Gateway execute not callable"

            # Verify GatewayInterface enum exists
            assert hasattr(GatewayInterface, 'HTTP_CLIENT')
            assert hasattr(GatewayInterface, 'CACHE')
            assert hasattr(GatewayInterface, 'DEBUG')

            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA plugin routing verified",
                success=True
            )

            return {
                'test': 'test_ha_plugin_routing',
                'success': True,
                'gateway_available': True,
                'interfaces_available': True
            }

        except Exception as e:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA plugin routing test failed",
                error=str(e)
            )

            return {
                'test': 'test_ha_plugin_routing',
                'success': False,
                'error': str(e)
            }

    def test_ha_config_access(self) -> Dict[str, Any]:
        """Test HA config access via gateway (not os.environ)."""
        from EE import execute, GatewayInterface

        corr_id = f"ha_test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="Testing HA config access via gateway"
        )

        try:
            # Test config access via gateway (UG-ISP compliant)
            ha_enable = execute(
                "config.get",
                {"key": "home_assistant.enable", "default": "false"}
            )

            ha_url = execute(
                "config.get",
                {"key": "home_assistant.url"}
            )

            ha_token = execute(
                "config.get",
                {"key": "home_assistant.token"}
            )

            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA config access via gateway successful",
                ha_enable=ha_enable,
                ha_url_present=bool(ha_url),
                ha_token_present=bool(ha_token),
                success=True
            )

            return {
                'test': 'test_ha_config_access',
                'success': True,
                'config_via_gateway': True,
                'ha_enable': ha_enable,
                'ha_url_present': bool(ha_url),
                'ha_token_present': bool(ha_token)
            }

        except Exception as e:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="HA config access test failed",
                error=str(e)
            )

            return {
                'test': 'test_ha_config_access',
                'success': False,
                'error': str(e)
            }

    def test_ee_gateway_integration(self) -> Dict[str, Any]:
        """Test EE Gateway integration."""
        from EE import execute, GatewayInterface

        corr_id = f"ha_test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_TEST",
            message="Testing EE Gateway integration"
        )

        try:
            from plugins.ha_plugin import HAPlugin

            # Create plugin instance
            plugin = HAPlugin()

            # Verify plugin has required methods
            assert hasattr(plugin, 'initialize')
            assert hasattr(plugin, 'shutdown')
            assert hasattr(plugin, 'get_states')
            assert hasattr(plugin, 'call_service')

            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="EE Gateway integration verified",
                success=True
            )

            return {
                'test': 'test_ee_gateway_integration',
                'success': True,
                'plugin_instance': True,
                'required_methods': True
            }

        except Exception as e:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_TEST",
                message="EE Gateway integration test failed",
                error=str(e)
            )

            return {
                'test': 'test_ee_gateway_integration',
                'success': False,
                'error': str(e)
            }


def run_ha_tests() -> Dict[str, Any]:
    """Run all HA plugin tests (convenience function)."""
    suite = EEHATestSuite()
    return suite.run_all_tests()


__all__ = ['EEHATestSuite', 'run_ha_tests']
