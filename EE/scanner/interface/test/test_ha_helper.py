"""HA Test Helper - Test Factory Support Module

Extracted from TestFactory to meet EE 2.1 line count limits.

This module contains HA-specific test logic to keep the main factory
under 400 lines.
"""

from __future__ import annotations
from typing import Any, Callable, Dict


def run_ha_test(
    test_type: str,
    call_operation: Callable[..., Any],
    logger: Any,
) -> Dict:
    """Run HA Gateway functional tests (UG-ISP compliant).

    **CRITICAL UG-ISP COMPLIANCE:**
    - ALL HA configuration via call_operation("config.get")
    - NO direct os.environ or os.getenv() calls
    - Tests execute through HA Gateway exactly like Lambda does
    - Validates full execution path: EE Gateway -> HA Gateway -> Home Assistant

    Test types:
    - connection: Test HA server connectivity (via HA Gateway HEALTH interface)
    - read_light: Read current light state (via HA Gateway DEVICES interface)
    - light_on: Turn light ON (via HA Gateway SERVICES interface)
    - light_off: Turn light OFF (via HA Gateway SERVICES interface)
    - contact_sensor: Read contact sensor state (via HA Gateway DEVICES interface)
    - temperature_sensor: Read temperature sensor (via HA Gateway DEVICES interface)
    - list_services: List all HA services (via HA Gateway SERVICES interface)
    - all: Run all tests

    Args:
        test_type: Type of HA test to run
        call_operation: Callback for cross-domain operations
        logger: Logger instance

    Returns:
        Test result dict with success, tests_total, tests_passed, tests_failed
    """
    logger.debug(f"Running HA test '{test_type}'")

    # **UG-ISP COMPLIANCE:** Get HA configuration via call_operation
    # NO direct os.environ access
    ha_enable = call_operation(
        'ha',  # HA domain
        'config.get',
        key='home_assistant.enable',
        default='false'
    )

    # Check if HA is enabled
    if ha_enable != 'true' and ha_enable != True:
        return {
            'success': False,
            'error': 'Home Assistant is not enabled. Set home_assistant.enable=true in gateway config.',
            'test_type': f'ha_{test_type}',
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    # Get other HA config via gateway
    ha_url = call_operation('ha', 'config.get',
                           key='home_assistant.url',
                           default='http://10.10.10.5:8123')
    ha_token = call_operation('ha', 'config.get',
                             key='home_assistant.token',
                             default='')
    ha_test_light = call_operation('ha', 'config.get',
                                  key='home_assistant.test_light',
                                  default='light.joe_s_workbench_light_group')
    ha_test_contact = call_operation('ha', 'config.get',
                                    key='home_assistant.test_contact',
                                    default='binary_sensor.den_living_room_door_sensor_door')
    ha_test_temp = call_operation('ha', 'config.get',
                                 key='home_assistant.test_temp',
                                 default='sensor.den_bedroom_ir_temperature')

    # Import test module (lazy import)
    import sys
    src_path = 'D:\\Code\\Project\\EE\\src'
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    try:
        from ha.test.ha_functional_tests import HAFunctionalTests
        tests = HAFunctionalTests()

        # Route to specific test
        test_methods = {
            'connection': tests.test_connection,
            'read_light': tests.test_read_light,
            'light_on': tests.test_light_on,
            'light_off': tests.test_light_off,
            'contact_sensor': tests.test_contact_sensor,
            'temperature_sensor': tests.test_temperature_sensor,
            'list_services': tests.test_list_services,
        }

        if test_type == 'all':
            results = tests.run_all_tests()
            return {
                'success': results['failed'] == 0,
                'test_type': 'ha_all',
                'tests_total': results.get('total', 0),
                'tests_passed': results.get('passed', 0),
                'tests_failed': results.get('failed', 0),
                'results': results
            }
        elif test_type in test_methods:
            success = test_methods[test_type]()
            return {
                'success': success,
                'test_type': f'ha_{test_type}',
                'tests_total': 1,
                'tests_passed': 1 if success else 0,
                'tests_failed': 0 if success else 1
            }
        else:
            return {
                'success': False,
                'error': f'Unknown HA test type: {test_type}',
                'test_type': 'ha_unknown'
            }

    except Exception as e:
        logger.error(f"HA test '{test_type}' error: {e}")
        return {
            'success': False,
            'error': str(e),
            'test_type': f'ha_{test_type}'
        }


__all__ = ['run_ha_test']
