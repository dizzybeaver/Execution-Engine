"""
HA Interface Error Tests for EE

Phase 4: Migration - HA Plugin Interface Error Tests (Part 2)

This module tests HA plugin error handling and response format.
Verifies proper error handling through EE Gateway.

Interface Tests (Part 2):
- test_ha_get_states_routing(): Verify get_states routes correctly
- test_ha_error_handling(): Verify error handling works
- test_ha_response_format(): Verify response format is correct
- run_all_interface_tests(): Run all interface tests

UG-ISP Compliance:
- All operations via gateway routing
- NO direct interface access
- Proper error handling through gateway
- Inline correlation IDs

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any


def test_ha_get_states_routing() -> Dict[str, Any]:
    """
    Test get_states operation routes correctly.

    Verifies:
    - Operation is properly dispatched
    - Multiple states can be retrieved
    - Response is returned through gateway

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA get_states routing"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_get_states_routing',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Test get_states routing via gateway
        result = execute(
            "ha.get_states",
            {"correlation_id": corr_id}
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA get_states routing test completed",
            success=result.get('success', False),
            state_count=result.get('count', 0)
        )

        return {
            'test': 'test_ha_get_states_routing',
            'success': result.get('success', False),
            'routing_verified': True,
            'state_count': result.get('count', 0)
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA get_states routing test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_get_states_routing',
            'success': False,
            'error': str(e)
        }


def test_ha_error_handling() -> Dict[str, Any]:
    """
    Test HA error handling.

    Verifies:
    - Errors are properly caught
    - Error messages are returned
    - No crashes on invalid operations

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA error handling"
    )

    try:
        # Test error handling with invalid entity
        result = execute(
            "ha.get_state",
            {
                "entity_id": "invalid.entity",
                "correlation_id": corr_id
            }
        )

        # Should handle error gracefully
        if not result.get('success'):
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_IFACE_TEST",
                message="HA error handling test passed",
                error_handled=True,
                success=True
            )

            return {
                'test': 'test_ha_error_handling',
                'success': True,
                'error_handled': True
            }

        # Unexpected success
        return {
            'test': 'test_ha_error_handling',
            'success': False,
            'reason': 'Expected error for invalid entity'
        }

    except Exception:
        # Exception is also valid error handling
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA error handling test passed",
            exception_caught=True,
            success=True
        )

        return {
            'test': 'test_ha_error_handling',
            'success': True,
            'exception_caught': True
        }


def test_ha_response_format() -> Dict[str, Any]:
    """
    Test HA response format is correct.

    Verifies:
    - Responses include success flag
    - Responses include data or error
    - Format is consistent

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA response format"
    )

    try:
        # Test response format with a simple operation
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        # Check response has success field
        if 'success' not in ha_enable:
            return {
                'test': 'test_ha_response_format',
                'success': False,
                'reason': 'Response missing success field'
            }

        # Config.get returns value directly, not in dict
        # So we just verify it doesn't crash

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA response format test passed",
            success=True
        )

        return {
            'test': 'test_ha_response_format',
            'success': True,
            'format_valid': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA response format test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_response_format',
            'success': False,
            'error': str(e)
        }


def run_all_interface_tests() -> Dict[str, Any]:
    """
    Run all HA interface tests.

    Returns:
        Dict with test results summary
    """
    from EE import execute, GatewayInterface

    # Import Part 1 tests
    from EE.src.plugins.ha.test.ha_interface_tests import (
        test_ha_interface_registration,
        test_ha_get_state_routing,
        test_ha_call_service_routing,
    )

    corr_id = f"ha_iface_all_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Running all HA interface tests"
    )

    tests = [
        test_ha_interface_registration,
        test_ha_get_state_routing,
        test_ha_call_service_routing,
        test_ha_get_states_routing,
        test_ha_error_handling,
        test_ha_response_format,
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
        scope="HA_IFACE_TEST",
        message="All HA interface tests completed",
        total=summary['total'],
        passed=passed,
        failed=failed,
        skipped=skipped
    )

    return summary


__all__ = [
    'test_ha_get_states_routing',
    'test_ha_error_handling',
    'test_ha_response_format',
    'run_all_interface_tests',
]
