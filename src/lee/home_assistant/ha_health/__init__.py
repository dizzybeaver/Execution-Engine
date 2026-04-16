# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_health - Home Assistant Health Monitoring Interface
Version: 1.0.0
Description: Core implementation for Home Assistant health monitoring and diagnostics

This module provides the core health monitoring functionality including:
- System health checks
- Component status monitoring
- Performance diagnostics
- Connectivity testing

Architecture: home_assistant.ha_gateway → home_assistant.interface.ha_health → home_assistant.ha_health.core

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# Core implementation imports
from lee.home_assistant.ha_health.ha_health_generic import (
    check_component_health_impl,
    check_system_health_impl,
    get_diagnostic_info_impl,
    get_performance_report_impl,
    test_connectivity_impl,
)

__all__ = [
    # Core implementations
    "check_system_health_impl",
    "check_component_health_impl",
    "get_performance_report_impl",
    "get_diagnostic_info_impl",
    "test_connectivity_impl",
]
