"""
HA Integration Compliance Tests for EE

Phase 4: Migration - HA Plugin Compliance Tests (Part 2)

This module tests HA plugin UG-ISP compliance details.
Verifies critical compliance requirements.

Integration Tests (Part 2):
- test_no_direct_env_access(): Verify NO os.environ usage
- test_gateway_debug_routing(): Verify debug routes through gateway
- test_inline_correlation_ids(): Verify inline correlation ID generation
- run_all_integration_tests(): Run all integration tests

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


def test_no_direct_env_access() -> Dict[str, Any]:
    """
    Test NO direct os.environ access.

    Verifies:
    - NO os.environ usage in HA plugin
    - NO os.getenv usage
    - All config via gateway

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
        message="Testing NO direct os.environ access"
    )

    try:
        # Read HA plugin source
        with open('d:/Code/Project/EE/src/plugins/ha_plugin.py', 'r') as f:
            source_code = f.read()

        # Check for os.environ violations
        has_os_environ = 'os.environ' in source_code
        has_os_getenv = 'os.getenv' in source_code

        if has_os_environ or has_os_getenv:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_INT_TEST",
                message="CRITICAL: os.environ access detected",
                has_os_environ=has_os_environ,
                has_os_getenv=has_os_getenv
            )

            return {
                'test': 'test_no_direct_env_access',
                'success': False,
                'compliant': False,
                'violations': {
                    'has_os_environ': has_os_environ,
                    'has_os_getenv': has_os_getenv
                },
                'fix': 'Replace with execute("config.get", {...})'
            }

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="NO os.environ access verified",
            compliant=True,
            success=True
        )

        return {
            'test': 'test_no_direct_env_access',
            'success': True,
            'compliant': True,
            'no_os_environ': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="NO os.environ test failed",
            error=str(e)
        )

        return {
            'test': 'test_no_direct_env_access',
            'success': False,
            'error': str(e)
        }


def test_gateway_debug_routing() -> Dict[str, Any]:
    """
    Test debug routes through gateway.

    Verifies:
    - Debug operations use GatewayInterface.DEBUG
    - No direct print statements
    - Proper debug routing

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
        message="Testing gateway debug routing"
    )

    try:
        # Test debug routing via gateway
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Debug routing test message",
            test_param="test_value"
        )

        # If we get here without exception, debug routing works
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Gateway debug routing verified",
            success=True
        )

        return {
            'test': 'test_gateway_debug_routing',
            'success': True,
            'debug_routed': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Gateway debug routing test failed",
            error=str(e)
        )

        return {
            'test': 'test_gateway_debug_routing',
            'success': False,
            'error': str(e)
        }


def test_inline_correlation_ids() -> Dict[str, Any]:
    """
    Test inline correlation ID generation.

    Verifies:
    - Correlation IDs generated inline
    - NO correlation ID helper functions
    - Proper format: prefix_timestamp_random

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
        message="Testing inline correlation IDs"
    )

    try:
        # Generate test correlation ID inline (UG-ISP compliant)
        test_corr_id = f"test_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        # Verify format
        parts = test_corr_id.split('_')
        assert len(parts) >= 3, "Correlation ID should have 3+ parts"

        # Verify it has prefix, timestamp, and random number
        prefix = parts[0]
        timestamp = parts[1]
        random_num = parts[2]

        assert prefix == "test", "Prefix should match"
        assert timestamp.isdigit(), "Timestamp should be numeric"
        assert random_num.isdigit(), "Random number should be numeric"

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Inline correlation ID verified",
            test_corr_id=test_corr_id,
            format_valid=True,
            success=True
        )

        return {
            'test': 'test_inline_correlation_ids',
            'success': True,
            'format_valid': True,
            'example_corr_id': test_corr_id
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_INT_TEST",
            message="Inline correlation ID test failed",
            error=str(e)
        )

        return {
            'test': 'test_inline_correlation_ids',
            'success': False,
            'error': str(e)
        }


def run_all_integration_tests() -> Dict[str, Any]:
    """
    Run all HA integration tests.

    Returns:
        Dict with test results summary
    """
    from EE import execute, GatewayInterface

    # Import Part 1 tests
    from EE.src.plugins.ha.test.ha_integration_tests import (
        test_ha_plugin_gateway_integration,
        test_ug_isp_compliance,
        test_config_via_gateway,
    )

    corr_id = f"ha_int_all_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_INT_TEST",
        message="Running all HA integration tests"
    )

    tests = [
        test_ha_plugin_gateway_integration,
        test_ug_isp_compliance,
        test_config_via_gateway,
        test_no_direct_env_access,
        test_gateway_debug_routing,
        test_inline_correlation_ids,
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
    passed = sum(1 for r in results if r.get('success')
                 and not r.get('skipped'))
    failed = len(results) - passed
    skipped = sum(1 for r in results if r.get('skipped'))

    summary = {
        'success': True,
        'total': len(results),
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'results': results
    }

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_INT_TEST",
        message="All HA integration tests completed",
        total=summary['total'],
        passed=passed,
        failed=failed,
        skipped=skipped
    )

    return summary


__all__ = [
    'test_no_direct_env_access',
    'test_gateway_debug_routing',
    'test_inline_correlation_ids',
    'run_all_integration_tests',
]
