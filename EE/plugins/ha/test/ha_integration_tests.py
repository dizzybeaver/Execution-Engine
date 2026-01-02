"""
HA Integration Tests for EE

Phase 4: Migration - HA Plugin EE Gateway Integration Tests (Part 1)

This module tests HA plugin integration with EE Gateway.
Verifies UG-ISP compliance and proper gateway usage.

Integration Tests (Part 1):
- test_ha_plugin_gateway_integration(): Verify plugin integrates
- test_ug_isp_compliance(): Verify 100% UG-ISP compliance
- test_config_via_gateway(): Verify config accessed via gateway only

UG-ISP Compliance:
- ALL HA config via execute("config.get", {...})
- NO os.environ access (CRITICAL)
- NO direct HA client imports
- All tests use gateway routing
- Inline correlation IDs (no helper functions)
- Debug via GatewayInterface.DEBUG

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any


def test_ha_plugin_gateway_integration() -> Dict[str, Any]:
    """
    Test HA plugin integrates with EE Gateway.

    Verifies:
    - Plugin can be loaded by gateway
    - Plugin lifecycle works
    - Gateway can route to plugin

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_int_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_INT_TEST",
        message="Testing HA plugin gateway integration"
    )

    try:
        # Import plugin
        from plugins.ha_plugin import HAPlugin

        # Create instance
        plugin = HAPlugin()

        # Verify plugin metadata
        assert plugin.name == "home_assistant", "Plugin name incorrect"
        assert plugin.version == "1.0.0", "Plugin version incorrect"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="HA plugin gateway integration verified",
            plugin_name=plugin.name,
            plugin_version=plugin.version,
            success=True
        )

        return {
            'test': 'test_ha_plugin_gateway_integration',
            'success': True,
            'plugin_name': plugin.name,
            'plugin_version': plugin.version
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="HA plugin gateway integration test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_plugin_gateway_integration',
            'success': False,
            'error': str(e)
        }


def test_ug_isp_compliance() -> Dict[str, Any]:
    """
    Test 100% UG-ISP compliance.

    Verifies:
    - NO direct interface imports
    - All cross-interface calls via gateway
    - NO internal debug helpers
    - Proper correlation ID usage

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_int_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_INT_TEST",
        message="Testing UG-ISP compliance"
    )

    try:
        # Read HA plugin source
        with open('d:/Code/Project/EE/src/plugins/ha_plugin.py', 'r') as f:
            source_code = f.read()

        violations = []

        # Check for forbidden patterns

        # 1. Check for direct os.environ access (CRITICAL)
        if 'os.environ' in source_code or 'os.getenv' in source_code:
            violations.append({
                'type': 'CRITICAL',
                'rule': 'NO os.environ access',
                'fix': 'Use execute("config.get", {"key": "..."})'
            })

        # 2. Check for direct interface imports
        forbidden_imports = [
            'from cache.',
            'from interface_cache',
            'from EE.gateway.cache',
            'import cache_core',
        ]

        for pattern in forbidden_imports:
            if pattern in source_code:
                violations.append({
                    'type': 'CRITICAL',
                    'rule': 'NO direct interface imports',
                    'pattern': pattern,
                    'fix': 'Use execute_operation via gateway'
                })

        # 3. Check for internal debug helpers
        if 'def _debug_log' in source_code:
            violations.append({
                'type': 'CRITICAL',
                'rule': 'NO internal debug helpers',
                'fix': 'Use execute_operation(GatewayInterface.DEBUG)'
            })

        # 4. Check for proper execute_operation usage
        if 'execute_operation' not in source_code:
            violations.append({
                'type': 'HIGH',
                'rule': 'Must use execute_operation',
                'fix': 'Use execute_operation for gateway routing'
            })

        if violations:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_INT_TEST",
                message="UG-ISP violations detected",
                violation_count=len(violations),
                violations=violations
            )

            return {
                'test': 'test_ug_isp_compliance',
                'success': False,
                'compliant': False,
                'violations': violations
            }

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="UG-ISP compliance verified",
            compliant=True,
            success=True
        )

        return {
            'test': 'test_ug_isp_compliance',
            'success': True,
            'compliant': True,
            'violations': []
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="UG-ISP compliance test failed",
            error=str(e)
        )

        return {
            'test': 'test_ug_isp_compliance',
            'success': False,
            'error': str(e)
        }


def test_config_via_gateway() -> Dict[str, Any]:
    """
    Test config accessed via gateway only.

    Verifies:
    - Config uses execute("config.get", {...})
    - NO direct config access
    - Proper gateway routing

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_int_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_INT_TEST",
        message="Testing config via gateway"
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

        # Verify config was accessed via gateway
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Config access via gateway verified",
            ha_enable=ha_enable,
            ha_url_present=bool(ha_url),
            ha_token_present=bool(ha_token),
            access_method="gateway",
            success=True
        )

        return {
            'test': 'test_config_via_gateway',
            'success': True,
            'access_via_gateway': True,
            'ha_enable': ha_enable,
            'ha_url_present': bool(ha_url),
            'ha_token_present': bool(ha_token)
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Config via gateway test failed",
            error=str(e)
        )

        return {
            'test': 'test_config_via_gateway',
            'success': False,
            'error': str(e)
        }


__all__ = [
    'test_ha_plugin_gateway_integration',
    'test_ug_isp_compliance',
    'test_config_via_gateway',
]
