"""system_collector.py - System Information Collection
Version: 2026-03-18
Purpose: Collect and return system information
License: Apache 2.0
"""

import os
import platform
import sys
from typing import Any


def _get_system_info_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get comprehensive system information."""
    info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "architecture": platform.architecture(),
        "hostname": platform.node(),
        "environment": dict(os.environ),
    }
    return info


def _get_platform_info_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get platform-specific information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "platform": platform.platform(),
    }


def _get_python_info_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get Python runtime information."""
    return {
        "version": sys.version,
        "version_info": sys.version_info,
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "path": sys.path,
        "api_version": sys.api_version,
    }


__all__ = [
    "_get_system_info_implementation",
    "_get_platform_info_implementation",
    "_get_python_info_implementation",
]
