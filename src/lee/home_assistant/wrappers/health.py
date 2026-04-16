"""Health Wrapper Functions Namespace

5 functions for health monitoring.

Usage:
    from lee.home_assistant.wrappers import health

    # Check component health
    health_status = health.check_component_health(component='homeassistant')

    # Check system health
    system_health = health.check_system_health()

    # Get diagnostic info
    diagnostics = health.get_diagnostic_info(component='homeassistant')

    # Get performance report
    report = health.get_performance_report(component='homeassistant')

    # Test connectivity
    result = health.test_connectivity(url='http://localhost:8123')
"""

# Import all health wrapper functions
from lee.home_assistant.interface.wrappers.ha_health_wrappers import (
    check_component_health,
    check_system_health,
    get_diagnostic_info,
    get_performance_report,
    test_connectivity,
)

__all__ = [
    'check_component_health',
    'check_system_health',
    'get_diagnostic_info',
    'get_performance_report',
    'test_connectivity',
]
