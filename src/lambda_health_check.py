"""LEE Lambda Health Check Handler

Provides comprehensive health check endpoints for monitoring:
- System health
- Dependency health
- Configuration health
- Performance metrics
- Operational status

Author: LEE Development Team
Created: 2026-04-06
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=wrong-import-position
from lee.gateway import execute_operation, GatewayInterface
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def lambda_health_check_handler(event, context):
    """AWS Lambda health check handler.

    Supports multiple health check types:
    - basic: Quick health check
    - full: Comprehensive health check
    - dependencies: Check all dependencies
    - performance: Performance metrics
    - configuration: Configuration validation

    Args:
        event: Lambda event with health check type
        context: Lambda context

    Returns:
        Health check response with status and details
    """

    start_time = time.perf_counter()

    try:
        # Parse health check type
        check_type = event.get('check_type', 'basic')

        # Route to appropriate health check using dictionary dispatch
        health_check_func = _HEALTH_CHECK_DISPATCH.get(
            check_type,
            lambda: {
                'status': 'error',
                'error': f'Unknown check_type: {check_type}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
        health_result = health_check_func()

        # Add metadata
        health_result['timestamp'] = datetime.now(timezone.utc).isoformat()
        health_result['check_duration_ms'] = (time.perf_counter() - start_time) * 1000
        health_result['request_id'] = context.request_id if context else 'local'

        # Return as JSON
        return {
            'statusCode': 200 if health_result.get('status') == 'healthy' else 503,
            'headers': {
                'Content-Type': 'application/json',
                'X-Health-Status': health_result.get('status', 'unknown')
            },
            'body': json.dumps(health_result, indent=2)
        }

    except (RuntimeError, ValueError, TypeError) as e:
        # Health check itself failed
        error_result = {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'check_duration_ms': (time.perf_counter() - start_time) * 1000
        }

        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_result, indent=2)
        }


def basic_health_check() -> Dict[str, Any]:
    """Basic health check - quick system status."""

    checks = []
    all_healthy = True

    # Check 1: Lambda environment
    lambda_mode = os.environ.get('LAMBDA_MODE', 'unknown')
    checks.append({
        'name': 'lambda_environment',
        'status': 'pass' if lambda_mode in ['normal', 'test'] else 'warn',
        'value': lambda_mode
    })

    # Check 2: Gateway availability
    try:
        execute_operation(GatewayInterface.LOGGING, 'log_info', message='Health check ping')
        checks.append({'name': 'gateway', 'status': 'pass', 'value': 'available'})
    except (RuntimeError, ValueError, TypeError, ImportError) as e:
        checks.append({'name': 'gateway', 'status': 'fail', 'value': f'unavailable: {e}'})
        all_healthy = False

    # Check 3: Memory usage
    try:
        # pylint: disable=import-outside-toplevel
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        checks.append({
            'name': 'memory',
            'status': 'pass' if memory_percent < 90 else 'warn',
            'value': f'{memory_percent}% used'
        })
    except ImportError:
        checks.append({'name': 'memory', 'status': 'skip', 'value': 'psutil not available'})

    # Overall status
    overall_status = 'healthy' if all_healthy else 'unhealthy'

    return {
        'status': overall_status,
        'check_type': 'basic',
        'checks': checks,
        'summary': {
            'total': len(checks),
            'passed': sum(1 for c in checks if c['status'] == 'pass'),
            'failed': sum(1 for c in checks if c['status'] == 'fail'),
            'warned': sum(1 for c in checks if c['status'] == 'warn')
        }
    }


def full_health_check() -> Dict[str, Any]:
    """Comprehensive health check - all systems."""

    start_time = time.perf_counter()

    # Run all health checks
    basic = basic_health_check()
    dependencies = dependency_health_check()
    performance = performance_health_check()
    configuration = configuration_health_check()

    # Aggregate results
    all_checks = []
    all_checks.extend(basic.get('checks', []))
    all_checks.extend(dependencies.get('checks', []))
    all_checks.extend(performance.get('checks', []))
    all_checks.extend(configuration.get('checks', []))

    # Overall health
    failed_checks = sum(1 for c in all_checks if c['status'] == 'fail')
    overall_status = 'healthy' if failed_checks == 0 else 'unhealthy'

    return {
        'status': overall_status,
        'check_type': 'full',
        'checks': all_checks,
        'summary': {
            'total': len(all_checks),
            'passed': sum(1 for c in all_checks if c['status'] == 'pass'),
            'failed': failed_checks,
            'warned': sum(1 for c in all_checks if c['status'] == 'warn'),
            'skipped': sum(1 for c in all_checks if c['status'] == 'skip')
        },
        'details': {
            'basic': basic.get('summary'),
            'dependencies': dependencies.get('summary'),
            'performance': performance.get('details'),
            'configuration': configuration.get('summary')
        },
        'check_duration_ms': (time.perf_counter() - start_time) * 1000
    }


def dependency_health_check() -> Dict[str, Any]:
    """Check all external dependencies."""

    checks = []
    all_healthy = True

    # Check 1: Home Assistant connection
    ha_enabled = os.environ.get(
        'HOME_ASSISTANT_ENABLE', 'false'
    ).lower() == 'true'
    if ha_enabled:
        try:
            # pylint: disable=import-outside-toplevel
            from lee.home_assistant import ha_gateway
            # Try to get HA status
            ha_gateway.ha_execute_operation(HAGatewayInterface.HEALTH, 'get_status')
            checks.append({
                'name': 'home_assistant',
                'status': 'pass',
                'value': 'connected'
            })
        except (RuntimeError, ValueError, TypeError, ConnectionError, TimeoutError) as e:
            checks.append({
                'name': 'home_assistant',
                'status': 'fail',
                'value': f'disconnected: {e}'
            })
            all_healthy = False
    else:
        checks.append({
            'name': 'home_assistant',
            'status': 'skip',
            'value': 'disabled'
        })

    # Check 2: Cache system
    try:
        # pylint: disable=import-outside-toplevel
        from lee.lee_cache import cache_get, cache_set
        cache_set('health_check', 'ok', ttl=10)
        value = cache_get('health_check')
        if value == 'ok':
            checks.append({
                'name': 'cache',
                'status': 'pass',
                'value': 'operational'
            })
        else:
            checks.append({
                'name': 'cache',
                'status': 'fail',
                'value': 'not working'
            })
            all_healthy = False
    except (RuntimeError, ValueError, TypeError) as e:
        checks.append({
            'name': 'cache',
            'status': 'fail',
            'value': f'error: {e}'
        })
        all_healthy = False

    # Check 3: Circuit breaker
    try:
        # pylint: disable=import-outside-toplevel,no-name-in-module
        from lee.circuit_breaker import get_circuit_breaker
        get_circuit_breaker('test')
        checks.append({
            'name': 'circuit_breaker',
            'status': 'pass',
            'value': 'available'
        })
    except (RuntimeError, ValueError, TypeError, ImportError) as e:
        checks.append({
            'name': 'circuit_breaker',
            'status': 'fail',
            'value': f'error: {e}'
        })
        all_healthy = False

    # Check 4: Metrics system
    try:
        # pylint: disable=import-outside-toplevel,no-name-in-module
        from lee.metrics import MetricsRecorder
        MetricsRecorder()
        checks.append({
            'name': 'metrics',
            'status': 'pass',
            'value': 'available'
        })
    except (RuntimeError, ValueError, TypeError, ImportError) as e:
        checks.append({
            'name': 'metrics',
            'status': 'fail',
            'value': f'error: {e}'
        })
        all_healthy = False

    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'summary': {
            'total': len(checks),
            'passed': sum(1 for c in checks if c['status'] == 'pass'),
            'failed': sum(1 for c in checks if c['status'] == 'fail'),
            'skipped': sum(1 for c in checks if c['status'] == 'skip')
        }
    }


def performance_health_check() -> Dict[str, Any]:
    """Check performance metrics."""

    checks = []

    # Check 1: Cold start time
    cold_start_time = os.environ.get('COLD_START_TIME_MS', 'unknown')
    checks.append({
        'name': 'cold_start_time',
        'status': 'pass' if cold_start_time != 'unknown' else 'skip',
        'value': f'{cold_start_time}ms',
        'target': '<630ms'
    })

    # Check 2: Profiler stats
    try:
        stats = execute_operation(
            GatewayInterface.DEBUG, 'profiler_get_stats'
        )
        if stats:
            checks.append({
                'name': 'profiler',
                'status': 'pass',
                'value': f'{len(stats)} operations tracked'
            })
        else:
            checks.append({
                'name': 'profiler',
                'status': 'skip',
                'value': 'no stats yet'
            })
    except (RuntimeError, ValueError, TypeError, KeyError) as e:
        checks.append({
            'name': 'profiler',
            'status': 'fail',
            'value': f'error: {e}'
        })

    # Check 3: Memory pressure
    try:
        # pylint: disable=import-outside-toplevel
        import psutil
        memory = psutil.virtual_memory()
        checks.append({
            'name': 'memory_pressure',
            'status': 'pass' if memory.percent < 80 else 'warn',
            'value': f'{memory.percent}% used',
            'available': f'{memory.available / 1024 / 1024:.0f} MB'
        })
    except ImportError:
        checks.append({
            'name': 'memory_pressure',
            'status': 'skip',
            'value': 'psutil not available'
        })

    return {
        'status': 'healthy',
        'checks': checks,
        'details': {
            'profiler_stats': stats if 'stats' in locals() else None
        }
    }


def configuration_health_check() -> Dict[str, Any]:
    """Validate configuration."""

    checks = []
    all_valid = True

    # Check 1: Required environment variables
    required_vars = [
        'LAMBDA_MODE',
        'HOME_ASSISTANT_ENABLE'
    ]

    for var in required_vars:
        if os.environ.get(var):
            checks.append({
                'name': f'env_var_{var}',
                'status': 'pass',
                'value': 'set'
            })
        else:
            checks.append({
                'name': f'env_var_{var}',
                'status': 'fail',
                'value': 'missing'
            })
            all_valid = False

    # Check 2: HA configuration
    if os.environ.get('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true':
        ha_url = os.environ.get('HOME_ASSISTANT_URL')
        if ha_url:
            checks.append({
                'name': 'ha_config',
                'status': 'pass',
                'value': f'URL: {ha_url}'
            })
        else:
            checks.append({
                'name': 'ha_config',
                'status': 'fail',
                'value': 'HA_URL missing'
            })
            all_valid = False

    return {
        'status': 'healthy' if all_valid else 'unhealthy',
        'checks': checks,
        'summary': {
            'total': len(checks),
            'passed': sum(1 for c in checks if c['status'] == 'pass'),
            'failed': sum(1 for c in checks if c['status'] == 'fail')
        }
    }


# Health check dispatch dictionary (O(1) lookup)
# Defined after all health check functions to avoid forward reference issues
_HEALTH_CHECK_DISPATCH = {
    'basic': basic_health_check,
    'full': full_health_check,
    'dependencies': dependency_health_check,
    'performance': performance_health_check,
    'configuration': configuration_health_check,
}


# For local testing
if __name__ == '__main__':
    # Test health check
    class MockContext:  # pylint: disable=missing-class-docstring
        request_id = 'test-request-123'

    test_event = {'check_type': 'basic'}
    result = lambda_health_check_handler(test_event, MockContext())
    print(json.dumps(json.loads(result['body']), indent=2))
