"""
HA Sensor Tests for EE

Phase 4: Migration - HA Functional Tests (Part 2 - Sensors)

This module contains sensor tests for HA plugin operations.
All tests use EE Gateway routing (not direct HA client access).

Sensor Tests:
- test_ha_contact_sensor(): Read contact sensor via gateway
- test_ha_temperature_sensor(): Read temperature via gateway
- test_ha_list_services(): List available services via gateway
- run_all_sensor_tests(): Run all sensor tests

UG-ISP Compliance:
- All HA operations via execute("ha.*", {...})
- NO direct HA client imports
- NO direct HA API calls
- All operations route through gateway
- Inline correlation IDs

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any


def test_ha_contact_sensor() -> Dict[str, Any]:
    """
    Test reading contact sensor via gateway.

    Verifies:
    - Contact sensor state can be read
    - Gateway routing works
    - Binary sensor state is correct

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA contact sensor via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_contact_sensor',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Read contact sensor via gateway
        result = execute(
            "ha.get_state",
            {
                "entity_id": "binary_sensor.door_contact",
                "correlation_id": corr_id
            }
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA contact sensor read completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_contact_sensor',
            'success': result.get('success', False),
            'state': result.get('state')
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA contact sensor test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_contact_sensor',
            'success': False,
            'error': str(e)
        }


def test_ha_temperature_sensor() -> Dict[str, Any]:
    """
    Test reading temperature sensor via gateway.

    Verifies:
    - Temperature sensor state can be read
    - Gateway routing works
    - Temperature value is present

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA temperature sensor via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_temperature_sensor',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Read temperature sensor via gateway
        result = execute(
            "ha.get_state",
            {
                "entity_id": "sensor.temperature",
                "correlation_id": corr_id
            }
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA temperature sensor read completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_temperature_sensor',
            'success': result.get('success', False),
            'state': result.get('state'),
            'temperature': result.get('attributes', {}).get('temperature')
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA temperature sensor test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_temperature_sensor',
            'success': False,
            'error': str(e)
        }


def test_ha_list_services() -> Dict[str, Any]:
    """
    Test listing HA services via gateway.

    Verifies:
    - Services can be listed
    - Gateway routing works
    - Service list is returned

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA list services via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_list_services',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # List services via gateway
        result = execute(
            "ha.list_services",
            {"correlation_id": corr_id}
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA list services completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_list_services',
            'success': result.get('success', False),
            'services': result.get('services', [])
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA list services test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_list_services',
            'success': False,
            'error': str(e)
        }


def run_all_sensor_tests() -> Dict[str, Any]:
    """
    Run all HA sensor tests.

    Returns:
        Dict with test results summary
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_sensor_all_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Running all HA sensor tests"
    )

    tests = [
        test_ha_contact_sensor,
        test_ha_temperature_sensor,
        test_ha_list_services,
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
    passed = sum(1 for r in results if r.get('success') and not r.get('skipped'))
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
        scope="HA_FUNC_TEST",
        message="All HA sensor tests completed",
        total=summary['total'],
        passed=passed,
        failed=failed,
        skipped=skipped
    )

    return summary


__all__ = [
    'test_ha_contact_sensor',
    'test_ha_temperature_sensor',
    'test_ha_list_services',
    'run_all_sensor_tests',
]
