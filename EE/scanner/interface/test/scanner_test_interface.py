"""Test interface router (UG-ISP Router).

Test execution operations.

**CRITICAL UG-ISP COMPLIANCE:**
- ALL configuration access via gateway.execute("config.get")
- NO direct os.environ or os.getenv() calls
- HA functional tests through gateway only
- Lazy function-level imports only

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

import subprocess
import json
from pathlib import Path
from typing import Any, List, Dict


def _test_all(path: str = '.', verbose: bool = False) -> dict:
    """Run all tests using pytest.

    Args:
        path: Path to test directory
        verbose: Enable verbose output

    Returns:
        Test result dict
    """
    test_path = Path(path)

    if not test_path.exists():
        return {
            'success': False,
            'error': f'Test path not found: {path}',
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'duration': 0
        }

    # Build pytest command with JSON output
    cmd = ['pytest', str(test_path), '-v', '--tb=short']

    if verbose:
        cmd.append('-vv')

    try:
        # Run pytest and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout + result.stderr

        # Parse pytest output for results
        tests_passed = output.count('PASSED')
        tests_failed = output.count('FAILED')
        tests_total = tests_passed + tests_failed

        # Check for error summary
        error_summary = []
        if tests_failed > 0:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'FAILED' in line:
                    # Get context around failure
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                    error_summary.append({
                        'test': line.strip(),
                        'context': context
                    })

        return {
            'success': result.returncode == 0,
            'tests_total': tests_total,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed,
            'duration': getattr(result, 'elapsed', 0),
            'errors': error_summary,
            'exit_code': result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Test execution timeout (>300s)',
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'duration': 300
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'duration': 0
        }


def _test_suite(suite_name: str, base_path: str = '.', verbose: bool = False) -> dict:
    """Run specific test suite.

    Args:
        suite_name: Test suite name (directory or file pattern)
        base_path: Base path containing test suites
        verbose: Enable verbose output

    Returns:
        Test result dict
    """
    suite_path = Path(base_path) / suite_name

    if not suite_path.exists():
        return {
            'success': False,
            'error': f'Test suite not found: {suite_path}',
            'suite': suite_name,
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    # Build pytest command for specific suite
    cmd = ['pytest', str(suite_path), '-v', '--tb=short']

    if verbose:
        cmd.append('-vv')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout + result.stderr

        tests_passed = output.count('PASSED')
        tests_failed = output.count('FAILED')
        tests_total = tests_passed + tests_failed

        error_summary = []
        if tests_failed > 0:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'FAILED' in line:
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                    error_summary.append({
                        'test': line.strip(),
                        'context': context
                    })

        return {
            'success': result.returncode == 0,
            'suite': suite_name,
            'tests_total': tests_total,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed,
            'errors': error_summary,
            'exit_code': result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Test execution timeout (>300s)',
            'suite': suite_name,
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'suite': suite_name,
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }


def _test_file(file_path: str, verbose: bool = False) -> dict:
    """Run tests for single file.

    Args:
        file_path: Path to test file
        verbose: Enable verbose output

    Returns:
        Test result dict
    """
    test_file = Path(file_path)

    if not test_file.exists():
        return {
            'success': False,
            'error': f'Test file not found: {file_path}',
            'file': str(test_file),
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    if test_file.suffix != '.py':
        return {
            'success': False,
            'error': f'Not a Python test file: {file_path}',
            'file': str(test_file),
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    cmd = ['pytest', str(test_file), '-v', '--tb=short']

    if verbose:
        cmd.append('-vv')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout + result.stderr

        tests_passed = output.count('PASSED')
        tests_failed = output.count('FAILED')
        tests_total = tests_passed + tests_failed

        error_summary = []
        if tests_failed > 0:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'FAILED' in line:
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                    error_summary.append({
                        'test': line.strip(),
                        'context': context
                    })

        return {
            'success': result.returncode == 0,
            'file': str(test_file),
            'tests_total': tests_total,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed,
            'errors': error_summary,
            'exit_code': result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Test execution timeout (>120s)',
            'file': str(test_file),
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file': str(test_file),
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }


def _test_ha(test_type: str, **kwargs) -> dict:
    """Run HA Gateway functional tests (UG-ISP compliant).

    **CRITICAL UG-ISP COMPLIANCE:**
    - ALL HA configuration via gateway.execute("config.get")
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
        **kwargs: Additional parameters (not currently used)

    Returns:
        Test result dict with success, tests_total, tests_passed, tests_failed
    """
    # Lazy function-level import for gateway
    from gateway import execute

    # **UG-ISP COMPLIANCE:** Get HA configuration via gateway.execute
    # NO direct os.environ access
    ha_enable = execute("config.get", {
        "key": "home_assistant.enable",
        "default": "false"
    })

    # Check if HA is enabled
    if ha_enable != "true" and ha_enable != True:
        return {
            'success': False,
            'error': 'Home Assistant is not enabled. Set home_assistant.enable=true in gateway config.',
            'test_type': f'ha_{test_type}',
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    # Get other HA config via gateway
    ha_url = execute("config.get", {
        "key": "home_assistant.url",
        "default": "http://10.10.10.5:8123"
    })

    ha_token = execute("config.get", {
        "key": "home_assistant.token",
        "default": ""
    })

    ha_test_light = execute("config.get", {
        "key": "home_assistant.test_light",
        "default": "light.joe_s_workbench_light_group"
    })

    ha_test_contact = execute("config.get", {
        "key": "home_assistant.test_contact",
        "default": "binary_sensor.den_living_room_door_sensor_door"
    })

    ha_test_temp = execute("config.get", {
        "key": "home_assistant.test_temp",
        "default": "sensor.den_bedroom_ir_temperature"
    })

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
        return {
            'success': False,
            'error': str(e),
            'test_type': f'ha_{test_type}'
        }


# Dispatch dictionary - O(1) operation routing
_TEST_DISPATCH = {
    # pytest operations
    'all': lambda **kw: _test_all(kw.get('path', '.'), kw.get('verbose', False)),
    'suite': lambda **kw: _test_suite(
        kw.get('suite_name'),
        kw.get('base_path', '.'),
        kw.get('verbose', False)
    ),
    'file': lambda **kw: _test_file(kw.get('file_path'), kw.get('verbose', False)),
    # HA functional test operations
    'ha_connection': lambda **kw: _test_ha('connection', **kw),
    'ha_read_light': lambda **kw: _test_ha('read_light', **kw),
    'ha_light_on': lambda **kw: _test_ha('light_on', **kw),
    'ha_light_off': lambda **kw: _test_ha('light_off', **kw),
    'ha_contact_sensor': lambda **kw: _test_ha('contact_sensor', **kw),
    'ha_temperature_sensor': lambda **kw: _test_ha('temperature_sensor', **kw),
    'ha_list_services': lambda **kw: _test_ha('list_services', **kw),
    'ha_all': lambda **kw: _test_ha('all', **kw),
}


def execute_test_operation(operation: str, **kwargs) -> Any:
    """Route test operation requests.

    Args:
        operation: Operation name (all, suite, file)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown
    """
    if operation not in _TEST_DISPATCH:
        raise ValueError(
            f"Unknown test operation: '{operation}'. "
            f"Valid: {', '.join(_TEST_DISPATCH.keys())}"
        )

    handler = _TEST_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_test_operation']
